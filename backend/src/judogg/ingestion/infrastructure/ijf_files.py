"""Only the layout of the example IJF files is supported: real data comes from the IJF API."""

import json
import re
from pathlib import Path
from typing import Any

from judogg.ingestion.application.errors import LoadError
from judogg.ingestion.application.raw_responses import (
    CATEGORIES,
    COMPETITION_LIST,
    CONTEST_PARTS,
    CONTESTS,
    RawResponse,
)

SUBDIRECTORIES = ("", "gs_fra2026", "minor")
# File 04 duplicates contest 0021 of file 03: importing it would count that contest twice.
SKIPPED = frozenset({"04_single_contest_details.json"})
FIXED_CATEGORIES = {"02_competition_categories.json": "3081", "gs_fra2026/02_competition_categories.json": "3131"}
MINOR_CATEGORIES = re.compile(r"minor/02_categories_(\d+)\.json")
CONTEST_FILES = re.compile(r"(03_category_contests_with_events|gs_fra2026/03_contests_.+|minor/03_contests_.+)\.json")


class UnsupportedFile(LoadError):
    pass


def read_ijf_files(directory: Path) -> list[RawResponse]:
    responses = []
    for path in _json_files(directory):
        relative = path.relative_to(directory).as_posix()
        if relative in SKIPPED:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise UnsupportedFile(f"{relative} is not valid JSON: {error}") from error
        response = _response(relative, payload)
        if response is not None:
            responses.append(response)
    return responses


def _json_files(directory: Path) -> list[Path]:
    files = []
    for subdirectory in SUBDIRECTORIES:
        folder = directory / subdirectory
        if folder.is_dir():
            files += [p for p in folder.glob("*.json") if not p.name.startswith(".")]
    return sorted(files)


def _response(relative: str, payload: Any) -> RawResponse | None:
    if relative == "01_competitions_list.json":
        return RawResponse(COMPETITION_LIST, {}, payload)
    if relative in FIXED_CATEGORIES:
        return RawResponse(CATEGORIES, {"id_competition": FIXED_CATEGORIES[relative]}, payload)
    if match := MINOR_CATEGORIES.fullmatch(relative):
        return RawResponse(CATEGORIES, {"id_competition": match.group(1)}, payload)
    if CONTEST_FILES.fullmatch(relative):
        contests = payload.get("contests") if isinstance(payload, dict) else None
        if not contests:
            return None  # an empty category: nothing to load, and no contest to read its ids from
        try:
            params = {
                "id_competition": str(contests[0]["id_competition"]),  # never from the file name
                "id_weight": str(contests[0]["id_weight"]),
                "part": CONTEST_PARTS,
            }
        except (KeyError, TypeError) as error:
            raise UnsupportedFile(f"{relative}: the first contest has no {error}") from error
        return RawResponse(CONTESTS, params, payload)
    raise UnsupportedFile(f"{relative} is not part of the supported example layout")
