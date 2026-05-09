"""Tests for main.py application wiring.

Covers singleton build/close lifecycle, file creation on close,
and instance reset behaviour.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from record.service import RecordService


@pytest.fixture(autouse=True)
def _reset_singleton() -> None:
    """Ensure a clean singleton state before and after each test."""
    import main

    main.close_service()
    yield
    main.close_service()


def test_build_service_returns_record_service(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """build_service returns an instance of RecordService."""
    import main

    path = tmp_path / "record.json"
    # Mocking the RECORD_FILE_PATH to use the temporary path
    monkeypatch.setattr(main, "RECORD_FILE_PATH", path)
    svc = main.build_service()
    # Asserting that the service built from the wriing is of type RecordService
    assert isinstance(svc, RecordService)


def test_build_service_singleton(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Calling build_service twice returns the same instance."""
    import main

    path = tmp_path / "record.json"
    monkeypatch.setattr(main, "RECORD_FILE_PATH", path)
    # Build service stores the newly created instance as a singleton variable
    # So subsequent calls to build_service should return the same instance
    # Asserting that the two calls to build_service return the same instance
    assert main.build_service() is main.build_service()


def test_close_service_clears_instance_and_writes_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """close_service persists records to disk and sets instance to None."""
    import main

    path = tmp_path / "record.json"
    monkeypatch.setattr(main, "RECORD_FILE_PATH", path)
    main.build_service()
    main.close_service()
    # Instance should be closed and set to None
    assert getattr(main, "_SERVICE_INSTANCE") is None
    # File should still exist
    assert path.exists()


def test_close_service_when_not_built(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Calling close_service without prior build does not raise."""
    import main

    monkeypatch.setattr(main, "RECORD_FILE_PATH", tmp_path / "x.json")
    # Should do nothing as the service has not been built
    main.close_service()


def test_second_build_after_close_new_instance(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """After close, a subsequent build_service creates a fresh instance."""
    import main

    monkeypatch.setattr(main, "RECORD_FILE_PATH", tmp_path / "a.json")
    first = main.build_service()
    main.close_service()
    monkeypatch.setattr(main, "RECORD_FILE_PATH", tmp_path / "b.json")
    second = main.build_service()
    # Asserting that the two instances are different as the second instance was created after the first instance was closed
    assert first is not second
