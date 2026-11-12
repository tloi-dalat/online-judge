import copy
import json
from dataclasses import dataclass
from typing import Callable, Optional

from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse, QueryDict
from django.http.response import HttpResponseRedirectBase
from django.template.response import TemplateResponse
from django.urls import resolve, reverse
from django.utils.datastructures import MultiValueDict
from django.utils.html import strip_tags


class AgentError(Exception):
    def __init__(self, message, status=400, errors=None):
        super().__init__(message)
        self.message = str(message)
        self.status = status
        self.errors = errors

    def as_dict(self):
        error = {'code': self.status, 'message': self.message}
        if self.errors:
            error['fields'] = self.errors
        return error


@dataclass(frozen=True)
class Action:
    name: str
    func: Callable
    description: str
    toolset: str
    read_only: bool
    params: dict
    required: tuple
    destructive: bool = False
    permission: Optional[str] = None

    def is_allowed(self, user):
        return self.permission is None or user.has_perm(self.permission)

    def schema(self):
        return {
            'name': self.name,
            'description': self.description,
            'toolset': self.toolset,
            'read_only': self.read_only,
            'destructive': self.destructive,
            'input_schema': {
                'type': 'object',
                'properties': self.params,
                'required': list(self.required),
                'additionalProperties': False,
            },
        }


ACTIONS = {}


def action(name, description, toolset, read_only, params=None, required=(), destructive=False, permission=None):
    def decorator(func):
        ACTIONS[name] = Action(
            name=name, func=func, description=description, toolset=toolset, read_only=read_only,
            params=params or {}, required=tuple(required), destructive=destructive, permission=permission,
        )
        return func
    return decorator


_JSON_TYPES = {
    'string': (str,),
    'integer': (int,),
    'number': (int, float),
    'boolean': (bool,),
}


def validate_args(act, args):
    if not isinstance(args, dict):
        raise AgentError('Arguments must be a JSON object.')
    unknown = set(args) - set(act.params)
    if unknown:
        raise AgentError('Unknown argument(s): %s.' % ', '.join(sorted(unknown)))
    missing = [name for name in act.required if args.get(name) in (None, '')]
    if missing:
        raise AgentError('Missing required argument(s): %s.' % ', '.join(missing))
    for name, value in args.items():
        expected = _JSON_TYPES.get(act.params[name].get('type'))
        if value is not None and expected and (not isinstance(value, expected) or
                                               (isinstance(value, bool) and bool not in expected)):
            raise AgentError('Argument "%s" must be of type %s.' % (name, act.params[name]['type']))


def _query_dict(values):
    result = QueryDict(mutable=True)
    for key, value in (values or {}).items():
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            result.setlist(key, [str(v) for v in value])
        elif isinstance(value, bool):
            result[key] = 'on' if value else ''
        else:
            result[key] = str(value)
    return result


_STATUS_MESSAGES = {
    403: 'Permission denied.',
    404: 'Not found.',
    405: 'Method not allowed.',
    429: 'Too many requests.',
}


def call_view(request, url_name, args=(), method='GET', data=None, query=None):
    path = reverse(url_name, args=args)
    match = resolve(path)

    sub = copy.copy(request)
    sub.method = method
    sub.path = sub.path_info = path
    sub.resolver_match = match
    sub.GET = _query_dict(query)
    sub.POST = _query_dict(data)
    sub._files = MultiValueDict()
    sub.META = {**request.META, 'REQUEST_METHOD': method, 'QUERY_STRING': sub.GET.urlencode()}

    try:
        response = match.func(sub, *match.args, **match.kwargs)
    except Http404:
        raise AgentError(_STATUS_MESSAGES[404], 404)
    except PermissionDenied as e:
        raise AgentError(str(e) or _STATUS_MESSAGES[403], 403)

    if isinstance(response, HttpResponseRedirectBase) or response.status_code == 204:
        return response

    title = getattr(response, 'agent_title', None)
    if title is not None:
        message = strip_tags(str(getattr(response, 'agent_message', ''))).strip()
        status = response.status_code if response.status_code >= 400 else 400
        raise AgentError('%s: %s' % (title, message) if message else title, status)

    if isinstance(response, TemplateResponse):
        form = (response.context_data or {}).get('form')
        if form is not None and form.is_bound and form.errors:
            errors = {field: [e['message'] for e in errs] for field, errs in form.errors.get_json_data().items()}
            raise AgentError('Invalid input.', 400, errors=errors)

    if response.status_code >= 400:
        text = strip_tags(response.content.decode('utf-8', 'replace')).strip()
        if not text or len(text) > 300:
            text = _STATUS_MESSAGES.get(response.status_code, 'Request failed.')
        raise AgentError(text, response.status_code)

    if isinstance(response, (TemplateResponse, JsonResponse)):
        return response

    raise AgentError('The site did not complete the action. Check the inputs and try again.')


def json_body(response):
    return json.loads(response.content)


def redirect_target(response):
    match = resolve(response.url.split('#')[0].split('?')[0])
    return match.url_name, match.kwargs
