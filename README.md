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

## Phase-one API

Use `RecordService` from `record`:

```python
from record import JsonRecordRepository, RecordService

repository = JsonRecordRepository("src/record/record.json")
service = RecordService(repository=repository)
```

Available methods in phase one:

- `create_record(record_type, payload) -> dict`
- `get_record(record_type, record_id) -> dict`
- `load() -> None`
- `save() -> None`
- `close() -> None`

## GUI-backend contract (phase one)

- Service construction: `from main import build_service`.
- Service shutdown: `from main import close_service`.
- Create: returns created record dict with `id` and `type`.
- Get: returns one record dict by `record_type` and `record_id`.
- Exception mapping:
- `RecordValidationError` for invalid payload or id.
- `RecordNotFoundError` for missing record.

## Record types in phase one

- `client`
- `airline`
