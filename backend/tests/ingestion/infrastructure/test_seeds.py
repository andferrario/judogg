from pathlib import Path

import pytest
from ijf_helpers import SEEDS

from judogg.ingestion.application.errors import LoadError
from judogg.ingestion.infrastructure.seeds import load_exclusion_rules


def test_load_exclusion_rules() -> None:
    rules = load_exclusion_rules(SEEDS / "exclusions.yaml")
    assert rules.ranks == frozenset({"Kata Tournament", "Team event", "Mixed Teams"})
    assert [reason for _, reason in rules.name_patterns] == [
        "name contains Kata",
        "name contains Ne-Waza",
        "name contains Paralympic",
        "name contains Deaf",
        "name contains IBSA",
    ]
    assert rules.name_patterns[1][0].search("World NE-WAZA Championships")


def test_missing_or_broken_rules_are_a_load_error(tmp_path: Path) -> None:
    with pytest.raises(LoadError, match="exclusion rules"):
        load_exclusion_rules(tmp_path / "missing.yaml")
    (tmp_path / "broken.yaml").write_text("ranks: [a]\n")
    with pytest.raises(LoadError, match="exclusion rules"):
        load_exclusion_rules(tmp_path / "broken.yaml")
