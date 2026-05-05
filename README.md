# Record Management Service

Backend service for managing travel-agent records.

## Project skeleton

This repository follows the provided assignment layout:

```text
.
├── docs/
├── requirements.txt
├── src/
│   ├── conf/
│   │   └── settings.py
│   ├── data/
│   ├── gui/
│   ├── main.py
│   └── record/
│       └── record.json
└── tests/
```

## Service interface

Use `RecordService` from `record`:

```python
from record import JsonRecordRepository, RecordService

repository = JsonRecordRepository("src/record/record.json")
service = RecordService(repository=repository)
```

Available methods:

- `create_record(record_type, payload) -> dict`
- `get_record(record_type, record_id) -> dict`
- `list_records(record_type=None) -> list[dict]`
- `search_records(record_type=None, **filters) -> list[dict]`
- `update_record(record_type, record_id, updates) -> dict`
- `delete_record(record_type, record_id) -> dict`
- `load() -> None`
- `save() -> None`
- `close() -> None`

## GUI-backend contract

- Service construction: `from main import build_service`.
- Service shutdown: `from main import close_service`.
- Create: returns created record dict with `id` and `type`.
- Get: returns one record by `record_type` and `record_id`.
- List/Search: return collections of records, with case-insensitive string search.
- Update: updates mutable fields and returns the updated record.
- Delete: deletes one record and returns deleted record payload.

Exception mapping for GUI:

- `RecordValidationError`: invalid payload, id, relationship reference, or storage read/write failure.
- `RecordNotFoundError`: requested record does not exist.
- `RecordConflictError`: delete blocked due to linked flight records.

## Record types

- `client`
- `airline`
- `flight`

## Role boundaries

- Programmer role:
- Implements domain contracts, validation, storage, and service behavior.
- Maintains architecture and code quality (for example, SOLID refactors).

- Tester role:
- Adds and maintains unit/integration test coverage.
- Defines and executes edge-case and regression scenarios.

## Validation and persistence

- Payloads are strictly validated by record type.
- Flight records require existing `client_id` and `airline_id`.
- Storage is JSON-backed through `JsonRecordRepository`.
- Storage writes are atomic and maintain a `.bak` recovery snapshot.

## Commit message policy

This project follows PyInstaller commit message guidelines:

- Guide: https://pyinstaller.org/en/stable/development/commit-messages.html
- Example: https://github.com/pyinstaller/pyinstaller/commit/5c1628e66e18e2bb1c44faa88387b1f627181b43

Format:

- First line: `<subsystem>: <present-tense summary>.`
- Keep first line <= 72 characters (target <= 50).
- Add a blank line, then explain why and what changed.
- Wrap body lines to around 72 characters.
