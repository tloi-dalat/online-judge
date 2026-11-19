import json
import re
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from judge.models import Contest, Language, Problem, Submission
from judge.models.problem import SubmissionSourceAccess
from judge.models.tests.util import create_blogpost, create_contest, create_contest_problem, create_organization, \
    create_problem, create_user

ADMIN_PERMISSIONS = (
    'edit_own_problem', 'edit_own_contest', 'edit_organization_post', 'create_organization_problem',
    'create_private_contest', 'change_problem', 'change_contest', 'change_blogpost', 'rejudge_submission',
)
JOIN_BUTTON = 'participate-button join-warning'
SPECTATE_BUTTON = 'participate-button spectate-warning'


def create_submission(user, problem, contest=None):
    return Submission.objects.create(
        user=user.profile, problem=problem, contest_object=contest, language=Language.get_python3(),
        result='WA', status='D', time=0.1, memory=1024, points=0, case_points=0, case_total=1,
    )


class OrganizationAdminAccessTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        _now = timezone.now()
        cls.owner = create_user(username='owner', is_staff=True, user_permissions=ADMIN_PERMISSIONS)
        cls.co_admin = create_user(username='co_admin', is_staff=True, user_permissions=ADMIN_PERMISSIONS)
        cls.admin_no_perms = create_user(username='admin_no_perms')
        cls.other_admin = create_user(username='other_admin', is_staff=True, user_permissions=ADMIN_PERMISSIONS)
        cls.site_org_editor = create_user(username='site_org_editor', user_permissions=('edit_all_organization',))
        cls.member = create_user(username='member')

        cls.org = create_organization(name='school', admins=('owner', 'co_admin', 'admin_no_perms'))
        cls.other_org = create_organization(name='other', admins=('other_admin',))
        for user in (cls.owner, cls.co_admin, cls.admin_no_perms, cls.member):
            user.profile.organizations.add(cls.org)
        cls.other_admin.profile.organizations.add(cls.other_org)

        org_private = {'is_public': False, 'is_organization_private': True, 'organization': cls.org}
        cls.private_problem = create_problem(code='school_hidden', authors=('owner',), **org_private)
        cls.shared_problem = create_problem(code='school_shared', authors=('owner', 'admin_no_perms'), **org_private)
        cls.not_org_private_problem = create_problem(
            code='school_not_private', is_public=False, organization=cls.org, authors=('owner',),
        )
        cls.other_org_problem = create_problem(
            code='other_hidden', is_public=False, is_organization_private=True, organization=cls.other_org,
            authors=('other_admin',),
        )
        cls.public_problem = create_problem(
            code='site_public', is_public=True, submission_source_visibility_mode=SubmissionSourceAccess.ONLY_OWN,
        )

        running = {'start_time': _now - timezone.timedelta(days=1), 'end_time': _now + timezone.timedelta(days=1)}
        org_contest = {
            'is_organization_private': True, 'organization': cls.org, 'authors': ('owner',),
            'scoreboard_visibility': Contest.SCOREBOARD_HIDDEN,
        }
        cls.hidden_contest = create_contest(key='school_hidden', is_visible=False, **running, **org_contest)
        cls.private_contest = create_contest(
            key='school_private', is_visible=True, is_private=True, **running, **org_contest,
        )
        create_contest_problem(contest=cls.private_contest, problem=cls.public_problem)
        cls.voi_contest = create_contest(
            key='school_voi', is_visible=True, format_name='voi',
            start_time=_now - timezone.timedelta(days=2), end_time=_now - timezone.timedelta(days=1),
            unfreeze_time=_now + timezone.timedelta(days=1),
            is_organization_private=True, organization=cls.org, authors=('owner',),
        )
        cls.other_org_contest = create_contest(
            key='other_hidden', is_visible=False, is_organization_private=True, organization=cls.other_org,
            authors=('other_admin',),
        )

        cls.contest_submission = create_submission(cls.member, cls.public_problem, cls.private_contest)
        cls.problem_submission = create_submission(cls.member, cls.private_problem)

        cls.hidden_post = create_blogpost(
            title='school_hidden_post', visible=False, organization=cls.org, authors=('owner',),
        )

    def fresh(self, obj):
        return type(obj).objects.get(pk=obj.pk)

    def assert_denied(self, response):
        if response.status_code == 200:
            self.assertTemplateUsed(response, 'generic-message.html')
        else:
            self.assertIn(response.status_code, (403, 404))

    def assert_allowed(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'generic-message.html')

    def test_problem_access(self):
        problem = self.private_problem
        self.assertTrue(self.fresh(problem).is_accessible_by(self.co_admin))
        self.assertTrue(self.fresh(problem).is_editable_by(self.co_admin))
        self.assertTrue(self.fresh(problem).is_editor(self.co_admin.profile))
        self.assertTrue(self.fresh(problem).is_testcase_accessible_by(self.co_admin))
        self.assertTrue(self.fresh(problem).is_subs_manageable_by(self.co_admin))
        self.assertTrue(self.fresh(problem).is_accessible_by(self.admin_no_perms))
        self.assertFalse(self.fresh(problem).is_editable_by(self.admin_no_perms))
        for user in (self.member, self.other_admin, self.site_org_editor):
            self.assertFalse(self.fresh(problem).is_accessible_by(user))
            self.assertFalse(self.fresh(problem).is_editable_by(user))

    def test_problem_requires_organization_private(self):
        for user in (self.co_admin, self.admin_no_perms):
            self.assertFalse(self.fresh(self.not_org_private_problem).is_accessible_by(user))
            self.assertFalse(self.fresh(self.not_org_private_problem).is_editable_by(user))

    def test_problem_querysets(self):
        visible = set(Problem.get_visible_problems(self.co_admin).values_list('code', flat=True))
        editable = set(Problem.get_editable_problems(self.co_admin).values_list('code', flat=True))
        self.assertTrue({'school_hidden', 'school_shared'} <= visible)
        self.assertTrue({'school_hidden', 'school_shared'} <= editable)
        self.assertFalse({'school_not_private', 'other_hidden'} & (visible | editable))
        self.assertIn('school_hidden', Problem.get_visible_problems(self.admin_no_perms).values_list('code', flat=True))
        self.assertFalse(Problem.get_editable_problems(self.admin_no_perms).exists())
        self.assertNotIn('school_hidden', Problem.get_visible_problems(self.member).values_list('code', flat=True))

    def test_access_follows_admin_list(self):
        self.org.admins.remove(self.co_admin.profile)
        self.assertFalse(self.fresh(self.private_problem).is_accessible_by(self.co_admin))
        self.assertFalse(self.fresh(self.hidden_contest).is_accessible_by(self.co_admin))
        self.assertFalse(self.fresh(self.hidden_post).is_editable_by(self.co_admin))
        self.assertNotIn('school_hidden', Problem.get_visible_problems(self.co_admin).values_list('code', flat=True))
        self.assertNotIn('school_hidden', Contest.get_visible_contests(self.co_admin).values_list('key', flat=True))

    def test_contest_access(self):
        for contest in (self.hidden_contest, self.private_contest):
            self.assertTrue(self.fresh(contest).is_accessible_by(self.co_admin))
            self.assertTrue(self.fresh(contest).is_editable_by(self.co_admin))
            self.assertTrue(self.fresh(contest).can_see_full_scoreboard(self.co_admin))
            self.assertTrue(self.fresh(contest).can_see_full_submission_list(self.co_admin))
            self.assertTrue(self.fresh(contest).is_accessible_by(self.admin_no_perms))
            self.assertFalse(self.fresh(contest).is_editable_by(self.admin_no_perms))
            for user in (self.member, self.other_admin, self.site_org_editor):
                self.assertFalse(self.fresh(contest).is_accessible_by(user))
                self.assertFalse(self.fresh(contest).is_editable_by(user))
                self.assertFalse(self.fresh(contest).can_see_full_scoreboard(user))

    def test_contest_querysets(self):
        visible = Contest.get_visible_contests(self.co_admin)
        self.assertCountEqual(
            visible.filter(organization=self.org).values_list('key', flat=True),
            ['school_hidden', 'school_private', 'school_voi'],
        )
        self.assertNotIn('other_hidden', visible.values_list('key', flat=True))
        annotated = visible.get(key='school_hidden')
        self.assertTrue(annotated.has_curator)
        self.assertTrue(annotated.can_see_full_scoreboard(self.co_admin))
        self.assertFalse(
            Contest.get_visible_contests(self.member).filter(key__in=['school_hidden', 'school_private']).exists(),
        )

    def test_hidden_results(self):
        self.assertTrue(self.fresh(self.voi_contest).should_hide_result(self.member))
        self.assertFalse(self.fresh(self.voi_contest).should_hide_result(self.co_admin))
        self.assertFalse(Contest.get_visible_contests(self.co_admin).get(key='school_voi')
                         .should_hide_result(self.co_admin))
        self.assertTrue(Contest.get_visible_contests(self.member).get(key='school_voi')
                        .should_hide_result(self.member))

    def test_post_access(self):
        post = self.fresh(self.hidden_post)
        self.assertTrue(post.is_editable_by(self.co_admin))
        self.assertTrue(post.can_see(self.co_admin))
        self.assertFalse(post.is_editable_by(self.admin_no_perms))
        for user in (self.member, self.other_admin, self.site_org_editor):
            self.assertFalse(post.is_editable_by(user))
            self.assertFalse(post.can_see(user))

    def test_views_as_co_admin(self):
        self.client.force_login(self.co_admin)
        for url in (
            reverse('problem_detail', args=['school_hidden']),
            reverse('problem_edit', args=['school_hidden']),
            reverse('contest_view', args=['school_hidden']),
            reverse('contest_edit', args=['school_hidden']),
            reverse('contest_view', args=['school_private']),
            reverse('contest_ranking', args=['school_private']),
            reverse('blog_post', args=[self.hidden_post.id, self.hidden_post.slug]),
            reverse('blog_post_edit', args=[self.hidden_post.id, self.hidden_post.slug]),
            reverse('admin:judge_problem_change', args=[self.private_problem.id]),
            reverse('admin:judge_contest_change', args=[self.hidden_contest.id]),
            reverse('admin:judge_blogpost_change', args=[self.hidden_post.id]),
        ):
            with self.subTest(url=url):
                self.assert_allowed(self.client.get(url))

        response = self.client.get(reverse('problem_list_organization', args=['school']))
        self.assertIn('school_hidden', [p.code for p in response.context['problems']])
        response = self.client.get(reverse('contest_list_organization', args=['school']))
        self.assertContains(response, reverse('contest_view', args=['school_hidden']))
        response = self.client.get(reverse('contest_list'))
        self.assertContains(response, SPECTATE_BUTTON)
        self.assertNotContains(response, JOIN_BUTTON)
        response = self.client.get(reverse('organization_home', args=['school']))
        self.assertIn(self.hidden_post, response.context['posts'])
        response = self.client.get(reverse('admin:judge_problem_changelist'))
        self.assertContains(response, 'school_hidden')
        response = self.client.get(reverse('admin:judge_contest_changelist'))
        self.assertContains(response, 'school_hidden')

    def test_views_denied(self):
        for user in (self.member, self.other_admin):
            self.client.force_login(user)
            for url in (
                reverse('problem_detail', args=['school_hidden']),
                reverse('problem_edit', args=['school_hidden']),
                reverse('contest_view', args=['school_hidden']),
                reverse('contest_view', args=['school_private']),
                reverse('contest_edit', args=['school_hidden']),
                reverse('blog_post', args=[self.hidden_post.id, self.hidden_post.slug]),
                reverse('blog_post_edit', args=[self.hidden_post.id, self.hidden_post.slug]),
            ):
                with self.subTest(user=user.username, url=url):
                    self.assert_denied(self.client.get(url))
        self.client.force_login(self.member)
        response = self.client.get(reverse('organization_home', args=['school']))
        self.assertNotIn(self.hidden_post, response.context['posts'])

    def test_organization_home_for_site_organization_editor(self):
        self.client.force_login(self.site_org_editor)
        response = self.client.get(reverse('organization_home', args=['school']))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.hidden_post, response.context['posts'])

    def test_bulk_delete_by_co_admin(self):
        self.client.force_login(self.co_admin)
        response = self.client.post(
            reverse('organization_problems_bulk_delete', args=['school']),
            {'problem_ids': [self.private_problem.id, self.shared_problem.id, self.not_org_private_problem.id]},
        )
        self.assertFalse(Problem.available.filter(code__in=['school_hidden', 'school_shared']).exists())
        self.assertTrue(Problem.available.filter(code='school_not_private').exists())
        self.assertCountEqual(
            [str(message) for message in get_messages(response.wsgi_request)],
            ['1 problem was skipped because you are not its author.', 'Successfully deleted 2 problems.'],
        )

    def test_bulk_delete_needs_edit_permission(self):
        self.client.force_login(self.admin_no_perms)
        response = self.client.get(reverse('organization_monthly_usage', args=['school']))
        self.assertNotIn(self.admin_no_perms.profile.id, self.deletable_by(response, self.private_problem))
        self.assertIn(self.admin_no_perms.profile.id, self.deletable_by(response, self.shared_problem))
        self.client.post(
            reverse('organization_problems_bulk_delete', args=['school']),
            {'problem_ids': [self.private_problem.id, self.shared_problem.id]},
        )
        self.assertTrue(Problem.available.filter(code='school_hidden').exists())
        self.assertFalse(Problem.available.filter(code='school_shared').exists())

    def test_bulk_delete_by_other_admin(self):
        self.client.force_login(self.other_admin)
        self.client.post(
            reverse('organization_problems_bulk_delete', args=['school']),
            {'problem_ids': [self.private_problem.id]},
        )
        self.assertTrue(Problem.available.filter(code='school_hidden').exists())

    def test_submissions_in_contest(self):
        submission = self.contest_submission
        self.assertTrue(self.fresh(submission).can_see_detail(self.co_admin))
        self.assertFalse(self.fresh(submission).can_see_detail(self.other_admin))
        source_url = reverse('submission_source', args=[submission.id])
        status_url = reverse('submission_status', args=[submission.id])

        self.client.force_login(self.co_admin)
        self.assert_allowed(self.client.get(status_url))
        self.assertContains(self.client.get(reverse('contest_all_submissions', args=['school_private'])), source_url)
        self.assertContains(self.client.get(reverse('all_submissions')), status_url)

        self.client.force_login(self.other_admin)
        self.assertNotContains(self.client.get(reverse('all_submissions')), status_url)

    def test_submission_admin(self):
        change_url = reverse('admin:judge_submission_change', args=[self.problem_submission.id])
        rejudge_url = reverse('admin:judge_submission_rejudge', args=[self.problem_submission.id])

        self.client.force_login(self.co_admin)
        self.assertContains(self.client.get(reverse('admin:judge_submission_changelist')), change_url)
        with patch.object(Submission, 'judge') as judge:
            self.assertEqual(self.client.post(rejudge_url).status_code, 302)
        judge.assert_called_once()

        with patch.object(Submission, 'judge') as judge:
            self.client.post(reverse('admin:judge_submission_changelist'), {
                'action': 'judge', '_selected_action': [self.problem_submission.id],
            })
        judge.assert_called_once()

        self.client.force_login(self.other_admin)
        self.assertNotContains(self.client.get(reverse('admin:judge_submission_changelist')), change_url)
        with patch.object(Submission, 'judge') as judge:
            self.assertEqual(self.client.post(rejudge_url).status_code, 403)
        judge.assert_not_called()

    def test_submission_list_queries_do_not_grow_per_contest(self):
        self.client.force_login(self.co_admin)
        url = reverse('all_submissions')

        def count_queries():
            with CaptureQueriesContext(connection) as queries:
                self.assertEqual(self.client.get(url).status_code, 200)
            return len(queries)

        self.client.get(url)
        before = count_queries()
        for key in ('school_extra_1', 'school_extra_2'):
            contest = create_contest(key=key, is_organization_private=True, organization=self.org)
            create_submission(self.member, self.public_problem, contest)
        self.assertEqual(count_queries(), before)

    def deletable_by(self, response, problem):
        match = re.search(r'value="%d"\s+data-author-ids="([^"]*)"' % problem.id, response.content.decode())
        self.assertIsNotNone(match, problem.code)
        return json.loads(match.group(1))

    def test_usage_dashboard_lets_co_admin_delete(self):
        self.client.force_login(self.co_admin)
        response = self.client.get(reverse('organization_monthly_usage', args=['school']))
        self.assertIn(self.co_admin.profile.id, self.deletable_by(response, self.private_problem))
        self.assertNotIn(self.co_admin.profile.id, self.deletable_by(response, self.not_org_private_problem))

        Problem.objects.filter(id=self.private_problem.id).update(archived_at=timezone.now())
        response = self.client.get(reverse('organization_archived_problems', args=['school']))
        self.assertIn(self.co_admin.profile.id, self.deletable_by(response, self.private_problem))

    def test_usage_dashboard_queries_do_not_grow_per_problem(self):
        self.client.force_login(self.co_admin)
        url = reverse('organization_monthly_usage', args=['school'])

        def count_queries():
            with CaptureQueriesContext(connection) as queries:
                self.assertEqual(self.client.get(url).status_code, 200)
            return len(queries)

        self.client.get(url)
        before = count_queries()
        for code in ('school_extra_1', 'school_extra_2'):
            create_problem(code=code, is_public=False, is_organization_private=True, organization=self.org)
        self.assertEqual(count_queries(), before)
