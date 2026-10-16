from collections.abc import Callable
from pathlib import Path

from judogg.ingestion.application.ports import RawResponseRepository
from judogg.ingestion.application.raw_responses import RawResponse


class ImportRawFiles:
    def __init__(self, raw: RawResponseRepository, reader: Callable[[Path], list[RawResponse]]) -> None:
        self._raw = raw
        self._reader = reader

    def execute(self, directory: Path) -> int:
        responses = self._reader(directory)
        for response in responses:
            self._raw.save(response)
        return len(responses)
