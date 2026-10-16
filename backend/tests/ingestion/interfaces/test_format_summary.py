from judogg.ingestion.application.rebuild_dataset import LoadSummary
from judogg.ingestion.interfaces.cli import format_summary


def test_summary_lines() -> None:
    summary = LoadSummary(
        table_counts={"contest": 3},
        included=1,
        excluded=(("Kata Open", "rank_name Kata Tournament"), ("Small Open", "technique tags on 10% of scores")),
        issues={},
        skipped={"missing country": 2},
        without_contests=(),
        excluded_per_reason={"rank_name Kata Tournament": 1, "technique tags on less than 70% of scores": 1},
        new_tag_groups=("121 (hantei)", "32"),
    )
    assert format_summary(summary).splitlines() == [
        "Rows per table:",
        "  contest: 3",
        "Competitions with contest data: 1 included, 2 excluded",
        "  rank_name Kata Tournament: 1",
        "  technique tags on less than 70% of scores: 1",
        "Excluded competitions:",
        "  Kata Open: rank_name Kata Tournament",
        "  Small Open: technique tags on 10% of scores",
        "Contests skipped:",
        "  missing country: 2",
        "Quality issues: none",
        "Unknown tag groups: 121 (hantei), 32",
    ]
