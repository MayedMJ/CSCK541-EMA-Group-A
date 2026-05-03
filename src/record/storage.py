"""Persistence helpers for loading and saving records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .error_messages import RecordErrorMessage
from .exceptions import RecordValidationError
from .repository import RecordRepository


class JsonRecordRepository(RecordRepository):
    """JSON file-based record repository."""

    def __init__(self, file_path: str | Path) -> None:
        self._file_path = Path(file_path)

    @property
    def file_path(self) -> Path:
        return self._file_path

    def load_records(self) -> list[dict[str, Any]]:
        if not self._file_path.exists():
            return []
        try:
            raw = self._file_path.read_text(encoding="utf-8")
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RecordValidationError(
                RecordErrorMessage.from_("storage_json_invalid")
            ) from exc

        if not isinstance(parsed, list):
            raise RecordValidationError(
                RecordErrorMessage.from_("storage_root_not_list")
            )

        records: list[dict[str, Any]] = []
        for index, item in enumerate(parsed):
            if not isinstance(item, dict):
                raise RecordValidationError(
                    RecordErrorMessage.from_(
                        "storage_item_not_dictionary", index=index
                    )
                )
            records.append(item)
        return records

    def save_records(self, records: list[dict[str, Any]]) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(records, ensure_ascii=False, indent=2, sort_keys=True)
        self._file_path.write_text(payload, encoding="utf-8")
