"""Tests for record.immutability module.

Covers freeze_record, thaw_record, and nested structure handling.
"""

from __future__ import annotations

from types import MappingProxyType

import pytest

from record.immutability import freeze_record, thaw_record


def test_freeze_returns_mapping_proxy() -> None:
    """freeze_record wraps a dict in an immutable MappingProxyType."""
    frozen = freeze_record({"a": 1})
    assert isinstance(frozen, MappingProxyType)


def test_frozen_mapping_cannot_be_mutated() -> None:
    """Attempting to assign to a frozen record raises TypeError."""
    frozen = freeze_record({"a": 1})
    with pytest.raises(TypeError):
        frozen["a"] = 2  # type: ignore[index]


def test_thaw_returns_mutable_dict() -> None:
    """thaw_record returns a plain dict that can be mutated safely."""
    frozen = freeze_record({"a": 1})
    thawed = thaw_record(frozen)
    thawed["a"] = 99
    assert thawed["a"] == 99
    assert frozen["a"] == 1  # type: ignore[index]


def test_thaw_is_deep_copy() -> None:
    """Mutating the thawed copy does not affect the frozen original."""
    original = {"nested": {"x": 1}}
    frozen = freeze_record(original)
    thawed = thaw_record(frozen)
    thawed["nested"]["x"] = 999
    assert frozen["nested"]["x"] == 1  # type: ignore[index]


def test_nested_list_freezes_to_tuple_and_thaws_to_list() -> None:
    """Lists become tuples when frozen and revert to lists when thawed."""
    original = {"items": [1, 2, {"k": "v"}]}
    frozen = freeze_record(original)
    inner = frozen["items"]  # type: ignore[index]
    assert isinstance(inner, tuple)
    thawed = thaw_record(frozen)
    assert thawed["items"] == [1, 2, {"k": "v"}]
    assert isinstance(thawed["items"], list)


def test_freeze_empty_dict() -> None:
    """Freezing an empty dict returns an empty MappingProxyType."""
    frozen = freeze_record({})
    assert isinstance(frozen, MappingProxyType)
    assert len(frozen) == 0
