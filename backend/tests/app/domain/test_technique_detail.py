from typing import Any

from app_fakes import THRESHOLDS, catalogue, filters, score

from judogg.app.domain.model import Athlete, ScoreRow, Tag
from judogg.app.domain.technique_detail import TechniqueDetail, build_technique_detail

UCHI = Tag(1, "uchi_mata", "Uchi-mata", "technique", "Ashi-waza", "standing")
SEOI = Tag(2, "seoi_nage", "Seoi-nage", "technique", "Te-waza", "standing")
ATHLETES = {i: Athlete(i, f"G{i}", f"F{i}", "ITA") for i in range(10, 40)}


def detail(scores: list[ScoreRow], **filter_overrides: Any) -> TechniqueDetail:
    return build_technique_detail(
        UCHI, scores, filters(**filter_overrides), catalogue(tags={1: UCHI, 2: SEOI}), ATHLETES, THRESHOLDS
    )


def test_trend_with_three_years_takes_the_score_sample_status() -> None:
    scores = [score(event_id=i, year=2023 + i % 3, technique_tag_id=1, athlete_id=10 + i) for i in range(30)]
    trend = detail(scores).trend
    assert [p.year for p in trend.points] == [2023, 2024, 2025]
    assert (trend.sample.status, trend.sample.n, trend.sample.unit) == ("ok", 3, "years")


def test_ruleset_changes_inside_the_trend_years() -> None:
    scores = [score(event_id=i, year=year, technique_tag_id=1) for i, year in enumerate((2017, 2019, 2025))]
    assert detail(scores).trend.ruleset_changes == (2018, 2025)


def test_country_lift_with_one_category_is_the_plain_lift() -> None:
    ita = [score(event_id=i, athlete_country="ITA", technique_tag_id=1 if i < 12 else 2) for i in range(30)]
    fra = [
        score(event_id=100 + i, athlete_id=20, athlete_country="FRA", technique_tag_id=1 if i < 6 else 2)
        for i in range(30)
    ]
    countries = {c.country_code: c for c in detail(ita + fra).countries.rows}
    plain = (12 / 30) / (18 / 60)
    assert countries["ITA"].lift == round(plain, 4)


def test_country_lift_compares_with_the_same_categories() -> None:
    heavy = [score(event_id=i, weight="m-100", athlete_country="ITA", technique_tag_id=1) for i in range(30)]
    light = [
        score(event_id=100 + i, weight="m-60", athlete_id=20, athlete_country="FRA", technique_tag_id=2)
        for i in range(30)
    ]
    countries = {c.country_code: c for c in detail(heavy + light).countries.rows}
    assert countries["ITA"].lift == 1.0  # all of m-100 is uchi-mata: as expected, not twice as often


def test_top_athletes_ties_by_ippon_then_id() -> None:
    scores = [
        score(event_id=1, athlete_id=12, technique_tag_id=1),
        score(event_id=2, athlete_id=11, technique_tag_id=1, score_value="ippon"),
        score(event_id=3, athlete_id=13, technique_tag_id=1),
    ]
    assert [a.athlete.id for a in detail(scores).top_athletes] == [11, 12, 13]
