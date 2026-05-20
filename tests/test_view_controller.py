"""Tests for the module gui.view_controller

prepare_payload covered for the four action times:
-prepare_action_data
-CRUD delegation
-error handling
-change_dropdown_value behavior"""

from __future__ import annotations

import os
import sys
import importlib.util
from unittest.mock import MagicMock

import pytest

# Fakes the libraries and record module so importing view_controller does not open an actual window.
# does not open a real Tk window or require the backend on disk.
sys.modules["tkinter"] = MagicMock()
sys.modules["tkinter.ttk"] = MagicMock()
sys.modules["customtkinter"] = MagicMock()
sys.modules["src"] = MagicMock()
sys.modules["src.record"] = MagicMock()
sys.modules["record"] = MagicMock()
sys.modules["main"] = MagicMock()

# Load view_controller directly from its file path since it cannot be imported normally.
_vc_path = os.path.join(
    os.path.dirname(__file__), "..", "src", "gui", "view_controller.py"
)
_spec = importlib.util.spec_from_file_location("view_controller", _vc_path)
view_controller = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(view_controller)



#Helpers
def _make_entry(value: str) -> MagicMock:
    """Return a fake entry widget whose .get() returns *value*."""
    entry = MagicMock()
    entry.get.return_value = value
    return entry


def _widget_pair(value: str) -> tuple[MagicMock, MagicMock]:
    """Return a (label, entry) pair mimicking a CTkLabel + CTkEntry row."""
    return (MagicMock(), _make_entry(value))


def _client_store(**overrides: str) -> dict:
    """Return a fake widget store with typical client fields.

    Any keyword argument overrides the default value for that label.
    """
    defaults = {
        "Name": "Mayed",
        "Address Line 1": "St 1",
        "Address Line 2": "",
        "Address Line 3": "",
        "City": "Sharjah",
        "State": "Sharjah",
        "Zip Code": "10",
        "Country": "UAE",
        "Phone Number": "+971555555555",
    }
    defaults.update(overrides)
    return {label: _widget_pair(val) for label, val in defaults.items()}


# Fixtures


@pytest.fixture(autouse=True)
def _reset_mocks() -> None:
    """Clear call history on the mocked service and message_label
    before every test so assertions are isolated."""
    view_controller.service.reset_mock()
    view_controller.message_label.reset_mock()





# prepare_payload


class TestPreparePayloadCreate:
    """Tests for prepare_payload when the action is 'Create Record'."""

    def test_returns_mapped_field_values(self) -> None:
        """Field labels are converted to snake_case keys with correct values."""
        store = _client_store()
        result = view_controller.prepare_payload(store, "Create Record")
        assert result["name"] == "Mayed"
        assert result["address_line_1"] == "St 1"
        assert result["city"] == "Sharjah"

    def test_excludes_id_and_type(self) -> None:
        """The returned dict must not contain 'id' or 'type' keys."""
        store = _client_store()
        result = view_controller.prepare_payload(store, "Create Record")
        assert "id" not in result
        assert "type" not in result


class TestPreparePayloadDelete:
    """Tests for prepare_payload when the action is 'Delete Record'."""

    def test_returns_integer_id(self) -> None:
        """The string typed into the ID field is returned as an int."""
        store = {"ID to Delete": _widget_pair("42")}
        result = view_controller.prepare_payload(store, "Delete Record")
        assert result == 42


class TestPreparePayloadUpdate:
    """Tests for prepare_payload when the action is 'Update Record'."""

    def test_returns_id_and_updates(self) -> None:
        """Returns a (record_id, updates) tuple with non-empty fields."""
        store = {
            "ID": _widget_pair("7"),
            "Name": _widget_pair("Mayed"),
            "City": _widget_pair(""),
        }
        record_id, updates = view_controller.prepare_payload(store, "Update Record")
        assert record_id == 7
        assert updates["name"] == "Mayed"
        assert "city" not in updates

    def test_empty_fields_are_excluded(self) -> None:
        """When all editable fields are blank the updates dict is empty."""
        store = {
            "ID": _widget_pair("1"),
            "Name": _widget_pair(""),
            "City": _widget_pair(""),
        }
        record_id, updates = view_controller.prepare_payload(store, "Update Record")
        assert record_id == 1
        assert updates == {}


class TestPreparePayloadSearch:
    """Tests for prepare_payload when the Search Record is the action"""

    def test_returns_integer_id(self) -> None:
        """The string typed into the search field is returned as an int."""
        store = {"ID to Search": _widget_pair("99")}
        result = view_controller.prepare_payload(store, "Search Record")
        assert result == 99



# Flight Create panel regression


class TestFlightCreatePanelHasForeignKeys:
    """Regression test for the Flight Create panel.

    The Flight schema requires client_id and airline_id (the foreign
    keys that link a flight to existing client and airline records).
    The Create panel must therefore render entry widgets for them, and
    label_variable_mapping must know how to translate those labels into
    the snake_case keys the backend expects.

    At time of writing, the [2:] slice in build_panel skips the first
    two flight labels (Client_ID and Airline ID), and
    label_variable_mapping is missing both entries, so flights cannot
    be created through the GUI. This test fails until both gaps are
    closed."""

    def test_flight_create_panel_offers_foreign_key_fields(self) -> None:
        """show_panel for Flight on the create frame must populate the
        widget store with Client_ID and Airline ID entries."""
        store: dict = {}
        view_controller.show_panel(
            store, view_controller.create_options_frame, "Flight"
        )
        assert "Client_ID" in store, (
            "Flight Create panel does not include a Client_ID field; "
            "backend will reject every create attempt"
        )
        assert "Airline ID" in store, (
            "Flight Create panel does not include an Airline ID field; "
            "backend will reject every create attempt"
        )

    def test_flight_foreign_key_labels_are_mapped(self) -> None:
        """label_variable_mapping must convert Client_ID -> client_id
        and Airline ID -> airline_id so that prepare_payload can build
        the backend payload without raising KeyError."""
        mapping = view_controller.label_variable_mapping
        assert mapping.get("Client_ID") == "client_id", (
            "label_variable_mapping is missing 'Client_ID' -> 'client_id'; "
            "prepare_payload would KeyError on Flight create"
        )
        assert mapping.get("Airline ID") == "airline_id", (
            "label_variable_mapping is missing 'Airline ID' -> 'airline_id'; "
            "prepare_payload would KeyError on Flight create"
        )



