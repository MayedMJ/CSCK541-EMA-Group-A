"""Persistence helpers for loading and saving records."""

from __future__ import annotations

import json
import os
import tempfile
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
        backup_path = self._backup_path()

        if self._file_path.exists():
            try:
                return self._read_records_from_path(self._file_path)
            except RecordValidationError as primary_error:
                if not backup_path.exists():
                    raise
                try:
                    recovered = self._read_records_from_path(backup_path)
                except RecordValidationError as backup_error:
                    raise primary_error from backup_error
                # Best-effort recovery from backup snapshot.
                self._try_restore_primary(recovered)
                return recovered

        if backup_path.exists():
            recovered = self._read_records_from_path(backup_path)
            self._try_restore_primary(recovered)
            return recovered

        return []

    def save_records(self, records: list[dict[str, Any]]) -> None:
        try:
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise RecordValidationError(
                RecordErrorMessage.from_(
                    "storage_write_failed",
                    path=str(self._file_path),
                    reason=str(exc),
                )
            ) from exc

        payload = json.dumps(records, ensure_ascii=False, indent=2, sort_keys=True)

        self._write_text_atomically(self._file_path, payload)
        # Keep a valid backup snapshot for recovery scenarios.
        self._write_text_atomically(self._backup_path(), payload)

    def _backup_path(self) -> Path:
        return self._file_path.with_name(f"{self._file_path.name}.bak")

    def _read_records_from_path(self, path: Path) -> list[dict[str, Any]]:
        try:
            raw = path.read_text(encoding="utf-8")
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RecordValidationError(
                RecordErrorMessage.from_("storage_json_invalid")
            ) from exc
        except UnicodeDecodeError as exc:
            raise RecordValidationError(
                RecordErrorMessage.from_(
                    "storage_read_failed",
                    path=str(path),
                    reason=str(exc),
                )
            ) from exc
        except OSError as exc:
            raise RecordValidationError(
                RecordErrorMessage.from_(
                    "storage_read_failed",
                    path=str(path),
                    reason=str(exc),
                )
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

    def _write_text_atomically(self, target: Path, payload: str) -> None:
        temp_path: Path | None = None
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=target.parent,
                prefix=f".{target.name}.",
                suffix=".tmp",
                delete=False,
            ) as temp_file:
                temp_file.write(payload)
                temp_file.flush()
                os.fsync(temp_file.fileno())
                temp_path = Path(temp_file.name)

            if temp_path is None:
                raise OSError("temporary file path is not available")
            os.replace(temp_path, target)
        except OSError as exc:
            raise RecordValidationError(
                RecordErrorMessage.from_(
                    "storage_write_failed",
                    path=str(target),
                    reason=str(exc),
                )
            ) from exc
        finally:
            if temp_path is not None and temp_path.exists():
                temp_path.unlink()

    def _try_restore_primary(self, records: list[dict[str, Any]]) -> None:
        payload = json.dumps(records, ensure_ascii=False, indent=2, sort_keys=True)
        try:
            self._write_text_atomically(self._file_path, payload)
        except RecordValidationError:
            # Load should still succeed even if recovery write is blocked.
            pass
