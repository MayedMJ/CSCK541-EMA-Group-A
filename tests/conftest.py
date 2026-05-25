"""Shared fixtures for pytest."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest


class FakeRepository:
    """In-memory RecordRepository for isolating RecordService from disk.

    Tracks how many times load_records and save_records are called and
    stores the last saved payload for assertion.
    """

    def __init__(self, records: list[dict[str, Any]] | None = None) -> None:
        self._records: list[dict[str, Any]] = [
            dict(r) for r in (records or [])
        ]
        self.load_calls = 0
        self.save_calls = 0
        self.last_saved: list[dict[str, Any]] | None = None

    def load_records(self) -> list[dict[str, Any]]:
        """Return a shallow copy of the stored records."""
        self.load_calls += 1
        return [dict(r) for r in self._records]

    def save_records(self, records: list[dict[str, Any]]) -> None:
        """Persist records into internal storage for later retrieval."""
        self.save_calls += 1
        self.last_saved = [dict(r) for r in records]
        self._records = [dict(r) for r in records]


# Supports overrides for scenario testing purposes
def client_payload(**overrides: Any) -> dict[str, Any]:
    """Return a valid client record payload with optional field overrides."""
    base: dict[str, Any] = {
        "name": "Ada Lovelace",
        "address_line_1": "1 Analytical Engine Way",
        "address_line_2": "",
        "address_line_3": "",
        "city": "London",
        "state": "England",
        "zip_code": "EC1A 1BB",
        "country": "UK",
        "phone_number": "+44 20 0000 0000",
    }
    base.update(overrides)
    return base


def airline_payload(**overrides: Any) -> dict[str, Any]:
    """Return a valid airline record payload with optional field overrides."""
    base: dict[str, Any] = {"company_name": "Transatlantic Airways"}
    base.update(overrides)
    return base


def flight_payload(
    client_id: int = 1,
    airline_id: int = 1,
    **overrides: Any,
) -> dict[str, Any]:
    """Return a valid flight record payload with optional field overrides."""
    base: dict[str, Any] = {
        "client_id": client_id,
        "airline_id": airline_id,
        "date": "2026-05-01T10:30:00",
        "start_city": "London",
        "end_city": "New York",
    }
    base.update(overrides)
    return base


@pytest.fixture
def tmp_json_path(tmp_path: Path) -> Path:
    """Provide a temporary file path for JSON record storage tests."""
    return tmp_path / "records.json"


@pytest.fixture
def fake_repo() -> FakeRepository:
    """Provide a fresh in-memory FakeRepository instance."""
    return FakeRepository()
