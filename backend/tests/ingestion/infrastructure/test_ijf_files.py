import shutil
from collections import Counter
from pathlib import Path

import pytest
from ijf_helpers import FIXTURES

from judogg.ingestion.application.raw_responses import RawResponse, params_hash
from judogg.ingestion.infrastructure.ijf_files import UnsupportedFile, read_ijf_files


def test_fixture_layout_maps_to_22_responses() -> None:
    responses = read_ijf_files(FIXTURES)
    assert Counter(r.endpoint for r in responses) == {
        "competition.get_list": 1,
        "competition.categories_full": 4,
        "contest.find": 17,
    }
    params = {(r.endpoint, tuple(sorted(r.params.items()))) for r in responses}
    assert ("competition.get_list", ()) in params
    assert ("competition.categories_full", (("id_competition", "3081"),)) in params
    assert ("competition.categories_full", (("id_competition", "1439"),)) in params
    assert (
        "contest.find",
        (("id_competition", "3081"), ("id_weight", "2"), ("part", "info,score_list,media,events")),
    ) in params
    assert {r.competition_id for r in responses if r.endpoint == "contest.find"} == {3081, 3131, 1439, 2942}


def test_hidden_files_and_other_extensions_are_ignored(tmp_path: Path) -> None:
    shutil.copy(FIXTURES / "01_competitions_list.json", tmp_path)
    (tmp_path / ".DS_Store").write_text("x")
    (tmp_path / "._01_competitions_list.json").write_text("x")
    (tmp_path / "IJF_API_GUIDE.md").write_text("x")
    assert [r.endpoint for r in read_ijf_files(tmp_path)] == ["competition.get_list"]


def test_unknown_json_file_is_an_error(tmp_path: Path) -> None:
    (tmp_path / "05_other.json").write_text("{}")
    with pytest.raises(UnsupportedFile, match=r"05_other\.json"):
        read_ijf_files(tmp_path)


def test_params_hash_is_canonical() -> None:
    assert params_hash({"b": "2", "a": "1"}) == params_hash({"a": "1", "b": "2"})
    assert params_hash({}) == "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"  # sha256("{}")
    assert RawResponse("competition.get_list", {}, []).competition_id is None


def test_empty_contest_files_are_skipped(tmp_path: Path) -> None:
    (tmp_path / "minor").mkdir()
    (tmp_path / "minor" / "03_contests_1439_w01.json").write_text('{"contests": []}')
    (tmp_path / "minor" / "03_contests_1439_w02.json").write_text("[]")
    assert read_ijf_files(tmp_path) == []


def test_invalid_json_is_a_load_error(tmp_path: Path) -> None:
    (tmp_path / "01_competitions_list.json").write_text("<html>")
    with pytest.raises(UnsupportedFile, match=r"01_competitions_list\.json is not valid JSON"):
        read_ijf_files(tmp_path)


def test_contest_file_without_ids_is_a_load_error(tmp_path: Path) -> None:
    (tmp_path / "minor").mkdir()
    (tmp_path / "minor" / "03_contests_1439_w01.json").write_text('{"contests": [{"id_fight": "1"}]}')
    with pytest.raises(UnsupportedFile, match=r"03_contests_1439_w01\.json: .*id_competition"):
        read_ijf_files(tmp_path)
