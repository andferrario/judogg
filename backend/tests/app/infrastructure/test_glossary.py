from pathlib import Path

from judogg.app.domain.meta import GlossaryEntry
from judogg.app.infrastructure.glossary import load_glossary

SEEDS = Path(__file__).parents[3] / "seeds"


def test_placeholders_are_replaced() -> None:
    glossary = {e.term: e.definition for e in load_glossary(SEEDS / "glossary.yaml", 2, 0.4)}
    assert "at least 2 times" in glossary["Repertoire"]
    assert "at least 40% of their scores" in glossary["Specialist"]


def test_order_is_kept() -> None:
    glossary = load_glossary(SEEDS / "glossary.yaml", 3, 0.5)
    assert glossary[0] == GlossaryEntry(
        "Score", "An ippon, waza-ari or yuko awarded to an athlete. Walkovers and withdrawals are not scores."
    )
    assert glossary[-1].term == "Competition level"
