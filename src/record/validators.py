"""Validation helpers for record payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .contracts import (
    ALLOWED_RECORD_TYPES,
    CLIENT_TYPE,
    RecordType,
    get_record_schema,
)
from .error_messages import RecordErrorMessage
from .exceptions import RecordValidationError

_CLIENT_OPTIONAL_EMPTY_FIELDS = get_record_schema(
    CLIENT_TYPE
).optional_empty_string_fields


def validate_record_payload(
    record_type: RecordType, payload: dict[str, Any]
) -> dict[str, Any]:
    """Validates and normalizes record payload for create/update operations."""
    if not isinstance(payload, dict):
        raise RecordValidationError(
            RecordErrorMessage.from_("record_payload_not_dictionary")
        )
    if record_type not in ALLOWED_RECORD_TYPES:
        raise RecordValidationError(
            RecordErrorMessage.from_(
                "record_type_not_allowed", record_type=record_type
            )
        )

    _validate_type_field(record_type, payload)
    schema = get_record_schema(record_type)
    fields = set(schema.required_fields)
    _assert_no_unknown_fields(payload, fields)
    _assert_required_fields(payload, fields)

    if record_type == CLIENT_TYPE:
        return {
            "name": _as_string(payload, "name"),
            "address_line_1": _as_string(payload, "address_line_1"),
            "address_line_2": _as_string(
                payload, "address_line_2", allow_empty=True
            ),
            "address_line_3": _as_string(
                payload, "address_line_3", allow_empty=True
            ),
            "city": _as_string(payload, "city"),
            "state": _as_string(payload, "state"),
            "zip_code": _as_string(payload, "zip_code"),
            "country": _as_string(payload, "country"),
            "phone_number": _as_string(payload, "phone_number"),
        }

    if record_type == "airline":
        return {
            "company_name": _as_string(payload, "company_name"),
        }

    return {
        "client_id": _as_positive_int(payload, "client_id"),
        "airline_id": _as_positive_int(payload, "airline_id"),
        "date": _as_iso_datetime(payload, "date"),
        "start_city": _as_string(payload, "start_city"),
        "end_city": _as_string(payload, "end_city"),
    }


def validate_stored_record(record: dict[str, Any]) -> dict[str, Any]:
    """Validates and normalizes a stored record loaded from disk."""
    if not isinstance(record, dict):
        raise RecordValidationError(
            RecordErrorMessage.from_("record_payload_not_dictionary")
        )
    if "type" not in record:
        raise RecordValidationError(
            RecordErrorMessage.from_(
                "record_payload_missing_field", field="type"
            )
        )
    record_type = _as_record_type(record["type"])
    if "id" not in record:
        raise RecordValidationError(
            RecordErrorMessage.from_(
                "record_payload_missing_field", field="id"
            )
        )
    record_id = _as_positive_int(record, "id")
    payload = validate_record_payload(record_type, record)
    payload["id"] = record_id
    payload["type"] = record_type
    return payload


def _as_record_type(value: Any) -> RecordType:
    if not isinstance(value, str):
        raise RecordValidationError(
            RecordErrorMessage.from_(
                "record_type_not_allowed", record_type=value
            )
        )
    normalized = value.strip().lower()
    if normalized not in ALLOWED_RECORD_TYPES:
        raise RecordValidationError(
            RecordErrorMessage.from_(
                "record_type_not_allowed", record_type=normalized
            )
        )
    return normalized  # type: ignore[return-value]


def _validate_type_field(
    record_type: RecordType, payload: dict[str, Any]
) -> None:
    if "type" not in payload:
        return
    if _as_record_type(payload["type"]) != record_type:
        raise RecordValidationError(
            RecordErrorMessage.from_(
                "record_type_mismatch", record_type=record_type
            )
        )


def _assert_no_unknown_fields(
    payload: dict[str, Any], allowed_fields: set[str]
) -> None:
    allowed_with_meta = set(allowed_fields)
    allowed_with_meta.add("type")
    allowed_with_meta.add("id")
    for key in payload.keys():
        if key not in allowed_with_meta:
            raise RecordValidationError(
                RecordErrorMessage.from_(
                    "record_payload_unknown_field", field=key
                )
            )


def _assert_required_fields(
    payload: dict[str, Any], required_fields: set[str]
) -> None:
    for field in required_fields:
        if field not in payload:
            raise RecordValidationError(
                RecordErrorMessage.from_(
                    "record_payload_missing_field", field=field
                )
            )


def _as_string(
    payload: dict[str, Any], field: str, *, allow_empty: bool = False
) -> str:
    value = payload.get(field)
    if not isinstance(value, str):
        raise RecordValidationError(
            RecordErrorMessage.from_(
                "record_payload_field_not_string", field=field
            )
        )
    normalized = value.strip()
    if not allow_empty and not normalized:
        raise RecordValidationError(
            RecordErrorMessage.from_("record_payload_field_empty", field=field)
        )
    if (
        allow_empty
        and field in _CLIENT_OPTIONAL_EMPTY_FIELDS
        and not normalized
    ):
        return ""
    return normalized


def _as_positive_int(payload: dict[str, Any], field: str) -> int:
    value = payload.get(field)
    if isinstance(value, bool):
        raise RecordValidationError(
            RecordErrorMessage.from_(
                "record_payload_field_not_integer", field=field
            )
        )

    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str) and value.strip().isdigit():
        parsed = int(value.strip())
    else:
        raise RecordValidationError(
            RecordErrorMessage.from_(
                "record_payload_field_not_integer", field=field
            )
        )

    if parsed <= 0:
        raise RecordValidationError(
            RecordErrorMessage.from_(
                "record_payload_field_not_positive_integer", field=field
            )
        )

    return parsed


def _as_iso_datetime(payload: dict[str, Any], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str):
        raise RecordValidationError(
            RecordErrorMessage.from_(
                "record_payload_field_not_iso_datetime", field=field
            )
        )

    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise RecordValidationError(
            RecordErrorMessage.from_(
                "record_payload_field_not_iso_datetime", field=field
            )
        ) from exc

    return parsed.isoformat(timespec="seconds")
