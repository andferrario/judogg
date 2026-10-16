import unicodedata

# Letters that Unicode decomposition does not reduce to a base letter, and apostrophe variants.
_TRANSLITERATION = str.maketrans(
    {
        "ł": "l",
        "Ł": "l",
        "ø": "o",
        "Ø": "o",
        "đ": "d",
        "Đ": "d",
        "ð": "d",
        "Ð": "d",
        "æ": "ae",
        "Æ": "ae",
        "œ": "oe",
        "Œ": "oe",
        "ß": "ss",
        "ı": "i",
        "þ": "th",
        "Þ": "th",
        "’": "'",
        "‘": "'",
        "ʼ": "'",
        "`": "'",
    }
)


def fold(text: str) -> str:
    """Search folding: "Łukasz" and "lukasz" must match, so the stored names and the query are folded alike."""
    decomposed = unicodedata.normalize("NFD", text.translate(_TRANSLITERATION))
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()
