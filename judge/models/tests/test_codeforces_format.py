from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from judge.contest_format import CodeforcesContestFormat
from judge.models import ContestSubmission, Language, Submission
from judge.models.tests.util import CommonDataMixin, create_contest, create_contest_participation, \
    create_contest_problem, create_problem


class CodeforcesContestFormatTestCase(CommonDataMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Create Codeforces contest: duration 200 minutes
        cls.contest_start = timezone.now() - timedelta(minutes=100)
        cls.contest_end = cls.contest_start + timedelta(minutes=200)

        cls.cf_contest = create_contest(
            key='cf_contest',
            name='Codeforces Test Contest',
            format_name='codeforces',
            start_time=cls.contest_start,
            end_time=cls.contest_end,
        )

        # Create two problems
        cls.problem_a = create_problem(code='prob_a')
        cls.problem_b = create_problem(code='prob_b')

        cls.cp_a = create_contest_problem(
            contest=cls.cf_contest,
            problem=cls.problem_a,
            points=500,
            order=1,
        )
        cls.cp_b = create_contest_problem(
            contest=cls.cf_contest,
            problem=cls.problem_b,
            points=1000,
            order=2,
        )

        # Create participation starting at contest start
        cls.participation = create_contest_participation(
            contest=cls.cf_contest,
            user='normal',
            real_start=cls.contest_start,
        )

    def test_codeforces_scoring(self):
        py3 = Language.get_python3()

        # Problem A:
        # Submission 1: WA at minute 10
        sub_a1 = Submission.objects.create(
            user=self.users['normal'].profile,
            problem=self.problem_a,
            language=py3,
            contest_object=self.cf_contest,
            result='WA',
            status='D',
            case_points=0,
            case_total=10,
        )
        Submission.objects.filter(id=sub_a1.id).update(date=self.contest_start + timedelta(minutes=10))
        ContestSubmission.objects.create(
            submission=sub_a1,
            problem=self.cp_a,
            participation=self.participation,
            points=0.0,
        )

        # Submission 2: WA at minute 20
        sub_a2 = Submission.objects.create(
            user=self.users['normal'].profile,
            problem=self.problem_a,
            language=py3,
            contest_object=self.cf_contest,
            result='WA',
            status='D',
            case_points=0,
            case_total=10,
        )
        Submission.objects.filter(id=sub_a2.id).update(date=self.contest_start + timedelta(minutes=20))
        ContestSubmission.objects.create(
            submission=sub_a2,
            problem=self.cp_a,
            participation=self.participation,
            points=0.0,
        )

        # Submission 3: AC at minute 30
        sub_a3 = Submission.objects.create(
            user=self.users['normal'].profile,
            problem=self.problem_a,
            language=py3,
            contest_object=self.cf_contest,
            result='AC',
            status='D',
            case_points=10,
            case_total=10,
        )
        Submission.objects.filter(id=sub_a3.id).update(date=self.contest_start + timedelta(minutes=30))
        ContestSubmission.objects.create(
            submission=sub_a3,
            problem=self.cp_a,
            participation=self.participation,
            points=500.0,
        )

        # Problem B:
        # Submission 1: WA at minute 40
        sub_b1 = Submission.objects.create(
            user=self.users['normal'].profile,
            problem=self.problem_b,
            language=py3,
            contest_object=self.cf_contest,
            result='WA',
            status='D',
            case_points=0,
            case_total=10,
        )
        Submission.objects.filter(id=sub_b1.id).update(date=self.contest_start + timedelta(minutes=40))
        ContestSubmission.objects.create(
            submission=sub_b1,
            problem=self.cp_b,
            participation=self.participation,
            points=0.0,
        )

        # Submission 2: AC at minute 50
        sub_b2 = Submission.objects.create(
            user=self.users['normal'].profile,
            problem=self.problem_b,
            language=py3,
            contest_object=self.cf_contest,
            result='AC',
            status='D',
            case_points=10,
            case_total=10,
        )
        Submission.objects.filter(id=sub_b2.id).update(date=self.contest_start + timedelta(minutes=50))
        ContestSubmission.objects.create(
            submission=sub_b2,
            problem=self.cp_b,
            participation=self.participation,
            points=1000.0,
        )

        # Run update
        self.cf_contest.format.update_participation(self.participation)

        # Reload from DB
        self.participation.refresh_from_db()

        # Computations:
        # Duration: 200.0 mins
        # min_points_ratio: 0.3
        # decay_rate: 0.004
        #
        # Prob A (500 pts):
        # time_ac: minute 30
        # score_decay: 30 * 0.004 * 500 = 60.0
        # base_score: max(150, 500 - 60.0) = 440.0
        # wrong_subs before AC: 2 (sub_a1, sub_a2)
        # points_gained: max(0, 440.0 - 50 * 2) = 340.0
        # penalty: 30 + 20 * 2 = 70.0 mins
        #
        # Prob B (1000 pts):
        # time_ac: minute 50
        # score_decay: 50 * 0.004 * 1000 = 200.0
        # base_score: max(300, 1000 - 200.0) = 800.0
        # wrong_subs before AC: 1 (sub_b1)
        # points_gained: max(0, 800.0 - 50 * 1) = 750.0
        # penalty: 50 + 20 * 1 = 70.0 mins
        #
        # Total:
        # Score = 340.0 + 750.0 = 1090.0
        # Cumtime = (70.0 + 70.0) * 60 = 8400.0 seconds

        self.assertEqual(self.participation.score, 1090.0)
        self.assertEqual(self.participation.cumtime, 8400.0)

        # Check format_data
        format_data = self.participation.format_data
        prob_a_key = str(self.cp_a.id)
        prob_b_key = str(self.cp_b.id)

        self.assertIn(prob_a_key, format_data)
        self.assertEqual(format_data[prob_a_key]['points'], 340.0)
        self.assertEqual(format_data[prob_a_key]['penalty'], 2)
        self.assertEqual(format_data[prob_a_key]['time'], 30 * 60)

        self.assertIn(prob_b_key, format_data)
        self.assertEqual(format_data[prob_b_key]['points'], 750.0)
        self.assertEqual(format_data[prob_b_key]['penalty'], 1)
        self.assertEqual(format_data[prob_b_key]['time'], 50 * 60)


class CodeforcesScoringRulesTestCase(CommonDataMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.start = timezone.now() - timedelta(minutes=100)
        cls.contest = create_contest(
            key='cf_rules',
            format_name='codeforces',
            start_time=cls.start,
            end_time=cls.start + timedelta(minutes=200),
            frozen_last_minutes=60,
        )
        cls.problem = create_problem(code='cf_rules_a')
        cls.contest_problem = create_contest_problem(contest=cls.contest, problem=cls.problem, points=500, order=1,
                                                     partial=True)
        cls.participation = create_contest_participation(contest=cls.contest, user='normal', real_start=cls.start)

    def submit(self, minute, result, points):
        submission = Submission.objects.create(
            user=self.users['normal'].profile,
            problem=self.problem,
            language=Language.get_python3(),
            contest_object=self.contest,
            result=result,
            status='D',
            case_points=points / 50,
            case_total=10,
        )
        Submission.objects.filter(id=submission.id).update(date=self.start + timedelta(minutes=minute))
        return ContestSubmission.objects.create(
            submission=submission,
            problem=self.contest_problem,
            participation=self.participation,
            points=points,
        )

    def update(self):
        self.contest.format.update_participation(self.participation)
        self.participation.refresh_from_db()
        return self.participation.format_data[str(self.contest_problem.id)]

    def breakdown(self, contest_submission):
        return ContestSubmission.objects.get(id=contest_submission.id).contest_points_breakdown

    def test_minimum_points_include_wrong_submission_penalty(self):
        for minute in range(1, 9):
            self.submit(minute, 'WA', 0.0)
        accepted = self.submit(10, 'AC', 500.0)

        data = self.update()
        self.assertAlmostEqual(data['points'], 150.0)
        self.assertEqual(data['raw_points'], 500.0)
        self.assertEqual(data['penalty'], 8)
        self.assertAlmostEqual(self.participation.score, 150.0)
        self.assertEqual(self.participation.cumtime, (10 + 20 * 8) * 60)

        breakdown = self.breakdown(accepted)
        self.assertTrue(breakdown['is_minimum'])
        self.assertAlmostEqual(breakdown['minimum_points'], 150.0)
        self.assertAlmostEqual(breakdown['points_gained'], 150.0)

    def test_partial_points(self):
        self.submit(10, 'WA', 0.0)
        partial = self.submit(30, 'WA', 250.0)

        data = self.update()
        self.assertAlmostEqual(data['points'], 0.5 * (500 - 30 * 0.004 * 500) - 50)
        self.assertEqual(data['raw_points'], 250.0)
        self.assertEqual(data['penalty'], 1)
        self.assertAlmostEqual(self.breakdown(partial)['points_gained'], data['points'])

    def test_unsolved_problem(self):
        self.submit(10, 'WA', 0.0)
        self.submit(20, 'TLE', 0.0)

        data = self.update()
        self.assertEqual(data['points'], 0.0)
        self.assertEqual(data['penalty'], 2)
        self.assertEqual(self.participation.score, 0)
        self.assertEqual(self.participation.cumtime, 0)

    def test_no_scoreboard_freeze(self):
        self.submit(150, 'AC', 500.0)

        data = self.update()
        self.assertNotIn('pending', data)
        self.assertNotIn('frozen_points', data)
        self.assertEqual(self.participation.frozen_score, 0)
        self.assertFalse(self.contest.is_frozen)

    def test_submission_points_are_per_submission(self):
        wrong = self.submit(10, 'WA', 0.0)
        partial = self.submit(20, 'WA', 250.0)
        accepted = self.submit(40, 'AC', 500.0)
        self.update()

        self.assertEqual(ContestSubmission.objects.get(id=wrong.id).contest_points, 0.0)
        self.assertAlmostEqual(ContestSubmission.objects.get(id=partial.id).contest_points,
                               0.5 * (500 - 20 * 0.004 * 500) - 50)
        self.assertAlmostEqual(ContestSubmission.objects.get(id=accepted.id).contest_points,
                               500 - 40 * 0.004 * 500 - 2 * 50)

    def test_other_formats_keep_submission_points(self):
        contest = create_contest(key='cf_rules_default')
        contest_problem = create_contest_problem(contest=contest, problem=self.problem, points=500, order=1)
        participation = create_contest_participation(contest=contest, user='normal')
        submission = Submission.objects.create(
            user=self.users['normal'].profile,
            problem=self.problem,
            language=Language.get_python3(),
            contest_object=contest,
            result='WA',
            status='D',
        )
        contest_submission = ContestSubmission.objects.create(
            submission=submission,
            problem=contest_problem,
            participation=participation,
            points=250.0,
        )
        contest.format.update_participation(participation)

        contest_submission = ContestSubmission.objects.get(id=contest_submission.id)
        self.assertIsNone(contest_submission.contest_points_breakdown)
        self.assertEqual(contest_submission.contest_points, 250.0)

    def test_validate_config(self):
        CodeforcesContestFormat.validate(None)
        CodeforcesContestFormat.validate({'penalty_per_wrong_points': 50, 'min_points_ratio': 0.25})
        for config in ({'decay_rate': True}, {'decay_rate': '0.004'}, {'min_points_ratio': 1.5}, {'unknown': 1}, []):
            with self.assertRaises(ValidationError):
                CodeforcesContestFormat.validate(config)
