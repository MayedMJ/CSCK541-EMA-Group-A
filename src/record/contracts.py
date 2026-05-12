"""Record data contract types and constants."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Literal, TypedDict

CLIENT_TYPE = "client"
AIRLINE_TYPE = "airline"
FLIGHT_TYPE = "flight"

RecordType = Literal["client", "airline", "flight"]
RelationDependency = tuple[RecordType, str]


class ClientPayload(TypedDict):
    name: str
    address_line_1: str
    address_line_2: str
    address_line_3: str
    city: str
    state: str
    zip_code: str
    country: str
    phone_number: str


class AirlinePayload(TypedDict):
    company_name: str


class FlightPayload(TypedDict):
    client_id: int
    airline_id: int
    date: str
    start_city: str
    end_city: str


class ClientRecord(ClientPayload):
    id: int
    type: Literal["client"]


class AirlineRecord(AirlinePayload):
    id: int
    type: Literal["airline"]


class FlightRecord(FlightPayload):
    id: int
    type: Literal["flight"]


@dataclass(frozen=True)
class RecordSchema:
    """Schema metadata used by validation and service layers."""

    required_fields: tuple[str, ...]
    optional_empty_string_fields: frozenset[str] = frozenset()


def _typed_dict_fields(payload_type: type[Any]) -> tuple[str, ...]:
    """Extract field order from TypedDict schema definitions."""
    return tuple(payload_type.__annotations__.keys())


CLIENT_SCHEMA = RecordSchema(
    required_fields=_typed_dict_fields(ClientPayload),
    optional_empty_string_fields=frozenset(
        {"address_line_2", "address_line_3"}
    ),
)
AIRLINE_SCHEMA = RecordSchema(
    required_fields=_typed_dict_fields(AirlinePayload)
)
FLIGHT_SCHEMA = RecordSchema(required_fields=_typed_dict_fields(FlightPayload))

RECORD_SCHEMAS = MappingProxyType(
    {
        CLIENT_TYPE: CLIENT_SCHEMA,
        AIRLINE_TYPE: AIRLINE_SCHEMA,
        FLIGHT_TYPE: FLIGHT_SCHEMA,
    }
)

ALLOWED_RECORD_TYPES: frozenset[RecordType] = frozenset(RECORD_SCHEMAS.keys())

RECORD_RELATION_DEPENDENCIES = MappingProxyType(
    {
        CLIENT_TYPE: (),
        AIRLINE_TYPE: (),
        FLIGHT_TYPE: (
            (CLIENT_TYPE, "client_id"),
            (AIRLINE_TYPE, "airline_id"),
        ),
    }
)

FLIGHT_REFERENCE_FIELDS_BY_PARENT_TYPE = MappingProxyType(
    {
        CLIENT_TYPE: "client_id",
        AIRLINE_TYPE: "airline_id",
        FLIGHT_TYPE: None,
    }
)


def get_record_schema(record_type: RecordType) -> RecordSchema:
    """Return schema metadata for the provided record type."""
    return RECORD_SCHEMAS[record_type]


def get_relation_dependencies(
    record_type: RecordType,
) -> tuple[RelationDependency, ...]:
    """Return foreign-key dependencies for the provided record type."""
    return RECORD_RELATION_DEPENDENCIES[record_type]


def get_flight_reference_field(record_type: RecordType) -> str | None:
    """Return flight reference field for a parent type, if applicable."""
    return FLIGHT_REFERENCE_FIELDS_BY_PARENT_TYPE[record_type]


AnyRecord = ClientRecord | AirlineRecord | FlightRecord
