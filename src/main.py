"""Application entry point."""

from __future__ import annotations

from threading import Lock

from conf.settings import RECORD_FILE_PATH
from record import JsonRecordRepository, RecordService

_SERVICE_INSTANCE: RecordService | None = None
_SERVICE_LOCK = Lock()


def build_service() -> RecordService:
    """Returns a process-wide RecordService singleton instance."""
    global _SERVICE_INSTANCE
    if _SERVICE_INSTANCE is None:
        with _SERVICE_LOCK:
            if _SERVICE_INSTANCE is None:
                repository = JsonRecordRepository(RECORD_FILE_PATH)
                _SERVICE_INSTANCE = RecordService(repository=repository)
    return _SERVICE_INSTANCE


def close_service() -> None:
    """Closes and clears the singleton service instance."""
    global _SERVICE_INSTANCE
    if _SERVICE_INSTANCE is None:
        return
    with _SERVICE_LOCK:
        if _SERVICE_INSTANCE is not None:
            _SERVICE_INSTANCE.close()
            _SERVICE_INSTANCE = None


def main() -> None:
    """Starts the application GUI with backend service wiring."""
    service = build_service()
    try:
        from gui.view_controller import run_gui

        run_gui(service)
    finally:
        close_service()


if __name__ == "__main__":
    main()
