import time

from judge.agent_api.core import AgentError, action, call_view, json_body, redirect_target
from judge.jinja2.submission import submission_result_hidden
from judge.models import Language

PARTICIPANT = 'participant'
PENDING_STATUSES = ('QU', 'P', 'G')
MAX_WAIT = 60

_PAGE = {'type': 'integer', 'description': 'Page number, starting at 1.'}


def _iso(value):
    return value.isoformat() if value else None


def _page_info(context):
    page = context.get('page_obj')
    if page is None:
        return {}
    return {'page': page.number, 'has_next': page.has_next()}


def _submission_summary(submission, user):
    data = {
        'id': submission.id,
        'problem': submission.problem.code,
        'language': submission.language.key,
        'date': _iso(submission.date),
        'contest': submission.contest_object.key if submission.contest_object_id else None,
        'status': submission.status,
    }
    if submission_result_hidden(submission, user):
        data['result_hidden'] = True
    else:
        data.update(result=submission.result, points=submission.points, time=submission.time,
                    memory=submission.memory)
    return data


@action('me', 'Show the account the agent is acting as: profile, current contest and granted permissions.',
        PARTICIPANT, read_only=True)
def me(request):
    profile = request.profile
    participation = profile.current_contest
    return {
        'username': request.user.username,
        'display_name': profile.display_name,
        'points': profile.points,
        'performance_points': profile.performance_points,
        'problem_count': profile.problem_count,
        'rating': profile.rating,
        'is_unlisted': profile.is_unlisted,
        'preferred_language': profile.language.key,
        'current_contest': {
            'key': participation.contest.key,
            'virtual': participation.virtual,
            'spectating': participation.spectate,
            'ends_at': _iso(participation.end_time),
        } if participation else None,
        'permissions': sorted(request.user.get_all_permissions()),
    }


@action('list_problems', 'List problems visible to the user. Inside a contest, this lists the contest problems.',
        PARTICIPANT, read_only=True, params={
            'search': {'type': 'string', 'description': 'Search in problem code, name and source.'},
            'type': {'type': 'integer', 'description': 'Filter by problem type ID (see get_problem output).'},
            'min_points': {'type': 'number'},
            'max_points': {'type': 'number'},
            'hide_solved': {'type': 'boolean'},
            'page': _PAGE,
        })
def list_problems(request, search=None, type=None, min_points=None, max_points=None, hide_solved=None, page=None):
    response = call_view(request, 'problem_list', query={
        'search': search, 'type': type, 'point_start': min_points, 'point_end': max_points,
        'hide_solved': None if hide_solved is None else int(hide_solved), 'page': page,
    })
    context = response.context_data
    completed = set(context.get('completed_problem_ids') or ())
    return {
        'problems': [{
            'code': problem.code,
            'name': getattr(problem, 'i18n_name', None) or problem.name,
            'points': problem.points,
            'partial': problem.partial,
            'ac_rate': getattr(problem, 'ac_rate', None),
            'user_count': getattr(problem, 'user_count', None),
            'solved': problem.id in completed,
        } for problem in context['problems']],
        **_page_info(context),
    }


@action('get_problem', 'Get a problem statement (markdown), limits, allowed languages and how many submissions '
        'are left in the current contest.', PARTICIPANT, read_only=True, params={
            'code': {'type': 'string', 'description': 'Problem code.'},
        }, required=['code'])
