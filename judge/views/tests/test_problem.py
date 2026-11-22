from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from judge.models import Judge, Language, Submission, SubmissionSource
from judge.models.tests.util import (
    CommonDataMixin,
    create_contest,
    create_contest_participation,
    create_contest_problem,
    create_problem,
    create_solution,
    create_user,
)


class ProblemSubmitLanguageMemoryTestCase(CommonDataMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.problem_a = create_problem(
            code='problem_a',
            is_public=True,
        )
        cls.problem_b = create_problem(
            code='problem_b',
            is_public=True,
        )

        cls.python_lang, _ = Language.objects.get_or_create(
            key='PYTHON3',
            defaults={
                'name': 'Python 3',
                'short_name': 'Python 3',
                'common_name': 'Python',
            },
        )
        cls.cpp_lang, _ = Language.objects.get_or_create(
            key='CPP17',
            defaults={
                'name': 'C++ 17',
                'short_name': 'C++17',
                'common_name': 'C++',
            },
        )

        cls.user = cls.users['normal']
        cls.user.profile.language = cls.cpp_lang
        cls.user.profile.save()

    def test_default_language_no_submissions(self):
        self.assertEqual(Submission.objects.filter(user=self.user.profile).count(), 0)

        self.client.force_login(self.user)
        response = self.client.get(reverse('problem_submit', args=[self.problem_a.code]))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['default_lang'], self.cpp_lang)

    def test_default_language_after_submission(self):
        self.client.force_login(self.user)

        # Submit to problem_a in Python
        Submission.objects.create(
            user=self.user.profile,
            problem=self.problem_a,
            language=self.python_lang,
            status='D',
        )

        # Query submit page for problem_b (never submitted before)
        # Should default to user's profile language (C++), NOT Python
        response = self.client.get(reverse('problem_submit', args=[self.problem_b.code]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['default_lang'], self.cpp_lang)

        # Query submit page for problem_a
        # Should default to the last submission on problem_a (Python)
        response = self.client.get(reverse('problem_submit', args=[self.problem_a.code]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['default_lang'], self.python_lang)

        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.language, self.cpp_lang)

    def test_default_language_resubmit(self):
        self.client.force_login(self.user)

        # Create old submission in Python
        submission_python = Submission.objects.create(
            user=self.user.profile,
            problem=self.problem_a,
            language=self.python_lang,
            status='D',
        )
        SubmissionSource.objects.create(
            submission=submission_python,
            source='print("Hello Python")',
        )

        # Create latest submission in C++
        submission_cpp = Submission.objects.create(
            user=self.user.profile,
            problem=self.problem_a,
            language=self.cpp_lang,
            status='D',
        )
        SubmissionSource.objects.create(
            submission=submission_cpp,
            source='print("Hello C++")',
        )

        # Verify absolute last submission is C++
        last_submission = Submission.objects.filter(user=self.user.profile).order_by('-id').first()
        self.assertEqual(last_submission.language, self.cpp_lang)

        # Request resubmit page for submission_python (Python)
        response = self.client.get(
            reverse('problem_submit', kwargs={'problem': self.problem_a.code, 'submission': submission_python.id}),
        )
        self.assertEqual(response.status_code, 200)

        # Should default to the resubmitted language (Python), NOT the latest (C++)
        self.assertEqual(response.context['default_lang'], self.python_lang)

    def test_default_language_unavailable_for_problem(self):
        # Set user's profile language to Python, which will be the default language
        # since the user has no submissions to problem_b.
        self.user.profile.language = self.python_lang
        self.user.profile.save()

        self.client.force_login(self.user)

        # Setup problem_b so that it only allows CPP17 language and has an online judge
        self.problem_b.allowed_languages.add(self.cpp_lang)
        # The submit form (and its language warning) is only shown for problems with test data.
        self.problem_b.is_manually_managed = True
        self.problem_b.save()
        judge = Judge.objects.create(
            name='test_judge',
            online=True,
            storages=[self.problem_b.effective_storage],
        )
        judge.runtimes.add(self.cpp_lang)

        # Query submit page for problem_b
        response = self.client.get(reverse('problem_submit', args=[self.problem_b.code]))
        self.assertEqual(response.status_code, 200)

        # default_lang context should be python_lang (from profile language)
        self.assertEqual(response.context['default_lang'], self.python_lang)

        # The warning alert should be displayed in the HTML because Python is not usable
        # in problem_b.usable_languages
        self.assertContains(response, 'alert-warning')
        self.assertContains(response, '<b>Python 3</b>')


class ProblemEditorialInContestTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        cls.user = create_user(username='contestant')

        cls.contest = create_contest(
            key='contest_in',
            start_time=now - timezone.timedelta(hours=1),
            end_time=now + timezone.timedelta(hours=2),
            is_visible=True,
        )

        cls.problem_in = create_problem(
            code='prob_in',
            is_public=True,
        )
        create_solution(
            problem=cls.problem_in,
            is_public=True,
            publish_on=now - timezone.timedelta(days=1),
            content='Editorial in contest',
        )
        create_contest_problem(
            contest=cls.contest,
            problem=cls.problem_in,
            order=1,
        )

        cls.problem_in_no_sol = create_problem(
            code='prob_in_no_sol',
            is_public=True,
        )
        create_contest_problem(
            contest=cls.contest,
            problem=cls.problem_in_no_sol,
            order=2,
        )

        cls.problem_out = create_problem(
            code='prob_out',
            is_public=True,
        )
        create_solution(
            problem=cls.problem_out,
            is_public=True,
            publish_on=now - timezone.timedelta(days=1),
            content='Editorial outside contest',
        )

        cls.participation = create_contest_participation(
            contest=cls.contest,
            user=cls.user.profile,
            real_start=now - timezone.timedelta(minutes=30),
        )
        cls.user.profile.current_contest = cls.participation
        cls.user.profile.save()

    def test_user_in_contest_cannot_view_current_contest_editorial(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('problem_editorial', args=[self.problem_in.code]))
        self.assertEqual(response.status_code, 403)

        response = self.client.post(reverse('problem_editorial', args=[self.problem_in.code]), {'comment': 'test'})
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('problem_editorial', args=[self.problem_in_no_sol.code]))
        self.assertEqual(response.status_code, 404)

    def test_user_in_contest_can_view_outside_contest_editorial(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('problem_editorial', args=[self.problem_out.code]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editorial outside contest')

    def test_user_leaving_live_contest_cannot_view_editorial(self):
        self.client.force_login(self.user)
        self.client.post(reverse('contest_leave', args=[self.contest.key]))
        response = self.client.get(reverse('problem_editorial', args=[self.problem_in.code]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('problem_detail', args=[self.problem_in.code]))
        self.assertNotContains(response, reverse('problem_editorial', args=[self.problem_in.code]))
