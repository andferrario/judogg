from app_fakes import EmptyReader

from judogg.app.application.use_cases import SearchAthletes
from judogg.app.domain.model import Athlete


class RecordingReader(EmptyReader):
    def __init__(self) -> None:
        self.terms: list[str] = []

    def search_athletes(self, term: str) -> list[Athlete]:
        self.terms.append(term)
        return []


def test_the_search_term_is_trimmed_and_folded_like_the_stored_names() -> None:
    reader = RecordingReader()
    SearchAthletes(reader).execute({"q": "  ŁUKASZ O\u2019Neil  "})
    assert reader.terms == ["lukasz o'neil"]
