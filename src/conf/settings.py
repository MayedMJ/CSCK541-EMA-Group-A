"""Application configuration values."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RECORD_FILE_PATH = PROJECT_ROOT / "src" / "record" / "record.json"
