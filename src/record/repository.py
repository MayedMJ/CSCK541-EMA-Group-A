"""Repository abstraction for record persistence."""

from __future__ import annotations

from typing import Any, Protocol


class RecordRepository(Protocol):
    """Persistence contract used by RecordService."""

    def load_records(self) -> list[dict[str, Any]]:
        """Load all stored records."""

    def save_records(self, records: list[dict[str, Any]]) -> None:
        """Persist all records."""
