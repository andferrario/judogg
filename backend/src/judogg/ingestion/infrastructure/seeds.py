import re
from pathlib import Path

import yaml

from judogg.ingestion.application.errors import LoadError
from judogg.ingestion.domain.competitions import ExclusionRules


def load_exclusion_rules(path: Path) -> ExclusionRules:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return ExclusionRules(
            ranks=frozenset(str(rank) for rank in data["ranks"]),
            name_patterns=tuple(
                (re.compile(str(rule["pattern"]), re.IGNORECASE), str(rule["reason"])) for rule in data["names"]
            ),
        )
    except (OSError, yaml.YAMLError, KeyError, TypeError, re.error) as error:
        raise LoadError(f"exclusion rules {path}: {error!r}") from error
