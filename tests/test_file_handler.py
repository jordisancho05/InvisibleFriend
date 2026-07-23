"""Tests for FileHandler: JSON persistence of the assignments."""

import json
from pathlib import Path

import pytest

from invisible_friend.exceptions import InvisibleFriendError
from invisible_friend.utils.file_handler import FileHandler


def test_save_and_load_preserves_the_data(tmp_path: Path) -> None:
    """Round-trip through disk with no loss."""
    path = tmp_path / "data.json"
    data = {"assignments": {"Alice": "Bob"}, "total_participants": 2}

    FileHandler.save_json(path, data)

    assert FileHandler.load_json(path) == data


def test_save_preserves_accents_and_special_chars(tmp_path: Path) -> None:
    """The JSON is written as readable UTF-8, without escaping non-ASCII."""
    path = tmp_path / "data.json"

    FileHandler.save_json(path, {"assignments": {"Begoña": "Martín"}})

    content = path.read_text(encoding="utf-8")
    assert "Begoña" in content
    assert "Martín" in content
    assert "\\u" not in content


def test_save_creates_intermediate_directories(tmp_path: Path) -> None:
    """No need to create output/ by hand before saving."""
    path = tmp_path / "output" / "nested" / "data.json"

    FileHandler.save_json(path, {"ok": True})

    assert path.exists()


def test_load_missing_file_raises_error(tmp_path: Path) -> None:
    """Reading something that is not there is a project error, not a bare FileNotFoundError."""
    with pytest.raises(InvisibleFriendError, match="not found"):
        FileHandler.load_json(tmp_path / "missing.json")


def test_load_corrupt_json_raises_error(tmp_path: Path) -> None:
    """A malformed JSON is translated into the domain error."""
    path = tmp_path / "broken.json"
    path.write_text("{this is not json", encoding="utf-8")

    with pytest.raises(InvisibleFriendError):
        FileHandler.load_json(path)


def test_save_assignments_wraps_with_the_total(tmp_path: Path) -> None:
    """The assignments file carries the mapping and the participant count."""
    path = tmp_path / "assignments.json"
    assignments = {"Alice": "Bob", "Bob": "Charlie", "Charlie": "Alice"}

    FileHandler.save_assignments(path, assignments)

    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved == {"assignments": assignments, "total_participants": 3}
