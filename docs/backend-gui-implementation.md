# Backend-GUI Implementation Guide

## Purpose
This document explains how the GUI should integrate with the backend.
It focuses on:

- **What** backend capabilities are available.
- **How** the GUI should call them.
- **When** each backend method should be used in app lifecycle.

## What: Backend Interface
The GUI should integrate through `main.py` and `RecordService`.

### Service lifecycle API
- `build_service() -> RecordService`
- `close_service() -> None`

### Record operations API
- `create_record(record_type, payload) -> dict`
- `get_record(record_type, record_id) -> dict`
- `list_records(record_type=None) -> list[dict]`
- `search_records(record_type=None, **filters) -> list[dict]`
- `update_record(record_type, record_id, updates) -> dict`
- `delete_record(record_type, record_id) -> dict`

### Example usage snippets
```python
from main import build_service; 
service = build_service()

client = service.create_record("client", payload)

item = service.get_record("client", 1)

rows = service.list_records("client")
rows = service.search_records("client", city="liverpool")

item = service.update_record("client", 1, {"city": "Split"})
item = service.delete_record("client", 1)

service.load()
service.save()
service.close()

from main import close_service; 
close_service()
```

### Supported record types
- `client`
- `airline`
- `flight`

## What: Data Shape
### Client payload fields
- `name`
- `address_line_1`
- `address_line_2`
- `address_line_3`
- `city`
- `state`
- `zip_code`
- `country`
- `phone_number`

### Airline payload fields
- `company_name`

### Flight payload fields
- `client_id`
- `airline_id`
- `date` (ISO datetime string)
- `start_city`
- `end_city`

### Returned records
All returned records include:
- `id` (int)
- `type` (`client` | `airline` | `flight`)

## How: Integration Pattern
Use one shared service instance for the whole GUI process.

### Startup
1. On app initialization, call `build_service()`.
2. Keep the returned service instance in app state.

Snippet:
```python
from main import build_service; service = build_service()
```

### During user actions
1. Collect form input in GUI.
2. Build payload dict.
3. Call service method (`create_record`, `update_record`, etc.).
4. Refresh UI from returned record(s) or with `list_records`.

Snippets:
```python
client = service.create_record("client", payload)
item = service.get_record("client", 1)
rows = service.list_records("client")
rows = service.search_records("client", city="liverpool")
item = service.update_record("client", 1, {"city": "Split"})
item = service.delete_record("client", 1)
```

### Shutdown
1. On app close event, call `close_service()`.
2. Do not manually call `save()` from each screen action.

Snippet:
```python
from main import close_service; 
close_service()
```

## How: Error Handling Contract
Catch backend exceptions and map to GUI messages:

- `RecordValidationError`
  - Invalid form input
  - Invalid IDs
  - Missing related records
  - Storage read/write failures
- `RecordNotFoundError`
  - Requested record does not exist
- `RecordConflictError`
  - Delete blocked by linked flight records

Recommended mapping:
- Show validation errors near input fields where possible.
- Show not-found/conflict as action-level banners or dialog messages.

Snippet:
```python
try:
    item = service.get_record("client", selected_id)
except RecordValidationError as exc:
    show_field_error(str(exc))
except RecordNotFoundError as exc:
    show_banner(str(exc))
except RecordConflictError as exc:
    show_dialog(str(exc))
```

## When: Method Usage Matrix
- Use `create_record` when user submits new client/airline/flight form.
- Use `get_record` when user opens details by ID.
- Use `list_records` for table/list screens.
- Use `search_records` for filter/search actions.
- Use `update_record` when user saves edited record.
- Use `delete_record` when user confirms deletion.
- Use `build_service` once at app startup.
- Use `close_service` once at app shutdown.

## Example GUI Flow
### Create client
1. User fills Create Client form.
2. GUI builds `payload` dict.
3. Call `service.create_record("client", payload)`.
4. On success, show created item and refresh list view.
5. On `RecordValidationError`, show validation message.

### Delete client
1. User selects client and confirms delete.
2. Call `service.delete_record("client", client_id)`.
3. On success, remove from UI list.
4. On `RecordConflictError`, show message that linked flights must be deleted first.

## Integration Notes
- Keep GUI/backend boundary clean: GUI should not touch repository or JSON directly.
- Treat backend as single source of truth.
- Re-read records after write operations.
- Keep `record_type` explicit in GUI action handlers.
