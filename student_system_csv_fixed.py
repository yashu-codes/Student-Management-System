import sys
import csv
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path

# ==========================================================
# 1. PASSWORD AUTHENTICATION DIALOG
# ==========================================================
def check_password():
    # Hidden root window so only the password prompt appears initially
    login_root = tk.Tk()
    login_root.withdraw()

    # Prompt user for password with masked characters
    entered_password = simpledialog.askstring(
        "Authentication Required",
        "Enter Password to Access System:",
        show="*"
    )

    if entered_password == "yashu1016":
        login_root.destroy()
        return True
    else:
        if entered_password is not None:
            messagebox.showerror("Access Denied", "Incorrect Password!")
        login_root.destroy()
        return False

# Trigger password check before running application
if not check_password():
    sys.exit()

# ==========================================================
# 2. PYTHON + CSV STUDENT MANAGEMENT SYSTEM
# ==========================================================

# ----------------------------------------------------------
# CSV SETTINGS (SAVED TO USER DOCUMENTS TO PREVENT PERMISSION BLOCKS)
# ----------------------------------------------------------
CSV_FILE = "student_manage.csv"

def get_app_folder():
    # Keep the CSV beside the Python file or EXE.
    # This makes it easy to see, test, and share the data file.
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

CSV_PATH = get_app_folder() / CSV_FILE

# ----------------------------------------------------------
# COLOR PALETTE
# ----------------------------------------------------------
COLOR_BG = "#EAF0F6"
COLOR_HEADER = "#EAF0F6"
COLOR_HEADER_TEXT = "#1B2A4A"
COLOR_CARD = "#F5F8FB"
COLOR_TEXT = "#4A4A4A"
COLOR_MUTED = "#6b7280"
COLOR_BORDER = "#B0BEC5"
COLOR_ENTRY_BG = "#FFFFFF"
COLOR_ADD = "#2563EB"
COLOR_ADD_HOVER = "#1D4ED8"
COLOR_VIEW = "#3B82F6"
COLOR_VIEW_HOVER = "#2563EB"
COLOR_UPDATE = "#5B7FA6"
COLOR_UPDATE_HOVER = "#456186"
COLOR_DELETE = "#B0413E"
COLOR_DELETE_HOVER = "#8F3230"
COLOR_CLEAR = "#C3D3E2"
COLOR_CLEAR_HOVER = "#AEC2D6"
COLOR_SEARCH = "#3B5998"
COLOR_SEARCH_HOVER = "#2C4373"
COLOR_MESSAGE = "#1B5E20"
COLOR_ROW_EVEN = "#FFFFFF"
COLOR_ROW_ODD = "#EAF0F6"
COLOR_ROW_SELECTED = "#BBD3EE"

HEADERS = ["ID", "Student Name", "Phone", "Course", "Fee"]

# ----------------------------------------------------------
# CSV FUNCTIONS
# ----------------------------------------------------------
def create_csv_file():
    """Create the CSV file with a header row if it does not exist."""
    try:
        if not CSV_PATH.exists():
            with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(HEADERS)
        return True
    except Exception as error:
        messagebox.showerror(
            "CSV Error",
            "Unable to create/open the CSV file.\n\n" + str(error)
        )
        return False

def load_records():
    """Return student records as [id, name, phone, course, fee]."""
    try:
        records = []

        with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header row

            for row in reader:
                if not row or all(value.strip() == "" for value in row):
                    continue

                if len(row) < 5:
                    continue

                try:
                    student_id = int(row[0])
                except (TypeError, ValueError):
                    continue

                name = row[1]
                phone = row[2]
                course = row[3]

                try:
                    fee = float(row[4]) if row[4] != "" else 0.0
                except (TypeError, ValueError):
                    fee = 0.0

                records.append([student_id, name, phone, course, fee])

        records.sort(key=lambda x: x[0])
        return records

    except FileNotFoundError:
        return []
    except Exception as error:
        messagebox.showerror(
            "CSV Error",
            "Unable to read the CSV file.\n\n" + str(error)
        )
        return []

def save_records(records):
    """Replace the CSV file contents with the supplied records."""
    try:
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)

            for student in records:
                writer.writerow([
                    student[0],
                    student[1],
                    student[2],
                    student[3],
                    f"{float(student[4]):.2f}"
                ])

        return True

    except Exception as error:
        messagebox.showerror(
            "CSV Error",
            "Unable to save the CSV file.\n\n" + str(error)
        )
        return False

def get_next_id(records):
    if not records:
        return 1
    return max(student[0] for student in records) + 1

