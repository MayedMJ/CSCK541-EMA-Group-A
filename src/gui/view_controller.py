from record import (RecordConflictError, RecordNotFoundError, RecordValidationError)
from main import build_service, close_service
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import sys
print(sys.executable)

service = build_service()


# ---------------------------
# View
# ---------------------------

# Configuration, Text and Data
title = "Airline Records Management System"
root = tk.Tk()
root.title(title)
root.geometry("1200x700")
root.minsize(1200, 700)
root.resizable(False, True)

buttons_frame = ttk.Frame(root)
buttons_frame.grid(row=2, column=0, columnspan=4, sticky="ew")

user_options = ("Create", "Delete", "Update", "Search")

client_box_labels = {
    "Client": [
        "ID",
        "Type",
        "Name",
        "Address Line 1",
        "Address Line 2",
        "Address Line 3",
        "City",
        "State",
        "Zip Code",
        "Country",
        "Phone Number"],
    "Airline": [
        "ID",
        "Type",
        "Company Name"],
    "Flight": [
        "Client ID",
        "Airline ID",
        "Date",
        "Start City",
        "End City"]}

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
    "Company Name": "company_name",
    "Date": "date",
    "Start City": "start_city",
    "End City": "end_city",
    "Client ID": "client_id",
    "Airline ID": "airline_id"
}

variable_label_mapping = {v: k for k, v in label_variable_mapping.items()}

option_types = {
    "Create": "Client",
    "Delete": "Client",
    "Update": "Client",
    "Search": "Client"
}


# Widget state storage
create_widgets = {}
delete_widgets = {}
update_widgets = {}
search_widgets = {}


# Helper functions
def create_dropdown_value():
    return tk.StringVar(root)


def create_dropdown(options, row, column, selected_value):
    cb = ttk.Combobox(
        upper_frame,
        textvariable=selected_value,
        values=options,
        state="readonly",
        width=16)
    cb.grid(row=row, column=column, padx=92, pady=10, sticky="nsew")
    return cb


def change_dropdown_value(selected_value, user_option):
    option_types[user_option] = selected_value.get()


def create_button(text, row, column, size, store, action_key):

    btn = ctk.CTkButton(
        buttons_frame,
        text=text,
        width=size,
        fg_color="navy",
        command=lambda: prepare_action_data(
            text,
            option_types[action_key].lower(),
            store
        )
    )

    btn.grid(row=row, column=column, padx=20, pady=10, sticky="ew")

    return btn


def create_textbox(row, column, frame):
    tb = ctk.CTkTextbox(frame, row=row, column=column)
    return tb


message_label = ctk.CTkLabel(
    buttons_frame,
    text="",
    font=("Arial", 20),
    text_color="green"
)

message_label.grid(row=0, column=0, columnspan=4, pady=5)



# Button Functions

def prepare_payload(active_dictionary: dict, text):

    value_dictionary = {}
    if text == "Create Record":
        for label, box in active_dictionary.items():
            key = label_variable_mapping[label]
            if key != "id" and key != "type":
                value_dictionary[key] = box[1].get()
        print(value_dictionary)
        return value_dictionary
    elif text == "Delete Record":
        return active_dictionary["ID to Delete"][1].get()
    elif text == "Update Record":
        for label, box in active_dictionary.items():
            key = label_variable_mapping[label]
            if key not in ("id", "type") and box[1].get():
                value_dictionary[key] = box[1].get()
        record_id = active_dictionary["ID"][1].get()
        return record_id, value_dictionary
    else:
        filters = {}
        for label, box in active_dictionary.items():
            if label == "Results":
                continue
            key = label_variable_mapping[label]
            value = box[1].get()

            if value:
                filters[key] = value
        print(filters)
        return filters


