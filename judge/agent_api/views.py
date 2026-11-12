import json
import logging

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from judge.agent_api.actions import ACTIONS
from judge.agent_api.core import AgentError, validate_args

logger = logging.getLogger('judge.agent_api')


def _error(message, status):
    return JsonResponse({'error': {'code': status, 'message': message}}, status=status)


def _authenticate(request):
    if not request.headers.get('authorization', '').startswith('Bearer ') or not request.user.is_authenticated:
        return _error('A Bearer API token is required.', 401)
    return None


def _over_rate_limit(user):
    limit = settings.VNOJ_AGENT_API_WRITE_LIMIT
    if not limit:
        return False
    key = 'agent_api_writes:%d:%d' % (user.id, int(timezone.now().timestamp() // 60))
    cache.add(key, 0, timeout=60)
    return cache.incr(key) > limit


@require_GET
def capabilities(request):
    error = _authenticate(request)
    if error:
        return error
    return JsonResponse({'data': {
        'username': request.user.username,
        'actions': [act.schema() for act in ACTIONS.values() if act.is_allowed(request.user)],
    }})


@require_GET
def openapi(request):
    paths = {}
    for act in ACTIONS.values():
        schema = act.schema()
        paths[reverse('agent_api_action', args=[act.name])] = {'post': {
            'operationId': act.name,
            'description': act.description,
            'requestBody': {
                'required': bool(act.required),
                'content': {'application/json': {'schema': schema['input_schema']}},
            },
            'responses': {'200': {'description': 'The action result, under "data".'}},
        }}
    return JsonResponse({
        'openapi': '3.1.0',
        'info': {'title': '%s agent API' % settings.SITE_NAME, 'version': '1'},
        'servers': [{'url': request.build_absolute_uri('/').rstrip('/')}],
        'components': {'securitySchemes': {'bearer': {'type': 'http', 'scheme': 'bearer'}}},
        'security': [{'bearer': []}],
        'paths': paths,
    })


@require_POST
def run_action(request, name):
    error = _authenticate(request)
    if error:
        return error

    act = ACTIONS.get(name)
    if act is None:
        return _error('Unknown action "%s".' % name, 404)
    if not act.is_allowed(request.user):
        return _error('Permission denied.', 403)

    try:
        args = json.loads(request.body or b'{}')
        validate_args(act, args)
        if not act.read_only and _over_rate_limit(request.user):
            raise AgentError('Too many write actions. Try again in a minute.', 429)
        result = act.func(request, **args)
    except json.JSONDecodeError:
        return _error('Request body must be JSON.', 400)
    except AgentError as e:
        if not act.read_only:
            logger.info('Agent action %s by %s failed: %s', name, request.user.username, e.message)
        return JsonResponse({'error': e.as_dict()}, status=e.status)

    if not act.read_only:
        logger.info('Agent action %s by %s succeeded: %s', name, request.user.username, result)
    return JsonResponse({'data': result})
