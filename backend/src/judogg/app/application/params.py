import re
from collections.abc import Mapping

from judogg.app.application.errors import InvalidParameter

Params = Mapping[str, str]

# ASCII digits only: int() would also accept "²"-like digits, "+5", "1_0" and fail on huge numbers.
_INTEGER = re.compile(r"[0-9]{1,9}")


def integer(value: str) -> int | None:
    return int(value) if _INTEGER.fullmatch(value) else None


def text(params: Params, name: str) -> str | None:
    value = params.get(name)
    return value if value else None


def items(params: Params, name: str) -> list[str]:
    value = text(params, name)
    return [item.strip() for item in value.split(",") if item.strip()] if value else []


def optional_int_param(params: Params, name: str, low: int, high: int) -> int | None:
    value = text(params, name)
    if value is None:
        return None
    number = integer(value)
    if number is None or not low <= number <= high:
        raise InvalidParameter(name, f"{name} must be an integer between {low} and {high}")
    return number


def int_param(params: Params, name: str, default: int, low: int, high: int) -> int:
    number = optional_int_param(params, name, low, high)
    return default if number is None else number


def choice[T: str](params: Params, name: str, choices: tuple[T, ...], default: T) -> T:
    value = text(params, name)
    if value is None:
        return default
    for allowed in choices:
        if value == allowed:
            return allowed
    raise InvalidParameter(name, f"{name} must be one of {', '.join(choices)}")


def members[T: str](params: Params, name: str, allowed: tuple[T, ...]) -> tuple[T, ...]:
    chosen = []
    for value in items(params, name):
        match = next((a for a in allowed if a == value), None)
        if match is None:
            raise InvalidParameter(name, f"{name} must be one of {', '.join(allowed)}")
        chosen.append(match)
    return tuple(chosen) if chosen else allowed
