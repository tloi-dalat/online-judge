from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from judge.models import ContestParticipation
from judge.models.tests.util import (
    create_contest,
    create_contest_participation,
    create_contest_problem,
    create_problem,
    create_user,
)


class ContestRankingHiddenResultTestCase(TestCase):
    """VOI hides results until the unfreeze time; the client-side ranking JSON must not leak them."""

    @classmethod
    def setUpTestData(cls):
        cls._now = timezone.now()

        cls.superuser = create_user(username='superuser', is_staff=True, is_superuser=True)
        cls.viewer = create_user(username='viewer')
        cls.carol = create_user(username='carol')

        cls.contest = create_contest(
            key='voi_hidden',
            format_name='voi',
            start_time=cls._now - timezone.timedelta(days=2),
            end_time=cls._now - timezone.timedelta(days=1),
            unfreeze_time=cls._now + timezone.timedelta(days=1),
            is_visible=True,
            scoreboard_cache_timeout=60,
        )
        cls.problem_a = create_contest_problem(contest=cls.contest, problem=create_problem('voi_a'), order=1)
        cls.problem_b = create_contest_problem(contest=cls.contest, problem=create_problem('voi_b'), order=2)

        # 'zed' is ranked first by score but sorts last by name.
        create_contest_participation(
            contest=cls.contest, user='zed', score=200, cumtime=0,
            format_data={str(cls.problem_a.id): {'time': 0, 'points': 100},
                         str(cls.problem_b.id): {'time': 0, 'points': 100}},
        )
        create_contest_participation(
            contest=cls.contest, user='amy', score=50, cumtime=0,
            format_data={str(cls.problem_a.id): {'time': 0, 'points': 50}},
        )

    def setUp(self):
        cache.clear()

    def get_ranking_json(self, user=None):
        if user is not None:
            self.client.force_login(user)
        response = self.client.get(reverse('contest_ranking', args=[self.contest.key]), {'data': ''})
        self.assertEqual(response.status_code, 200)
        return response.json()

    def set_unfreeze_time(self, delta):
        self.contest.unfreeze_time = self._now + delta
        self.contest.save()

    def test_results_hidden_for_normal_user(self):
        data = self.get_ranking_json(self.viewer)
        self.assertTrue(data['contest']['result_hidden'])

        participations = data['participations']
        # Ordered by name, not by score, so row order doesn't leak the standings.
        self.assertEqual([p['user']['username'] for p in participations], ['amy', 'zed'])
        for p in participations:
            self.assertEqual(p['rank'], '?')
            self.assertIsNone(p['score'])
            self.assertIsNone(p['cumtime'])
            self.assertIsNone(p['tiebreaker'])
            for entry in p['format_data'].values():
                self.assertEqual(entry, {'hidden': True})

        # Only which problems were attempted is exposed.
        amy = participations[0]
        self.assertEqual(set(amy['format_data']), {str(self.problem_a.id)})

    def test_results_hidden_for_anonymous_user(self):
        data = self.get_ranking_json()
        self.assertTrue(data['contest']['result_hidden'])
        self.assertTrue(all(p['score'] is None for p in data['participations']))

    def test_results_visible_for_superuser(self):
        data = self.get_ranking_json(self.superuser)
        self.assertFalse(data['contest']['result_hidden'])
        participations = data['participations']
        self.assertEqual([p['user']['username'] for p in participations], ['zed', 'amy'])
        self.assertEqual([p['rank'] for p in participations], [1, 2])
        self.assertEqual(participations[0]['score'], 200)

    def test_results_visible_after_unfreeze(self):
        self.set_unfreeze_time(-timezone.timedelta(hours=1))
        data = self.get_ranking_json(self.viewer)
        self.assertFalse(data['contest']['result_hidden'])
        self.assertEqual([p['user']['username'] for p in data['participations']], ['zed', 'amy'])
        self.assertEqual(data['participations'][1]['score'], 50)

    def test_cached_visible_ranking_not_served_to_hidden_viewer(self):
        self.set_unfreeze_time(-timezone.timedelta(hours=1))

        # Anonymous viewer populates the cache with the revealed ranking.
        self.assertFalse(self.get_ranking_json()['contest']['result_hidden'])

        # A VOI participant replaying the contest virtually must still see nothing.
        participation = create_contest_participation(
            contest=self.contest, user=self.carol.profile, virtual=1, real_start=timezone.now(),
        )
        self.carol.profile.current_contest = participation
        self.carol.profile.save()

        data = self.get_ranking_json(self.carol)
        self.assertTrue(data['contest']['result_hidden'])
        self.assertTrue(all(p['score'] is None for p in data['participations']))
        self.assertNotIn('replay_url', data['contest'])


class ContestReplayHiddenResultTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls._now = timezone.now()

    def make_contest(self, key, format_name, unfreeze_time=None):
        return create_contest(
            key=key,
            format_name=format_name,
            start_time=self._now - timezone.timedelta(days=2),
            end_time=self._now - timezone.timedelta(days=1),
            unfreeze_time=unfreeze_time,
            is_visible=True,
        )

    def test_default_contest_is_replayable(self):
        self.assertTrue(self.make_contest('replay_default', 'default').can_replay)

    def test_voi_contest_is_never_replayable(self):
        self.assertFalse(self.make_contest('replay_voi', 'voi').can_replay)
        revealed = self.make_contest('replay_voi_revealed', 'voi', self._now - timezone.timedelta(hours=1))
        self.assertFalse(revealed.can_replay)

    def test_contest_is_not_replayable_while_results_are_hidden(self):
        hidden = self.make_contest('replay_icpc_hidden', 'icpc', self._now + timezone.timedelta(days=1))
        self.assertFalse(hidden.can_replay)
        revealed = self.make_contest('replay_icpc_revealed', 'icpc', self._now - timezone.timedelta(hours=1))
        self.assertTrue(revealed.can_replay)

    def test_replay_data_endpoint_refuses_voi(self):
        contest = self.make_contest('replay_voi_endpoint', 'voi', self._now - timezone.timedelta(hours=1))
        response = self.client.get(reverse('contest_replay_data', args=[contest.key, contest.replay_version]))
        # ContestMixin turns the Http404 into its "No such contest" page; no replay data is served.
        self.assertNotEqual(response['Content-Type'], 'application/json')
        self.assertContains(response, 'No such contest')

    def test_participation_model_live_constant(self):
        # Guard: the ranking JSON relies on LIVE == 0 for "live" participations.
        self.assertEqual(ContestParticipation.LIVE, 0)
