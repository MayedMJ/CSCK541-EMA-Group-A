"""Tests for record.service.RecordService.

Covers CRUD operations, list/search, relation constraints, load/save
delegation, close behaviour, ID sequencing, and records property.
"""

from __future__ import annotations

import pytest

from record.contracts import AIRLINE_TYPE, CLIENT_TYPE, FLIGHT_TYPE
from record.exceptions import (
    RecordConflictError,
    RecordNotFoundError,
    RecordValidationError,
)
from record.service import RecordService
from tests.conftest import (
    FakeRepository,
    airline_payload,
    client_payload,
    flight_payload,
)


@pytest.fixture
def empty_service(fake_repo: FakeRepository) -> RecordService:
    """Provide a RecordService backed by an empty FakeRepository."""
    return RecordService(repository=fake_repo, auto_load=True)


class TestCreateRecord:
    """Tests for RecordService.create_record."""

    def test_assigns_id_and_type_client(
        self, empty_service: RecordService
    ) -> None:
        """First created client record gets id=1 and type='client'."""
        out = empty_service.create_record(CLIENT_TYPE, client_payload())
        assert out["id"] == 1
        assert out["type"] == CLIENT_TYPE

    def test_second_create_increments_id_same_type(
        self, empty_service: RecordService
    ) -> None:
        """Sequential creates of the same type produce incrementing IDs."""
        empty_service.create_record(CLIENT_TYPE, client_payload())
        out = empty_service.create_record(
            CLIENT_TYPE,
            client_payload(name="Second"),
        )
        assert out["id"] == 2
        assert out["name"] == "Second"

    def test_different_types_have_independent_ids(
        self, empty_service: RecordService
    ) -> None:
        """ID sequences are independent per record type."""
        c = empty_service.create_record(CLIENT_TYPE, client_payload())
        a = empty_service.create_record(AIRLINE_TYPE, airline_payload())
        assert c["id"] == 1
        assert a["id"] == 1

    def test_invalid_type_raises(self, empty_service: RecordService) -> None:
        """Creating with an unknown type raises RecordValidationError."""
        with pytest.raises(RecordValidationError):
            empty_service.create_record("unknown", {})  # type: ignore[arg-type]

    def test_non_dict_payload_raises(
        self, empty_service: RecordService
    ) -> None:
        """Creating with a non-dict payload raises RecordValidationError."""
        with pytest.raises(RecordValidationError):
            empty_service.create_record(CLIENT_TYPE, "bad")  # type: ignore[arg-type]


class TestGetRecord:
    """Tests for RecordService.get_record."""

    def test_retrieves_by_type_and_id(
        self, empty_service: RecordService
    ) -> None:
        """A created record can be retrieved by its type and id."""
        created = empty_service.create_record(CLIENT_TYPE, client_payload())
        got = empty_service.get_record(CLIENT_TYPE, created["id"])
        assert got["name"] == "Ada Lovelace"

    def test_not_found(self, empty_service: RecordService) -> None:
        """Getting a non-existent record raises RecordNotFoundError."""
        with pytest.raises(RecordNotFoundError):
            empty_service.get_record(CLIENT_TYPE, 99)

    def test_accepts_string_id(self, empty_service: RecordService) -> None:
        """Record ID passed as a digit string is normalised to int."""
        created = empty_service.create_record(CLIENT_TYPE, client_payload())
        got = empty_service.get_record(CLIENT_TYPE, str(created["id"]))  # type: ignore[arg-type]
        assert got["id"] == created["id"]

    @pytest.mark.parametrize(
        "bad_id",
        ["abc", True, 0, -5],
        ids=["non_digit_string", "boolean", "zero", "negative"],
    )
    def test_invalid_id_raises(
        self, empty_service: RecordService, bad_id: object
    ) -> None:
        """Non-positive-integer IDs raise RecordValidationError."""
        with pytest.raises(RecordValidationError):
            empty_service.get_record(CLIENT_TYPE, bad_id)  # type: ignore[arg-type]

    def test_whitespace_padded_string_id(
        self, empty_service: RecordService
    ) -> None:
        """Whitespace around a digit string is stripped before lookup."""
        created = empty_service.create_record(CLIENT_TYPE, client_payload())
        got = empty_service.get_record(CLIENT_TYPE, " 1 ")  # type: ignore[arg-type]
        assert got["id"] == created["id"]


