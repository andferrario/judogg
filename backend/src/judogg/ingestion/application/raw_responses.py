import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

COMPETITION_LIST = "competition.get_list"
CATEGORIES = "competition.categories_full"
CONTESTS = "contest.find"
CONTEST_PARTS = "info,score_list,media,events"


def params_hash(params: Mapping[str, str]) -> str:
    """Keys sorted, values as strings, no spaces: the stored hashes depend on this exact form."""
    canonical = json.dumps({key: str(value) for key, value in params.items()}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


@dataclass(frozen=True)
class RawResponse:
    endpoint: str
    params: Mapping[str, str]
    payload: Any

    @property
    def competition_id(self) -> int | None:
        value = self.params.get("id_competition")
        return int(value) if value is not None else None
