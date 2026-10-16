"""Many competitions have no events or no technique tags: they cannot answer which techniques score."""

from collections.abc import Sequence
from decimal import ROUND_HALF_UP, Decimal

from judogg.ingestion.domain.constants import MIN_TAG_COVERAGE
from judogg.ingestion.domain.model import Inclusion, ParsedContest, QualityIssue

FOUR_DECIMALS = Decimal("0.0001")
LOW_TAG_COVERAGE = f"technique tags on less than {MIN_TAG_COVERAGE:.0%} of scores"


def decide_inclusion(contests: Sequence[ParsedContest]) -> Inclusion:
    if not contests:
        return Inclusion(None, None, (), ())  # nothing written: not excluded, simply no contests
    with_events = tuple(c for c in contests if c.n_events > 0)
    if not with_events:
        return Inclusion("no events", None, (), ())
    coverage = _tag_coverage(with_events)
    if coverage is not None and coverage < MIN_TAG_COVERAGE:
        percent = (coverage * 100).quantize(Decimal("1"), ROUND_HALF_UP)
        return Inclusion(f"technique tags on {percent}% of scores", coverage, (), ())
    issues = tuple(QualityIssue("no_events", c.contest.id, None, {}) for c in contests if c.n_events == 0)
    return Inclusion(None, coverage, with_events, issues)


def reason_kind(inclusion: Inclusion) -> str | None:
    """Coverage reasons carry their percentage: grouped, they count the competitions per cause."""
    if inclusion.exclusion_reason is not None and inclusion.tag_coverage is not None:
        return LOW_TAG_COVERAGE
    return inclusion.exclusion_reason


def _tag_coverage(contests: Sequence[ParsedContest]) -> Decimal | None:
    scores = {(s.event_id, s.athlete_id) for c in contests for s in c.scores}
    if not scores:
        return None
    tagged = {(s.event_id, s.athlete_id) for c in contests for s in c.scores if s.technique_tag_id is not None}
    return (Decimal(len(tagged)) / Decimal(len(scores))).quantize(FOUR_DECIMALS, ROUND_HALF_UP)
