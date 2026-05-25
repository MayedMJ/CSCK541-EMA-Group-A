import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

# --- Shared configuration / mappings ---
title = "Airline Records Management System"

client_box_labels = {
    "Client": ["ID", "Type", "Name", "Address Line 1", "Address Line 2", "Address Line 3",
               "City", "State", "Zip Code", "Country", "Phone Number"],
    "Airline": ["ID", "Type", "Company Name"],
    "Flight Record": ["Client_ID", "Airline ID", "Date", "Start City", "End City"]
}

label_variable_mapping = {
    "ID": "id",
    "Type": "type",
    "Name": "name",
    "Address Line 1": "address_line_1",
    "Address Line 2": "address_line_2",
    "Address Line 3": "address_line_3",
    "City": "city",
    "State": "state",
    "Zip Code": "zip_code",
    "Country": "country",
    "Phone Number": "phone_number",
}

variable_label_mapping = {v: k for k, v in label_variable_mapping.items()}

user_options = ("Create", "Delete", "Update", "Search")


# --- View: widget construction and layout only ---
class View:
    def __init__(self):
        # Root window
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("1200x560")
        self.root.resizable(False, True)

        # Frames
        self.buttons_frame = ttk.Frame(self.root)
        self.buttons_frame.grid(row=2, column=0, columnspan=4, sticky="ew")

        # Equal 4-column layout
        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1, uniform="cols")
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_rowconfigure(2, minsize=80)

        self.upper_frame = ttk.Frame(self.root)
        self.upper_frame.grid(row=0, column=0, columnspan=4, sticky="ew")

        self.create_options_frame = ttk.Frame(self.root)
        self.delete_options_frame = ttk.Frame(self.root)
        self.update_options_frame = ttk.Frame(self.root)
        self.search_options_frame = ttk.Frame(self.root)
        self.create_options_frame.grid(row=1, column=0, sticky="nsew")
        self.delete_options_frame.grid(row=1, column=1, sticky="nsew")
        self.update_options_frame.grid(row=1, column=2, sticky="nsew")
        self.search_options_frame.grid(row=1, column=3, sticky="nsew")

        for i in range(4):
            self.buttons_frame.grid_columnconfigure(i, weight=1)
        for frame in (self.create_options_frame, self.delete_options_frame,
                      self.update_options_frame, self.search_options_frame):
            frame.grid_columnconfigure(1, weight=1)

        # Widget state storage
        self.create_widgets = {}
        self.delete_widgets = {}
        self.update_widgets = {}
        self.search_widgets = {}

        # Dropdown variables (exposed for the controller to bind)
        self.create_value = tk.StringVar(self.root)
        self.delete_value = tk.StringVar(self.root)
        self.update_value = tk.StringVar(self.root)
        self.search_value = tk.StringVar(self.root)

        # Message label (updated by controller)
        self.message_label = ctk.CTkLabel(
            self.buttons_frame,
            text="",
            font=("Arial", 20),
            text_color="green"
        )
        self.message_label.grid(row=0, column=0, columnspan=4, pady=5)

        # Buttons registry (button widget, its store mapping)
        self.buttons = {}

        # Build static UI
        self.create_title()
        self.show_dropdown_labels()

        # Create dropdowns in the header
        self.create_dropdown(("Client", "Airline", "Flight Record"), 2, 0, self.create_value)
        self.create_dropdown(("Client", "Airline", "Flight Record"), 2, 1, self.delete_value)
        self.create_dropdown(("Client", "Airline", "Flight Record"), 2, 2, self.update_value)
        self.create_dropdown(("Client", "Airline", "Flight Record"), 2, 3, self.search_value)

        # Create action buttons (commands will be wired by controller)
        btn = self.create_button("Create Record", 1, 0, 150, self.create_widgets, command=None)
        self.buttons["Create"] = (btn, self.create_widgets)
        btn = self.create_button("Delete Record", 1, 1, 150, self.delete_widgets, command=None)
        self.buttons["Delete"] = (btn, self.delete_widgets)
        btn = self.create_button("Update Record", 1, 2, 150, self.update_widgets, command=None)
        self.buttons["Update"] = (btn, self.update_widgets)
        btn = self.create_button("Search Record", 1, 3, 150, self.search_widgets, command=None)
        self.buttons["Search"] = (btn, self.search_widgets)

        # Initial build of panels with default "Client" type
        self.show_panel(self.create_widgets, self.create_options_frame, "Client")
        self.show_panel(self.delete_widgets, self.delete_options_frame, "Client")
        self.show_panel(self.update_widgets, self.update_options_frame, "Client")
        self.show_panel(self.search_widgets, self.search_options_frame, "Client")

    # UI helpers
    def create_dropdown(self, options, row, column, selected_value):
        cb = ttk.Combobox(self.upper_frame, textvariable=selected_value,
                          values=options, state="readonly", width=16)
        cb.grid(row=row, column=column, padx=92, pady=10, sticky="nsew")
        return cb

    def create_button(self, text, row, column, size, store, command=None):
        btn = ctk.CTkButton(
            self.buttons_frame,
            text=text,
            width=size,
            fg_color="navy",
            command=command
        )
        btn.grid(row=row, column=column, padx=20, pady=10, sticky="ew")
        return btn

    def create_textbox(self, row, column, frame):
        tb = ctk.CTkTextbox(frame, row=row, column=column)
        return tb

    def create_title(self):
        ctk.CTkLabel(
            self.upper_frame,
            text=title,
            font=("Arial", 30)
        ).grid(row=0, column=0, columnspan=4, pady=10)

    def show_dropdown_labels(self):
        for i, option in enumerate(user_options):
            ctk.CTkLabel(self.upper_frame, text=option, font=("Arial", 16)).grid(
                row=1, column=i, padx=10, pady=5
            )

    # Panel building (pure UI)
    def build_panel(self, frame, record_type, store):
        """
        Create widgets ONCE per panel, based on record type.
        """
        # clear old widgets visually if any exist
        for w in list(store.values()):
            try:
                w[0].destroy()
            except Exception:
                pass
            try:
                w[1].destroy()
            except Exception:
                pass

        store.clear()

        if frame in (self.create_options_frame, self.update_options_frame):
            for i, label in enumerate(client_box_labels[record_type][2:]):
                lbl = ctk.CTkLabel(frame, text=label, font=("Arial", 12))
                ent = ctk.CTkEntry(frame, width=150)

                lbl.grid(row=i, column=0, padx=10, pady=5, sticky="w")
                ent.grid(row=i, column=1, padx=10, pady=5, sticky="ew")

                store[label] = (lbl, ent)
        elif frame == self.delete_options_frame:
            lbl = ctk.CTkLabel(frame, text="ID to Delete", font=("Arial", 12))
            ent = ctk.CTkEntry(frame, width=150)
            lbl.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            ent.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
            store["ID to Delete"] = (lbl, ent)
        elif frame == self.search_options_frame:
            lbl = ctk.CTkLabel(frame, text="ID to Search", font=("Arial", 12))
            ent = ctk.CTkEntry(frame, width=150)
            lbl.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            ent.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
            store["ID to Search"] = (lbl, ent)

            lbl = ctk.CTkLabel(frame, text="Results", font=("Arial", 12))
            ent = ctk.CTkTextbox(frame, width=100, height=200, wrap="word", border_width=1, border_color="black")
            lbl.grid(row=1, column=0, padx=10, pady=5, sticky="w")
            ent.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
            store["Results"] = (lbl, ent)

    def show_panel(self, store, frame, record_type):
        self.build_panel(frame, record_type, store)