# ----------------------------------------------------------
# GUI FUNCTIONS
# ----------------------------------------------------------
def clear_fields():
    entry_name.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    entry_course.delete(0, tk.END)
    entry_fee.delete(0, tk.END)
    entry_search.delete(0, tk.END)
    tree.selection_remove(tree.selection())

def populate_tree(records, label_text="Total Students"):
    for item in tree.get_children():
        tree.delete(item)

    for index, student in enumerate(records):
        row_tag = "even" if index % 2 == 0 else "odd"
        tree.insert(
            "",
            tk.END,
            values=(
                student[0],
                student[1],
                student[2],
                student[3],
                f"{float(student[4]):.2f}"
            ),
            tags=(row_tag,)
        )

    total_label.config(text=f"{label_text}: {len(records)}")

def add_student():
    name = entry_name.get().strip()
    phone = entry_phone.get().strip()
    course = entry_course.get().strip()
    fee_text = entry_fee.get().strip()

    if name == "" or phone == "" or course == "" or fee_text == "":
        messagebox.showwarning(
            "Input Error",
            "Please enter all student details."
        )
        return

    try:
        fee = float(fee_text)
    except ValueError:
        messagebox.showwarning(
            "Input Error",
            "Fee must be a number."
        )
        return

    records = load_records()
    new_student = [
        get_next_id(records),
        name,
        phone,
        course,
        fee
    ]
    records.append(new_student)

    if save_records(records):
        messagebox.showinfo(
            "Success",
            "Student added successfully!"
        )
        clear_fields()
        view_students()

def view_students():
    records = load_records()
    populate_tree(records, "Total Students")

def search_student():
    search_text = entry_search.get().strip().lower()

    if search_text == "":
        view_students()
        return

    records = load_records()
    filtered = []

    for student in records:
        if (
            search_text in str(student[1]).lower()
            or search_text in str(student[2]).lower()
            or search_text in str(student[3]).lower()
        ):
            filtered.append(student)

    populate_tree(filtered, "Search Results")

def select_student(event):
    selected = tree.focus()

    if selected == "":
        return

    values = tree.item(selected, "values")

    if not values:
        return

    entry_name.delete(0, tk.END)
    entry_name.insert(0, values[1])

    entry_phone.delete(0, tk.END)
    entry_phone.insert(0, values[2])

    entry_course.delete(0, tk.END)
    entry_course.insert(0, values[3])

    entry_fee.delete(0, tk.END)
    entry_fee.insert(0, values[4])

def update_student():
    selected = tree.focus()

    if selected == "":
        messagebox.showwarning(
            "Update",
            "Please select a student from the table."
        )
        return

    values = tree.item(selected, "values")
    student_id = int(values[0])

    name = entry_name.get().strip()
    phone = entry_phone.get().strip()
    course = entry_course.get().strip()
    fee_text = entry_fee.get().strip()

    if name == "" or phone == "" or course == "" or fee_text == "":
        messagebox.showwarning(
            "Input Error",
            "Please enter all student details."
        )
        return

    try:
        fee = float(fee_text)
    except ValueError:
        messagebox.showwarning(
            "Input Error",
            "Fee must be a number."
        )
        return

    records = load_records()

    for student in records:
        if student[0] == student_id:
            student[1] = name
            student[2] = phone
            student[3] = course
            student[4] = fee
            break

    if save_records(records):
        messagebox.showinfo(
            "Success",
            "Student updated successfully!"
        )
        clear_fields()
        view_students()

def delete_student():
    selected = tree.focus()

    if selected == "":
        messagebox.showwarning(
            "Delete",
            "Please select a student from the table."
        )
        return

    values = tree.item(selected, "values")
    student_id = int(values[0])
    student_name = values[1]

    answer = messagebox.askyesno(
        "Confirm Delete",
        f"Do you want to delete {student_name}?"
    )

    if not answer:
        return

    records = load_records()
    records = [student for student in records if student[0] != student_id]

    if save_records(records):
        messagebox.showinfo(
            "Success",
            "Student deleted successfully!"
        )
        clear_fields()
        view_students()

# ----------------------------------------------------------
# HOVER-COLOR BUTTON HELPER
# ----------------------------------------------------------
def make_button(
    parent,
    text,
    base_color,
    hover_color,
    command,
    width=15,
    text_color="#ffffff"
):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        font=("Segoe UI", 10, "bold"),
        bg=base_color,
        fg=text_color,
        activebackground=hover_color,
        activeforeground=text_color,
        relief="solid",
        bd=1,
        highlightbackground=COLOR_BORDER,
        highlightthickness=1,
        padx=6,
        pady=8,
        cursor="hand2"
    )

    btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
    btn.bind("<Leave>", lambda e: btn.config(bg=base_color))

    return btn

