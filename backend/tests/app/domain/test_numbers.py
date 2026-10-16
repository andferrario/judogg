from decimal import Decimal

import pytest
from app_fakes import THRESHOLDS

from judogg.app.domain.numbers import (
    Sample,
    athlete_sample,
    count_sample,
    ratio,
    round4,
    rounded_mean,
    rounded_percent,
)


@pytest.mark.parametrize(
    ("numerator", "denominator", "expected"),
    [(1, 3, 0.3333), (2, 3, 0.6667), (1, 8, 0.125), (1, 20000, 0.0001), (0, 5, 0.0), (5, 0, None)],
)
def test_ratio_rounds_half_up_to_four_decimals(numerator: int, denominator: int, expected: float | None) -> None:
    assert ratio(numerator, denominator) == expected


def test_round4() -> None:
    assert round4(None) is None
    assert round4(0.123456) == 0.1235
    assert round4(Decimal("0.00005")) == 0.0001


def test_rounded_mean_and_percent() -> None:
    assert rounded_mean(5, 2) == 3
    assert rounded_mean(0, 0) is None
    assert rounded_percent(1, 8) == 13


@pytest.mark.parametrize(("n", "status"), [(20, "ok"), (19, "small"), (5, "small"), (4, "insufficient")])
def test_count_sample(n: int, status: str) -> None:
    assert count_sample(n, THRESHOLDS) == Sample(status, n, "scores")  # type: ignore[arg-type]


@pytest.mark.parametrize(("n", "status"), [(10, "ok"), (9, "small"), (4, "insufficient")])
def test_athlete_sample(n: int, status: str) -> None:
    assert athlete_sample(n, THRESHOLDS) == Sample(status, n, "athletes")  # type: ignore[arg-type]


def test_sample_unit() -> None:
    assert count_sample(3, THRESHOLDS, "contests").unit == "contests"
