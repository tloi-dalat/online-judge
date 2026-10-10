import os
import shutil
import tempfile
from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from judge.models import Contest, ContestProblem, Problem, ProblemGroup, ProblemTranslation, Profile


def fake_render_pdf(*, title, html, **kwargs):
    return ('%PDF ' + title + '\n' + html).encode()


def pdf_enabled():
    return mock.patch.multiple('judge.views.contests', PDF_RENDERING_ENABLED=True,
                               render_pdf=mock.DEFAULT)


class ContestPdfTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.outsider = user_model.objects.create_user(username='outsider', password='pw')
        Profile.objects.create(user=cls.outsider)
        cls.superuser = user_model.objects.create_superuser(username='root', password='pw', email='root@example.com')
        Profile.objects.create(user=cls.superuser)

        cls.group = ProblemGroup.objects.create(name='group', full_name='Group')
        now = timezone.now()
        # A visible contest that has not started yet, with private problems.
        cls.contest = Contest.objects.create(key='upcoming', name='Upcoming Contest', is_visible=True,
                                             start_time=now + timedelta(days=1), end_time=now + timedelta(days=2))
        cls.first = cls.make_problem('secret_one', 'Secret One', 'FIRST SECRET STATEMENT')
        cls.second = cls.make_problem('secret_two', 'Secret Two', 'SECOND SECRET STATEMENT')
        ContestProblem.objects.create(contest=cls.contest, problem=cls.second, points=1, order=2)
        ContestProblem.objects.create(contest=cls.contest, problem=cls.first, points=1, order=1)
        ProblemTranslation.objects.create(problem=cls.first, language='vi', name='Bài một',
                                          description='ĐỀ BÀI TIẾNG VIỆT')

    @classmethod
    def make_problem(cls, code, name, description, is_public=False):
        return Problem.objects.create(code=code, name=name, description=description, group=cls.group, time_limit=1,
                                      memory_limit=65536, points=1, is_public=is_public)

    def get_pdf(self, language='en'):
        with pdf_enabled() as mocks:
            mocks['render_pdf'].side_effect = fake_render_pdf
            response = self.client.get(reverse('contest_all_problems_pdf', args=[self.contest.key, language]))
            content = b''.join(response.streaming_content) if response.streaming else response.content
            return response, content, mocks['render_pdf']


@override_settings(DMOJ_PDF_PROBLEM_CACHE=None)
class ContestPdfAccessTest(ContestPdfTestBase):
    def test_anonymous_cannot_get_private_statements(self):
        response, content, render = self.get_pdf()
        self.assertFalse(render.called)
        self.assertNotIn(b'SECRET STATEMENT', content)
        self.assertNotEqual(response['Content-Type'], 'application/pdf')

    def test_outsider_cannot_get_private_statements(self):
        self.client.force_login(self.outsider)
        response, content, render = self.get_pdf()
        self.assertFalse(render.called)
        self.assertNotIn(b'SECRET STATEMENT', content)

    def test_superuser_gets_problems_in_contest_order(self):
        self.client.force_login(self.superuser)
        response, content, render = self.get_pdf('en')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('filename=upcoming.en.pdf', response['Content-Disposition'])
        body = content.decode()
        self.assertLess(body.index('FIRST SECRET STATEMENT'), body.index('SECOND SECRET STATEMENT'))

    def test_translated_statement_is_used(self):
        self.client.force_login(self.superuser)
        response, content, render = self.get_pdf('vi')
        body = content.decode()
        self.assertIn('Bài một', body)
        self.assertIn('ĐỀ BÀI TIẾNG VIỆT', body)
        self.assertNotIn('FIRST SECRET STATEMENT', body)
        self.assertIn('SECOND SECRET STATEMENT', body)

    def test_disabled_without_pdfoid(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('contest_all_problems_pdf', args=[self.contest.key, 'en']))
        self.assertNotEqual(response.get('Content-Type'), 'application/pdf')


class ContestPdfCacheTest(ContestPdfTestBase):
    def setUp(self):
        self.cache_dir = tempfile.mkdtemp()
        self.override = override_settings(DMOJ_PDF_PROBLEM_CACHE=self.cache_dir)
        self.override.enable()
        self.client.force_login(self.superuser)

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.cache_dir)

    def cached(self):
        return sorted(os.listdir(self.cache_dir))

    def test_cache_does_not_clash_with_problem_code(self):
        clash = self.make_problem(self.contest.key, 'Clash', 'CLASH STATEMENT', is_public=True)
        self.get_pdf()
        self.assertEqual(self.cached(), ['contest-%d.en.pdf' % self.contest.id])
        self.assertFalse(os.path.exists(os.path.join(self.cache_dir, '%s.en.pdf' % clash.code)))

    def test_cache_is_reused(self):
        self.get_pdf()
        _, _, render = self.get_pdf()
        self.assertFalse(render.called)

    def assert_invalidated_by(self, change):
        self.get_pdf()
        self.assertEqual(len(self.cached()), 1)
        change()
        self.assertEqual(self.cached(), [])
        _, content, render = self.get_pdf()
        self.assertTrue(render.called)
        return content.decode()

    def test_problem_edit_invalidates(self):
        def change():
            self.first.description = 'UPDATED STATEMENT'
            self.first.save()
        self.assertIn('UPDATED STATEMENT', self.assert_invalidated_by(change))

    def test_translation_edit_invalidates(self):
        translation = ProblemTranslation.objects.get(problem=self.first)
        translation.description = 'ĐỀ MỚI'
        self.assert_invalidated_by(translation.save)
        self.get_pdf()
        self.assert_invalidated_by(translation.delete)

    def test_contest_problem_list_change_invalidates(self):
        extra = self.make_problem('extra', 'Extra', 'EXTRA STATEMENT')
        body = self.assert_invalidated_by(
            lambda: ContestProblem.objects.create(contest=self.contest, problem=extra, points=1, order=3))
        self.assertIn('EXTRA STATEMENT', body)
        body = self.assert_invalidated_by(lambda: ContestProblem.objects.get(problem=extra).delete())
        self.assertNotIn('EXTRA STATEMENT', body)

    def test_contest_edit_invalidates(self):
        def change():
            self.contest.name = 'Renamed Contest'
            self.contest.save()
        self.assert_invalidated_by(change)


class ContestRawTemplateTest(TestCase):
    def test_uses_same_mathjax_as_problem_raw(self):
        def scripts(template):
            with open(get_template(template).origin.name, encoding='utf-8') as f:
                source = f.read()
            return [line.strip() for line in source.splitlines() if 'mathjax' in line.lower() or 'MathJax' in line]

        self.assertEqual(scripts('contest/all-problems-raw.html'), scripts('problem/raw.html'))