class TestUpdateRecord:
    """Tests for RecordService.update_record."""

    def test_updates_fields(self, empty_service: RecordService) -> None:
        """Providing new field values merges them into the existing record."""
        created = empty_service.create_record(CLIENT_TYPE, client_payload())
        out = empty_service.update_record(
            CLIENT_TYPE,
            created["id"],
            {"name": "Updated"},
        )
        assert out["name"] == "Updated"
        assert out["id"] == created["id"]

    def test_rejects_id_change(self, empty_service: RecordService) -> None:
        """Attempting to change the record ID raises RecordValidationError."""
        created = empty_service.create_record(CLIENT_TYPE, client_payload())
        with pytest.raises(RecordValidationError):
            empty_service.update_record(
                CLIENT_TYPE,
                created["id"],
                {"id": 999},
            )

    def test_rejects_type_change(self, empty_service: RecordService) -> None:
        """Changing the record type raises RecordValidationError."""
        created = empty_service.create_record(CLIENT_TYPE, client_payload())
        with pytest.raises(RecordValidationError):
            empty_service.update_record(
                CLIENT_TYPE,
                created["id"],
                {"type": "airline"},
            )

    def test_non_dict_updates_raises(
        self, empty_service: RecordService
    ) -> None:
        """Passing non-dict updates raises RecordValidationError."""
        created = empty_service.create_record(CLIENT_TYPE, client_payload())
        with pytest.raises(RecordValidationError):
            empty_service.update_record(
                CLIENT_TYPE,
                created["id"],
                "not a dict",  # type: ignore[arg-type]
            )

    def test_update_flight_happy_path(
        self, empty_service: RecordService
    ) -> None:
        """Updating a flight merges new values and validates relations."""
        c = empty_service.create_record(CLIENT_TYPE, client_payload())
        a = empty_service.create_record(AIRLINE_TYPE, airline_payload())
        f = empty_service.create_record(
            FLIGHT_TYPE,
            flight_payload(client_id=c["id"], airline_id=a["id"]),
        )
        out = empty_service.update_record(
            FLIGHT_TYPE, f["id"], {"end_city": "Paris"}
        )
        assert out["end_city"] == "Paris"
        assert out["client_id"] == c["id"]

    def test_update_flight_invalid_relation_raises(
        self, empty_service: RecordService
    ) -> None:
        """Updating a flight to a missing parent raises validation."""
        c = empty_service.create_record(CLIENT_TYPE, client_payload())
        a = empty_service.create_record(AIRLINE_TYPE, airline_payload())
        f = empty_service.create_record(
            FLIGHT_TYPE,
            flight_payload(client_id=c["id"], airline_id=a["id"]),
        )
        with pytest.raises(RecordValidationError):
            empty_service.update_record(
                FLIGHT_TYPE, f["id"], {"client_id": 999}
            )


class TestDeleteRecord:
    """Tests for RecordService.delete_record."""

    def test_removes_record(self, empty_service: RecordService) -> None:
        """Deleting a record removes it from storage and returns it."""
        created = empty_service.create_record(CLIENT_TYPE, client_payload())
        deleted = empty_service.delete_record(CLIENT_TYPE, created["id"])
        assert deleted["id"] == created["id"]
        with pytest.raises(RecordNotFoundError):
            empty_service.get_record(CLIENT_TYPE, created["id"])

    def test_not_found(self, empty_service: RecordService) -> None:
        """Deleting a non-existent record raises RecordNotFoundError."""
        with pytest.raises(RecordNotFoundError):
            empty_service.delete_record(CLIENT_TYPE, 1)

    def test_accepts_string_id(self, empty_service: RecordService) -> None:
        """Record ID passed as a digit string is normalised for deletion."""
        created = empty_service.create_record(CLIENT_TYPE, client_payload())
        deleted = empty_service.delete_record(CLIENT_TYPE, str(created["id"]))  # type: ignore[arg-type]
        assert deleted["id"] == created["id"]
        with pytest.raises(RecordNotFoundError):
            empty_service.get_record(CLIENT_TYPE, created["id"])


class TestListAndSearch:
    """Tests for RecordService.list_records and search_records."""

    def test_list_all(self, empty_service: RecordService) -> None:
        """list_records with no filter returns all records."""
        empty_service.create_record(CLIENT_TYPE, client_payload())
        empty_service.create_record(AIRLINE_TYPE, airline_payload())
        assert len(empty_service.list_records()) == 2

    def test_list_filtered_by_type(self, empty_service: RecordService) -> None:
        """list_records with a type filter returns only matching records."""
        empty_service.create_record(CLIENT_TYPE, client_payload())
        empty_service.create_record(AIRLINE_TYPE, airline_payload())
        clients = empty_service.list_records(CLIENT_TYPE)
        assert len(clients) == 1
        assert clients[0]["type"] == CLIENT_TYPE

    def test_search_case_insensitive_strings(
        self, empty_service: RecordService
    ) -> None:
        """String filter values match case-insensitively."""
        empty_service.create_record(CLIENT_TYPE, client_payload())
        hits = empty_service.search_records(name="ADA LOVELACE")
        assert len(hits) == 1

    def test_search_int_equality(self, empty_service: RecordService) -> None:
        """Integer filter values match by exact equality."""
        c = empty_service.create_record(CLIENT_TYPE, client_payload())
        empty_service.create_record(AIRLINE_TYPE, airline_payload())
        empty_service.create_record(
            FLIGHT_TYPE,
            flight_payload(client_id=c["id"], airline_id=1),
        )
        hits = empty_service.search_records(FLIGHT_TYPE, client_id=c["id"])
        assert len(hits) == 1

    def test_search_no_match(self, empty_service: RecordService) -> None:
        """Search with no matching records returns an empty list."""
        empty_service.create_record(CLIENT_TYPE, client_payload())
        assert empty_service.search_records(name="Nobody") == []

    def test_search_filter_key_not_in_record(
        self, empty_service: RecordService
    ) -> None:
        """Filtering on a key absent from the record yields no matches."""
        empty_service.create_record(CLIENT_TYPE, client_payload())
        assert empty_service.search_records(nonexistent_field="x") == []