def get_problem(request, code):
    context = call_view(request, 'problem_detail', args=[code]).context_data
    problem = context['problem']
    contest_problem = context.get('contest_problem')
    limits = context.get('language_limits') or {}
    form = context.get('form')
    languages = form.fields['language'].queryset if form is not None else problem.usable_languages
    data = {
        'code': problem.code,
        'name': context['title'],
        'statement': context['description'],
        'statement_language': context['language'],
        'time_limit': problem.time_limit,
        'memory_limit_kb': problem.memory_limit,
        'points': contest_problem.points if contest_problem else problem.points,
        'partial': contest_problem.partial if contest_problem else problem.partial,
        'io_method': problem.io_method,
        'languages': [{
            'key': language.key,
            'name': language.name,
            **({'time_limit': limits[language.id].time_limit,
                'memory_limit_kb': limits[language.id].memory_limit} if language.id in limits else {}),
        } for language in languages],
        'contest': contest_problem.contest.key if contest_problem else None,
        'submissions_left': context.get('submissions_left'),
        'solved': problem.id in (context.get('completed_problem_ids') or ()),
    }
    if not contest_problem or not contest_problem.contest.hide_problem_tags:
        data['types'] = [{'id': t.id, 'name': t.full_name} for t in problem.types.all()]
    if not contest_problem or not contest_problem.contest.hide_problem_authors:
        data['authors'] = [author.username for author in problem.authors.all()]
    editorial = context.get('editorial')
    data['has_editorial'] = bool(editorial and editorial.is_accessible_by(request.user) and not request.in_contest)
    return data


@action('get_editorial', 'Get the editorial of a problem, if the user can see it.', PARTICIPANT, read_only=True,
        params={'code': {'type': 'string', 'description': 'Problem code.'}}, required=['code'])
def get_editorial(request, code):
    context = call_view(request, 'problem_editorial', args=[code]).context_data
    solution = context.get('solution')
    if solution is None:
        return {'code': code, 'editorial': None}
    return {'code': code, 'editorial': solution.content, 'publish_on': _iso(solution.publish_on)}


@action('submit_solution', 'Submit source code to a problem. Returns the submission ID; judging runs in the '
        'background, so use get_submission to read the result.', PARTICIPANT, read_only=False, params={
            'problem': {'type': 'string', 'description': 'Problem code.'},
            'language': {'type': 'string', 'description': 'Language key, e.g. CPP17 or PY3 (see get_problem).'},
            'source': {'type': 'string', 'description': 'Full source code.'},
        }, required=['problem', 'language', 'source'])
def submit_solution(request, problem, language, source):
    try:
        language_id = Language.objects.values_list('id', flat=True).get(key=language)
    except Language.DoesNotExist:
        raise AgentError('Unknown language "%s".' % language, errors={'language': ['Unknown language key.']})
    response = call_view(request, 'problem_submit', args=[problem], method='POST',
                         data={'language': language_id, 'source': source, 'judge': ''})
    _, kwargs = redirect_target(response)
    return {'submission_id': kwargs['submission']}


@action('get_submission', 'Get the status and result of a submission, including per-test-case results when the '
        'problem shows them. Status QU/P/G means it is still judging; pass wait to block until judging finishes.',
        PARTICIPANT, read_only=True, params={
            'id': {'type': 'integer', 'description': 'Submission ID.'},
            'wait': {'type': 'integer', 'description': 'Seconds to wait for judging to finish (max %d).' % MAX_WAIT},
        }, required=['id'])
def get_submission(request, id, wait=None):
    deadline = time.monotonic() + min(max(wait or 0, 0), MAX_WAIT)
    while True:
        data = _submission_status(request, id)
        if (data['status'] not in PENDING_STATUSES and data['is_graded']) or time.monotonic() >= deadline:
            return data
        time.sleep(1)


def _submission_status(request, id):
    context = call_view(request, 'submission_status', args=[id]).context_data
    submission = context['submission']
    data = {
        'id': submission.id,
        'problem': submission.problem.code,
        'language': submission.language.key,
        'date': _iso(submission.date),
        'contest': submission.contest_object.key if submission.contest_object_id else None,
        'status': submission.status,
        'is_graded': submission.is_graded,
    }
    if context['result_hidden']:
        data['result_hidden'] = True
        return data

    data.update(result=submission.result, points=submission.points, total=submission.problem.points,
                time=submission.time, memory_kb=submission.memory, time_limit=context['time_limit'])
    if submission.status == 'CE':
        data['compile_error'] = submission.error
        return data
    if submission.error:
        data['compile_warnings'] = submission.error

    show_cases = context['can_view_testcase_status']
    if show_cases or context['can_view_batch_status']:
        batches = []
        for batch in context['batches']:
            entry = {}
            if batch['id']:
                entry.update(batch=batch['id'], points=batch.get('points'), total=batch.get('total'))
                if not show_cases:
                    entry['status'] = batch.get('status')
            if show_cases:
                entry['cases'] = [{
                    'case': case.case,
                    'status': case.status,
                    'time': case.time,
                    'memory_kb': case.memory,
                    'points': case.points,
                    'total': case.total,
                    'feedback': case.feedback,
                } for case in batch['cases']]
            batches.append(entry)
        data['batches'] = batches
    return data


