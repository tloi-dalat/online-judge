import time

from judge.agent_api.core import ACTIONS, AgentError, action, call_view, describe_forms, form_data, json_body, \
    redirect_target
from judge.jinja2.submission import submission_result_hidden
from judge.models import Comment, Language, Profile

__all__ = ['ACTIONS']

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
            'id': problem.id,
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
        'id': problem.id,
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
                'participation_id': participation.get('id'),
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
    if not request.profile.contest_history.filter(contest__key=key, virtual=0).exists():
        raise AgentError('Could not register. The contest may require an access code or agreeing to its terms.')
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


@action('create_problem_ticket', 'Open a ticket about a problem (e.g. an unclear statement). It goes to the '
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


COMMUNITY = 'community'
AUTHOR = 'author'
MODERATOR = 'moderator'

_COMMENT_PAGES = {
    'problem': lambda target: ('problem_comments', [target]),
    'editorial': lambda target: ('problem_editorial_comments', [target]),
    'contest': lambda target: ('contest_comments', [target]),
    'blog': lambda target: ('blog_post_comments', [int(target), 'post']),
}

_COMMENT_TARGET = {
    'on': {'type': 'string', 'enum': sorted(_COMMENT_PAGES),
           'description': 'What the comments are on: a problem, its editorial, a contest or a blog post.'},
    'target': {'type': 'string', 'description': 'Problem code, contest key or blog post ID.'},
}


def _comment_page(on, target):
    if on not in _COMMENT_PAGES:
        raise AgentError('"on" must be one of: %s.' % ', '.join(sorted(_COMMENT_PAGES)))
    try:
        return _COMMENT_PAGES[on](target)
    except ValueError:
        raise AgentError('Blog post target must be a numeric ID.')


def _vote_direction(direction):
    if direction not in ('up', 'down'):
        raise AgentError('direction must be "up" or "down".')
    return direction


@action('list_comments', 'List the comments on a problem, editorial, contest or blog post (newest threads first).',
        COMMUNITY, read_only=True, params={**_COMMENT_TARGET, 'page': _PAGE}, required=['on', 'target'])
def list_comments(request, on, target, page=None):
    url_name, args = _comment_page(on, target)
    context = call_view(request, url_name, args=args, query={'page': page}).context_data
    comments = context.get('comment_list') or []
    data = {
        'locked': bool(context.get('comment_lock')),
        'comments': [{
            'id': comment.id,
            'author': comment.author.username,
            'time': _iso(comment.time),
            'parent': comment.parent_id,
            'score': comment.score,
            'my_vote': getattr(comment, 'vote_score', None),
            'body': comment.body,
        } for comment in comments],
    }
    page_obj = context.get('comments_page_obj')
    if page_obj is not None:
        data.update(page=page_obj.number, has_next=page_obj.has_next())
    return data


@action('post_comment', 'Post a comment, or reply to one, on a problem, editorial, contest or blog post.',
        COMMUNITY, read_only=False, params={
            **_COMMENT_TARGET,
            'body': {'type': 'string', 'description': 'Comment text, in markdown.'},
            'parent': {'type': 'integer', 'description': 'ID of the comment to reply to.'},
        }, required=['on', 'target', 'body'])
def post_comment(request, on, target, body, parent=None):
    url_name, args = _comment_page(on, target)
    call_view(request, url_name, args=args, method='POST', data={'body': body, 'parent': parent or ''})
    comment = Comment.objects.filter(author=request.profile).order_by('-id').first()
    return {'comment_id': comment.id if comment else None}


@action('edit_comment', 'Edit one of your comments.', COMMUNITY, read_only=False, params={
    'id': {'type': 'integer', 'description': 'Comment ID.'},
    'body': {'type': 'string', 'description': 'New comment text, in markdown.'},
}, required=['id', 'body'])
def edit_comment(request, id, body):
    call_view(request, 'comment_edit', args=[id], method='POST', data={'body': body})
    return {'comment_id': id}


@action('vote_comment', 'Upvote or downvote a comment.', COMMUNITY, read_only=False, params={
    'id': {'type': 'integer', 'description': 'Comment ID.'},
    'direction': {'type': 'string', 'enum': ['up', 'down']},
}, required=['id', 'direction'])
def vote_comment(request, id, direction):
    url_name = 'comment_upvote' if _vote_direction(direction) == 'up' else 'comment_downvote'
    call_view(request, url_name, method='POST', data={'id': id})
    return {'comment_id': id, 'voted': direction}


def _post_summary(post):
    return {
        'id': post.id,
        'title': post.title,
        'authors': [author.username for author in post.authors.all()],
        'publish_on': _iso(post.publish_on),
        'score': post.score,
        'summary': post.summary,
    }


@action('list_blog_posts', 'List blog posts on the home feed, newest first.', COMMUNITY, read_only=True,
        params={'page': _PAGE})
def list_blog_posts(request, page=None):
    context = call_view(request, 'blog_post_list', query={'page': page}).context_data
    return {'posts': [_post_summary(post) for post in context['posts']], **_page_info(context)}


@action('get_blog_post', 'Read a blog post.', COMMUNITY, read_only=True,
        params={'id': {'type': 'integer', 'description': 'Blog post ID.'}}, required=['id'])
def get_blog_post(request, id):
    post = call_view(request, 'blog_post', args=[id, 'post']).context_data['post']
    return {**_post_summary(post), 'content': post.content,
            'organization': post.organization.slug if post.organization_id else None,
            'my_vote': getattr(post, 'vote_score', None)}


@action('vote_blog_post', 'Upvote or downvote a blog post.', COMMUNITY, read_only=False, params={
    'id': {'type': 'integer', 'description': 'Blog post ID.'},
    'direction': {'type': 'string', 'enum': ['up', 'down']},
}, required=['id', 'direction'])
def vote_blog_post(request, id, direction):
    url_name = 'blog_upvote' if _vote_direction(direction) == 'up' else 'blog_downvote'
    call_view(request, url_name, method='POST', data={'id': id})
    return {'post_id': id, 'voted': direction}


def _organization_summary(org):
    return {
        'slug': org.slug,
        'name': org.name,
        'short_name': org.short_name,
        'is_open': org.is_open,
        'member_count': org.member_count,
    }


@action('list_organizations', 'List organizations.', COMMUNITY, read_only=True, params={'page': _PAGE})
def list_organizations(request, page=None):
    context = call_view(request, 'organization_list', query={'page': page}).context_data
    return {'organizations': [_organization_summary(org) for org in context['organizations']],
            **_page_info(context)}


@action('get_organization', 'Get an organization and its latest posts.', COMMUNITY, read_only=True,
        params={'slug': {'type': 'string', 'description': 'Organization slug.'}}, required=['slug'])
def get_organization(request, slug):
    context = call_view(request, 'organization_home', args=[slug]).context_data
    org = context['organization']
    return {
        **_organization_summary(org),
        'about': org.about,
        'admins': [admin.username for admin in org.admins.all()],
        'is_member': request.profile.organizations.filter(id=org.id).exists(),
        'posts': [_post_summary(post) for post in context.get('posts', [])],
    }


@action('join_organization', 'Join an open organization.', COMMUNITY, read_only=False,
        params={'slug': {'type': 'string', 'description': 'Organization slug.'}}, required=['slug'])
def join_organization(request, slug):
    call_view(request, 'join_organization', args=[slug], method='POST')
    return {'joined': slug}


@action('leave_organization', 'Leave an organization.', COMMUNITY, read_only=False,
        params={'slug': {'type': 'string', 'description': 'Organization slug.'}}, required=['slug'])
def leave_organization(request, slug):
    call_view(request, 'leave_organization', args=[slug], method='POST')
    return {'left': slug}


@action('request_join_organization', 'Ask to join a closed organization.', COMMUNITY, read_only=False, params={
    'slug': {'type': 'string', 'description': 'Organization slug.'},
    'reason': {'type': 'string', 'description': 'Why you want to join.'},
}, required=['slug', 'reason'])
def request_join_organization(request, slug, reason):
    call_view(request, 'request_organization', args=[slug], method='POST', data={'reason': reason})
    return {'requested': slug}


def _user_summary(profile):
    return {
        'id': profile.id,
        'username': profile.username,
        'display_name': profile.display_name,
        'points': profile.points,
        'performance_points': profile.performance_points,
        'problem_count': profile.problem_count,
        'rating': profile.rating,
    }


@action('list_users', 'List users on the leaderboard.', COMMUNITY, read_only=True, params={
    'sort': {'type': 'string', 'enum': ['rating', 'points', 'performance_points', 'problem_count']},
    'page': _PAGE,
})
def list_users(request, sort=None, page=None):
    context = call_view(request, 'user_list', query={'order': sort and '-' + sort, 'page': page}).context_data
    return {'users': [{'rank': rank, **_user_summary(profile)} for rank, profile in context['users']],
            **_page_info(context)}


@action('get_user', "Get a user's profile.", COMMUNITY, read_only=True,
        params={'username': {'type': 'string'}}, required=['username'])
def get_user(request, username):
    profile = call_view(request, 'user_page', args=[username]).context_data['user']
    return {
        **_user_summary(profile),
        'about': profile.about,
        'organizations': [org.slug for org in profile.organizations.filter(is_unlisted=False)],
    }


@action('list_user_submissions', "List a user's submissions, newest first, optionally for one problem.",
        COMMUNITY, read_only=True, params={
            'username': {'type': 'string'},
            'problem': {'type': 'string', 'description': 'Problem code.'},
            'page': _PAGE,
        }, required=['username'])
def list_user_submissions(request, username, problem=None, page=None):
    if problem:
        response = call_view(request, 'user_submissions', args=[problem, username], query={'page': page})
    else:
        response = call_view(request, 'all_user_submissions', args=[username], query={'page': page})
    context = response.context_data
    return {'submissions': [_submission_summary(s, request.user) for s in context['submissions']],
            **_page_info(context)}


@action('get_submission_source', 'Get the source code of a submission, if the user may see it.', COMMUNITY,
        read_only=True, params={'id': {'type': 'integer', 'description': 'Submission ID.'}}, required=['id'])
def get_submission_source(request, id):
    context = call_view(request, 'submission_source', args=[id]).context_data
    submission = context['submission']
    return {'id': submission.id, 'user': submission.user.username, 'problem': submission.problem.code,
            'language': submission.language.key, 'source': context['raw_source']}


@action('abort_submission', 'Abort one of your submissions that is still being judged.', PARTICIPANT,
        read_only=False, params={'id': {'type': 'integer', 'description': 'Submission ID.'}}, required=['id'])
def abort_submission(request, id):
    call_view(request, 'submission_abort', args=[id], method='POST')
    return {'submission_id': id, 'aborted': True}


_TARGETS = {
    'problem': ({'type': 'string', 'description': 'Problem code.'}, lambda t: [t]),
    'contest': ({'type': 'string', 'description': 'Contest key.'}, lambda t: [t]),
    'organization': ({'type': 'string', 'description': 'Organization slug.'}, lambda t: [t]),
    'user': ({'type': 'string', 'description': 'Username.'}, lambda t: [t]),
    'blog_post': ({'type': 'string', 'description': 'Blog post ID.'}, lambda t: [int(t), 'post']),
    'ticket': ({'type': 'string', 'description': 'Ticket ID.'}, lambda t: [int(t)]),
}

FORM_PAGES = {}


def _form_page(name, url_name, description, toolset, target=None, permission=(), destructive=False):
    FORM_PAGES[name] = (url_name, target)
    params = {'values': {
        'type': 'object',
        'description': 'Field values by field name, as listed by get_form. Fields left out keep their current value.',
    }}
    required = ['values']
    if target:
        params['target'] = _TARGETS[target][0]
        required.insert(0, 'target')

    def handler(request, values, target=None):
        return submit_form(request, name, target, values)

    action(name, description + ' Call get_form first to see the fields.', toolset, read_only=False,
           params=params, required=required, destructive=destructive, permission=permission)(handler)


def _form_args(name, target):
    url_name, target_type = FORM_PAGES[name]
    if not target_type:
        return url_name, []
    if target in (None, ''):
        raise AgentError('This form needs a target (%s).' % _TARGETS[target_type][0]['description'])
    try:
        return url_name, _TARGETS[target_type][1](target)
    except ValueError:
        raise AgentError('Invalid target "%s".' % target)


def submit_form(request, name, target, values):
    url_name, args = _form_args(name, target)
    data = form_data(call_view(request, url_name, args=args).context_data)
    for key, value in values.items():
        if value is None or value is False:
            data.pop(key, None)
        else:
            data[key] = value
    response = call_view(request, url_name, args=args, method='POST', data=data)
    result = {'done': True}
    if hasattr(response, 'url'):
        result['redirect'] = response.url
        try:
            result['page'], result['page_args'] = redirect_target(response)
        except Exception:
            pass
    return result


_form_page('create_blog_post', 'blog_post_new', 'Write a new blog post.', COMMUNITY)
_form_page('edit_blog_post', 'blog_post_edit', 'Edit one of your blog posts.', COMMUNITY, target='blog_post')
_form_page('create_problem', 'problem_create', 'Create a problem.', AUTHOR, permission='judge.add_problem')
_form_page('create_organization_problem', 'problem_create_organization',
           'Create a problem inside an organization you administer.', AUTHOR, target='organization')
_form_page('edit_problem', 'problem_edit', 'Edit a problem: statement, limits, languages, editorial.', AUTHOR,
           target='problem', permission='judge.edit_own_problem')
_form_page('edit_problem_types', 'problem_edit_type_group', 'Change the types and group of a problem.', AUTHOR,
           target='problem', permission='judge.edit_type_group_all_problem')
_form_page('clone_problem', 'problem_clone', 'Clone a problem under a new code.', AUTHOR, target='problem',
           permission='judge.clone_problem')
_form_page('create_contest', 'contest_new', 'Create a contest.', AUTHOR, permission='judge.add_contest')
_form_page('create_organization_contest', 'contest_create_organization',
           'Create a contest inside an organization you administer.', AUTHOR, target='organization')
_form_page('edit_contest', 'contest_edit', 'Edit a contest: settings, times and its problems.', AUTHOR,
           target='contest', permission=('judge.edit_own_contest', 'judge.edit_all_contest'))
_form_page('clone_contest', 'contest_clone', 'Clone a contest under a new key.', AUTHOR, target='contest',
           permission='judge.clone_contest')
_form_page('announce_contest', 'contest_announce', 'Post an announcement to contest participants.', AUTHOR,
           target='contest', permission=('judge.edit_own_contest', 'judge.edit_all_contest'))
_form_page('create_organization', 'organization_create', 'Create an organization.', MODERATOR,
           permission='judge.add_organization')
_form_page('edit_organization', 'edit_organization', 'Edit an organization you administer.', MODERATOR,
           target='organization')
_form_page('ban_user', 'user_ban', 'Ban a user.', MODERATOR, target='user', permission='judge.ban_user',
           destructive=True)
_form_page('unban_user', 'user_unban', 'Unban a user.', MODERATOR, target='user', permission='judge.ban_user')
_form_page('edit_ticket_notes', 'ticket_notes', 'Edit the staff notes on a ticket.', MODERATOR, target='ticket',
           permission='judge.change_ticket')


@action('get_form', 'Show the fields of a form (for create_*/edit_* and other form actions) with their current '
        'values and choices.', COMMUNITY, read_only=True, params={
            'form': {'type': 'string', 'description': 'The form action name, e.g. edit_problem.'},
            'target': {'type': 'string', 'description': 'Problem code, contest key, username, ... if the form '
                                                        'needs one.'},
        }, required=['form'])
def get_form(request, form, target=None):
    if form not in FORM_PAGES:
        raise AgentError('Unknown form. One of: %s.' % ', '.join(sorted(FORM_PAGES)))
    if not ACTIONS[form].is_allowed(request.user):
        raise AgentError('Permission denied.', 403)
    url_name, args = _form_args(form, target)
    return {'form': form, **describe_forms(call_view(request, url_name, args=args).context_data)}


@action('delete_blog_post', 'Delete a blog post.', MODERATOR, read_only=False, destructive=True,
        permission='judge.delete_blogpost',
        params={'id': {'type': 'integer', 'description': 'Blog post ID.'}}, required=['id'])
def delete_blog_post(request, id):
    call_view(request, 'blog_post_delete', args=[id, 'post'], method='POST')
    return {'deleted': id}


@action('delete_problem', 'Delete a problem.', AUTHOR, read_only=False, destructive=True,
        permission='judge.edit_own_problem',
        params={'code': {'type': 'string', 'description': 'Problem code.'}}, required=['code'])
def delete_problem(request, code):
    call_view(request, 'problem_delete', args=[code], method='POST')
    return {'deleted': code}


@action('delete_contest', 'Delete a contest that has no ratings.', AUTHOR, read_only=False, destructive=True,
        permission=('judge.edit_own_contest', 'judge.edit_all_contest'),
        params={'key': {'type': 'string', 'description': 'Contest key.'}}, required=['key'])
def delete_contest(request, key):
    call_view(request, 'contest_delete', args=[key], method='POST')
    return {'deleted': key}


@action('make_contest_problems_public', 'Make every problem in a contest public.', AUTHOR, read_only=False,
        permission=('judge.edit_own_contest', 'judge.edit_all_contest'),
        params={'key': {'type': 'string', 'description': 'Contest key.'}}, required=['key'])
def make_contest_problems_public(request, key):
    call_view(request, 'contest_problems_make_public', args=[key], method='POST')
    return {'contest': key, 'problems_public': True}


@action('disqualify_participant', 'Disqualify a contest participation, or undo it. Get participation_id from '
        'get_contest_ranking.', MODERATOR, read_only=False, destructive=True,
        permission=('judge.edit_own_contest', 'judge.edit_all_contest'), params={
            'key': {'type': 'string', 'description': 'Contest key.'},
            'participation_id': {'type': 'integer'},
        }, required=['key', 'participation_id'])
def disqualify_participant(request, key, participation_id):
    call_view(request, 'contest_participation_disqualify', args=[key], method='POST',
              data={'participation': participation_id})
    return {'contest': key, 'participation_id': participation_id}


@action('rejudge_submission', 'Rejudge a submission.', MODERATOR, read_only=False,
        permission='judge.rejudge_submission',
        params={'id': {'type': 'integer', 'description': 'Submission ID.'}}, required=['id'])
def rejudge_submission(request, id):
    call_view(request, 'submission_rejudge', method='POST', data={'id': id})
    return {'submission_id': id, 'rejudging': True}


@action('hide_comment', 'Hide a comment and its replies.', MODERATOR, read_only=False, destructive=True,
        permission='judge.change_comment',
        params={'id': {'type': 'integer', 'description': 'Comment ID.'}}, required=['id'])
def hide_comment(request, id):
    call_view(request, 'comment_hide', method='POST', data={'id': id})
    return {'comment_id': id, 'hidden': True}


@action('set_ticket_contributive', 'Mark a ticket as a good contribution or not (gives contribution points).',
        MODERATOR, read_only=False, permission='judge.change_ticket', params={
            'id': {'type': 'integer', 'description': 'Ticket ID.'},
            'contributive': {'type': 'boolean'},
        }, required=['id', 'contributive'])
def set_ticket_contributive(request, id, contributive):
    call_view(request, 'ticket_good' if contributive else 'ticket_norm', args=[id], method='POST')
    return {'ticket_id': id, 'contributive': contributive}


@action('kick_organization_user', 'Remove a member from an organization you administer.', MODERATOR,
        read_only=False, destructive=True, params={
            'slug': {'type': 'string', 'description': 'Organization slug.'},
            'username': {'type': 'string'},
        }, required=['slug', 'username'])
def kick_organization_user(request, slug, username):
    profile = Profile.objects.filter(user__username=username).first()
    if profile is None:
        raise AgentError('No such user.', 404)
    call_view(request, 'organization_user_kick', args=[slug], method='POST', data={'user': profile.id})
    return {'organization': slug, 'removed': username}
