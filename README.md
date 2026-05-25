# Record Management Service

Backend service for managing travel-agent records.

## Requirements

- Python 3.10 or newer.
- No third-party runtime dependencies are required for the backend service.
- Development tools for testing and linting are listed in `requirements.txt`.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Alternatively, install the project with its development extras:

```bash
python -m pip install -e ".[dev]"
```

## Run the backend

Run the backend entry point:

```bash
python src/main.py
```

This initializes the shared `RecordService`, loads records from
`src/data/record.json`, and closes the service cleanly. The GUI package is
reserved for the interface layer; backend methods are exposed through
`main.build_service()` and `main.close_service()`.

## Run tests

Run the full test suite:

```bash
python -m pytest
```

Run tests with coverage:

```bash
python -m pytest --cov=src
```

## Run linting

Check formatting and lint rules with Ruff:

```bash
ruff check .
```

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
│   │   └── record.json
│   ├── gui/
│   ├── main.py
│   └── record/
└── tests/
```

## Service interface

Use `RecordService` from `record`:

```python
from record import JsonRecordRepository, RecordService

repository = JsonRecordRepository("src/data/record.json")
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

Integration guide:
- `docs/backend-gui-implementation.md`

- Service construction: `from main import build_service`.
- Service shutdown: `from main import close_service`.
- Create: returns created record dict with `id` and `type`.
- Get: returns one record by `record_type` and `record_id`.
- List/Search: return collections of records with case-insensitive
  string search.
- Update: updates mutable fields and returns the updated record.
- Delete: deletes one record and returns deleted record payload.

Exception mapping for GUI:

- `RecordValidationError`: invalid payload, id, relationship
  reference, or storage read/write failure.
- `RecordNotFoundError`: requested record does not exist.
- `RecordConflictError`: delete blocked due to linked flight
  records.

## Record types

- `client`
- `airline`
- `flight`

## Validation and persistence

- Payloads are strictly validated by record type.
- Flight records require existing `client_id` and `airline_id`.
- Storage is JSON-backed through `JsonRecordRepository`.
- Storage writes are atomic and maintain a `.bak` recovery snapshot.

## Commit message policy

This project follows PyInstaller commit message guidelines:

- Guide: https://pyinstaller.org/en/stable/development/commit-messages.html
- Example: https://github.com/pyinstaller/pyinstaller/commit/5c1628e

Format:

- First line: `<subsystem>: <present-tense summary>.`
- Keep first line <= 72 characters (target <= 50).
- Add a blank line, then explain why and what changed.
- Wrap body lines to around 72 characters.