def prepare_action_data(text, record_type, store):

    try:

        if text == "Create Record":
            service.create_record(record_type, prepare_payload(store, text))
            service.save()

            message_label.configure(
                text="Record created successfully!",
                text_color="green"
            )

        elif text == "Delete Record":
            service.delete_record(record_type, prepare_payload(store, text))
            service.save()

            message_label.configure(
                text="Record deleted successfully!",
                text_color="green"
            )

        elif text == "Update Record":
            record_id, updates = prepare_payload(store, text)

            service.update_record(record_type, record_id, updates)
            service.save()

            message_label.configure(
                text="Record updated successfully!",
                text_color="green"
            )

        else:
            textbox_info = service.search_records(
                record_type,
                **prepare_payload(store, text)
            )
            store["Results"][1].delete("1.0", "end")
            for record in textbox_info:
                for key, value in record.items():
                    if key not in ("type"):
                        store["Results"][1].insert(
                            "end",
                            f"{variable_label_mapping[key]}: {value}\n"
                        )

                store["Results"][1].insert("end", "----------------\n")
            message_label.configure(
                text="Search completed successfully!",
                text_color="green"
            )

    except RecordValidationError as e:

        message_label.configure(
            text=f"Validation Error: {e}",
            text_color="red"
        )
    except RecordConflictError as e:

        message_label.configure(
            text=f"Conflict Error: {e}",
            text_color="red"
        )
    except RecordNotFoundError as e:

        message_label.configure(
            text=f"Not Found Error: {e}",
            text_color="red"
        )


# Panel
def build_panel(frame, record_type, store):
    """
    Create widgets ONCE per panel, based on record type.
    """
    # clear old widgets visually if any exist
    for w in store.values():
        w[0].destroy()
        w[1].destroy()

    store.clear()

    if frame in (create_options_frame, update_options_frame):
        for i, label in enumerate(client_box_labels[record_type][2:] if (frame == create_options_frame and record_type != "Flight")  else [label for label in client_box_labels[record_type] if label != "Type"]):
            lbl = ctk.CTkLabel(frame, text=label, font=("Arial", 12))
            ent = ctk.CTkEntry(frame, width=150)
            lbl.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ent.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            store[label] = (lbl, ent)
    elif frame == delete_options_frame:
        lbl = ctk.CTkLabel(frame, text="ID to Delete", font=("Arial", 12))
        ent = ctk.CTkEntry(frame, width=150)
        lbl.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ent.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        store["ID to Delete"] = (lbl, ent)
    if frame == search_options_frame:
        for i, label in enumerate(
            client_box_labels[record_type][2:]
            if record_type != "Flight"
            else [l for l in client_box_labels[record_type] if l not in ["Type", "Client ID", "Airline ID"]]
        ):
            lbl = ctk.CTkLabel(frame, text=label, font=("Arial", 12))
            ent = ctk.CTkEntry(frame, width=150)

            lbl.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ent.grid(row=i, column=1, padx=10, pady=5, sticky="ew")

            store[label] = (lbl, ent)
        # Add a Results Textbox with border
        lbl = ctk.CTkLabel(frame, text="Results", font=("Arial", 12))
        ent = ctk.CTkTextbox(frame, width=200, height=120, border_width=1, border_color="grey")
        lbl.grid(row=len(client_box_labels[record_type]), column=0, padx=10, pady=5, sticky="w")
        ent.grid(row=len(client_box_labels[record_type]), column=1, padx=10, pady=5, sticky="ew")
        store["Results"] = (lbl, ent)


def show_panel(store, frame, record_type):
    build_panel(frame, record_type, store)


# UI creation helpers
def create_title():
    ctk.CTkLabel(
        upper_frame,
        text=title,
        font=("Arial", 30)
    ).grid(row=0, column=0, columnspan=4, pady=10)


def show_dropdown_labels():
    for i, option in enumerate(user_options):
        ctk.CTkLabel(upper_frame, text=option, font=("Arial", 16)).grid(
            row=1, column=i, padx=10, pady=5
        )


