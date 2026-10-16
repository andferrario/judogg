from datetime import date
from decimal import Decimal

import pytest
from ijf_helpers import SEOI_NAGE, make_competition, raw_contest, raw_event
from sqlalchemy import Engine, text

from judogg.ingestion.domain.model import Inclusion, ParsedContest, QualityIssue, Ruleset, RulesetKey
from judogg.ingestion.domain.parser import parse_contest
from judogg.ingestion.infrastructure.dataset_repository import PostgresDatasetRepository

RULESET = Ruleset(2025, RulesetKey(False, True, 1, 2), 2025, 2027, "2025–")


def parsed(fight: str, family_white: str) -> ParsedContest:
    raw = raw_contest(
        id_fight=fight,
        family_name_white=family_white,
        given_name_white="Zoë",
        events=[raw_event(int(fight), "3", tags=[SEOI_NAGE])],
        waza_w="1",
    )
    result = parse_contest(raw, make_competition())
    assert isinstance(result, ParsedContest)
    return result


def test_rebuild_writes_everything_and_keeps_the_latest_athlete_names(engine: Engine) -> None:
    repository = PostgresDatasetRepository(engine)
    with repository.rebuild() as writer:
        writer.add_rulesets([RULESET])
        writer.add_competitions([make_competition(), make_competition(id=2, date_from=date(2025, 2, 1))])
        writer.add_contests([parsed("1", "OLD")])
        writer.add_contests([parsed("2", "NEW")])
        writer.add_issues([QualityIssue("unknown_weight", 99, None, {"weight": "-75"})])
        writer.set_inclusion(2, Inclusion("no events", None, (), ()))
        writer.set_inclusion(1, Inclusion(None, Decimal("1.0000"), (), ()))
    counts = repository.table_counts()
    assert counts == {
        "ruleset": 1,
        "competition": 2,
        "athlete": 2,
        "tag": 1,
        "contest": 2,
        "score": 2,
        "penalty": 0,
        "data_quality_issue": 1,
    }
    with engine.connect() as conn:
        assert conn.execute(
            text("SELECT family_name, search_name, search_name_rev FROM app.athlete WHERE id = 10")
        ).one() == (
            "NEW",
            "zoe new",
            "new zoe",
        )
        assert conn.execute(
            text("SELECT id, exclusion_reason, tag_coverage FROM app.competition ORDER BY id")
        ).all() == [
            (1, None, Decimal("1.0000")),
            (2, "no events", None),
        ]


def test_a_failing_rebuild_keeps_the_previous_tables(engine: Engine) -> None:
    repository = PostgresDatasetRepository(engine)
    with repository.rebuild() as writer:
        writer.add_rulesets([RULESET])
        writer.add_competitions([make_competition()])
    with pytest.raises(RuntimeError), repository.rebuild() as writer:
        writer.add_rulesets([RULESET])
        raise RuntimeError("parser failure")
    assert repository.table_counts()["competition"] == 1
