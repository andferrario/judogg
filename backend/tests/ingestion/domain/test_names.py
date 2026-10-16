import pytest

from judogg.ingestion.domain.names import normalise_name


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Kata-Guruma", "Kata-guruma"),
        ("Non-Combativity", "Non-combativity"),
        ("Unorthodox kumi-kata too long", "Unorthodox kumi-kata too long"),
        ("", ""),
    ],
)
def test_normalise_name(raw: str, expected: str) -> None:
    assert normalise_name(raw) == expected
