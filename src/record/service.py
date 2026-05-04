"""Service layer for record CRUD and search operations."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from .contracts import (
    ALLOWED_RECORD_TYPES,
    FLIGHT_TYPE,
    RecordType,
    get_flight_reference_field,
    get_relation_dependencies,
)
from .error_messages import RecordErrorMessage
from .exceptions import RecordConflictError, RecordNotFoundError, RecordValidationError
from .immutability import freeze_record, thaw_record
from .repository import RecordRepository
from .storage import JsonRecordRepository
from .validators import validate_record_payload, validate_stored_record

LOGGER = logging.getLogger(__name__)


class RecordService:
    """Application service that stores records as list-of-dictionaries."""

    def __init__(
        self,
        repository: RecordRepository | None = None,
        *,
        auto_load: bool = True,
    ) -> None:
        self._repository = repository or JsonRecordRepository("src/record/record.json")
        self._records: tuple[Mapping[str, Any], ...] = ()
        self._next_ids: dict[RecordType, int] = {
            record_type: 1 for record_type in ALLOWED_RECORD_TYPES
        }
        if auto_load:
            self.load()

    @property
    def records(self) -> list[dict[str, Any]]:
        """Returns a detached snapshot of all records."""
        return [thaw_record(record) for record in self._records]

    def load(self) -> None:
        """Loads records from storage."""
        loaded = self._repository.load_records()
        validated = [validate_stored_record(record) for record in loaded]
        self._records = tuple(freeze_record(record) for record in validated)
        self._rebuild_next_ids()

    def save(self) -> None:
        """Saves records to storage."""
        self._repository.save_records(self.records)

    def close(self) -> None:
        """Closes the service and persists pending changes."""
        self.save()

    def list_records(
        self, record_type: RecordType | None = None
    ) -> list[dict[str, Any]]:
        if record_type is None:
            return [thaw_record(record) for record in self._records]
        return [
            thaw_record(record)
            for record in self._records
            if record.get("type") == record_type
        ]

    def search_records(
        self,
        record_type: RecordType | None = None,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        candidates = (
            self._records
            if record_type is None
            else tuple(r for r in self._records if r.get("type") == record_type)
        )
        matched: list[dict[str, Any]] = []
        for record in candidates:
            ok = True
            for key, expected in filters.items():
                if key not in record:
                    ok = False
                    break
                value = record[key]
                if isinstance(value, str) and isinstance(expected, str):
                    if value.lower() != expected.lower():
                        ok = False
                        break
                elif value != expected:
                    ok = False
                    break
            if ok:
                matched.append(thaw_record(record))
        return matched

    def get_record(self, record_type: RecordType, record_id: int) -> dict[str, Any]:
        normalized_id = self._normalize_record_id(record_id)
        idx = self._find_index(record_type, normalized_id)
        return thaw_record(self._records[idx])

    def create_record(
        self,
        record_type: RecordType,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        if not isinstance(payload, dict):
            self._raise_validation_error("record_payload_not_dictionary")
        if record_type not in ALLOWED_RECORD_TYPES:
            self._raise_validation_error(
                "record_type_not_allowed", record_type=record_type
            )

        normalized_payload = validate_record_payload(record_type, payload)

        for related_type, related_field in get_relation_dependencies(record_type):
            self._assert_related_record_exists(
                related_type, normalized_payload[related_field]
            )

        new_record = dict(normalized_payload)
        new_record["id"] = self._generate_id(record_type)
        new_record["type"] = record_type

        self._records = (*self._records, freeze_record(new_record))
        LOGGER.info(
            "The record is created with recordType: {}, recordId: {}".format(
                record_type, new_record["id"]
            )
        )
        return thaw_record(self._records[-1])

    def update_record(
        self,
        record_type: RecordType,
        record_id: int,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        if not isinstance(updates, dict):
            self._raise_validation_error("record_update_payload_not_dictionary")

        normalized_id = self._normalize_record_id(record_id)
        idx = self._find_index(record_type, normalized_id)
        updated = thaw_record(self._records[idx])
        if "id" in updates and updates["id"] != normalized_id:
            self._raise_validation_error("record_id_cannot_be_changed")
        if "type" in updates and updates["type"] != record_type:
            self._raise_validation_error(
                "record_type_mismatch", record_type=record_type
            )

        updated.update(updates)
        normalized_payload = validate_record_payload(record_type, updated)
        for related_type, related_field in get_relation_dependencies(record_type):
            self._assert_related_record_exists(
                related_type, normalized_payload[related_field]
            )

        updated_record = dict(normalized_payload)
        updated_record["id"] = normalized_id
        updated_record["type"] = record_type

        frozen = freeze_record(updated_record)
        self._records = self._records[:idx] + (frozen,) + self._records[idx + 1 :]

        LOGGER.info(
            "The record is updated with recordType: {}, recordId: {}".format(
                record_type, normalized_id
            )
        )
        return thaw_record(frozen)

    def delete_record(self, record_type: RecordType, record_id: int) -> dict[str, Any]:
        normalized_id = self._normalize_record_id(record_id)
        related_key = get_flight_reference_field(record_type)
        if related_key is not None:
            self._assert_no_related_flights(record_type, normalized_id, related_key)

        idx = self._find_index(record_type, normalized_id)
        deleted = self._records[idx]
        self._records = self._records[:idx] + self._records[idx + 1 :]

        LOGGER.info(
            "The record is deleted with recordType: {}, recordId: {}".format(
                record_type, normalized_id
            )
        )
        return thaw_record(deleted)

    def _find_index(self, record_type: RecordType, record_id: int) -> int:
        for index, record in enumerate(self._records):
            if record.get("type") == record_type and record.get("id") == record_id:
                return index

        error_text = RecordErrorMessage.from_(
            "record_not_found", record_type=record_type, record_id=record_id
        )
        LOGGER.debug(error_text)
        raise RecordNotFoundError(error_text)

    def _raise_validation_error(self, key: str, **kwargs: object) -> None:
        error_text = RecordErrorMessage.from_(key, **kwargs)
        LOGGER.warning(error_text)
        raise RecordValidationError(error_text)

    def _normalize_record_id(self, record_id: Any) -> int:
        if isinstance(record_id, bool):
            self._raise_validation_error("record_id_not_positive_integer")
        if isinstance(record_id, int):
            parsed = record_id
        elif isinstance(record_id, str) and record_id.strip().isdigit():
            parsed = int(record_id.strip())
        else:
            self._raise_validation_error("record_id_not_positive_integer")

        if parsed <= 0:
            self._raise_validation_error("record_id_not_positive_integer")

        return parsed

    def _generate_id(self, record_type: RecordType) -> int:
        next_id = self._next_ids[record_type]
        self._next_ids[record_type] += 1
        return next_id

    def _rebuild_next_ids(self) -> None:
        for record_type in ALLOWED_RECORD_TYPES:
            max_id = 0
            for record in self._records:
                if record.get("type") == record_type and isinstance(
                    record.get("id"), int
                ):
                    max_id = max(max_id, record["id"])
            self._next_ids[record_type] = max_id + 1

    def _assert_related_record_exists(
        self,
        record_type: RecordType,
        record_id: Any,
    ) -> None:
        normalized_id = self._normalize_record_id(record_id)
        for record in self._records:
            if record.get("type") == record_type and record.get("id") == normalized_id:
                return

        self._raise_validation_error(
            "record_related_not_found",
            record_type=record_type,
            record_id=normalized_id,
        )

    def _assert_no_related_flights(
        self,
        record_type: RecordType,
        record_id: int,
        related_key: str,
    ) -> None:
        has_related = any(
            record.get("type") == FLIGHT_TYPE and record.get(related_key) == record_id
            for record in self._records
        )
        if has_related:
            error_text = RecordErrorMessage.from_(
                "record_delete_conflict_linked_flights",
                record_type=record_type,
                record_id=record_id,
            )
            LOGGER.warning(error_text)
            raise RecordConflictError(error_text)