@action('list_my_submissions', "List the user's own submissions, newest first, optionally for one problem.",
        PARTICIPANT, read_only=True, params={
            'problem': {'type': 'string', 'description': 'Problem code.'},
            'page': _PAGE,
        })
def list_my_submissions(request, problem=None, page=None):
    username = request.user.username
    if problem:
        response = call_view(request, 'user_submissions', args=[problem, username], query={'page': page})
    else:
        response = call_view(request, 'all_user_submissions', args=[username], query={'page': page})
    context = response.context_data
    return {
        'submissions': [_submission_summary(s, request.user) for s in context['submissions']],
        **_page_info(context),
    }


def _contest_summary(contest):
    return {
        'key': contest.key,
        'name': contest.name,
        'start_time': _iso(contest.start_time),
        'end_time': _iso(contest.end_time),
        'window': str(contest.time_limit) if contest.time_limit else None,
        'format': contest.format_name,
        'is_rated': contest.is_rated,
        'requires_access_code': bool(contest.access_code),
    }


@action('list_contests', 'List contests: the ones the user is in, ongoing, upcoming and past (paginated).',
        PARTICIPANT, read_only=True, params={
            'search': {'type': 'string', 'description': 'Search past contests by name or key.'},
            'page': _PAGE,
        })
def list_contests(request, search=None, page=None):
    context = call_view(request, 'contest_list', query={'search': search, 'page': page}).context_data
    return {
        'participating': [_contest_summary(p.contest) for p in context['active_participations']],
        'ongoing': [_contest_summary(c) for c in context['current_contests']],
        'upcoming': [_contest_summary(c) for c in context['future_contests']],
        'past': [_contest_summary(c) for c in context['past_contests']],
        **_page_info(context),
    }


@action('get_contest', 'Get contest details, announcements, and its problems (shown once the user is in the '
        'contest or it has ended).', PARTICIPANT, read_only=True, params={
            'key': {'type': 'string', 'description': 'Contest key.'},
        }, required=['key'])
def get_contest(request, key):
    context = call_view(request, 'contest_view', args=[key]).context_data
    contest = context['contest']
    data = {
        **_contest_summary(contest),
        'summary': contest.summary,
        'description': contest.description,
        'require_registration': contest.require_registration,
        'can_join': contest.can_join,
        'ended': contest.ended,
        'has_joined': context['has_joined'],
        'is_in_contest': context['is_in_contest'],
        'announcements': [{'title': a.title, 'body': a.description, 'date': _iso(a.date)}
                          for a in context['announcements']],
    }
    if context['is_in_contest'] or contest.ended or request.user.is_superuser or \
            context['is_editor'] or context['is_tester']:
        completed = set(context['completed_problem_ids'])
        attempted = set(context['attempted_problem_ids'])
        problems = []
        for index, problem in enumerate(context['contest_problems']):
            entry = {
                'label': contest.get_label_for_problem(index),
                'code': problem.code if context['can_view_all_problems'] or problem.is_public else None,
                'name': problem.i18n_name or problem.name,
                'points': problem.points,
                'time_limit': problem.time_limit,
                'memory_limit_kb': problem.memory_limit,
            }
            if not context['result_hidden']:
                entry['solved'] = problem.id in completed
                entry['attempted'] = problem.id in attempted
            problems.append(entry)
        data['problems'] = problems
    return data


