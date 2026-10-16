from app_fakes import score

from judogg.app.domain.scores import (
    BIN_LABELS,
    SideCounts,
    TimingBin,
    ValueCounts,
    ValueShares,
    distinct,
    side_counts,
    technique_groups,
    timing,
)


def test_a_combination_is_one_distinct_score() -> None:
    rows = [score(technique_tag_id=1), score(technique_tag_id=2), score(event_id=2)]
    assert distinct(rows) == [rows[0], rows[2]]
    assert distinct([score(), score(athlete_id=20)]) == [score(), score(athlete_id=20)]


def test_timing_has_nine_bins_with_golden_score_last() -> None:
    bins = timing([score(time_bin=0, score_value="ippon"), score(time_bin=0), score(time_bin=8, score_value="yuko")])
    assert len(bins) == len(BIN_LABELS) == 9
    assert bins[0] == TimingBin(0, "0:00–0:30", 2, 1, 1, 0)
    assert bins[8] == TimingBin(8, "Golden score", 1, 0, 0, 1)
    assert bins[4].n == 0


def test_technique_groups() -> None:
    groups = technique_groups(
        [
            score(technique_tag_id=1, score_value="ippon", direction="left"),
            score(event_id=2, technique_tag_id=1, athlete_id=11, is_awasete=True, direction="right"),
            score(event_id=3, technique_tag_id=None, direction="unknown"),
        ]
    )
    seoi = groups[1]
    assert (seoi.n, seoi.athletes, seoi.awasete) == (2, {10, 11}, 1)
    assert seoi.counts() == ValueCounts(1, 1, 0)
    assert seoi.shares() == ValueShares(0.5, 0.5, 0.0)
    assert seoi.side_counts() == SideCounts(1, 1, 0)
    assert groups[None].n == 1


def test_side_counts() -> None:
    rows = [score(direction="left"), score(direction="left"), score(direction="unknown")]
    assert side_counts(rows) == SideCounts(2, 0, 1)
