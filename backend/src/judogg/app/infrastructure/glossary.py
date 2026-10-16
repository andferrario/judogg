from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import yaml

from judogg.app.domain.meta import GlossaryEntry


def load_glossary(path: Path, min_scores_technique: int, specialist_share: float) -> tuple[GlossaryEntry, ...]:
    percent = Decimal(repr(specialist_share * 100)).quantize(Decimal("1"), ROUND_HALF_UP)
    values = {"min_scores_technique": str(min_scores_technique), "specialist_share": f"{percent}%"}
    entries = yaml.safe_load(path.read_text(encoding="utf-8"))
    return tuple(GlossaryEntry(str(e["term"]), str(e["definition"]).format(**values)) for e in entries)
