"""Helpers to enforce immutable in-memory record storage."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from types import MappingProxyType
from typing import Any


def freeze_record(record: dict[str, Any]) -> Mapping[str, Any]:
    """Convert mutable record into immutable nested structures."""
    return deep_freeze(record)


def thaw_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Convert immutable record back to mutable plain Python containers."""
    thawed = deep_thaw(record)
    return thawed if isinstance(thawed, dict) else deepcopy(dict(record))


def deep_freeze(value: Any) -> Any:
    if isinstance(value, dict):
        frozen_dict = {key: deep_freeze(val) for key, val in value.items()}
        return MappingProxyType(frozen_dict)
    if isinstance(value, list):
        return tuple(deep_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(deep_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(deep_freeze(item) for item in value)
    return value


def deep_thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: deep_thaw(val) for key, val in value.items()}
    if isinstance(value, tuple):
        return [deep_thaw(item) for item in value]
    if isinstance(value, frozenset):
        return [deep_thaw(item) for item in value]
    return deepcopy(value)