# ==========================================================
# START GUI
# ==========================================================
if not create_csv_file():
    sys.exit()

# ----------------------------------------------------------
# MAIN WINDOW
# ----------------------------------------------------------
root = tk.Tk()
root.title("Yashu Student Management System")
root.geometry("1000x720")
root.resizable(True, True)
root.configure(bg=COLOR_BG)

# ----------------------------------------------------------
# TTK STYLING
# ----------------------------------------------------------
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background=COLOR_ROW_EVEN,
    fieldbackground=COLOR_ROW_EVEN,
    foreground=COLOR_TEXT,
    rowheight=30,
    font=("Segoe UI", 10, "bold"),
    borderwidth=1,
    relief="solid"
)

style.configure(
    "Treeview.Heading",
    background=COLOR_HEADER,
    foreground=COLOR_HEADER_TEXT,
    font=("Segoe UI", 10, "bold"),
    relief="solid",
    borderwidth=1,
    padding=8
)

style.map(
    "Treeview.Heading",
    background=[("active", COLOR_HEADER)]
)

style.map(
    "Treeview",
    background=[("selected", COLOR_ROW_SELECTED)],
    foreground=[("selected", COLOR_TEXT)]
)

# ----------------------------------------------------------
# HEADER BAR
# ----------------------------------------------------------
header_frame = tk.Frame(
    root,
    bg=COLOR_HEADER,
    height=80,
    highlightbackground=COLOR_BORDER,
    highlightthickness=2
)
header_frame.pack(fill="x", side="top")
header_frame.pack_propagate(False)

title_label = tk.Label(
    header_frame,
    text="STUDENT MANAGEMENT SYSTEM",
    font=("Segoe UI", 22, "bold"),
    bg=COLOR_HEADER,
    fg=COLOR_HEADER_TEXT
)
title_label.pack(expand=True)

# ----------------------------------------------------------
# BODY CONTAINER
# ----------------------------------------------------------
body_frame = tk.Frame(root, bg=COLOR_BG)
body_frame.pack(fill="both", expand=True, padx=20, pady=15)

# ----------------------------------------------------------
# INPUT CARD
# ----------------------------------------------------------
input_card = tk.Frame(
    body_frame,
    bg=COLOR_CARD,
    highlightbackground=COLOR_BORDER,
    highlightthickness=1
)
input_card.pack(fill="x", pady=(0, 15))

input_frame = tk.Frame(input_card, bg=COLOR_CARD)
input_frame.pack(padx=20, pady=18)

def make_field_label(text, row, col):
    tk.Label(
        input_frame,
        text=text,
        font=("Segoe UI", 11, "bold"),
        bg=COLOR_CARD,
        fg=COLOR_TEXT
    ).grid(row=row, column=col, padx=(0, 10), pady=8, sticky="e")

def make_entry(row, col):
    e = tk.Entry(
        input_frame,
        width=32,
        font=("Segoe UI", 11, "bold"),
        bg=COLOR_ENTRY_BG,
        fg=COLOR_TEXT,
        relief="solid",
        highlightthickness=1,
        highlightbackground=COLOR_BORDER,
        highlightcolor=COLOR_BORDER,
        insertbackground=COLOR_TEXT
    )
    e.grid(row=row, column=col, padx=(0, 30), pady=8, ipady=4)
    return e

make_field_label("Student Name:", 0, 0)
entry_name = make_entry(0, 1)

make_field_label("Course:", 0, 2)
entry_course = make_entry(0, 3)

make_field_label("Phone Number:", 1, 0)
entry_phone = make_entry(1, 1)

make_field_label("Fee:", 1, 2)
entry_fee = make_entry(1, 3)

# ----------------------------------------------------------
# BUTTON BAR
# ----------------------------------------------------------
button_frame = tk.Frame(body_frame, bg=COLOR_BG)
button_frame.pack(pady=(0, 15))

make_button(
    button_frame,
    "ADD STUDENT",
    COLOR_ADD,
    COLOR_ADD_HOVER,
    add_student,
    text_color="#ffffff"
).grid(row=0, column=0, padx=6)

make_button(
    button_frame,
    "VIEW STUDENTS",
    COLOR_VIEW,
    COLOR_VIEW_HOVER,
    view_students,
    text_color="#ffffff"
).grid(row=0, column=1, padx=6)

make_button(
    button_frame,
    "UPDATE STUDENT",
    COLOR_UPDATE,
    COLOR_UPDATE_HOVER,
    update_student,
    width=17,
    text_color="#ffffff"
).grid(row=0, column=2, padx=6)