@action('get_contest_ranking', "Get the contest scoreboard (top rows plus the user's own row), as the user is "
        'allowed to see it.', PARTICIPANT, read_only=True, params={
            'key': {'type': 'string', 'description': 'Contest key.'},
            'limit': {'type': 'integer', 'description': 'Number of top rows to return (default 20).'},
        }, required=['key'])
def get_contest_ranking(request, key, limit=20):
    data = json_body(call_view(request, 'contest_ranking', args=[key], query={'data': 1}))
    username = request.user.username
    rows = []
    for index, participation in enumerate(data['participations']):
        user = participation.get('user') or {}
        if index < limit or user.get('username') == username:
            rows.append({
                'rank': participation.get('rank'),
                'username': user.get('username'),
                'score': participation.get('score'),
                'cumtime': participation.get('cumtime'),
                'problems': participation.get('format_data'),
            })
    return {
        'contest': {k: data['contest'].get(k) for k in ('key', 'format', 'ended', 'result_hidden', 'is_frozen')},
        'problems': [{'id': p['id'], 'label': p['label'], 'code': p['code'], 'points': p['points']}
                     for p in data['problems']],
        'total_rows': len(data['participations']),
        'rows': rows,
    }


_ENTRY_PARAMS = {
    'key': {'type': 'string', 'description': 'Contest key.'},
    'access_code': {'type': 'string', 'description': 'Access code, if the contest requires one.'},
    'agree_terms': {'type': 'boolean', 'description': 'Agree to the contest terms, if it has any.'},
}


@action('register_contest', 'Register for a contest that requires registration.', PARTICIPANT, read_only=False,
        params=_ENTRY_PARAMS, required=['key'])
def register_contest(request, key, access_code=None, agree_terms=False):
    call_view(request, 'contest_register', args=[key], method='POST',
              data={'access_code': access_code, 'terms_agreed': agree_terms})
    return {'registered': key}


@action('join_contest', 'Join an ongoing contest, or start a virtual participation if it has ended. While in a '
        'contest, submissions count for it.', PARTICIPANT, read_only=False, params=_ENTRY_PARAMS, required=['key'])
def join_contest(request, key, access_code=None, agree_terms=False):
    call_view(request, 'contest_join', args=[key], method='POST',
              data={'access_code': access_code, 'terms_agreed': agree_terms})
    request.profile.refresh_from_db()
    participation = request.profile.current_contest
    if participation is None or participation.contest.key != key:
        raise AgentError('Could not join the contest. It may require an access code or agreeing to its terms.')
    return {'joined': key, 'virtual': participation.virtual, 'spectating': participation.spectate,
            'ends_at': _iso(participation.end_time)}


@action('leave_contest', 'Leave the contest the user is currently in.', PARTICIPANT, read_only=False,
        params={'key': {'type': 'string', 'description': 'Contest key.'}}, required=['key'])
def leave_contest(request, key):
    call_view(request, 'contest_leave', args=[key], method='POST')
    return {'left': key}


@action('list_tickets', 'List tickets the user can see (their own, or ones assigned to them).', PARTICIPANT,
        read_only=True, params={
            'open_only': {'type': 'boolean'},
            'own_only': {'type': 'boolean'},
            'page': _PAGE,
        })
def list_tickets(request, open_only=False, own_only=False, page=None):
    context = call_view(request, 'ticket_list', query={
        'open': int(open_only), 'own': int(own_only), 'page': page,
    }).context_data
    return {
        'tickets': [{
            'id': ticket.id,
            'title': ticket.title,
            'user': ticket.user.username,
            'is_open': ticket.is_open,
            'time': _iso(ticket.time),
            'linked_item': str(ticket.linked_item),
        } for ticket in context['tickets']],
        **_page_info(context),
    }


@action('get_ticket', 'Get a ticket and its messages.', PARTICIPANT, read_only=True,
        params={'id': {'type': 'integer', 'description': 'Ticket ID.'}}, required=['id'])
