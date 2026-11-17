from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from judge.models import Contest, Language, Problem, Submission
from judge.models.tests.util import create_blogpost, create_contest, create_organization, create_problem, \
    create_user

ADMIN_PERMISSIONS = (
    'edit_own_problem', 'edit_own_contest', 'edit_organization_post', 'create_organization_problem',
    'create_private_contest', 'change_problem', 'change_contest', 'change_blogpost',
)


class OrganizationAdminAccessTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        _now = timezone.now()
        cls.owner = create_user(username='owner', is_staff=True, user_permissions=ADMIN_PERMISSIONS)
        cls.co_admin = create_user(username='co_admin', is_staff=True, user_permissions=ADMIN_PERMISSIONS)
        cls.admin_no_perms = create_user(username='admin_no_perms')
        cls.other_admin = create_user(username='other_admin', is_staff=True, user_permissions=ADMIN_PERMISSIONS)
        cls.member = create_user(username='member')

        cls.org = create_organization(name='school', admins=('owner', 'co_admin', 'admin_no_perms'))
        cls.other_org = create_organization(name='other', admins=('other_admin',))
        for user in (cls.owner, cls.co_admin, cls.admin_no_perms, cls.member):
            user.profile.organizations.add(cls.org)
        cls.other_admin.profile.organizations.add(cls.other_org)

        cls.private_problem = create_problem(
            code='school_hidden',
            is_public=False,
            is_organization_private=True,
            organization=cls.org,
            authors=('owner',),
        )
        cls.not_org_private_problem = create_problem(
            code='school_not_private',
            is_public=False,
            is_organization_private=False,
            organization=cls.org,
            authors=('owner',),
        )
        cls.other_org_problem = create_problem(
            code='other_hidden',
            is_public=False,
            is_organization_private=True,
            organization=cls.other_org,
            authors=('other_admin',),
        )

        cls.hidden_contest = create_contest(
            key='school_hidden',
            is_visible=False,
            is_organization_private=True,
            organization=cls.org,
            authors=('owner',),
            start_time=_now - timezone.timedelta(days=1),
            end_time=_now + timezone.timedelta(days=1),
        )
        cls.private_contest = create_contest(
            key='school_private',
            is_visible=True,
            is_private=True,
            is_organization_private=True,
            organization=cls.org,
            authors=('owner',),
        )
        cls.other_org_contest = create_contest(
            key='other_hidden',
            is_visible=False,
            is_organization_private=True,
            organization=cls.other_org,
            authors=('other_admin',),
        )

        cls.submission = Submission.objects.create(
            user=cls.member.profile,
            problem=cls.private_problem,
            language=Language.get_python3(),
            contest_object=cls.private_contest,
            result='WA',
            status='D',
            time=0.1,
            memory=1024,
            points=0,
            case_points=0,
            case_total=1,
        )

        cls.hidden_post = create_blogpost(
            title='school_hidden_post',
            visible=False,
            organization=cls.org,
            authors=('owner',),
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
        self.assertTrue(self.fresh(problem).is_accessible_by(self.admin_no_perms))
        self.assertFalse(self.fresh(problem).is_editable_by(self.admin_no_perms))
        for user in (self.member, self.other_admin):
            self.assertFalse(self.fresh(problem).is_accessible_by(user))
            self.assertFalse(self.fresh(problem).is_editable_by(user))

    def test_problem_requires_organization_private(self):
        for user in (self.co_admin, self.admin_no_perms):
            self.assertFalse(self.fresh(self.not_org_private_problem).is_accessible_by(user))
            self.assertFalse(self.fresh(self.not_org_private_problem).is_editable_by(user))

    def test_problem_querysets(self):
        visible = set(Problem.get_visible_problems(self.co_admin).values_list('code', flat=True))
        editable = set(Problem.get_editable_problems(self.co_admin).values_list('code', flat=True))
        self.assertIn('school_hidden', visible)
        self.assertIn('school_hidden', editable)
        self.assertNotIn('school_not_private', visible | editable)
        self.assertNotIn('other_hidden', visible | editable)
        self.assertIn('school_hidden', Problem.get_visible_problems(self.admin_no_perms).values_list('code', flat=True))
        self.assertFalse(Problem.get_editable_problems(self.admin_no_perms).exists())
        self.assertNotIn('school_hidden', Problem.get_visible_problems(self.member).values_list('code', flat=True))

    def test_contest_access(self):
        for contest in (self.hidden_contest, self.private_contest):
            self.assertTrue(self.fresh(contest).is_accessible_by(self.co_admin))
            self.assertTrue(self.fresh(contest).is_editable_by(self.co_admin))
            self.assertTrue(self.fresh(contest).can_see_full_scoreboard(self.co_admin))
            self.assertTrue(self.fresh(contest).is_accessible_by(self.admin_no_perms))
            self.assertFalse(self.fresh(contest).is_editable_by(self.admin_no_perms))
            for user in (self.member, self.other_admin):
                self.assertFalse(self.fresh(contest).is_accessible_by(user))
                self.assertFalse(self.fresh(contest).is_editable_by(user))

    def test_contest_querysets(self):
        visible = Contest.get_visible_contests(self.co_admin)
        self.assertCountEqual(
            visible.filter(organization=self.org).values_list('key', flat=True),
            ['school_hidden', 'school_private'],
        )
        self.assertNotIn('other_hidden', visible.values_list('key', flat=True))
        annotated = visible.get(key='school_hidden')
        self.assertTrue(annotated.has_organization_admin)
        self.assertFalse(annotated.should_hide_result(self.co_admin))
        self.assertFalse(Contest.get_visible_contests(self.member).filter(organization=self.org).exists())

    def test_post_access(self):
        post = self.fresh(self.hidden_post)
        self.assertTrue(post.is_editable_by(self.co_admin))
        self.assertTrue(post.can_see(self.co_admin))
        self.assertFalse(post.is_editable_by(self.admin_no_perms))
        for user in (self.member, self.other_admin):
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
        self.assertEqual(response.status_code, 200)
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
                reverse('problem_edit', args=['school_hidden']),
                reverse('contest_edit', args=['school_hidden']),
                reverse('blog_post_edit', args=[self.hidden_post.id, self.hidden_post.slug]),
            ):
                with self.subTest(user=user.username, url=url):
                    self.assert_denied(self.client.get(url))
            self.assert_denied(self.client.get(reverse('contest_view', args=['school_hidden'])))
            self.assert_denied(self.client.get(reverse('contest_view', args=['school_private'])))
            self.assert_denied(self.client.get(reverse('problem_detail', args=['school_hidden'])))
        self.client.force_login(self.member)
        response = self.client.get(reverse('organization_home', args=['school']))
        self.assertNotIn(self.hidden_post, response.context['posts'])

    def test_bulk_delete_by_co_admin(self):
        self.client.force_login(self.co_admin)
        self.client.post(
            reverse('organization_problems_bulk_delete', args=['school']),
            {'problem_ids': [self.private_problem.id, self.not_org_private_problem.id]},
        )
        self.assertFalse(Problem.available.filter(id=self.private_problem.id).exists())
        self.assertTrue(Problem.available.filter(id=self.not_org_private_problem.id).exists())

    def test_bulk_delete_by_other_admin(self):
        self.client.force_login(self.other_admin)
        self.client.post(
            reverse('organization_problems_bulk_delete', args=['school']),
            {'problem_ids': [self.private_problem.id]},
        )
        self.assertTrue(Problem.available.filter(id=self.private_problem.id).exists())

    def test_submissions(self):
        submission = Submission.objects.get(pk=self.submission.pk)
        self.assertTrue(submission.can_see_detail(self.co_admin))
        self.assertFalse(Submission.objects.get(pk=self.submission.pk).can_see_detail(self.other_admin))
        self.client.force_login(self.co_admin)
        self.assert_allowed(self.client.get(reverse('submission_status', args=[self.submission.id])))
        response = self.client.get(reverse('admin:judge_submission_changelist'))
        self.assertContains(response, reverse('admin:judge_submission_change', args=[self.submission.id]))
        response = self.client.get(reverse('contest_all_submissions', args=['school_private']))
        self.assertContains(response, reverse('submission_status', args=[self.submission.id]))
        response = self.client.get(reverse('all_submissions'))
        self.assertEqual(response.status_code, 200)
        self.client.force_login(self.other_admin)
        response = self.client.get(reverse('admin:judge_submission_changelist'))
        self.assertNotContains(response, reverse('admin:judge_submission_change', args=[self.submission.id]))
