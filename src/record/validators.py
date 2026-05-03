"""Validation helpers for record payloads."""

from __future__ import annotations

from typing import Any

from .contracts import AIRLINE_TYPE, CLIENT_TYPE, RecordType
from .error_messages import RecordErrorMessage
from .exceptions import RecordValidationError

_CLIENT_FIELDS = {
    "name",
    "address_line_1",
    "address_line_2",
    "address_line_3",
    "city",
    "state",
    "zip_code",
    "country",
    "phone_number",
}
_AIRLINE_FIELDS = {"company_name"}
_OPTIONAL_EMPTY_STRING_FIELDS = {"address_line_2", "address_line_3"}


def validate_record_payload(
    record_type: RecordType, payload: dict[str, Any]
) -> dict[str, Any]:
    """Validates and normalizes record payload for create/update operations."""
    if not isinstance(payload, dict):
        raise RecordValidationError(
            RecordErrorMessage.from_("record_payload_not_dictionary")
        )
    if record_type not in {CLIENT_TYPE, AIRLINE_TYPE}:
        raise RecordValidationError(
            RecordErrorMessage.from_("record_type_not_allowed", record_type=record_type)
        )

    _validate_type_field(record_type, payload)
    fields = _CLIENT_FIELDS if record_type == CLIENT_TYPE else _AIRLINE_FIELDS
    _assert_no_unknown_fields(payload, fields)
    _assert_required_fields(payload, fields)

    if record_type == CLIENT_TYPE:
        return {
            "name": _as_string(payload, "name"),
            "address_line_1": _as_string(payload, "address_line_1"),
            "address_line_2": _as_string(payload, "address_line_2", allow_empty=True),
            "address_line_3": _as_string(payload, "address_line_3", allow_empty=True),
            "city": _as_string(payload, "city"),
            "state": _as_string(payload, "state"),
            "zip_code": _as_string(payload, "zip_code"),
            "country": _as_string(payload, "country"),
            "phone_number": _as_string(payload, "phone_number"),
        }

    return {
        "company_name": _as_string(payload, "company_name"),
    }


def validate_stored_record(record: dict[str, Any]) -> dict[str, Any]:
    """Validates and normalizes a stored record loaded from disk."""
    if not isinstance(record, dict):
        raise RecordValidationError(
            RecordErrorMessage.from_("record_payload_not_dictionary")
        )
    if "type" not in record:
        raise RecordValidationError(
            RecordErrorMessage.from_("record_payload_missing_field", field="type")
        )
    record_type = _as_record_type(record["type"])
    if "id" not in record:
        raise RecordValidationError(
            RecordErrorMessage.from_("record_payload_missing_field", field="id")
        )
    record_id = _as_positive_int(record["id"])
    payload = validate_record_payload(record_type, record)
    payload["id"] = record_id
    payload["type"] = record_type
    return payload


def _as_record_type(value: Any) -> RecordType:
    if not isinstance(value, str):
        raise RecordValidationError(
            RecordErrorMessage.from_("record_type_not_allowed", record_type=value)
        )
    normalized = value.strip().lower()
    if normalized not in {CLIENT_TYPE, AIRLINE_TYPE}:
        raise RecordValidationError(
            RecordErrorMessage.from_("record_type_not_allowed", record_type=normalized)
        )
    return normalized  # type: ignore[return-value]


def _validate_type_field(record_type: RecordType, payload: dict[str, Any]) -> None:
    if "type" not in payload:
        return
    if _as_record_type(payload["type"]) != record_type:
        raise RecordValidationError(
            RecordErrorMessage.from_("record_type_mismatch", record_type=record_type)
        )


def _assert_no_unknown_fields(payload: dict[str, Any], allowed_fields: set[str]) -> None:
    allowed_with_meta = set(allowed_fields)
    allowed_with_meta.add("type")
    allowed_with_meta.add("id")
    for key in payload.keys():
        if key not in allowed_with_meta:
            raise RecordValidationError(
                RecordErrorMessage.from_("record_payload_unknown_field", field=key)
            )


def _assert_required_fields(payload: dict[str, Any], required_fields: set[str]) -> None:
    for field in required_fields:
        if field not in payload:
            raise RecordValidationError(
                RecordErrorMessage.from_("record_payload_missing_field", field=field)
            )


def _as_string(payload: dict[str, Any], field: str, *, allow_empty: bool = False) -> str:
    value = payload.get(field)
    if not isinstance(value, str):
        raise RecordValidationError(
            RecordErrorMessage.from_("record_payload_field_not_string", field=field)
        )
    normalized = value.strip()
    if not allow_empty and not normalized:
        raise RecordValidationError(
            RecordErrorMessage.from_("record_payload_field_empty", field=field)
        )
    if allow_empty and field in _OPTIONAL_EMPTY_STRING_FIELDS and not normalized:
        return ""
    return normalized


def _as_positive_int(value: Any) -> int:
    if isinstance(value, bool):
        raise RecordValidationError(
            RecordErrorMessage.from_("record_id_not_positive_integer")
        )
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str) and value.strip().isdigit():
        parsed = int(value.strip())
    else:
        raise RecordValidationError(
            RecordErrorMessage.from_("record_id_not_positive_integer")
        )

    if parsed <= 0:
        raise RecordValidationError(
            RecordErrorMessage.from_("record_id_not_positive_integer")
        )

    return parsed
