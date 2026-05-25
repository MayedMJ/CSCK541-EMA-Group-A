"""Tests for record.contracts module.

Covers schema lookups, relation dependency resolution, and
flight reference field retrieval.
"""

from __future__ import annotations

from record.contracts import (
    AIRLINE_TYPE,
    ALLOWED_RECORD_TYPES,
    CLIENT_SCHEMA,
    CLIENT_TYPE,
    FLIGHT_TYPE,
    get_flight_reference_field,
    get_record_schema,
    get_relation_dependencies,
)


def test_get_record_schema_client() -> None:
    """get_record_schema returns the CLIENT_SCHEMA for client type."""
    assert get_record_schema(CLIENT_TYPE) is CLIENT_SCHEMA


def test_get_record_schema_airline() -> None:
    """Airline schema has only company_name as a required field."""
    assert get_record_schema(AIRLINE_TYPE).required_fields == ("company_name",)


def test_get_record_schema_flight() -> None:
    """Flight schema includes client_id in its required fields."""
    assert "client_id" in get_record_schema(FLIGHT_TYPE).required_fields


def test_get_relation_dependencies_flight() -> None:
    """Flight type depends on both client and airline via FK fields."""
    deps = get_relation_dependencies(FLIGHT_TYPE)
    assert deps == (
        (CLIENT_TYPE, "client_id"),
        (AIRLINE_TYPE, "airline_id"),
    )


def test_get_relation_dependencies_non_flight_empty() -> None:
    """Client and airline types have no relation dependencies."""
    assert get_relation_dependencies(CLIENT_TYPE) == ()
    assert get_relation_dependencies(AIRLINE_TYPE) == ()


def test_get_flight_reference_field_client() -> None:
    """Client type maps to client_id in flight records."""
    assert get_flight_reference_field(CLIENT_TYPE) == "client_id"


def test_get_flight_reference_field_airline() -> None:
    """Airline type maps to airline_id in flight records."""
    assert get_flight_reference_field(AIRLINE_TYPE) == "airline_id"


def test_get_flight_reference_field_flight() -> None:
    """Flight type has no self-referencing field; returns None."""
    assert get_flight_reference_field(FLIGHT_TYPE) is None


def test_allowed_record_types_contains_all_three() -> None:
    """ALLOWED_RECORD_TYPES includes client, airline, and flight."""
    assert ALLOWED_RECORD_TYPES == frozenset({"client", "airline", "flight"})