# prepare_action_data


class TestPrepareActionDataCreate:
    """Tests for the Create path of prepare_action_data."""

    def test_delegates_to_service_create_and_save(self) -> None:
        """create_record and save are each called exactly once."""
        store = _client_store()
        view_controller.prepare_action_data("Create Record", "client", store)
        view_controller.service.create_record.assert_called_once()
        view_controller.service.save.assert_called_once()

    def test_shows_green_success_message(self) -> None:
        """Message label is a green success string."""
        store = _client_store()
        view_controller.prepare_action_data("Create Record", "client", store)
        view_controller.message_label.configure.assert_called_once_with(
            text="Record created successfully!", text_color="green"
        )


class TestPrepareActionDataDelete:
    """Tests for the Delete path of prepare_action_data."""

    def test_delegates_to_service_delete_and_save(self) -> None:
        """delete_record is called with the correct type and ID."""
        store = {"ID to Delete": _widget_pair("5")}
        view_controller.prepare_action_data("Delete Record", "client", store)
        view_controller.service.delete_record.assert_called_once_with("client", 5)
        view_controller.service.save.assert_called_once()

    def test_shows_green_success_message(self) -> None:
        """Message label is a green success string."""
        store = {"ID to Delete": _widget_pair("5")}
        view_controller.prepare_action_data("Delete Record", "client", store)
        view_controller.message_label.configure.assert_called_once_with(
            text="Record deleted successfully!", text_color="green"
        )


class TestPrepareActionDataUpdate:
    """Tests for the Update path of prepare_action_data."""

    def test_delegates_to_service_update_and_save(self) -> None:
        """update_record and save are each called exactly once."""
        store = {
            "ID": _widget_pair("3"),
            "Name": _widget_pair("Mayed"),
        }
        view_controller.prepare_action_data("Update Record", "client", store)
        view_controller.service.update_record.assert_called_once()
        view_controller.service.save.assert_called_once()

    def test_shows_green_success_message(self) -> None:
        """The message label is updated with a green success string."""
        store = {
            "ID": _widget_pair("3"),
            "Name": _widget_pair("Mayed"),
        }
        view_controller.prepare_action_data("Update Record", "client", store)
        view_controller.message_label.configure.assert_called_once_with(
            text="Record updated successfully!", text_color="green"
        )


class TestPrepareActionDataSearch:
    """Tests for the Search path of prepare_action_data."""

    def test_delegates_to_service_get_record(self) -> None:
        """get_record is called with the correct type and ID"""
        view_controller.service.get_record.return_value = {"name": "Mayed"}
        results_box = MagicMock()
        store = {
            "ID to Search": _widget_pair("10"),
            "Results": (MagicMock(), results_box),
        }
        view_controller.prepare_action_data("Search Record", "client", store)
        view_controller.service.get_record.assert_called_once_with("client", 10)

    def test_displays_result_in_textbox(self) -> None:
        """Results is cleared and has shows new record. """
        view_controller.service.get_record.return_value = {"name": "Mayed"}
        results_box = MagicMock()
        store = {
            "ID to Search": _widget_pair("10"),
            "Results": (MagicMock(), results_box),
        }
        view_controller.prepare_action_data("Search Record", "client", store)
        results_box.delete.assert_called_once_with("1.0", "end")
        results_box.insert.assert_called_once()

    def test_shows_green_success_message(self) -> None:
        """Updated message displayed in green"""
        view_controller.service.get_record.return_value = {"name": "Mayed"}
        results_box = MagicMock()
        store = {
            "ID to Search": _widget_pair("10"),
            "Results": (MagicMock(), results_box),
        }
        view_controller.prepare_action_data("Search Record", "client", store)
        view_controller.message_label.configure.assert_called_once_with(
            text="Search completed successfully!", text_color="green"
        )


class TestPrepareActionDataError:
    """Tests the error hadnling inside prepare_action_data."""

    def test_service_exception_shows_red_error(self) -> None:
        """Error is shown in red when it gets raised"""
        view_controller.service.create_record.side_effect = ValueError("bad data")
        store = _client_store()
        view_controller.prepare_action_data("Create Record", "client", store)
        view_controller.message_label.configure.assert_called_once_with(
            text="Error: bad data", text_color="red"
        )
        view_controller.service.create_record.side_effect = None






# change_dropdown_value
class TestChangeDropdownValue:
    """Tests for change_dropdown_value helper."""

    def test_updates_option_types_to_airline(self) -> None:
        """Airline selection updates option_types"""
        mock_var = MagicMock()
        mock_var.get.return_value = "Airline"
        view_controller.change_dropdown_value(mock_var, "Create")
        assert view_controller.option_types["Create"] == "Airline"

    def test_updates_option_types_to_flight_record(self) -> None:
        """Flight record selection updates option_types"""
        mock_var = MagicMock()
        mock_var.get.return_value = "Flight Record"
        view_controller.change_dropdown_value(mock_var, "Search")
        assert view_controller.option_types["Search"] == "Flight Record"