class TestRecordsProperty:
    """Tests for the records property snapshot."""

    def test_returns_mutable_copy(self, empty_service: RecordService) -> None:
        """The records property returns a detached mutable list."""
        empty_service.create_record(CLIENT_TYPE, client_payload())
        snapshot = empty_service.records
        snapshot.clear()
        assert len(empty_service.records) == 1


class TestRelationConstraints:
    """Tests for foreign-key relationship enforcement."""

    def test_flight_requires_existing_client_and_airline(
        self, empty_service: RecordService
    ) -> None:
        """Creating a flight without a matching client/airline raises."""
        with pytest.raises(RecordValidationError):
            empty_service.create_record(FLIGHT_TYPE, flight_payload())

    def test_delete_client_blocked_when_flights_exist(
        self, empty_service: RecordService
    ) -> None:
        """Deleting a client with linked flights raises conflict."""
        c = empty_service.create_record(CLIENT_TYPE, client_payload())
        a = empty_service.create_record(AIRLINE_TYPE, airline_payload())
        empty_service.create_record(
            FLIGHT_TYPE,
            flight_payload(client_id=c["id"], airline_id=a["id"]),
        )
        with pytest.raises(RecordConflictError):
            empty_service.delete_record(CLIENT_TYPE, c["id"])

    def test_delete_airline_blocked_when_flights_exist(
        self, empty_service: RecordService
    ) -> None:
        """Deleting an airline with linked flights raises conflict."""
        c = empty_service.create_record(CLIENT_TYPE, client_payload())
        a = empty_service.create_record(AIRLINE_TYPE, airline_payload())
        empty_service.create_record(
            FLIGHT_TYPE,
            flight_payload(client_id=c["id"], airline_id=a["id"]),
        )
        with pytest.raises(RecordConflictError):
            empty_service.delete_record(AIRLINE_TYPE, a["id"])

    def test_delete_allowed_after_removing_flights(
        self, empty_service: RecordService
    ) -> None:
        """Once linked flights are removed, parent records can be deleted."""
        c = empty_service.create_record(CLIENT_TYPE, client_payload())
        a = empty_service.create_record(AIRLINE_TYPE, airline_payload())
        f = empty_service.create_record(
            FLIGHT_TYPE,
            flight_payload(client_id=c["id"], airline_id=a["id"]),
        )
        empty_service.delete_record(FLIGHT_TYPE, f["id"])
        empty_service.delete_record(CLIENT_TYPE, c["id"])
        assert empty_service.list_records(CLIENT_TYPE) == []


class TestLoadSave:
    """Tests for load and save delegation to the repository."""

    def test_save_invokes_repository(
        self,
        empty_service: RecordService,
        fake_repo: FakeRepository,
    ) -> None:
        """Calling save() delegates to the repository's save_records."""
        assert fake_repo.save_calls == 0
        empty_service.save()
        assert fake_repo.save_calls == 1
        assert fake_repo.last_saved == []

    def test_load_called_on_construct(self, fake_repo: FakeRepository) -> None:
        """Repository load_records is called once during construction."""
        RecordService(repository=fake_repo, auto_load=True)
        assert fake_repo.load_calls == 1

    def test_close_triggers_save(
        self,
        empty_service: RecordService,
        fake_repo: FakeRepository,
    ) -> None:
        """Calling close() persists current records via save."""
        empty_service.create_record(CLIENT_TYPE, client_payload())
        empty_service.close()
        assert fake_repo.save_calls == 1
        assert len(fake_repo.last_saved) == 1


class TestIdSequencingAfterReload:
    """Tests for correct ID continuation across save/reload cycles."""

    def test_next_id_continues_after_reload(
        self, fake_repo: FakeRepository
    ) -> None:
        """A new service instance resumes IDs from the highest stored value."""
        s1 = RecordService(repository=fake_repo, auto_load=True)
        s1.create_record(CLIENT_TYPE, client_payload())
        s1.save()
        s2 = RecordService(repository=fake_repo, auto_load=True)
        out = s2.create_record(CLIENT_TYPE, client_payload(name="Next"))
        assert out["id"] == 2
