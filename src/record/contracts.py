"""Record data contract types and constants."""

from __future__ import annotations

from typing import Literal, TypedDict

CLIENT_TYPE = "client"
AIRLINE_TYPE = "airline"

RecordType = Literal["client", "airline"]


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


class ClientRecord(ClientPayload):
    id: int
    type: Literal["client"]


class AirlineRecord(AirlinePayload):
    id: int
    type: Literal["airline"]


AnyRecord = ClientRecord | AirlineRecord
