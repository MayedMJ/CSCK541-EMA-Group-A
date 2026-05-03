"""Record management package."""

from .contracts import AIRLINE_TYPE, CLIENT_TYPE, RecordType
from .error_messages import RecordErrorMessage
from .exceptions import (
    RecordConflictError,
    RecordError,
    RecordNotFoundError,
    RecordValidationError,
)
from .repository import RecordRepository
from .storage import JsonRecordRepository

__all__ = [
    "AIRLINE_TYPE",
    "CLIENT_TYPE",
    "RecordError",
    "RecordErrorMessage",
    "RecordConflictError",
    "RecordNotFoundError",
    "RecordRepository",
    "RecordType",
    "RecordValidationError",
    "JsonRecordRepository",
]