def get_ticket(request, id):
    context = call_view(request, 'ticket', args=[id]).context_data
    ticket = context['ticket']
    return {
        'id': ticket.id,
        'title': ticket.title,
        'user': ticket.user.username,
        'is_open': ticket.is_open,
        'linked_item': str(ticket.linked_item),
        'assignees': [a.username for a in context['assignees']],
        'messages': [{
            'user': message.user.username,
            'time': _iso(message.time),
            'action': message.action,
            'body': message.body,
        } for message in context['ticket_messages']],
    }


_TICKET_PARAMS = {
    'title': {'type': 'string', 'description': 'Short title (max 100 characters).'},
    'body': {'type': 'string', 'description': 'Description, in markdown.'},
}


@action('create_problem_ticket', "Open a ticket about a problem (e.g. an unclear statement). It goes to the "
        "problem's authors, or the contest's authors during a contest.", PARTICIPANT, read_only=False, params={
            'problem': {'type': 'string', 'description': 'Problem code.'},
            **_TICKET_PARAMS,
        }, required=['problem', 'title', 'body'])
def create_problem_ticket(request, problem, title, body):
    response = call_view(request, 'new_problem_ticket', args=[problem], method='POST',
                         data={'title': title, 'body': body})
    return {'ticket_id': redirect_target(response)[1]['pk']}


@action('create_issue_ticket', 'Open a general ticket about an issue on the site.', PARTICIPANT, read_only=False,
        params={
            **_TICKET_PARAMS,
            'issue_url': {'type': 'string', 'description': 'Link to the page the issue is about.'},
        }, required=['title', 'body', 'issue_url'])
def create_issue_ticket(request, title, body, issue_url):
    response = call_view(request, 'new_issue_ticket', method='POST',
                         data={'title': title, 'body': body, 'issue_url': issue_url}, query={'issue_url': issue_url})
    return {'ticket_id': redirect_target(response)[1]['pk']}


@action('reply_ticket', 'Post a reply on a ticket.', PARTICIPANT, read_only=False, params={
    'id': {'type': 'integer', 'description': 'Ticket ID.'},
    'body': {'type': 'string', 'description': 'Reply, in markdown.'},
}, required=['id', 'body'])
def reply_ticket(request, id, body):
    call_view(request, 'ticket', args=[id], method='POST', data={'body': body})
    return {'ticket_id': id}


@action('set_ticket_open', 'Close or reopen a ticket.', PARTICIPANT, read_only=False, params={
    'id': {'type': 'integer', 'description': 'Ticket ID.'},
    'open': {'type': 'boolean', 'description': 'true to reopen, false to close.'},
}, required=['id', 'open'])
def set_ticket_open(request, id, open):
    call_view(request, 'ticket_open' if open else 'ticket_close', args=[id], method='POST')
    return {'ticket_id': id, 'is_open': open}


@action('list_notifications', "List the user's notifications, newest first.", PARTICIPANT, read_only=True, params={
    'unread_only': {'type': 'boolean'},
    'page': _PAGE,
})
def list_notifications(request, unread_only=False, page=None):
    context = call_view(request, 'notification_list', query={
        'status': 'unread' if unread_only else 'all', 'page': page,
    }).context_data
    return {
        'notifications': [{
            'id': n.id,
            'title': n.title,
            'body': n.body,
            'url': n.url,
            'time': _iso(n.time),
            'read': n.read,
        } for n in context['notifications']],
        **_page_info(context),
    }


@action('mark_notifications_read', 'Mark one notification, or all of them, as read.', PARTICIPANT, read_only=False,
        params={'id': {'type': 'integer', 'description': 'Notification ID. Omit to mark all as read.'}})
def mark_notifications_read(request, id=None):
    data = {'all': '1'} if id is None else {'id': id, 'read': '1'}
    return json_body(call_view(request, 'notification_mark_read', method='POST', data=data))
