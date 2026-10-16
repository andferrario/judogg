import json
from collections.abc import Sequence
from datetime import date
from functools import cache
from pathlib import Path
from typing import Any

from judogg.ingestion.domain.competitions import ExclusionRules, build_competitions
from judogg.ingestion.domain.model import Competition, ParsedContest
from judogg.ingestion.domain.parser import parse_contest
from judogg.ingestion.infrastructure.seeds import load_exclusion_rules

FIXTURES = Path(__file__).parent / "fixtures" / "ijf"


def raw_tag(id_tag: int, code_short: str, name: str, id_group: str, id_groups: str) -> dict[str, Any]:
    return {"id_tag": str(id_tag), "code_short": code_short, "name": name, "id_group": id_group, "id_groups": id_groups}


SEOI_NAGE = raw_tag(1, "seoi_nage", "Seoi-nage", "33", "28,33,97,98")
UCHI_MATA = raw_tag(2, "uchi_mata", "Uchi-mata", "29", "28,29,97,98")
KESA_GATAME = raw_tag(3, "kesa_gatame", "Kesa-gatame", "25", "23,25,97,98")
NEW_GROUP_TECHNIQUE = raw_tag(4, "new_throw", "New-throw", "32", "28,32,97,98")
NON_COMBATIVITY = raw_tag(5, "non_combativity", "Non-Combativity", "112", "97,109,110,112")
NEW_GROUP_REASON = raw_tag(6, "new_reason", "New-reason", "115", "97,109,110,115")
LEFT = raw_tag(7, "left", "Left", "126", "97,122,126")
RIGHT = raw_tag(8, "right", "Right", "126", "97,122,126")
FUSEN_GACHI = raw_tag(9, "fusen_gachi", "Fusen-Gachi", "121", "97,120,121")
KIKEN_GACHI = raw_tag(10, "kiken_gachi", "Kiken-gachi", "121", "97,120,121")
OTHER_WIN = raw_tag(11, "hantei", "Hantei", "121", "97,120,121")
OSAEKOMI = raw_tag(12, "osaekomi", "Osaekomi", "124", "97,122,124")
CANCEL_WAZA_ARI = raw_tag(13, "cancel_waza_ari", "Cancel Waza-ari", "123", "97,122,123")


SEEDS = Path(__file__).parents[1] / "seeds"


def load_fixture(relative: str) -> Any:
    return json.loads((FIXTURES / relative).read_text(encoding="utf-8"))


@cache
def exclusion_rules() -> ExclusionRules:
    return load_exclusion_rules(SEEDS / "exclusions.yaml")


@cache
def fixture_competitions() -> dict[int, Competition]:
    competitions, _ = build_competitions(load_fixture("01_competitions_list.json"), exclusion_rules())
    return {c.id: c for c in competitions}


def make_competition(**overrides: Any) -> Competition:
    values: dict[str, Any] = {
        "id": 1,
        "code": "test2025",
        "name": "Test Grand Prix 2025",
        "rank_name": "Grand Prix",
        "date_from": date(2025, 1, 1),
        "date_to": date(2025, 1, 2),
        "year": 2025,
        "ruleset_id": 2025,
        "level": "elite",
        "exclusion_reason": None,
    }
    values.update(overrides)
    return Competition(**values)


def raw_contest(**overrides: Any) -> dict[str, Any]:
    """A finished senior -73 M contest between athlete 10 (white, ITA) and 20 (blue, FRA), no events."""
    values: dict[str, Any] = {
        "id_fight": "1",
        "contest_code_long": "test2025_0001_m_0073_0001",
        "age": "Seniors",
        "id_fight_team": None,
        "is_finished": "1",
        "weight": "-73",
        "id_person_white": "10",
        "family_name_white": "WHITE",
        "given_name_white": "Wanda",
        "country_short_white": "ITA",
        "id_person_blue": "20",
        "family_name_blue": "BLUE",
        "given_name_blue": "Bruno",
        "country_short_blue": "FRA",
        "gs": "0",
        "duration": "00:04:00",
        "fight_duration": "240",
        "ippon_w": "0",
        "waza_w": "0",
        "yuko_w": "0",
        "penalty_w": "0",
        "ippon_b": "0",
        "waza_b": "0",
        "yuko_b": "0",
        "penalty_b": "0",
        "events": [],
    }
    values.update(overrides)
    return values


def raw_event(
    event_id: int,
    event_type: str,
    *,
    actors: Sequence[int] = (10,),
    tags: Sequence[dict[str, Any]] = (),
    time_sc: str = "10",
    time_real: str = "12",
    is_gs: str = "0",
) -> dict[str, Any]:
    return {
        "id_event": str(event_id),
        "id_contest_event_type": event_type,
        "time_sc": time_sc,
        "time_real": time_real,
        "is_gs": is_gs,
        "tags": list(tags),
        "actors": [{"actor_type": "competitor", "id_person": str(a)} for a in actors],
    }


def fixture_contest(relative: str, code: str) -> dict[str, Any]:
    contests: list[dict[str, Any]] = load_fixture(relative)["contests"]
    return next(c for c in contests if c["contest_code_long"] == code)


GUADALAJARA = "03_category_contests_with_events.json"


def parse_fixture(relative: str, code: str) -> ParsedContest:
    raw = fixture_contest(relative, code)
    result = parse_contest(raw, fixture_competitions()[int(raw["id_competition"])])
    assert isinstance(result, ParsedContest)
    return result