# --- Controller: event handlers and service interactions ---
class Controller:
    def __init__(self, view: View, service):
        self.view = view
        self.service = service

        # Keeps track of selected record type per operation
        self.option_types = {
            "Create": "Client",
            "Delete": "Client",
            "Update": "Client",
            "Search": "Client"
        }

        # Wire dropdown traces to update functions
        self.view.create_value.trace_add("write", lambda *a: self.update_create())
        self.view.delete_value.trace_add("write", lambda *a: self.update_delete())
        self.view.update_value.trace_add("write", lambda *a: self.update_update())
        self.view.search_value.trace_add("write", lambda *a: self.update_search())

        # Wire button commands (bind correct store and option at creation)
        for action_key in ("Create", "Delete", "Update", "Search"):
            btn, store = self.view.buttons[action_key]
            # capture loop variables with defaults
            btn.configure(command=lambda t=f"{action_key} Record", k=action_key, s=store: self.prepare_action_data(t, self.option_types[k].lower(), s))

    # Dropdown update handlers
    def update_create(self):
        self.option_types["Create"] = self.view.create_value.get()
        self.view.show_panel(self.view.create_widgets, self.view.create_options_frame, self.option_types["Create"])

    def update_delete(self):
        self.option_types["Delete"] = self.view.delete_value.get()
        self.view.show_panel(self.view.delete_widgets, self.view.delete_options_frame, self.option_types["Delete"])

    def update_update(self):
        self.option_types["Update"] = self.view.update_value.get()
        self.view.show_panel(self.view.update_widgets, self.view.update_options_frame, self.option_types["Update"])

    def update_search(self):
        self.option_types["Search"] = self.view.search_value.get()
        self.view.show_panel(self.view.search_widgets, self.view.search_options_frame, self.option_types["Search"])

    # Payload preparation
    def prepare_payload(self, active_dictionary: dict, text):
        value_dictionary = {}
        if text == "Create Record":
            for label, box in active_dictionary.items():
                key = label_variable_mapping[label]
                if key != "id" and key != "type":
                    value_dictionary[key] = box[1].get()
            return value_dictionary
        elif text == "Delete Record":
            return int(active_dictionary["ID to Delete"][1].get())
        elif text == "Update Record":
            for label, box in active_dictionary.items():
                key = label_variable_mapping[label]
                if key not in ("id", "type") and box[1].get():
                    value_dictionary[key] = box[1].get()
            record_id = int(active_dictionary["ID"][1].get())
            return record_id, value_dictionary
        else:  # Search
            return int(active_dictionary["ID to Search"][1].get())

    # Action handler
    def prepare_action_data(self, text, record_type, store):
        try:
            if text == "Create Record":
                self.service.create_record(record_type, self.prepare_payload(store, text))
                self.service.save()
                self.view.message_label.configure(text="Record created successfully!", text_color="green")
            elif text == "Delete Record":
                self.service.delete_record(record_type, self.prepare_payload(store, text))
                self.service.save()
                self.view.message_label.configure(text="Record deleted successfully!", text_color="green")
            elif text == "Update Record":
                record_id, updates = self.prepare_payload(store, text)
                self.service.update_record(record_type, record_id, updates)
                self.service.save()
                self.view.message_label.configure(text="Record updated successfully!", text_color="green")
            else:  # Search
                textbox_info = self.service.get_record(record_type, self.prepare_payload(store, text))
                store["Results"][1].delete("1.0", "end")
                for key, value in textbox_info.items():
                    if key != "type" and key != "id":
                        store["Results"][1].insert("end", str(f"{variable_label_mapping[key]}: {value}\n"))
                self.view.message_label.configure(text="Search completed successfully!", text_color="green")
        except Exception as e:
            self.view.message_label.configure(text=f"Error: {e}", text_color="red")


# --- Orchestration / Run ---
def run_gui(service=None):
    """
    Instantiate View and Controller. If `service` is None the caller should
    provide one; otherwise the caller can pass a RecordService instance.
    """
    # Delayed import so this module remains import-friendly
    from src.record import JsonRecordRepository, RecordService

    if service is None:
        repository = JsonRecordRepository("src/data/record.json")
        service = RecordService(repository=repository)

    view = View()
    Controller(view, service)
    view.root.mainloop()


# Preserve previous top-level behavior: run GUI when executed as script
if __name__ == "__main__":
    run_gui()