from django.db.models import Q
from django.utils import timezone

from judge.contest_format.atcoder import AtCoderContestFormat
from judge.contest_format.default import DefaultContestFormat
from judge.contest_format.ecoo import ECOOContestFormat
from judge.contest_format.icpc import ICPCContestFormat
from judge.contest_format.ioi import IOIContestFormat
from judge.contest_format.legacy_ioi import LegacyIOIContestFormat
from judge.contest_format.registry import choices, formats
from judge.contest_format.vnoj import VNOJContestFormat
from judge.contest_format.voi import VOIContestFormat


def hide_result_format_names():
    return [name for name, cls in formats.items()
            if getattr(cls, 'hides_results_before_unfreeze', False)]


def hidden_result_contest_q(own=False):
    now = timezone.now()
    hide_formats = hide_result_format_names()
    q = (
        Q(format_name__in=hide_formats, unfreeze_time__gt=now) |
        Q(format_name__in=hide_formats, unfreeze_time__isnull=True, end_time__gt=now)
    )
    if not own:
        q |= Q(end_time__lte=now, unfreeze_time__gt=now)
    return q


def hidden_result_contest_ids(profile=None, own=False):
    from judge.models import Contest

    cache_attr = '_own_hidden_result_contest_ids' if own else '_hidden_result_contest_ids'
    if profile is not None:
        cached = getattr(profile, cache_attr, None)
        if cached is not None:
            return cached

    ids = set(Contest.objects.filter(hidden_result_contest_q(own)).values_list('id', flat=True))
    if profile is not None and profile.current_contest_id is not None:
        participation = profile.current_contest
        if participation.contest.format_name in hide_result_format_names():
            ids.add(participation.contest_id)

    result = frozenset(ids)
    if profile is not None:
        setattr(profile, cache_attr, result)
    return result


def hidden_result_submission_q(profile=None):
    hidden = hidden_result_contest_ids(profile)
    q = Q(contest_object__in=hidden)
    if profile is not None:
        own_visible = hidden - hidden_result_contest_ids(profile, own=True)
        if own_visible:
            q &= ~Q(user=profile, contest_object__in=own_visible)
    return q
