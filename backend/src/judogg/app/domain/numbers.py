from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from judogg.app.domain.model import Thresholds

SampleStatus = Literal["ok", "small", "insufficient"]
SampleUnit = Literal["scores", "penalties", "contests", "athletes", "years"]

_FOUR_DECIMALS = Decimal("0.0001")
_UNIT = Decimal("1")


def round4(value: float | Decimal | None) -> float | None:
    if value is None:
        return None
    exact = value if isinstance(value, Decimal) else Decimal(repr(value))
    return float(exact.quantize(_FOUR_DECIMALS, ROUND_HALF_UP))


def ratio(numerator: float, denominator: float) -> float | None:
    if not denominator:
        return None
    return round4(Decimal(numerator) / Decimal(denominator))


def rounded_mean(total: int, count: int) -> int | None:
    if not count:
        return None
    return int((Decimal(total) / Decimal(count)).quantize(_UNIT, ROUND_HALF_UP))


def rounded_percent(part: int, whole: int) -> int:
    return int((Decimal(100 * part) / Decimal(whole)).quantize(_UNIT, ROUND_HALF_UP))


@dataclass(frozen=True)
class Sample:
    status: SampleStatus
    n: int
    unit: SampleUnit


def _status(n: int, ok: int, small: int) -> SampleStatus:
    if n >= ok:
        return "ok"
    if n >= small:
        return "small"
    return "insufficient"


def count_sample(n: int, thresholds: Thresholds, unit: SampleUnit = "scores") -> Sample:
    return Sample(_status(n, thresholds.sample_ok, thresholds.sample_small), n, unit)


def athlete_sample(n: int, thresholds: Thresholds) -> Sample:
    return Sample(_status(n, thresholds.athlete_sample_ok, thresholds.athlete_sample_small), n, "athletes")