make_button(
    button_frame,
    "DELETE STUDENT",
    COLOR_DELETE,
    COLOR_DELETE_HOVER,
    delete_student,
    width=17,
    text_color="#ffffff"
).grid(row=0, column=3, padx=6)

make_button(
    button_frame,
    "CLEAR",
    COLOR_CLEAR,
    COLOR_CLEAR_HOVER,
    clear_fields,
    width=12,
    text_color="#333333"
).grid(row=0, column=4, padx=6)

# ----------------------------------------------------------
# SEARCH BAR
# ----------------------------------------------------------
search_card = tk.Frame(
    body_frame,
    bg=COLOR_CARD,
    highlightbackground=COLOR_BORDER,
    highlightthickness=1
)
search_card.pack(fill="x", pady=(0, 15))

search_frame = tk.Frame(search_card, bg=COLOR_CARD)
search_frame.pack(padx=20, pady=12)

tk.Label(
    search_frame,
    text="Search Student:",
    font=("Segoe UI", 11, "bold"),
    bg=COLOR_CARD,
    fg=COLOR_TEXT
).grid(row=0, column=0, padx=(0, 10))

entry_search = tk.Entry(
    search_frame,
    width=40,
    font=("Segoe UI", 11, "bold"),
    bg=COLOR_ENTRY_BG,
    fg=COLOR_TEXT,
    relief="solid",
    highlightthickness=1,
    highlightbackground=COLOR_BORDER,
    highlightcolor=COLOR_BORDER,
    insertbackground=COLOR_TEXT
)
entry_search.grid(row=0, column=1, padx=10, ipady=4)

make_button(
    search_frame,
    "SEARCH",
    COLOR_SEARCH,
    COLOR_SEARCH_HOVER,
    search_student,
    width=12,
    text_color="#ffffff"
).grid(row=0, column=2, padx=10)

# ----------------------------------------------------------
# TOTAL STUDENTS LABEL
# ----------------------------------------------------------
total_label = tk.Label(
    body_frame,
    text="Total Students: 0",
    font=("Segoe UI", 12, "bold"),
    bg=COLOR_BG,
    fg=COLOR_TEXT
)
total_label.pack(pady=(0, 8), anchor="w")

# ----------------------------------------------------------
# TABLE CARD
# ----------------------------------------------------------
table_card = tk.Frame(
    body_frame,
    bg=COLOR_CARD,
    highlightbackground=COLOR_BORDER,
    highlightthickness=1
)
table_card.pack(fill="both", expand=True)

table_frame = tk.Frame(table_card, bg=COLOR_CARD)
table_frame.pack(fill="both", expand=True, padx=10, pady=10)

# ----------------------------------------------------------
# TREEVIEW
# ----------------------------------------------------------
columns = (
    "ID",
    "Student Name",
    "Phone",
    "Course",
    "Fee"
)

tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=12
)

tree.heading("ID", text="ID")
tree.heading("Student Name", text="Student Name")
tree.heading("Phone", text="Phone")
tree.heading("Course", text="Course")
tree.heading("Fee", text="Fee")

tree.column("ID", width=60, anchor="center")
tree.column("Student Name", width=220)
tree.column("Phone", width=160)
tree.column("Course", width=180)
tree.column("Fee", width=120, anchor="e")

tree.tag_configure("even", background=COLOR_ROW_EVEN)
tree.tag_configure("odd", background=COLOR_ROW_ODD)

# ----------------------------------------------------------
# SCROLLBAR
# ----------------------------------------------------------
scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=tree.yview
)

tree.configure(yscrollcommand=scrollbar.set)

tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# ----------------------------------------------------------
# SELECT RECORD
# ----------------------------------------------------------
tree.bind("<ButtonRelease-1>", select_student)

# ----------------------------------------------------------
# STATUS BAR
# ----------------------------------------------------------
status_bar = tk.Frame(
    root,
    bg=COLOR_HEADER,
    height=30,
    highlightbackground=COLOR_BORDER,
    highlightthickness=2
)
status_bar.pack(fill="x", side="bottom")
status_bar.pack_propagate(False)

status_label = tk.Label(
    status_bar,
    text="●  Connected to CSV (Saved beside application)",
    font=("Segoe UI", 9, "bold"),
    bg=COLOR_HEADER,
    fg=COLOR_MESSAGE
)
status_label.pack(pady=5)

# ----------------------------------------------------------
# LOAD RECORDS & START MAIN LOOP
# ----------------------------------------------------------
view_students()
root.mainloop()