"""Centralized error message strings."""

from __future__ import annotations


class RecordErrorMessage:
    """Factory for formatted record-service error messages."""

    _TEMPLATES: dict[str, str] = {
        "record_payload_not_dictionary": (
            "The record payload is not valid with reason: "
            "payload must be a dictionary"
        ),
        "record_update_payload_not_dictionary": (
            "The record update payload is not valid with reason: "
            "updates must be a dictionary"
        ),
        "record_type_not_allowed": (
            "The record type is not allowed with recordType: {record_type}"
        ),
        "record_not_found": (
            "The record is not found with recordType: "
            "{record_type}, recordId: {record_id}"
        ),
        "record_id_not_positive_integer": (
            "The record id is not valid with reason: "
            "id must be a positive integer"
        ),
        "record_type_mismatch": (
            "The record type is not valid with reason: "
            "payload type must be {record_type}"
        ),
        "record_id_cannot_be_changed": (
            "The record update is not valid with reason: "
            "id cannot be changed"
        ),
        "record_payload_missing_field": (
            "The record payload is not valid with reason: "
            "missing field: {field}"
        ),
        "record_payload_unknown_field": (
            "The record payload is not valid with reason: "
            "unknown field: {field}"
        ),
        "record_payload_field_not_string": (
            "The record payload is not valid with reason: "
            "field {field} must be a string"
        ),
        "record_payload_field_empty": (
            "The record payload is not valid with reason: "
            "field {field} cannot be empty"
        ),
        "record_payload_field_not_integer": (
            "The record payload is not valid with reason: "
            "field {field} must be an integer"
        ),
        "record_payload_field_not_positive_integer": (
            "The record payload is not valid with reason: "
            "field {field} must be a positive integer"
        ),
        "record_payload_field_not_iso_datetime": (
            "The record payload is not valid with reason: "
            "field {field} must be an ISO date/time string"
        ),
        "record_related_not_found": (
            "The related record is not found with recordType: "
            "{record_type}, recordId: {record_id}"
        ),
        "record_delete_conflict_linked_flights": (
            "The record cannot be deleted with recordType: "
            "{record_type}, recordId: {record_id}, "
            "reason: related flight records exist"
        ),
        "storage_json_invalid": (
            "The record storage is not valid with reason: "
            "file does not contain valid JSON"
        ),
        "storage_root_not_list": (
            "The record storage is not valid with reason: "
            "JSON root must be a list"
        ),
        "storage_item_not_dictionary": (
            "The record storage is not valid with reason: "
            "item at index {index} must be a dictionary"
        ),
        "storage_read_failed": (
            "The record storage cannot be read with path: {path}, reason: {reason}"
        ),
        "storage_write_failed": (
            "The record storage cannot be written with path: {path}, reason: {reason}"
        ),
    }

    @classmethod
    def from_(cls, key: str, **kwargs: object) -> str:
        """Returns a formatted message from a well known template key."""
        if key not in cls._TEMPLATES:
            raise ValueError(f"The error message template is not found with key: {key}")
        return cls._TEMPLATES[key].format(**kwargs)
