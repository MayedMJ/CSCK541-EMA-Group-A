import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import sys
print(sys.executable)
from src.record import JsonRecordRepository, RecordService


repository = JsonRecordRepository("src/data/record.json")
service = RecordService(repository=repository)


# ---------------------------
# View
# ---------------------------

# Configuration, Text and Data
title = "Airline Records Management System"
root = tk.Tk()
root.title(title)
root.geometry("1200x660")
root.resizable(False, False)

buttons_frame = ttk.Frame(root)
buttons_frame.grid(row=2, column=0, columnspan=4, sticky="ew")

user_options = ("Create", "Delete", "Update", "Search")

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
    cb = ttk.Combobox(upper_frame, textvariable=selected_value, values=options, state="readonly", width = 16)
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
        return int(active_dictionary["ID to Delete"][1].get())
    elif text == "Update Record":
        for label, box in active_dictionary.items():
            key = label_variable_mapping[label]
            if key not in ("id", "type") and box[1].get():
                value_dictionary[key] = box[1].get()
        record_id = int(active_dictionary["ID"][1].get())
        return record_id, value_dictionary
    else:
        return int(active_dictionary["ID to Search"][1].get())
    
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
            textbox_info = service.get_record(
                record_type,
                prepare_payload(store, text)
            )

            store["Results"][1].delete("1.0", "end")
            store["Results"][1].insert("1.0", str(textbox_info))

            message_label.configure(
                text="Search completed successfully!",
                text_color="green"
            )

    except Exception as e:

        message_label.configure(
            text=f"Error: {e}",
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
        for i, label in enumerate(client_box_labels[record_type]):
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
    elif frame == search_options_frame:
        lbl = ctk.CTkLabel(frame, text="ID to Search", font=("Arial", 12))
        ent = ctk.CTkEntry(frame, width=150)
        lbl.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ent.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        store["ID to Search"] = (lbl, ent)

        lbl = ctk.CTkLabel(frame, text="Results", font=("Arial", 12))
        ent = ctk.CTkTextbox(frame, width = 100, height = 300, wrap = "word", border_width = 1, border_color = "black")
        lbl.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ent.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
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


for frame in [create_options_frame, delete_options_frame, update_options_frame, search_options_frame]:
    frame.grid_columnconfigure(1, weight=1)


# Dropdowns

create_value = create_dropdown_value()
delete_value = create_dropdown_value()
update_value = create_dropdown_value()
search_value = create_dropdown_value()



create_dropdown(("Client", "Airline", "Flight Record"), 2, 0, create_value)
create_dropdown(("Client", "Airline", "Flight Record"), 2, 1, delete_value)
create_dropdown(("Client", "Airline", "Flight Record"), 2, 2, update_value)
create_dropdown(("Client", "Airline", "Flight Record"), 2, 3, search_value)


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


def update_delete():
    change_dropdown_value(delete_value, "Delete")
    show_panel(delete_widgets, delete_options_frame, option_types["Delete"])


def update_update():
    change_dropdown_value(update_value, "Update")
    show_panel(update_widgets, update_options_frame, option_types["Update"])

def update_search():
    change_dropdown_value(search_value, "Search")
    show_panel(search_widgets, search_options_frame, option_types["Search"])


# Event bindings
create_value.trace_add("write", lambda *args: update_create())
delete_value.trace_add("write", lambda *args: update_delete())
update_value.trace_add("write", lambda *args: update_update())
search_value.trace_add("write", lambda *args: update_search())

# Run
root.mainloop()