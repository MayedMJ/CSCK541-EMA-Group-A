"""Custom exceptions for record management service."""

from __future__ import annotations


class RecordError(Exception):
    """Base exception for record management errors."""


class RecordValidationError(RecordError):
    """Raised when payload or query validation fails."""


class RecordNotFoundError(RecordError):
    """Raised when requested record does not exist."""


class RecordConflictError(RecordError):
    """Raised when operation violates relation constraints."""
