"""Integration tests across service, validators, and JSON repository.

Validates that the full stack (RecordService + JsonRecordRepository + validators)
works end-to-end with real file I/O.
"""

from __future__ import annotations

from pathlib import Path

from record.contracts import AIRLINE_TYPE, CLIENT_TYPE, FLIGHT_TYPE
from record.service import RecordService
from record.storage import JsonRecordRepository

from tests.conftest import airline_payload, client_payload, flight_payload


def test_create_save_reload_round_trip(tmp_path: Path) -> None:
    """Records created, saved, and loaded by a new instance are identical.

    Flights require two foreign keys (client_id, airline_id); parents must exist
    before create. We assert the reloaded flight still references those ids.
    """
    path = tmp_path / "records.json"
    repo1 = JsonRecordRepository(path)
    s1 = RecordService(repository=repo1, auto_load=True)

    client = s1.create_record(CLIENT_TYPE, client_payload())
    airline = s1.create_record(AIRLINE_TYPE, airline_payload())
    client_id = client["id"]
    airline_id = airline["id"]
    s1.create_record(
        FLIGHT_TYPE,
        flight_payload(client_id=client_id, airline_id=airline_id),
    )
    s1.close()

    repo2 = JsonRecordRepository(path)
    s2 = RecordService(repository=repo2, auto_load=True)
    all_records = s2.list_records()
    assert len(all_records) == 3
    types = {r["type"] for r in all_records}
    assert types == {CLIENT_TYPE, AIRLINE_TYPE, FLIGHT_TYPE}

    flight = next(r for r in all_records if r["type"] == FLIGHT_TYPE)
    assert flight["client_id"] == client_id
    assert flight["airline_id"] == airline_id
    assert s2.get_record(CLIENT_TYPE, client_id)["id"] == client_id
    assert s2.get_record(AIRLINE_TYPE, airline_id)["id"] == airline_id


def test_update_persists_across_reload(tmp_path: Path) -> None:
    """An updated record is still modified after save and reload."""
    path = tmp_path / "records.json"
    repo = JsonRecordRepository(path)
    s1 = RecordService(repository=repo, auto_load=True)
    created = s1.create_record(CLIENT_TYPE, client_payload())
    s1.update_record(CLIENT_TYPE, created["id"], {"name": "New Name"})
    s1.close()

    s2 = RecordService(repository=JsonRecordRepository(path), auto_load=True)
    loaded = s2.get_record(CLIENT_TYPE, created["id"])
    assert loaded["name"] == "New Name"


def test_delete_persists_across_reload(tmp_path: Path) -> None:
    """A deleted record is absent after save and reload."""
    path = tmp_path / "records.json"
    repo = JsonRecordRepository(path)
    s1 = RecordService(repository=repo, auto_load=True)
    c = s1.create_record(CLIENT_TYPE, client_payload())
    s1.delete_record(CLIENT_TYPE, c["id"])
    s1.close()

    s2 = RecordService(repository=JsonRecordRepository(path), auto_load=True)
    assert s2.list_records(CLIENT_TYPE) == []
