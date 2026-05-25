"""Tests for record.validators module.

Covers validate_record_payload and validate_stored_record with valid inputs,
missing fields, unknown fields, type mismatches, and edge cases.
"""

from __future__ import annotations

import pytest

from record.contracts import AIRLINE_TYPE, CLIENT_TYPE, FLIGHT_TYPE
from record.exceptions import RecordValidationError
from record.validators import validate_record_payload, validate_stored_record
from tests.conftest import airline_payload, client_payload, flight_payload


class TestValidateRecordPayload:
    """Tests for validate_record_payload across all three record types."""

    def test_client_valid(self) -> None:
        """Valid client payload is accepted and normalised correctly."""
        result = validate_record_payload(CLIENT_TYPE, client_payload())
        # Asserting some of the fields align
        assert result["name"] == "Ada Lovelace"
        assert result["address_line_2"] == ""
        assert result["address_line_3"] == ""

    def test_airline_valid(self) -> None:
        """Valid airline payload returns only company_name."""
        result = validate_record_payload(AIRLINE_TYPE, airline_payload())
        assert result == {"company_name": "Transatlantic Airways"}

    def test_flight_valid(self) -> None:
        """Valid flight payload normalises IDs and date."""
        result = validate_record_payload(FLIGHT_TYPE, flight_payload())
        assert result["client_id"] == 1
        assert result["airline_id"] == 1
        assert result["date"].startswith("2026-05-01")

    def test_flight_accepts_string_digits_for_ids(self) -> None:
        """Numeric strings for client_id/airline_id are coerced to int."""
        result = validate_record_payload(
            FLIGHT_TYPE,
            flight_payload(client_id="2", airline_id="3"),
        )
        assert result["client_id"] == 2
        assert result["airline_id"] == 3

    @pytest.mark.parametrize("field", ["name", "address_line_1", "city"])
    def test_client_missing_required_field(self, field: str) -> None:
        """Omitting a required client field raises RecordValidationError."""
        # All client fields are required, but some may be empty strings.
        payload = client_payload()
        del payload[field]
        with pytest.raises(RecordValidationError):
            validate_record_payload(CLIENT_TYPE, payload)

    def test_airline_missing_company_name(self) -> None:
        """Empty airline payload is rejected for missing company_name."""
        # Airline type has only one field which is required (company_name)
        with pytest.raises(RecordValidationError):
            validate_record_payload(AIRLINE_TYPE, {})

    @pytest.mark.parametrize(
        "field",
        ["client_id", "airline_id", "date", "start_city", "end_city"],
    )
    def test_flight_missing_required_field(self, field: str) -> None:
        """Omitting a required flight field raises RecordValidationError."""
        p = flight_payload()
        del p[field]
        with pytest.raises(RecordValidationError):
            validate_record_payload(FLIGHT_TYPE, p)

    # Generic error handling cases
    def test_unknown_field_rejected(self) -> None:
        """Extra fields not in the schema are rejected."""
        p = client_payload()
        p["extra"] = "nope"
        with pytest.raises(RecordValidationError):
            validate_record_payload(CLIENT_TYPE, p)

    def test_payload_must_be_dict(self) -> None:
        """Non-dict payload raises RecordValidationError."""
        with pytest.raises(RecordValidationError):
            validate_record_payload(CLIENT_TYPE, [])  # type: ignore[arg-type]

    def test_disallowed_record_type(self) -> None:
        """An unrecognised record type raises RecordValidationError."""
        with pytest.raises(RecordValidationError):
            validate_record_payload("unknown", {})  # type: ignore[arg-type]

    def test_type_field_mismatch(self) -> None:
        """Payload type must match record_type."""
        p = client_payload(type="airline")  # type: ignore[misc]
        with pytest.raises(RecordValidationError):
            validate_record_payload(CLIENT_TYPE, p)

    def test_non_string_name(self) -> None:
        """Integer value for a string field raises RecordValidationError."""
        with pytest.raises(RecordValidationError):
            validate_record_payload(CLIENT_TYPE, client_payload(name=123))  # type: ignore[arg-type]

    def test_empty_required_string_field(self) -> None:
        """A required string field with only whitespace is rejected."""
        with pytest.raises(RecordValidationError):
            validate_record_payload(CLIENT_TYPE, client_payload(name="   "))

    @pytest.mark.parametrize(
        "bad_client_id",
        [True, 1.5, 0, -1],
        ids=["bool", "float", "zero", "negative"],
    )
    def test_invalid_client_id_field_flight(
        self, bad_client_id: object
    ) -> None:
        """Invalid client_id values for flights are rejected."""
        with pytest.raises(RecordValidationError):
            validate_record_payload(
                FLIGHT_TYPE,
                flight_payload(client_id=bad_client_id),  # type: ignore[arg-type]
            )

    @pytest.mark.parametrize(
        "bad_airline_id",
        [True, 1.5, 0, -1],
        ids=["bool", "float", "zero", "negative"],
    )
    def test_invalid_airline_id_field_flight(
        self, bad_airline_id: object
    ) -> None:
        """Invalid airline_id values for flights are rejected."""
        with pytest.raises(RecordValidationError):
            validate_record_payload(
                FLIGHT_TYPE,
                flight_payload(airline_id=bad_airline_id),  # type: ignore[arg-type]
            )

    @pytest.mark.parametrize(
        "bad_date",
        ["", "not-a-date", "2026-13-01T10:00:00"],
    )
    def test_flight_invalid_date(self, bad_date: str) -> None:
        """Non-ISO or impossible dates raise RecordValidationError."""
        with pytest.raises(RecordValidationError):
            validate_record_payload(FLIGHT_TYPE, flight_payload(date=bad_date))

    def test_flight_date_accepts_z_suffix(self) -> None:
        """Trailing Z (UTC indicator) is accepted and normalised."""
        result = validate_record_payload(
            FLIGHT_TYPE,
            flight_payload(date="2026-05-01T10:30:00Z"),
        )
        assert "2026-05-01" in result["date"]

    def test_flight_non_string_date(self) -> None:
        """Non-string date value is rejected."""
        with pytest.raises(RecordValidationError):
            validate_record_payload(
                FLIGHT_TYPE,
                flight_payload(date=12345),  # type: ignore[arg-type]
            )