# Equal 4-column layout
for i in range(4):
    root.grid_columnconfigure(i, weight=1, uniform="cols")

root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=0)
root.grid_rowconfigure(2, minsize=80)


# Frames
upper_frame = ttk.Frame(root)
upper_frame.grid(row=0, column=0, columnspan=4, sticky="ew")

create_options_frame = ttk.Frame(root)
delete_options_frame = ttk.Frame(root)
update_options_frame = ttk.Frame(root)
search_options_frame = ttk.Frame(root)
create_options_frame.grid(row=1, column=0, sticky="nsew")
delete_options_frame.grid(row=1, column=1, sticky="nsew")
update_options_frame.grid(row=1, column=2, sticky="nsew")
search_options_frame.grid(row=1, column=3, sticky="nsew")


for i in range(4):
    buttons_frame.grid_columnconfigure(i, weight=1)


for frame in [
        create_options_frame,
        delete_options_frame,
        update_options_frame,
        search_options_frame]:
    frame.grid_columnconfigure(1, weight=1)


# Dropdowns

create_value = create_dropdown_value()
delete_value = create_dropdown_value()
update_value = create_dropdown_value()
search_value = create_dropdown_value()


create_dropdown(("Client", "Airline", "Flight"), 2, 0, create_value)
create_dropdown(("Client", "Airline", "Flight"), 2, 1, delete_value)
create_dropdown(("Client", "Airline", "Flight"), 2, 2, update_value)
create_dropdown(("Client", "Airline", "Flight"), 2, 3, search_value)


# Static UI
create_title()
show_dropdown_labels()

create_button("Create Record", 1, 0, 150, create_widgets, "Create")
create_button("Delete Record", 1, 1, 150, delete_widgets, "Delete")
create_button("Update Record", 1, 2, 150, update_widgets, "Update")
create_button("Search Record", 1, 3, 150, search_widgets, "Search")

# Initial build
show_panel(create_widgets, create_options_frame, "Client")
show_panel(delete_widgets, delete_options_frame, "Client")
show_panel(update_widgets, update_options_frame, "Client")
show_panel(search_widgets, search_options_frame, "Client")

# ---------------------------
# Controller
# ---------------------------

# Dropdown handlers


def update_create():
    change_dropdown_value(create_value, "Create")
    show_panel(create_widgets, create_options_frame, option_types["Create"])
    if option_types["Search"] == "Client":
        root.minsize(1200, 700)
    elif option_types["Create"] == "Client" or option_types ["Update"] == "Client" or option_types ["Search"] == "Client":
        root.minsize(1200, 600)
    else:
        root.minsize(1200, 450)


def update_delete():
    change_dropdown_value(delete_value, "Delete")
    show_panel(delete_widgets, delete_options_frame, option_types["Delete"])


def update_update():
    change_dropdown_value(update_value, "Update")
    show_panel(update_widgets, update_options_frame, option_types["Update"])
    if option_types["Search"] == "Client":
        root.minsize(1200, 700)
    elif option_types["Create"] == "Client" or option_types ["Update"] == "Client" or option_types ["Search"] == "Client":
        root.minsize(1200, 600)
    else:
        root.minsize(1200, 450)


def update_search():
    change_dropdown_value(search_value, "Search")
    show_panel(search_widgets, search_options_frame, option_types["Search"])
    if option_types["Search"] == "Client":
        root.minsize(1200, 700)
    elif option_types["Create"] == "Client" or option_types ["Update"] == "Client" or option_types ["Search"] == "Client":
        root.minsize(1200, 600)
    else:
        root.minsize(1200, 450)


# Event bindings
create_value.trace_add("write", lambda *args: update_create())
delete_value.trace_add("write", lambda *args: update_delete())
update_value.trace_add("write", lambda *args: update_update())
search_value.trace_add("write", lambda *args: update_search())

def on_close():
    close_service()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)


# Run
root.mainloop()
