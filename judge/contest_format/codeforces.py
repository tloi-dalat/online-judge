from django.core.exceptions import ValidationError
from django.db import connection
from django.utils.translation import gettext as _, gettext_lazy, ngettext

from judge.contest_format.registry import register_contest_format
from judge.contest_format.vnoj import DEFAULT_RANKING_SQL, ParticipationInfo, VNOJContestFormat
from judge.timezone import from_database_time


@register_contest_format('codeforces')
class CodeforcesContestFormat(VNOJContestFormat):
    name = gettext_lazy('Codeforces')
    config_defaults = {
        'min_points_ratio': 0.3,
        'penalty_per_wrong_points': 50.0,
        'penalty_per_wrong_time': 20.0,
        'decay_rate': 0.004,
    }
    config_validators = {
        'min_points_ratio': lambda x: 0.0 <= x <= 1.0,
        'penalty_per_wrong_points': lambda x: x >= 0.0,
        'penalty_per_wrong_time': lambda x: x >= 0.0,
        'decay_rate': lambda x: x >= 0.0,
    }

    @classmethod
    def validate(cls, config):
        if config is None:
            return

        if not isinstance(config, dict):
            raise ValidationError('Codeforces-styled contest expects no config or dict as config')

        for key, value in config.items():
            if key not in cls.config_defaults:
                raise ValidationError('unknown config key "%s"' % key)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValidationError('invalid type for config key "%s"' % key)
            if not cls.config_validators[key](value):
                raise ValidationError('invalid value "%s" for config key "%s"' % (value, key))

    def get_problem_points(self, max_points, points, minutes, wrong_submissions):
        if not points or not max_points:
            return 0.0
        ratio = points / max_points
        minimum = ratio * max_points * self.config['min_points_ratio']
        decayed = ratio * (max_points - minutes * self.config['decay_rate'] * max_points)
        return max(minimum, decayed - self.config['penalty_per_wrong_points'] * wrong_submissions)

    def get_problem_submissions(self, participation, problem_id):
        return participation.submissions.exclude(submission__result__isnull=True) \
                                        .exclude(submission__result__in=['IE', 'CE']) \
                                        .filter(problem_id=problem_id)

    def calculate_participation_info(self, participation, frozen=False) -> ParticipationInfo:
        cumtime = 0
        score = 0
        format_data = {}

        problems_points = {cp.id: cp.points for cp in participation.contest.contest_problems.all()}

        with connection.cursor() as cursor:
            cursor.execute(DEFAULT_RANKING_SQL, (participation.id, participation.id))

            for points, time, prob_id in cursor.fetchall():
                time = from_database_time(time)
                dt_seconds = (time - participation.start).total_seconds()
                dt_minutes = int(dt_seconds // 60)
                problem_subs = self.get_problem_submissions(participation, prob_id)

                if points:
                    wrong_submissions = problem_subs.filter(submission__date__lt=time).count()
                    max_points = problems_points.get(prob_id, points)
                    points_gained = self.get_problem_points(max_points, points, dt_minutes, wrong_submissions)
                    cumtime += dt_minutes + self.config['penalty_per_wrong_time'] * wrong_submissions
                    score += points_gained
                else:
                    wrong_submissions = problem_subs.count()
                    points_gained = 0.0

                format_data[str(prob_id)] = {
                    'time': dt_seconds,
                    'points': points_gained,
                    'raw_points': points,
                    'penalty': wrong_submissions,
                }

        return ParticipationInfo(
            cumtime=max(cumtime * 60, 0),
            score=round(score, self.contest.points_precision),
            tiebreaker=0.0,
            format_data=format_data,
        )

    def update_participation(self, participation):
        info = self.calculate_participation_info(participation)
        participation.cumtime = info.cumtime
        participation.score = info.score
        participation.tiebreaker = info.tiebreaker
        participation.format_data = info.format_data
        participation.save()

    def get_format_data_for_api(self, entry, problem_points, frozen=False):
        if not entry:
            return entry
        return {
            'points': entry.get('points', 0),
            'raw_points': entry.get('raw_points', 0),
            'time': entry.get('time', 0),
            'penalty': entry.get('penalty', 0),
        }

    def get_submission_breakdown(self, contest_submission):
        max_points = contest_submission.problem.points
        if not contest_submission.points:
            return {'is_ac': False, 'max_points': max_points, 'points_gained': 0.0}

        participation = contest_submission.participation
        submission = contest_submission.submission
        minutes = int((submission.date - participation.start).total_seconds() // 60)
        wrong_submissions = self.get_problem_submissions(participation, contest_submission.problem_id) \
                                .filter(submission__date__lt=submission.date).count()
        ratio = contest_submission.points / max_points
        minimum_points = ratio * max_points * self.config['min_points_ratio']
        points_gained = self.get_problem_points(max_points, contest_submission.points, minutes, wrong_submissions)

        return {
            'is_ac': True,
            'max_points': max_points,
            'points_original': contest_submission.points,
            'time_minutes': minutes,
            'score_decay': round(minutes * self.config['decay_rate'] * max_points, 3),
            'wrong_submissions': wrong_submissions,
            'penalty_points': round(self.config['penalty_per_wrong_points'] * wrong_submissions, 3),
            'is_minimum': points_gained <= minimum_points,
            'minimum_points': round(minimum_points, 3),
            'points_gained': round(points_gained, 3),
        }

    def get_short_form_display(self):
        yield _('Points decrease dynamically based on solving time.')
        yield _('Wrong submissions before first AC will deduct points and add penalty time.')

        min_points_ratio = self.config['min_points_ratio']
        yield _('Minimum points ratio for each problem: **%d%%**.') % int(min_points_ratio * 100)

        penalty_points = self.config['penalty_per_wrong_points']
        if penalty_points:
            yield _('Each wrong submission before the first AC will deduct **%.1f points**.') % penalty_points

        penalty_time = int(self.config['penalty_per_wrong_time'])
        if penalty_time:
            yield ngettext(
                'Each wrong submission before the first AC will incur a **penalty of %d minute**.',
                'Each wrong submission before the first AC will incur a **penalty of %d minutes**.',
                penalty_time,
            ) % penalty_time
