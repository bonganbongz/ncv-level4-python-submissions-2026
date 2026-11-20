
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import tempfile


class LearnerApp:

    def __init__(self, window):

        self.window = window
        self.window.title("Learner Records Management System")
        self.window.geometry("1050x700")
        self.window.configure(bg="#EAF0F6")

        self.learners = {}

        self.create_menu()

        self.create_gui()

        self.display_learners()

    def create_menu(self):

        menu_bar = tk.Menu(self.window)

        main_menu = tk.Menu(menu_bar, tearoff=0)

        main_menu.add_command(
            label="Add Learner",
            command=self.add_learner
        )

        main_menu.add_command(
            label="Rename Learner",
            command=self.rename_learner
        )

        main_menu.add_command(
            label="Edit Marks",
            command=self.edit_marks
        )

        main_menu.add_command(
            label="Delete Learner",
            command=self.delete_learner
        )

        main_menu.add_command(
            label="Find Learner",
            command=self.find_learner
        )

        main_menu.add_separator()

        main_menu.add_command(
            label="Exit",
            command=self.window.destroy
        )

        menu_bar.add_cascade(
            label="Main",
            menu=main_menu
        )

        printer_menu = tk.Menu(menu_bar, tearoff=0)

        printer_menu.add_command(
            label="Save Mark Sheet",
            command=self.save_marksheet
        )

        printer_menu.add_command(
            label="Print Mark Sheet",
            command=self.print_marksheet
        )

        menu_bar.add_cascade(
            label="Printer",
            menu=printer_menu
        )

        self.window.config(menu=menu_bar)

    def create_gui(self):

        heading = tk.Label(
            self.window,
            text="LEARNER RECORDS MANAGEMENT SYSTEM",
            font=("Arial", 20, "bold"),
            bg="#EAF0F6",
            fg="#17365D"
        )

        heading.pack(pady=15)

        input_frame = tk.LabelFrame(
            self.window,
            text="Learner Information",
            font=("Arial", 12, "bold"),
            bg="#EAF0F6",
            padx=15,
            pady=15
        )

        input_frame.pack(fill="x", padx=25, pady=10)

        tk.Label(
            input_frame,
            text="Learner Name:",
            bg="#EAF0F6"
        ).grid(row=0, column=0, padx=10, pady=8)

        self.name_entry = tk.Entry(
            input_frame,
            width=25,
            font=("Arial", 11)
        )

        self.name_entry.grid(row=0, column=1, padx=10)

        tk.Label(
            input_frame,
            text="Student Number:",
            bg="#EAF0F6"
        ).grid(row=0, column=2, padx=10)

        self.number_entry = tk.Entry(
            input_frame,
            width=20,
            font=("Arial", 11)
        )

        self.number_entry.grid(row=0, column=3, padx=10)

        tk.Label(
            input_frame,
            text="Assessment Marks:",
            bg="#EAF0F6"
        ).grid(row=1, column=0, padx=10, pady=8)

        self.marks_entry = tk.Entry(
            input_frame,
            width=25,
            font=("Arial", 11)
        )

        self.marks_entry.grid(row=1, column=1, padx=10)

        tk.Label(
            input_frame,
            text="Example: 75, 80, 65, 90",
            bg="#EAF0F6",
            fg="#555555"
        ).grid(row=1, column=2, columnspan=2, sticky="w")

        search_frame = tk.Frame(
            self.window,
            bg="#EAF0F6"
        )

        search_frame.pack(fill="x", padx=25, pady=10)

        tk.Label(
            search_frame,
            text="Find Learner:",
            font=("Arial", 11, "bold"),
            bg="#EAF0F6"
        ).pack(side="left", padx=5)

        self.search_entry = tk.Entry(
            search_frame,
            width=30,
            font=("Arial", 11)
        )

        self.search_entry.pack(side="left", padx=5)

        tk.Button(
            search_frame,
            text="FIND",
            command=self.find_learner,
            bg="#17365D",
            fg="white",
            width=12
        ).pack(side="left", padx=5)

        tk.Button(
            search_frame,
            text="SHOW ALL",
            command=self.show_all,
            bg="#6C757D",
            fg="white",
            width=12
        ).pack(side="left", padx=5)

        button_frame = tk.Frame(
            self.window,
            bg="#EAF0F6"
        )

        button_frame.pack(pady=10)

        buttons = [
            ("ADD LEARNER", self.add_learner, "#198754"),
            ("RENAME", self.rename_learner, "#0D6EFD"),
            ("EDIT MARKS", self.edit_marks, "#6F42C1"),
            ("DELETE", self.delete_learner, "#DC3545")
        ]

        for text, command, colour in buttons:

            tk.Button(
                button_frame,
                text=text,
                command=command,
                bg=colour,
                fg="white",
                font=("Arial", 10, "bold"),
                width=15,
                pady=7
            ).pack(side="left", padx=5)

        table_frame = tk.Frame(self.window)

        table_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=15
        )

        columns = (
            "rank",
            "name",
            "number",
            "marks",
            "average"
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12
        )

        self.table.heading("rank", text="RANK")
        self.table.heading("name", text="LEARNER NAME")
        self.table.heading("number", text="STUDENT NUMBER")
        self.table.heading("marks", text="ASSESSMENT MARKS")
        self.table.heading("average", text="AVERAGE (%)")

        self.table.column("rank", width=70, anchor="center")
        self.table.column("name", width=230, anchor="center")
        self.table.column("number", width=160, anchor="center")
        self.table.column("marks", width=300, anchor="center")
        self.table.column("average", width=130, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )

        self.table.configure(
            yscrollcommand=scrollbar.set
        )

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.average_label = tk.Label(
            self.window,
            text="CLASS AVERAGE: 0.00%",
            font=("Arial", 16, "bold"),
            bg="#17365D",
            fg="white",
            pady=15
        )

        self.average_label.pack(fill="x", padx=25, pady=10)

    def get_marks(self):

        text = self.marks_entry.get().strip()

        if not text:
            raise ValueError("Please enter assessment marks.")

        try:
            marks = [float(mark.strip())
                     for mark in text.split(",")]

        except ValueError:
            raise ValueError(
                "Enter marks as numbers separated by commas."
            )

        if not marks:
            raise ValueError("At least one mark is required.")

        if any(mark < 0 or mark > 100 for mark in marks):
            raise ValueError("Marks must be between 0 and 100.")

        return marks

    def add_learner(self):

        name = self.name_entry.get().strip()
        number = self.number_entry.get().strip()

        if not name or not number:
            messagebox.showwarning(
                "Missing Details",
                "Enter the learner name and student number."
            )
            return

        if number in self.learners:
            messagebox.showerror(
                "Duplicate",
                "This student number already exists."
            )
            return

        try:
            marks = self.get_marks()

        except ValueError as error:
            messagebox.showerror("Invalid Marks", str(error))
            return

        self.learners[number] = {
            "name": name,
            "marks": marks
        }

        self.clear_entries()
        self.display_learners()

        messagebox.showinfo(
            "Success",
            "Learner added successfully."
        )


    def rename_learner(self):

        number = self.get_selected_number()

        if number is None:
            return

        new_name = self.name_entry.get().strip()

        if not new_name:
            messagebox.showwarning(
                "Missing Name",
                "Enter the new learner name."
            )
            return

        self.learners[number]["name"] = new_name

        self.clear_entries()
        self.display_learners()

        messagebox.showinfo(
            "Success",
            "Learner name updated successfully."
        )


    def edit_marks(self):

        number = self.get_selected_number()

        if number is None:
            return

        try:
            marks = self.get_marks()

        except ValueError as error:
            messagebox.showerror("Invalid Marks", str(error))
            return

        self.learners[number]["marks"] = marks

        self.clear_entries()
        self.display_learners()

        messagebox.showinfo(
            "Success",
            "Assessment marks updated successfully."
        )


    def delete_learner(self):

        number = self.get_selected_number()

        if number is None:
            return

        confirm = messagebox.askyesno(
            "Delete Learner",
            "Are you sure you want to delete this learner?"
        )

        if confirm:

            del self.learners[number]

            self.clear_entries()
            self.display_learners()

    def get_selected_number(self):

        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a learner from the table."
            )
            return None

        values = self.table.item(selected[0], "values")

        return values[2]

    def find_learner(self):

        search = self.search_entry.get().strip().lower()

        if not search:
            messagebox.showwarning(
                "Search",
                "Enter a learner name or student number."
            )
            return

        self.table.selection_remove(
            self.table.selection()
        )

        found = []

        for item in self.table.get_children():

            values = self.table.item(item, "values")

            name = str(values[1]).lower()
            number = str(values[2]).lower()

            if search in name or search in number:
                found.append(item)

        if found:

            self.table.selection_set(found)
            self.table.focus(found[0])
            self.table.see(found[0])

            messagebox.showinfo(
                "Search Results",
                str(len(found)) + " matching learner(s) found."
            )

        else:

            messagebox.showinfo(
                "Not Found",
                "No matching learner was found."
            )


    def show_all(self):

        self.search_entry.delete(0, tk.END)
        self.display_learners()

    def display_learners(self):

        for item in self.table.get_children():
            self.table.delete(item)

        records = []

        for number, learner in self.learners.items():

            average = sum(learner["marks"]) / len(learner["marks"])

            records.append({
                "number": number,
                "name": learner["name"],
                "marks": learner["marks"],
                "average": average
            })

        records.sort(
            key=lambda learner: learner["average"],
            reverse=True
        )

        total_average = 0
        previous_average = None
        rank = 0

        for position, learner in enumerate(records, start=1):

            average = learner["average"]

            if average != previous_average:
                rank = position

            previous_average = average

            marks_text = ", ".join(
                f"{mark:g}" for mark in learner["marks"]
            )

            self.table.insert(
                "",
                tk.END,
                values=(
                    rank,
                    learner["name"],
                    learner["number"],
                    marks_text,
                    f"{average:.2f}%"
                )
            )

            total_average += average

        if records:
            class_average = total_average / len(records)
        else:
            class_average = 0

        self.average_label.config(
            text=f"CLASS AVERAGE: {class_average:.2f}%"
        )


    def clear_entries(self):

        self.name_entry.delete(0, tk.END)
        self.number_entry.delete(0, tk.END)
        self.marks_entry.delete(0, tk.END)

    def save_marksheet(self):

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Save Learner Mark Sheet"
        )

        if not path:
            return

        content = self.get_marksheet_text()

        with open(path, "w", encoding="utf-8") as file:
            file.write(content)

        messagebox.showinfo(
            "Saved",
            "Mark sheet saved successfully."
        )

    def print_marksheet(self):

        if not self.learners:
            messagebox.showwarning(
                "Empty Mark Sheet",
                "There are no learner records to print."
            )
            return

        content = self.get_marksheet_text()

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".txt",
                delete=False,
                encoding="utf-8"
            ) as file:

                file.write(content)
                path = file.name

            if os.name == "nt":
                os.startfile(path, "print")

                messagebox.showinfo(
                    "Printing",
                    "The mark sheet has been sent to the printer."
                )

            else:
                messagebox.showinfo(
                    "Print",
                    "Printing is configured for Windows. "
                    "Please save the mark sheet and print it manually."
                )

        except Exception as error:

            messagebox.showerror(
                "Printing Error",
                str(error)
            )

    def get_marksheet_text(self):

        records = []

        for number, learner in self.learners.items():

            average = sum(learner["marks"]) / len(learner["marks"])

            records.append({
                "number": number,
                "name": learner["name"],
                "marks": learner["marks"],
                "average": average
            })

        records.sort(
            key=lambda learner: learner["average"],
            reverse=True
        )

        lines = []

        lines.append("STUDENT LEARNER MARK SHEET")
        lines.append("=" * 95)
        lines.append(
            f"{'RANK':<8}{'LEARNER NAME':<25}"
            f"{'STUDENT NUMBER':<20}{'MARKS':<25}{'AVERAGE':>12}"
        )
        lines.append("-" * 95)

        total = 0
        previous_average = None
        rank = 0

        for position, learner in enumerate(records, start=1):

            average = learner["average"]

            if average != previous_average:
                rank = position

            previous_average = average

            marks = ", ".join(
                f"{mark:g}" for mark in learner["marks"]
            )

            lines.append(
                f"{rank:<8}{learner['name']:<25}"
                f"{learner['number']:<20}"
                f"{marks:<25}{average:>11.2f}%"
            )

            total += average

        class_average = total / len(records) if records else 0

        lines.append("-" * 95)
        lines.append(
            f"NUMBER OF LEARNERS: {len(records)}"
        )
        lines.append(
            f"CLASS AVERAGE: {class_average:.2f}%"
        )

        return "\n".join(lines)

def main():

    window = tk.Tk()

    application = LearnerApp(window)

    window.mainloop()


main()
