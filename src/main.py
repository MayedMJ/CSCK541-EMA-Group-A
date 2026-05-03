"""Application entry point."""

from __future__ import annotations

from conf.settings import RECORD_FILE_PATH


def main() -> None:
    """Starts the application entrypoint wiring."""
    _ = RECORD_FILE_PATH


if __name__ == "__main__":
    main()
