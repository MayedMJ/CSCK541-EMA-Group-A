"""Centralized error message strings."""

from __future__ import annotations


class RecordErrorMessage:
    """Factory for formatted record-service error messages."""

    _TEMPLATES: dict[str, str] = {
        "record_payload_not_dictionary": (
            "The record payload is not valid with reason: "
            "payload must be a dictionary"
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
    }

    @classmethod
    def from_(cls, key: str, **kwargs: object) -> str:
        """Returns a formatted message from a well known template key."""
        if key not in cls._TEMPLATES:
            raise ValueError(f"The error message template is not found with key: {key}")
        return cls._TEMPLATES[key].format(**kwargs)