class TestValidateStoredRecord:
    """Tests for validate_stored_record used during loading."""

    @pytest.mark.parametrize(
        ("raw", "expected_type", "check_field", "check_value"),
        [
            (
                {"id": 1, "type": "client", **client_payload()},
                CLIENT_TYPE,
                "name",
                "Ada Lovelace",
            ),
            (
                {"id": 1, "type": "airline", **airline_payload()},
                AIRLINE_TYPE,
                "company_name",
                "Transatlantic Airways",
            ),
            (
                {"id": 1, "type": "flight", **flight_payload()},
                FLIGHT_TYPE,
                "client_id",
                1,
            ),
        ],
        ids=["client", "airline", "flight"],
    )
    def test_stored_record_happy_path(
        self,
        raw: dict[str, object],
        expected_type: str,
        check_field: str,
        check_value: object,
    ) -> None:
        """A well-formed stored record passes validation."""
        out = validate_stored_record(raw)
        assert out["id"] == 1
        assert out["type"] == expected_type
        assert out[check_field] == check_value

    def test_type_normalized_case(self) -> None:
        """Uppercase type strings are normalised to lowercase."""
        raw = {
            "id": 1,
            "type": "CLIENT",
            **client_payload(),
        }
        out = validate_stored_record(raw)
        assert out["type"] == "client"

    @pytest.mark.parametrize(
        ("raw", "missing_field"),
        [
            ({"id": 1, **client_payload()}, "type"),
            ({"type": "client", **client_payload()}, "id"),
        ],
        ids=["missing_type", "missing_id"],
    )
    def test_missing_required_stored_record_metadata(
        self, raw: dict[str, object], missing_field: str
    ) -> None:
        """Stored records missing required metadata fields are rejected."""
        with pytest.raises(RecordValidationError):
            validate_stored_record(raw)  # type: ignore[arg-type]

    def test_not_dict(self) -> None:
        """Non-dict input is rejected."""
        with pytest.raises(RecordValidationError):
            validate_stored_record([])  # type: ignore[arg-type]
