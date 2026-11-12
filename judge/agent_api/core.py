import copy
import datetime
import json
from dataclasses import dataclass
from typing import Callable

from django import forms
from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse, QueryDict
from django.http.response import HttpResponseRedirectBase
from django.template.response import TemplateResponse
from django.urls import resolve, reverse
from django.utils.datastructures import MultiValueDict
from django.utils.duration import duration_string
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
    permission: tuple = ()

    def is_allowed(self, user):
        return not self.permission or any(user.has_perm(perm) for perm in self.permission)

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


def action(name, description, toolset, read_only, params=None, required=(), destructive=False, permission=()):
    def decorator(func):
        ACTIONS[name] = Action(
            name=name, func=func, description=description, toolset=toolset, read_only=read_only,
            params=params or {}, required=tuple(required), destructive=destructive,
            permission=(permission,) if isinstance(permission, str) else tuple(permission),
        )
        return func
    return decorator


_JSON_TYPES = {
    'string': (str,),
    'integer': (int,),
    'number': (int, float),
    'boolean': (bool,),
    'object': (dict,),
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

    if response.status_code >= 400:
        text = strip_tags(response.content.decode('utf-8', 'replace')).strip()
        if not text or len(text) > 300:
            text = _STATUS_MESSAGES.get(response.status_code, 'Request failed.')
        raise AgentError(text, response.status_code)

    if method == 'GET' or isinstance(response, JsonResponse):
        return response

    if isinstance(response, TemplateResponse):
        errors = _form_errors(response.context_data or {})
        if errors:
            raise AgentError('Invalid input.', 400, errors=errors)
    elif not response.get('Content-Type', '').startswith('text/html') or not _is_full_page(response):
        return response

    raise AgentError('The site did not complete the action. Check the inputs and try again.')


def _is_full_page(response):
    start = response.content[:2000].lower()
    return b'<html' in start or b'<!doctype' in start


def json_body(response):
    return json.loads(response.content)


def redirect_target(response):
    match = resolve(response.url.split('#')[0].split('?')[0])
    return match.url_name, match.kwargs


def _context_forms(context):
    for key, value in context.items():
        if isinstance(value, forms.BaseForm) and key != 'comment_form':
            yield value
        elif isinstance(value, forms.BaseFormSet):
            yield value.management_form
            yield from value.forms


def _form_errors(context):
    errors = {}
    for value in context.values():
        if isinstance(value, forms.BaseFormSet) and value.is_bound and value.non_form_errors():
            errors[value.prefix] = list(value.non_form_errors())
    forms_with_comment = list(_context_forms(context))
    if isinstance(context.get('comment_form'), forms.BaseForm):
        forms_with_comment.append(context['comment_form'])
    for form in forms_with_comment:
        if form.is_bound:
            for field, field_errors in form.errors.get_json_data().items():
                key = form.add_prefix(field) if field != '__all__' else (form.prefix or '__all__')
                errors[key] = [e['message'] for e in field_errors]
    return errors


def _encode(field, value):
    if isinstance(field, forms.FileField):
        return None
    if isinstance(field, forms.NullBooleanField):
        return {True: 'true', False: 'false'}.get(value, 'unknown')
    if isinstance(field, forms.BooleanField):
        return 'on' if value else None
    if isinstance(field, (forms.MultipleChoiceField, forms.ModelMultipleChoiceField)) and value in (None, ''):
        return []
    if value is None:
        return ''
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    if isinstance(value, (datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, datetime.timedelta):
        return duration_string(value)
    return str(value)


_FIELD_TYPES = (
    (forms.FileField, 'file (not supported)'),
    (forms.BooleanField, 'boolean'),
    (forms.ModelMultipleChoiceField, 'list of IDs'),
    (forms.ModelChoiceField, 'ID'),
    (forms.MultipleChoiceField, 'list of choices'),
    (forms.ChoiceField, 'choice'),
    (forms.IntegerField, 'integer'),
    (forms.FloatField, 'number'),
    (forms.DecimalField, 'number'),
    (forms.DateTimeField, 'datetime (ISO 8601)'),
    (forms.DateField, 'date (YYYY-MM-DD)'),
    (forms.DurationField, 'duration ([DD] [[HH:]MM:]SS)'),
)

_MAX_CHOICES = 100


def _field_type(field):
    return next((name for cls, name in _FIELD_TYPES if isinstance(field, cls)), 'string')


def _choices(field):
    if isinstance(field, forms.ModelChoiceField):
        if field.queryset.count() > _MAX_CHOICES:
            return None
    elif not isinstance(field, forms.ChoiceField) or len(field.choices) > _MAX_CHOICES:
        return None
    return [[str(value), str(label)] for value, label in field.choices if value != '']


def describe_forms(context):
    fields = []
    for form in _context_forms(context):
        for bound in form:
            field = bound.field
            entry = {
                'name': bound.html_name,
                'label': str(bound.label),
                'type': _field_type(field),
                'required': field.required,
                'value': _encode(field, bound.value()),
            }
            if field.help_text:
                entry['help'] = strip_tags(str(field.help_text))[:200]
            choices = _choices(field)
            if choices is not None:
                entry['choices'] = choices
            fields.append(entry)
    formsets = [{
        'prefix': value.prefix,
        'total_forms_field': value.management_form.add_prefix('TOTAL_FORMS'),
        'new_row_fields': [bound.html_name for bound in value.empty_form],
    } for value in context.values() if isinstance(value, forms.BaseFormSet)]
    return {'fields': fields, 'formsets': formsets}


def form_data(context):
    data = {}
    for form in _context_forms(context):
        for bound in form:
            value = _encode(bound.field, bound.value())
            if value is not None:
                data[bound.html_name] = value
    return data
