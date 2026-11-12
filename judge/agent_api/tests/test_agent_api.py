import json
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from judge.models import BlogPost, Comment, Contest, ContestParticipation, Judge, Language, Notification, \
    Organization, Problem, Profile, Submission, SubmissionTestCase, Ticket
from judge.models.tests.util import CommonDataMixin, create_blogpost, create_contest, create_contest_participation, \
    create_contest_problem, create_problem, create_problem_type, create_solution, create_user


class AgentAPITestMixin(CommonDataMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.problem = create_problem(code='aplusb', is_public=True, allowed_languages=('PY3',),
                                     description='Print a+b.')
        cls.private_problem = create_problem(code='secret', is_public=False)
        judge = Judge.objects.create(name='judge1', auth_key='key', online=True,
                                     storages=[cls.problem.effective_storage])
        judge.runtimes.add(Language.objects.get(key='PY3'))

    def setUp(self):
        self.token = self.users['normal'].profile.generate_api_token()

    def call(self, name, token=None, **args):
        return self.client.post(
            reverse('agent_api_action', args=[name]), data=json.dumps(args), content_type='application/json',
            HTTP_AUTHORIZATION='Bearer %s' % (token or self.token),
        )

    def ok(self, name, **args):
        response = self.call(name, **args)
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()['data']

    def fails(self, name, status, **args):
        response = self.call(name, **args)
        self.assertEqual(response.status_code, status, response.content)
        return response.json()['error']


class AgentAPIFrameworkTestCase(AgentAPITestMixin, TestCase):
    def test_requires_token(self):
        self.client.force_login(self.users['normal'])
        response = self.client.get(reverse('agent_api_capabilities'))
        self.assertEqual(response.status_code, 401)

    def test_capabilities(self):
        response = self.client.get(reverse('agent_api_capabilities'), HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(data['username'], 'normal')
        names = {a['name'] for a in data['actions']}
        self.assertIn('submit_solution', names)
        submit = next(a for a in data['actions'] if a['name'] == 'submit_solution')
        self.assertFalse(submit['read_only'])
        self.assertEqual(submit['input_schema']['required'], ['problem', 'language', 'source'])

    def test_openapi(self):
        response = self.client.get(reverse('agent_api_openapi'))
        self.assertEqual(response.status_code, 200)
        spec = response.json()
        operation = spec['paths'][reverse('agent_api_action', args=['submit_solution'])]['post']
        self.assertEqual(operation['operationId'], 'submit_solution')
        self.assertTrue(operation['requestBody']['required'])
        schema = operation['requestBody']['content']['application/json']['schema']
        self.assertEqual(schema['required'], ['problem', 'language', 'source'])
        self.assertEqual(len(spec['paths']), len({op['post']['operationId'] for op in spec['paths'].values()}))

    def test_unknown_action(self):
        self.fails('nope', 404)

    def test_argument_validation(self):
        self.assertIn('Missing', self.fails('get_problem', 400)['message'])
        self.assertIn('Unknown argument', self.fails('get_problem', 400, code='x', extra=1)['message'])
        self.assertIn('integer', self.fails('get_submission', 400, id='1')['message'])

    def test_me(self):
        data = self.ok('me')
        self.assertEqual(data['username'], 'normal')
        self.assertIsNone(data['current_contest'])
        self.assertEqual(data['permissions'], [])

    @override_settings(VNOJ_AGENT_API_WRITE_LIMIT=1)
    def test_write_rate_limit(self):
        self.ok('mark_notifications_read')
        self.fails('mark_notifications_read', 429)
        self.ok('me')


class AgentAPIProblemTestCase(AgentAPITestMixin, TestCase):
    def test_list_problems(self):
        codes = [p['code'] for p in self.ok('list_problems')['problems']]
        self.assertIn('aplusb', codes)
        self.assertNotIn('secret', codes)
        self.assertEqual([p['code'] for p in self.ok('list_problems', search='plus')['problems']], ['aplusb'])

    def test_get_problem(self):
        data = self.ok('get_problem', code='aplusb')
        self.assertEqual(data['statement'], 'Print a+b.')
        self.assertEqual([lang['key'] for lang in data['languages']], ['PY3'])

    def test_get_editorial(self):
        create_solution(problem=self.problem, content='Use addition.')
        self.assertTrue(self.ok('get_problem', code='aplusb')['has_editorial'])
        self.assertEqual(self.ok('get_editorial', code='aplusb')['editorial'], 'Use addition.')

    def test_private_problem_is_hidden(self):
        self.fails('get_problem', 404, code='secret')


@mock.patch('judge.models.Submission.judge')
class AgentAPISubmissionTestCase(AgentAPITestMixin, TestCase):
    def test_submit_and_read_result(self, judge):
        submission_id = self.ok('submit_solution', problem='aplusb', language='PY3',
                                source='print(sum(map(int, input().split())))')['submission_id']
        judge.assert_called_once()
        submission = Submission.objects.get(id=submission_id)
        self.assertEqual(submission.user, self.users['normal'].profile)

        submission.status, submission.result, submission.points = 'D', 'WA', 0
        submission.save()
        SubmissionTestCase.objects.create(submission=submission, case=1, status='AC', time=0.1, memory=1024,
                                          points=1, total=1)
        SubmissionTestCase.objects.create(submission=submission, case=2, status='WA', time=0.1, memory=1024,
                                          points=0, total=1)
        data = self.ok('get_submission', id=submission_id)
        self.assertEqual(data['result'], 'WA')
        self.assertEqual([c['status'] for c in data['batches'][0]['cases']], ['AC', 'WA'])

        listed = self.ok('list_my_submissions', problem='aplusb')['submissions']
        self.assertEqual([s['id'] for s in listed], [submission_id])

    @mock.patch('judge.agent_api.actions.time.sleep')
    def test_get_submission_wait(self, sleep, judge):
        submission = Submission.objects.create(user=self.users['normal'].profile, problem=self.problem,
                                               language=Language.objects.get(key='PY3'), status='QU')

        def finish(seconds):
            Submission.objects.filter(id=submission.id).update(status='D', result='AC', points=1)
        sleep.side_effect = finish

        self.assertEqual(self.ok('get_submission', id=submission.id)['status'], 'QU')
        sleep.assert_not_called()
        data = self.ok('get_submission', id=submission.id, wait=30)
        self.assertEqual((data['status'], data['result']), ('D', 'AC'))
        sleep.assert_called_once_with(1)

    def test_disallowed_language(self, judge):
        error = self.fails('submit_solution', 400, problem='aplusb', language='CPP17', source='x')
        self.assertIn('language', error['fields'])
        judge.assert_not_called()

    def test_unknown_language(self, judge):
        self.fails('submit_solution', 400, problem='aplusb', language='NOPE', source='x')

    def test_cannot_submit_to_private_problem(self, judge):
        self.fails('submit_solution', 403, problem='secret', language='PY3', source='x')
        judge.assert_not_called()

    def test_banned_user_gets_message(self, judge):
        self.problem.banned_users.add(self.users['normal'].profile)
        error = self.fails('submit_solution', 400, problem='aplusb', language='PY3', source='x')
        self.assertIn('Banned from submitting', error['message'])

    def test_cannot_read_others_submission(self, judge):
        other = create_user(username='other').profile
        submission = Submission.objects.create(user=other, problem=self.private_problem,
                                               language=Language.objects.get(key='PY3'))
        self.fails('get_submission', 403, id=submission.id)


class AgentAPIContestTestCase(AgentAPITestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.contest = create_contest(key='live', is_visible=True)
        create_contest_problem(contest=cls.contest, problem=cls.problem)
        cls.coded_contest = create_contest(key='coded', is_visible=True, access_code='letmein')
        cls.future_contest = create_contest(key='future', is_visible=True,
                                            start_time=timezone.now() + timezone.timedelta(days=1))

    def test_list_contests(self):
        data = self.ok('list_contests')
        self.assertIn('live', [c['key'] for c in data['ongoing']])
        self.assertIn('future', [c['key'] for c in data['upcoming']])

    def test_join_get_and_leave(self):
        self.assertNotIn('problems', self.ok('get_contest', key='live'))
        self.assertEqual(self.ok('join_contest', key='live')['joined'], 'live')
        self.assertEqual(self.ok('me')['current_contest']['key'], 'live')

        contest = self.ok('get_contest', key='live')
        self.assertTrue(contest['is_in_contest'])
        self.assertEqual([p['code'] for p in contest['problems']], ['aplusb'])

        ranking = self.ok('get_contest_ranking', key='live')
        self.assertEqual([r['username'] for r in ranking['rows']], ['normal'])

        self.ok('leave_contest', key='live')
        self.assertIsNone(self.ok('me')['current_contest'])

    @mock.patch('judge.models.Submission.judge')
    def test_submit_in_contest(self, judge):
        self.ok('join_contest', key='live')
        submission_id = self.ok('submit_solution', problem='aplusb', language='PY3', source='x')['submission_id']
        self.assertEqual(Submission.objects.get(id=submission_id).contest_object, self.contest)
        self.assertEqual(self.ok('get_submission', id=submission_id)['contest'], 'live')

    def test_join_requires_access_code(self):
        self.fails('join_contest', 400, key='coded')
        self.fails('join_contest', 400, key='coded', access_code='wrong')
        self.ok('join_contest', key='coded', access_code='letmein')

    def test_cannot_join_future_contest(self):
        self.assertIn('not currently ongoing', self.fails('join_contest', 400, key='future')['message'])
        self.assertFalse(ContestParticipation.objects.filter(contest=self.future_contest).exists())

    def test_leave_when_not_in_contest(self):
        self.fails('leave_contest', 404, key='live')


@mock.patch('judge.views.ticket.on_new_ticket.delay')
@mock.patch('judge.views.ticket.on_new_ticket_message.delay')
class AgentAPITicketTestCase(AgentAPITestMixin, TestCase):
    def test_ticket_flow(self, *mocks):
        ticket_id = self.ok('create_problem_ticket', problem='aplusb', title='Unclear', body='Is a negative?')[
            'ticket_id']
        self.assertEqual(Ticket.objects.get(id=ticket_id).user, self.users['normal'].profile)
        self.ok('reply_ticket', id=ticket_id, body='Also, how big is b?')
        self.ok('set_ticket_open', id=ticket_id, open=False)

        ticket = self.ok('get_ticket', id=ticket_id)
        self.assertFalse(ticket['is_open'])
        self.assertEqual([m['body'] for m in ticket['messages']][:2], ['Is a negative?', 'Also, how big is b?'])
        self.assertEqual([t['id'] for t in self.ok('list_tickets')['tickets']], [ticket_id])

    def test_issue_ticket(self, *mocks):
        ticket_id = self.ok('create_issue_ticket', title='Bug', body='Page broken', issue_url='https://oj/x')[
            'ticket_id']
        self.assertEqual(self.ok('get_ticket', id=ticket_id)['title'], 'Bug')

    def test_form_errors_are_reported(self, *mocks):
        error = self.fails('create_problem_ticket', 400, problem='aplusb', title='x' * 101, body='b')
        self.assertIn('title', error['fields'])

    def test_cannot_read_others_ticket(self, *mocks):
        other = create_user(username='other2').profile
        ticket = Ticket.objects.create(user=other, title='t', linked_item=self.problem)
        self.fails('get_ticket', 403, id=ticket.id)


class AgentAPINotificationTestCase(AgentAPITestMixin, TestCase):
    def test_notifications(self):
        profile = self.users['normal'].profile
        notification = Notification.objects.create(recipient=profile, title='Hello')
        data = self.ok('list_notifications', unread_only=True)
        self.assertEqual([n['id'] for n in data['notifications']], [notification.id])
        self.assertEqual(self.ok('mark_notifications_read')['unread_count'], 0)
        self.assertEqual(self.ok('list_notifications', unread_only=True)['notifications'], [])


@mock.patch('judge.signals.on_new_comment.delay')
@mock.patch('judge.comments.LockModel', mock.MagicMock())
class AgentAPICommunityTestCase(AgentAPITestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.author = create_user(username='author')
        cls.author.profile.problem_count = 10
        cls.author.profile.save()
        cls.post = create_blogpost(title='hello', visible=True, content='Welcome!', authors=('author',))

    def test_new_users_cannot_comment(self, *mocks):
        error = self.fails('post_comment', 400, on='problem', target='aplusb', body='First comment here')
        self.assertIn('solved at least', error['fields']['__all__'][0])

    def test_comment_flow(self, *mocks):
        profile = self.users['normal'].profile
        profile.problem_count = 10
        profile.save()
        comment_id = self.ok('post_comment', on='problem', target='aplusb', body='Nice problem')['comment_id']
        self.ok('edit_comment', id=comment_id, body='Very nice problem')
        comments = self.ok('list_comments', on='problem', target='aplusb')['comments']
        self.assertEqual([(c['id'], c['body']) for c in comments], [(comment_id, 'Very nice problem')])
        self.assertIn('own comments', self.fails('vote_comment', 400, id=comment_id, direction='up')['message'])

        self.token = self.author.profile.generate_api_token()
        reply = self.ok('post_comment', on='problem', target='aplusb', body='Thanks a lot!', parent=comment_id)
        self.ok('vote_comment', id=comment_id, direction='up')
        self.assertEqual(Comment.objects.get(id=comment_id).score, 1)
        self.assertEqual(Comment.objects.get(id=reply['comment_id']).parent_id, comment_id)

    def test_blog(self, *mocks):
        self.assertIn(self.post.id, [p['id'] for p in self.ok('list_blog_posts')['posts']])
        self.assertEqual(self.ok('get_blog_post', id=self.post.id)['content'], 'Welcome!')
        profile = self.users['normal'].profile
        profile.problem_count = 10
        profile.save()
        self.ok('vote_blog_post', id=self.post.id, direction='down')
        self.post.refresh_from_db()
        self.assertEqual(self.post.score, -1)

    def test_organizations(self, *mocks):
        Organization.objects.filter(slug='open').update(is_open=True)
        self.assertIn('open', [o['slug'] for o in self.ok('list_organizations')['organizations']])
        self.ok('join_organization', slug='open')
        self.assertTrue(self.ok('get_organization', slug='open')['is_member'])
        self.ok('leave_organization', slug='open')
        self.assertFalse(self.ok('get_organization', slug='open')['is_member'])

    def test_users(self, *mocks):
        self.assertEqual(self.ok('get_user', username='author')['problem_count'], 10)
        self.assertIn('author', [u['username'] for u in self.ok('list_users', sort='problem_count')['users']])
        self.fails('get_user', 404, username='nobody')

    @mock.patch('judge.models.Submission.judge')
    def test_submission_source_and_abort(self, judge, *mocks):
        submission_id = self.ok('submit_solution', problem='aplusb', language='PY3', source='print(1)')[
            'submission_id']
        self.assertEqual(self.ok('get_submission_source', id=submission_id)['source'], 'print(1)')
        listed = self.ok('list_user_submissions', username='normal')['submissions']
        self.assertEqual([s['id'] for s in listed], [submission_id])
        with mock.patch('judge.models.Submission.abort') as abort:
            self.ok('abort_submission', id=submission_id)
        abort.assert_called_once()

        self.token = self.author.profile.generate_api_token()
        self.fails('get_submission_source', 403, id=submission_id)
        self.fails('abort_submission', 403, id=submission_id)


@mock.patch('judge.signals.on_new_comment.delay')
class AgentAPIFormTestCase(AgentAPITestMixin, TestCase):
    def as_user(self, username):
        self.token = self.users[username].profile.generate_api_token()

    def test_form_actions_follow_permissions(self, *mocks):
        names = lambda: {a['name'] for a in self.client.get(  # noqa: E731
            reverse('agent_api_capabilities'), HTTP_AUTHORIZATION='Bearer ' + self.token).json()['data']['actions']}
        self.assertNotIn('edit_problem', names())
        self.assertIn('create_blog_post', names())
        self.fails('edit_problem', 403, target='aplusb', values={})
        self.fails('get_form', 403, form='edit_problem', target='aplusb')
        self.as_user('superuser')
        self.assertIn('edit_problem', names())

    def test_edit_problem_with_formsets(self, *mocks):
        self.problem.types.add(create_problem_type(name='math'))
        self.as_user('superuser')
        form = self.ok('get_form', form='edit_problem', target='aplusb')
        fields = {f['name']: f for f in form['fields']}
        self.assertEqual(fields['name']['value'], 'aplusb')
        self.assertIn('time_limit', fields)
        self.assertTrue(form['formsets'])

        self.ok('edit_problem', target='aplusb', values={'name': 'A plus B', 'time_limit': 2})
        self.problem.refresh_from_db()
        self.assertEqual((self.problem.name, self.problem.time_limit), ('A plus B', 2))
        self.assertEqual(list(self.problem.allowed_languages.values_list('key', flat=True)), ['PY3'])

        error = self.fails('edit_problem', 400, target='aplusb', values={'time_limit': 'fast'})
        self.assertIn('time_limit', error['fields'])

    def test_edit_contest_with_problem_formset(self, *mocks):
        self.as_user('superuser')
        contest = create_contest(key='edited', is_visible=True)
        create_contest_problem(contest=contest, problem=self.problem, points=50)
        form = self.ok('get_form', form='edit_contest', target='edited')
        names = {f['name'] for f in form['fields']}
        self.assertIn('contest_problems-0-points', names)
        self.ok('edit_contest', target='edited', values={'name': 'Edited round', 'contest_problems-0-points': 70})
        contest.refresh_from_db()
        self.assertEqual(contest.name, 'Edited round')
        self.assertEqual(contest.contest_problems.get().points, 70)

    def test_create_blog_post(self, *mocks):
        self.as_user('superuser')
        form = self.ok('get_form', form='create_blog_post')
        self.assertIn('title', {f['name'] for f in form['fields']})
        result = self.ok('create_blog_post', values={'title': 'Release notes', 'slug': 'release-notes',
                                                     'content': 'We shipped.', 'visible': True,
                                                     'publish_on': timezone.now().isoformat()})
        self.assertEqual(result['page'], 'blog_post')
        self.assertTrue(BlogPost.objects.filter(title='Release notes').exists())

    def test_ban_and_unban(self, *mocks):
        self.as_user('superuser')
        self.ok('ban_user', target='normal', values={'ban_reason': 'spam'})
        self.assertTrue(Profile.objects.get(user__username='normal').is_banned)
        self.ok('unban_user', target='normal', values={})
        self.assertFalse(Profile.objects.get(user__username='normal').is_banned)

    @mock.patch('judge.models.Submission.judge')
    def test_rejudge_and_hide_comment(self, judge, *mocks):
        submission = Submission.objects.create(user=self.users['normal'].profile, problem=self.problem,
                                               language=Language.objects.get(key='PY3'), status='D')
        comment = Comment.objects.create(author=self.users['normal'].profile, page='p:aplusb', body='spam')
        self.fails('rejudge_submission', 403, id=submission.id)
        self.as_user('superuser')
        self.ok('rejudge_submission', id=submission.id)
        judge.assert_called_once()
        self.ok('hide_comment', id=comment.id)
        self.assertTrue(Comment.objects.get(id=comment.id).hidden)


@mock.patch('judge.views.contests.on_new_contest.delay')
@mock.patch('judge.views.ticket.on_new_ticket.delay')
class AgentAPIManagementTestCase(AgentAPITestMixin, TestCase):
    def setUp(self):
        self.token = self.users['superuser'].profile.generate_api_token()

    def test_create_problem(self, *mocks):
        create_problem_type(name='math')
        form = {f['name']: f for f in self.ok('get_form', form='create_problem')['fields']}
        type_id = next(value for value, label in form['types']['choices'])
        group_id = next(value for value, label in form['group']['choices'])
        result = self.ok('create_problem', values={
            'code': 'newprob', 'name': 'New problem', 'description': 'Statement', 'time_limit': 1,
            'memory_limit': 65536, 'points': 5, 'types': [type_id], 'group': group_id,
        })
        self.assertEqual(result['page_args'], {'problem': 'newprob'})
        self.assertTrue(Problem.objects.filter(code='newprob', name='New problem').exists())

    def test_create_announce_and_delete_contest(self, *mocks):
        start = timezone.now() + timezone.timedelta(days=1)
        self.ok('create_contest', values={
            'key': 'newround', 'name': 'New round', 'description': 'Good luck',
            'start_time': start.isoformat(), 'end_time': (start + timezone.timedelta(hours=2)).isoformat(),
            'contest_problems-TOTAL_FORMS': 1, 'contest_problems-0-problem': self.problem.id,
            'contest_problems-0-points': 100, 'contest_problems-0-order': 1,
        })
        contest = Contest.objects.get(key='newround')
        self.assertEqual(list(contest.problems.values_list('code', flat=True)), ['aplusb'])
        self.ok('announce_contest', target='newround', values={'title': 'Hi', 'description': 'Read carefully'})
        self.assertEqual(contest.contestannouncement_set.get().title, 'Hi')
        self.ok('make_contest_problems_public', key='newround')
        self.ok('delete_contest', key='newround')
        self.assertFalse(Contest.objects.filter(key='newround').exists())

    def test_disqualify(self, *mocks):
        contest = create_contest(key='dq', is_visible=True)
        participation = create_contest_participation(contest=contest, user='normal')
        rows = self.ok('get_contest_ranking', key='dq')['rows']
        self.assertEqual(rows[0]['participation_id'], participation.id)
        self.ok('disqualify_participant', key='dq', participation_id=participation.id)
        participation.refresh_from_db()
        self.assertTrue(participation.is_disqualified)

    def test_tickets_and_organizations(self, *mocks):
        ticket = Ticket.objects.create(user=self.users['normal'].profile, title='t', linked_item=self.problem)
        self.ok('edit_ticket_notes', target=str(ticket.id), values={'notes': 'duplicate'})
        self.ok('set_ticket_contributive', id=ticket.id, contributive=True)
        ticket.refresh_from_db()
        self.assertEqual((ticket.notes, ticket.is_contributive), ('duplicate', True))

        Group.objects.get_or_create(name=settings.GROUP_PERMISSION_FOR_ORG_ADMIN)
        org = Organization.objects.get(slug='open')
        org.members.add(self.users['normal'].profile)
        org.admins.add(self.users['superuser'].profile)
        self.ok('edit_organization', target='open', values={'about': 'We code.'})
        self.assertEqual(Organization.objects.get(slug='open').about, 'We code.')
        self.ok('kick_organization_user', slug='open', username='normal')
        self.assertFalse(org.members.filter(id=self.users['normal'].profile.id).exists())

    def test_delete_problem(self, *mocks):
        self.ok('delete_problem', code='aplusb')
        self.assertTrue(Problem.objects.get(code='aplusb').is_deleted)
