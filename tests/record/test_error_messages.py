"""Tests for RecordErrorMessage template factory.

Covers formatting for every registered template key, unknown key handling,
and placeholder substitution.
"""

from __future__ import annotations

from typing import Any

import pytest

from record.error_messages import RecordErrorMessage

# Each row has a key, kwargs and must_contain
# key -> which template to use
# kwargs -> the values passed
# must_contain -> strings we expect to see in the final message
_TEMPLATE_FORMAT_CASES: list[tuple[str, dict[str, Any], tuple[str, ...]]] = [
    (
        "record_payload_not_dictionary",
        {},
        ("dictionary",),
    ),
    (
        "record_update_payload_not_dictionary",
        {},
        ("updates must be a dictionary",),
    ),
    (
        "record_type_not_allowed",
        {"record_type": "bogus"},
        ("bogus", "recordType"),
    ),
    (
        "record_not_found",
        {"record_type": "client", "record_id": 42},
        ("client", "42"),
    ),
    (
        "record_id_not_positive_integer",
        {},
        ("positive integer",),
    ),
    (
        "record_type_mismatch",
        {"record_type": "flight"},
        ("flight",),
    ),
    (
        "record_id_cannot_be_changed",
        {},
        ("id cannot be changed",),
    ),
    (
        "record_payload_missing_field",
        {"field": "name"},
        ("name", "missing field"),
    ),
    (
        "record_payload_unknown_field",
        {"field": "extra"},
        ("extra", "unknown field"),
    ),
    (
        "record_payload_field_not_string",
        {"field": "city"},
        ("city", "string"),
    ),
    (
        "record_payload_field_empty",
        {"field": "title"},
        ("title", "empty"),
    ),
    (
        "record_payload_field_not_integer",
        {"field": "count"},
        ("count", "integer"),
    ),
    (
        "record_payload_field_not_positive_integer",
        {"field": "id"},
        ("id", "positive integer"),
    ),
    (
        "record_payload_field_not_iso_datetime",
        {"field": "date"},
        ("date", "ISO"),
    ),
    (
        "record_related_not_found",
        {"record_type": "airline", "record_id": 9},
        ("airline", "9"),
    ),
    (
        "record_delete_conflict_linked_flights",
        {"record_type": "client", "record_id": 7},
        ("client", "7", "flight"),
    ),
    (
        "storage_json_invalid",
        {},
        ("valid JSON",),
    ),
    (
        "storage_root_not_list",
        {},
        ("list",),
    ),
    (
        "storage_item_not_dictionary",
        {"index": 3},
        ("3", "dictionary"),
    ),
    (
        "storage_read_failed",
        {"path": "/tmp/records.json", "reason": "permission denied"},
        ("/tmp/records.json", "permission denied"),
    ),
    (
        "storage_write_failed",
        {"path": "/out/records.json", "reason": "disk full"},
        ("/out/records.json", "disk full"),
    ),
]


@pytest.mark.parametrize(
    ("key", "kwargs", "must_contain"),
    _TEMPLATE_FORMAT_CASES,
    ids=[key for key, _, _ in _TEMPLATE_FORMAT_CASES],
)
def test_all_templates_format(
    key: str, kwargs: dict[str, Any], must_contain: tuple[str, ...]
) -> None:
    """Each registered template formats with the expected kwargs and text."""
    msg = RecordErrorMessage.from_(key, **kwargs)
    # Asserts that the message is non-empty and includes expected fragments.
    assert isinstance(msg, str)
    assert msg.strip()
    for fragment in must_contain:
        assert fragment in msg


def test_format_cases_cover_all_templates() -> None:
    """Every template key has a matching format case."""
    # Asserts that message templates align with format case keys.
    registered = frozenset(RecordErrorMessage._TEMPLATES)
    covered = frozenset(key for key, _, _ in _TEMPLATE_FORMAT_CASES)
    assert covered == registered


def test_unknown_key_raises_value_error() -> None:
    """An unregistered template key raises ValueError."""
    with pytest.raises(ValueError, match="template is not found"):
        RecordErrorMessage.from_("no_such_template_key")
