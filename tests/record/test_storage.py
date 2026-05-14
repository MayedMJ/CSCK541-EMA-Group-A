"""Tests for JsonRecordRepository (record.storage module).

Covers save/load round-trip, error cases (invalid JSON, wrong root type,
non-dict items), backup recovery, and file creation behaviour.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from record.exceptions import RecordValidationError
from record.storage import JsonRecordRepository
from tests.conftest import client_payload


def test_save_then_load_round_trip(tmp_json_path: Path) -> None:
    """Saving records and loading them back produces identical data."""
    repo = JsonRecordRepository(tmp_json_path)
    records = [
        {
            "id": 1,
            "type": "client",
            **client_payload(),
        }
    ]
    repo.save_records(records)
    loaded = repo.load_records()
    assert loaded == records


def test_load_missing_file_returns_empty(tmp_json_path: Path) -> None:
    """Loading when neither primary nor backup file exists returns []."""
    repo = JsonRecordRepository(tmp_json_path)
    assert repo.load_records() == []


@pytest.mark.parametrize(
    "file_text",
    [
        "{ not json",
        '{"x": 1}',
        "[1, 2]",
    ],
    ids=["invalid_json", "root_not_list", "item_not_dict"],
)
def test_load_invalid_payload_raises(
    tmp_json_path: Path, file_text: str
) -> None:
    """Invalid on-disk JSON raises RecordValidationError."""
    tmp_json_path.write_text(file_text, encoding="utf-8")
    repo = JsonRecordRepository(tmp_json_path)
    with pytest.raises(RecordValidationError):
        repo.load_records()


def test_backup_recovery_when_primary_corrupt(tmp_json_path: Path) -> None:
    """Corrupt primary with valid backup recovers records from backup."""
    good = [{"id": 1, "type": "client", **client_payload()}]
    payload = json.dumps(good, ensure_ascii=False, indent=2)
    tmp_json_path.write_text("<<<broken>>>", encoding="utf-8")
    bak = tmp_json_path.with_suffix(tmp_json_path.suffix + ".bak")
    bak.write_text(payload, encoding="utf-8")

    repo = JsonRecordRepository(tmp_json_path)
    loaded = repo.load_records()
    assert loaded == good


def test_backup_only_no_primary(tmp_json_path: Path) -> None:
    """If primary is missing but backup exists, records are recovered."""
    good = [{"id": 2, "type": "airline", "company_name": "Test Air"}]
    bak = tmp_json_path.with_name(tmp_json_path.name + ".bak")
    bak.write_text(json.dumps(good), encoding="utf-8")

    repo = JsonRecordRepository(tmp_json_path)
    loaded = repo.load_records()
    assert loaded == good


def test_both_corrupt_raises_primary_error(tmp_json_path: Path) -> None:
    """Both primary and backup corrupt raises the primary file's error."""
    tmp_json_path.write_text("bad primary", encoding="utf-8")
    bak = tmp_json_path.with_suffix(tmp_json_path.suffix + ".bak")
    bak.write_text("bad backup", encoding="utf-8")

    repo = JsonRecordRepository(tmp_json_path)
    with pytest.raises(RecordValidationError):
        repo.load_records()


def test_save_creates_primary_and_backup(tmp_json_path: Path) -> None:
    """After save, both primary file and .bak backup exist."""
    repo = JsonRecordRepository(tmp_json_path)
    repo.save_records([])
    assert tmp_json_path.exists()
    assert tmp_json_path.with_name(tmp_json_path.name + ".bak").exists()


def test_save_creates_parent_directories(tmp_path: Path) -> None:
    """Save creates missing parent directories automatically."""
    nested_path = tmp_path / "a" / "b" / "records.json"
    repo = JsonRecordRepository(nested_path)
    repo.save_records([{"id": 1, "type": "client", **client_payload()}])
    assert nested_path.exists()


def test_file_path_property(tmp_json_path: Path) -> None:
    """The file_path property returns the configured Path."""
    repo = JsonRecordRepository(tmp_json_path)
    assert repo.file_path == tmp_json_path
