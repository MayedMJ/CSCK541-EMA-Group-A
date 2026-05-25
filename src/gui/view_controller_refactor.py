"""Compatibility entry point for the refactored GUI module name."""

from __future__ import annotations

from gui.view_controller import run_gui

__all__ = ["run_gui"]


if __name__ == "__main__":
    run_gui()
