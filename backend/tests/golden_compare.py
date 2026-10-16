from typing import Any

TOLERANCE = 0.0001


def assert_same(actual: Any, expected: Any, path: str = "$") -> None:
    """Same keys, same list lengths and orders, numbers within 0.0001; `message` texts are not compared."""
    if isinstance(expected, dict):
        assert isinstance(actual, dict), f"{path}: expected an object, got {actual!r}"
        assert actual.keys() == expected.keys(), f"{path}: keys {sorted(actual)} != {sorted(expected)}"
        for key, value in expected.items():
            if key != "message":
                assert_same(actual[key], value, f"{path}.{key}")
    elif isinstance(expected, list):
        assert isinstance(actual, list), f"{path}: expected a list, got {actual!r}"
        assert len(actual) == len(expected), f"{path}: {len(actual)} items != {len(expected)}"
        for index, (got, want) in enumerate(zip(actual, expected, strict=True)):
            assert_same(got, want, f"{path}[{index}]")
    elif isinstance(expected, bool) or expected is None or isinstance(expected, str):
        assert actual == expected, f"{path}: {actual!r} != {expected!r}"
    else:
        assert isinstance(actual, int | float) and not isinstance(actual, bool), f"{path}: {actual!r} is not a number"
        assert abs(actual - expected) <= TOLERANCE, f"{path}: {actual} != {expected}"
