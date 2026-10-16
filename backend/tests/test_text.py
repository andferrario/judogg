import pytest

from judogg.text import fold


@pytest.mark.parametrize(
    ("raw", "folded"),
    [
        ("Ştefan Ö'Brien  Ñúñez", "stefan o'brien  nunez"),
        ("Łukasz Søren Đoković Æsir Œuvre Straße Işık Þór", "lukasz soren dokovic aesir oeuvre strasse isik thor"),
        ("O’Neil D‘Amico Kaʼai Mc`Kay", "o'neil d'amico ka'ai mc'kay"),
        ("İLKER", "ilker"),
    ],
)
def test_fold(raw: str, folded: str) -> None:
    assert fold(raw) == folded
