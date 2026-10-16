from judogg.ingestion.domain.constants import FIRST_YEAR, MIN_TAG_COVERAGE, WEIGHT_CATEGORY_IDS
from judogg.ingestion.domain.events import KNOWN_EVENT_TYPES, SCORE_VALUES, SUMMARY_FIELDS


def test_type_6_is_unknown_until_verified() -> None:
    assert {"1", "2", "3", "4", "5", "7", "8"} == KNOWN_EVENT_TYPES


def test_awasete_counts_as_waza_ari() -> None:
    assert (SCORE_VALUES["2"], SUMMARY_FIELDS["2"]) == ("waza_ari", "waza")


def test_history_start_and_tag_threshold() -> None:
    assert (FIRST_YEAR, str(MIN_TAG_COVERAGE)) == (2017, "0.7")
    assert len(WEIGHT_CATEGORY_IDS) == 14
