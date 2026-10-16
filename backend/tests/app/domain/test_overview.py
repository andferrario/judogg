from app_fakes import THRESHOLDS, contest, score

from judogg.app.domain.overview import build_overview, outcomes


def test_walkovers_are_counted_apart() -> None:
    contests = [
        contest(end_type="fusen_gachi"),
        contest(id=2, end_type="ippon", went_gs=True, duration_s=301),
        contest(id=3, end_type="score_gs", went_gs=True, duration_s=300),
    ]
    result = outcomes(contests, THRESHOLDS)
    assert (result.played, result.walkovers.fusen_gachi, result.walkovers.kiken_gachi) == (2, 1, 0)
    assert [(e.end_type, e.n, e.share) for e in result.end_types][:2] == [
        ("ippon", 1, 0.5),
        ("waza_ari_awasete", 0, 0.0),
    ]
    assert (result.gs_share, result.avg_duration_s, result.sample.unit) == (1.0, 301, "contests")


def test_overview_without_data() -> None:
    overview = build_overview([], [], THRESHOLDS)
    assert (overview.kpis.scores, overview.kpis.gs_share, overview.kpis.unknown_technique_share) == (0, None, None)
    assert (overview.outcomes.avg_duration_s, overview.sample.status) == (None, "insufficient")


def test_kpis_count_distinct_scores_and_known_techniques() -> None:
    scores = [
        score(technique_tag_id=1),
        score(technique_tag_id=2),
        score(event_id=2, technique_tag_id=None, direction="unknown"),
    ]
    kpis = build_overview(scores, [contest()], THRESHOLDS).kpis
    assert (kpis.scores, kpis.scoring_athletes, kpis.techniques) == (2, 1, 2)
    assert (kpis.unknown_side_share, kpis.unknown_technique_share) == (0.5, 0.5)
