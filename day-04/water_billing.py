import os
import sys

INPUT_FILE = "water_readings.txt"
REPORT_FILE = "billing_report.txt"
ERROR_FILE = "errors.log"

FREE_LIMIT = 6          
BAND2_LIMIT = 20        
RATE_BAND2 = 8.50       
RATE_BAND3 = 12.00      

LOW_LIMIT = 20          
MODERATE_LIMIT = 50     

EXPECTED_FIELDS = 5

def read_file_lines(filename):
    """Return (lines, error_message). Handles a missing/unreadable file."""
    try:
        file = open(filename, "r", encoding="utf-8")
        lines = file.readlines()
        file.close()
        return lines, ""
    except FileNotFoundError:
        return [], "File '" + filename + "' was not found. " \
                   "Place it in the same folder as this program."
    except OSError as problem:
        return [], "Could not read '" + filename + "': " + str(problem)

def clean_fields(line):
    """Split a line on commas and strip whitespace from every field."""
    raw_parts = line.strip().split(",")
    cleaned = []
    for part in raw_parts:
        cleaned.append(part.strip())
    return cleaned


def to_whole_number(text):
    """Convert text to int. Return None if it is not a valid whole number."""
    try:
        return int(text)
    except ValueError:
        return None


def validate_record(fields, accepted):
    """
    Check one record. Returns "" if valid, otherwise the rejection reason.
    'accepted' is the dictionary of valid records so far (duplicate check).
    """

    if len(fields) != EXPECTED_FIELDS:
        return "Wrong number of fields (expected 5, found " + str(len(fields)) + ")"

    meter, name, prev_text, curr_text, area = fields

    if meter == "":
        return "Missing meter number"
    if name == "":
        return "Missing household name"
    if prev_text == "":
        return "Missing previous reading"
    if curr_text == "":
        return "Missing current reading"
    if area == "":
        return "Missing area"

    if meter in accepted:
        return "Duplicate meter number " + meter

    previous = to_whole_number(prev_text)
    current = to_whole_number(curr_text)
    if previous is None:
        return "Non-numeric previous reading '" + prev_text + "'"
    if current is None:
        return "Non-numeric current reading '" + curr_text + "'"

    if previous < 0:
        return "Negative previous reading (" + str(previous) + ")"
    if current < 0:
        return "Negative current reading (" + str(current) + ")"

    if current < previous:
        return "Current reading (" + str(current) + \
               ") is below previous reading (" + str(previous) + ")"

    return ""


def build_records(lines):
    """
    Process every line. Returns (accepted_dict, rejected_list).
    rejected_list items are dictionaries: line number, raw text, reason.
    """
    accepted = {}
    rejected = []
    line_number = 0

    for line in lines:
        line_number = line_number + 1
        if line.strip() == "":                 
            continue

        fields = clean_fields(line)
        reason = validate_record(fields, accepted)

        if reason != "":
            rejected.append({"line": line_number,
                             "raw": line.strip(),
                             "reason": reason})
        else:
            meter, name, prev_text, curr_text, area = fields
            accepted[meter] = {"name": name,
                               "previous": int(prev_text),
                               "current": int(curr_text),
                               "area": area}
    return accepted, rejected

def calculate_consumption(previous, current):
    """Q4: monthly consumption in kL."""
    return current - previous


def calculate_bill(kl):
    """Q5: progressive tariff - free / R8.50 / R12.00 bands."""
    if kl <= FREE_LIMIT:
        charge = 0.0
    elif kl <= BAND2_LIMIT:
        charge = (kl - FREE_LIMIT) * RATE_BAND2
    else:
        charge = (BAND2_LIMIT - FREE_LIMIT) * RATE_BAND2 \
                 + (kl - BAND2_LIMIT) * RATE_BAND3
    return charge


def classify_consumption(kl):
    """Q6: LOW / MODERATE / HIGH."""
    if kl <= LOW_LIMIT:
        return "LOW"
    elif kl <= MODERATE_LIMIT:
        return "MODERATE"
    else:
        return "HIGH"


def add_billing_details(accepted):
    """Add consumption, charge and category to every accepted record."""
    for meter in accepted:
        rec = accepted[meter]
        rec["kl"] = calculate_consumption(rec["previous"], rec["current"])
        rec["charge"] = calculate_bill(rec["kl"])
        rec["category"] = classify_consumption(rec["kl"])

def top_five_consumers(accepted):
    """
    Keep a list of the five highest consumers, highest first.
    Each household is compared against the list using loops only.
    Ties keep the household that appeared first in the file.
    """
    top = []   

    for meter in accepted:
        kl = accepted[meter]["kl"]


        position = len(top)
        index = 0
        while index < len(top):
            if kl > top[index][1]:
                position = index
                break
            index = index + 1


        if position < 5:
            top.append(None)                      
            shift = len(top) - 1
            while shift > position:               
                top[shift] = top[shift - 1]
                shift = shift - 1
            top[position] = (meter, kl)
            if len(top) > 5:
                top.pop()                        
    return top

def calculate_summary(accepted, rejected):
    """Totals calculated with loops. Returns a dictionary."""
    s = {"accepted": 0, "rejected": len(rejected), "total_kl": 0,
         "total_revenue": 0.0, "LOW": 0, "MODERATE": 0, "HIGH": 0,
         "average_kl": 0.0, "areas": {}}

    for meter in accepted:
        rec = accepted[meter]
        s["accepted"] += 1
        s["total_kl"] += rec["kl"]
        s["total_revenue"] += rec["charge"]
        s[rec["category"]] += 1

        area = rec["area"]
        if area not in s["areas"]:
            s["areas"][area] = {"count": 0, "kl": 0, "revenue": 0.0}
        s["areas"][area]["count"] += 1
        s["areas"][area]["kl"] += rec["kl"]
        s["areas"][area]["revenue"] += rec["charge"]

    if s["accepted"] > 0:
        s["average_kl"] = s["total_kl"] / s["accepted"]
    return s


def write_billing_report(accepted, top, summary, filename=REPORT_FILE):
    """Write billing_report.txt."""
    line = "=" * 98
    out = open(filename, "w", encoding="utf-8")

    out.write(line + "\n")
    out.write("COMMUNITY WATER CONSUMPTION AND BILLING REPORT\n")
    out.write(line + "\n\n")

    out.write("SECTION 1: HOUSEHOLD BILLING DETAILS\n")
    out.write("-" * 98 + "\n")
    out.write("%-7s %-18s %-15s %8s %8s %8s %12s  %s\n" %
              ("Meter", "Household", "Area", "Prev", "Curr", "kL", "Bill (R)", "Category"))
    out.write("-" * 98 + "\n")
    for meter in accepted:
        r = accepted[meter]
        out.write("%-7s %-18s %-15s %8d %8d %8d %12.2f  %s\n" %
                  (meter, r["name"], r["area"], r["previous"], r["current"],
                   r["kl"], r["charge"], r["category"]))

    out.write("\n" + "SECTION 2: TOP 5 HIGHEST-CONSUMING HOUSEHOLDS\n")
    out.write("-" * 98 + "\n")
    out.write("%-5s %-7s %-18s %-15s %8s %12s\n" %
              ("Rank", "Meter", "Household", "Area", "kL", "Bill (R)"))
    rank = 1
    for meter, kl in top:
        r = accepted[meter]
        out.write("%-5d %-7s %-18s %-15s %8d %12.2f\n" %
                  (rank, meter, r["name"], r["area"], kl, r["charge"]))
        rank += 1

    out.write("\n" + "SECTION 3: SUMMARY\n")
    out.write("-" * 98 + "\n")
    out.write("Records accepted        : %d\n" % summary["accepted"])
    out.write("Records rejected        : %d\n" % summary["rejected"])
    out.write("Total consumption       : %d kL\n" % summary["total_kl"])
    out.write("Average consumption     : %.2f kL per household\n" % summary["average_kl"])
    out.write("Total billed revenue    : R%.2f\n" % summary["total_revenue"])
    out.write("LOW households          : %d\n" % summary["LOW"])
    out.write("MODERATE households     : %d\n" % summary["MODERATE"])
    out.write("HIGH households         : %d\n\n" % summary["HIGH"])
    out.write("%-16s %10s %12s %14s\n" % ("Area", "Households", "kL", "Revenue (R)"))
    for area in summary["areas"]:
        a = summary["areas"][area]
        out.write("%-16s %10d %12d %14.2f\n" % (area, a["count"], a["kl"], a["revenue"]))
    out.write(line + "\n")
    out.close()


def write_error_log(rejected, filename=ERROR_FILE):
    """Write errors.log - one entry per rejected record with its reason."""
    out = open(filename, "w", encoding="utf-8")
    out.write("REJECTED RECORDS LOG\n" + "=" * 70 + "\n")
    for item in rejected:
        out.write("Line %d | %s\n    Reason: %s\n" %
                  (item["line"], item["raw"], item["reason"]))
    out.write("=" * 70 + "\nTotal rejected: %d\n" % len(rejected))
    out.close()

def run_pipeline(filename, folder):
    """
    Full workflow. Returns a result dictionary (or one with an 'error' key).
    Output files are written into 'folder'.
    """
    lines, problem = read_file_lines(filename)
    if problem != "":
        return {"error": problem}

    accepted, rejected = build_records(lines)
    add_billing_details(accepted)
    top = top_five_consumers(accepted)
    summary = calculate_summary(accepted, rejected)

    report_path = os.path.join(folder, REPORT_FILE)
    error_path = os.path.join(folder, ERROR_FILE)
    write_billing_report(accepted, top, summary, report_path)
    write_error_log(rejected, error_path)

    return {"error": "", "lines": len(lines), "accepted": accepted,
            "rejected": rejected, "top": top, "summary": summary,
            "report_path": report_path, "error_path": error_path}


def run_console_version():
    """Plain text mode:  python water_billing.py --cli"""
    folder = os.path.dirname(os.path.abspath(__file__))
    result = run_pipeline(os.path.join(folder, INPUT_FILE), folder)
    if result["error"] != "":
        print("ERROR:", result["error"])
        return
    print("Lines read      :", result["lines"])
    print("Records accepted:", result["summary"]["accepted"])
    print("Records rejected:", result["summary"]["rejected"])
    print("Top 5 consumers :")
    rank = 1
    for meter, kl in result["top"]:
        print("  %d. %s %-18s %d kL" % (rank, meter, result["accepted"][meter]["name"], kl))
        rank += 1
    print("Created:", REPORT_FILE, "and", ERROR_FILE)

def launch_gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    SIDEBAR_BG = "#111827"
    SIDEBAR_HOVER = "#1f2937"
    SIDEBAR_ACTIVE = "#0ea5e9"
    CANVAS_BG = "#f3f4f6"
    CARD_BG = "#ffffff"
    BORDER = "#e5e7eb"
    TEXT_PRIMARY = "#111827"
    TEXT_SECONDARY = "#6b7280"

    EMERALD = "#059669"
    SKY = "#0284c7"
    AMBER = "#d97706"
    ROSE = "#e11d48"

    ROW_BG = {"LOW": "#ecfdf5", "MODERATE": "#fffbeb", "HIGH": "#fff1f2"}

    class WaterBillingDashboard:
        def __init__(self, root):
            self.root = root
            self.folder = os.path.dirname(os.path.abspath(__file__))
            self.file_path = os.path.join(self.folder, INPUT_FILE)
            self.result = None
            self.active_page = "billing"
            self.nav_buttons = {}

            self.root.title("Municipal Water Billing Portal")
            self.root.geometry("1240x780")
            self.root.minsize(1040, 660)
            self.root.configure(bg=CANVAS_BG)

            self.configure_styles()
            self.build_layout()
            self.switch_page("billing")
            self.run_processing()

        def configure_styles(self):
            style = ttk.Style()
            try:
                style.theme_use("clam")
            except tk.TclError:
                pass

            style.configure(
                "Custom.Treeview",
                rowheight=28,
                font=("Segoe UI", 10),
                background=CARD_BG,
                fieldbackground=CARD_BG,
                foreground=TEXT_PRIMARY,
                borderwidth=0,
            )
            style.configure(
                "Custom.Treeview.Heading",
                font=("Segoe UI", 10, "bold"),
                background="#f8fafc",
                foreground=TEXT_PRIMARY,
                relief="flat",
                padding=(8, 6),
            )
            style.map("Custom.Treeview.Heading", background=[("active", "#e2e8f0")])
            style.map(
                "Custom.Treeview",
                background=[("selected", SKY)],
                foreground=[("selected", "#ffffff")],
            )
            style.configure("TCombobox", padding=5)

        def build_layout(self):
            
            self.sidebar = tk.Frame(self.root, bg=SIDEBAR_BG, width=230)
            self.sidebar.pack(side="left", fill="y")
            self.sidebar.pack_propagate(False)

            brand = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
            brand.pack(fill="x", padx=20, pady=(24, 20))
            tk.Label(
                brand,
                text="HYDROBILL",
                bg=SIDEBAR_BG,
                fg=SIDEBAR_ACTIVE,
                font=("Segoe UI", 16, "bold"),
            ).pack(anchor="w")
            tk.Label(
                brand,
                text="Water Tariff & Audit System",
                bg=SIDEBAR_BG,
                fg="#9ca3af",
                font=("Segoe UI", 9),
            ).pack(anchor="w", pady=(2, 0))

            tk.Frame(self.sidebar, bg="#1f2937", height=1).pack(fill="x", padx=16, pady=(0, 14))

            nav_items = [
                ("billing", "📋  Household Billing"),
                ("top5", "🏆  Top 5 Consumers"),
                ("areas", "🗺️  Area Breakdown"),
                ("errors", "⚠️  Rejected Log"),
                ("calculator", "🧮  Tariff Simulator"),
                ("tests", "✅  System Verification"),
            ]

            for key, label in nav_items:
                btn = tk.Button(
                    self.sidebar,
                    text=label,
                    anchor="w",
                    bg=SIDEBAR_BG,
                    fg="#d1d5db",
                    activebackground=SIDEBAR_HOVER,
                    activeforeground="#ffffff",
                    font=("Segoe UI", 10, "bold"),
                    relief="flat",
                    bd=0,
                    padx=20,
                    pady=11,
                    cursor="hand2",
                    command=lambda k=key: self.switch_page(k),
                )
                btn.pack(fill="x", padx=10, pady=2)
                self.nav_buttons[key] = btn

            footer = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
            footer.pack(side="bottom", fill="x", padx=14, pady=18)
            tk.Label(
                footer,
                text="GENERATED REPORTS",
                bg=SIDEBAR_BG,
                fg="#6b7280",
                font=("Segoe UI", 8, "bold"),
            ).pack(anchor="w", padx=6, pady=(0, 6))

            for label, fname in [("📄 Open Billing Report", REPORT_FILE), ("🚨 Open Error Log", ERROR_FILE)]:
                tk.Button(
                    footer,
                    text=label,
                    anchor="w",
                    bg="#1f2937",
                    fg="#e5e7eb",
                    activebackground="#374151",
                    activeforeground="#ffffff",
                    font=("Segoe UI", 9),
                    relief="flat",
                    bd=0,
                    padx=12,
                    pady=8,
                    cursor="hand2",
                    command=lambda f=fname: self.open_external_file(f),
                ).pack(fill="x", pady=3)

            self.main_area = tk.Frame(self.root, bg=CANVAS_BG)
            self.main_area.pack(side="right", fill="both", expand=True)

            self.build_topbar()
            self.build_kpi_strip()

            self.page_container = tk.Frame(self.main_area, bg=CANVAS_BG)
            self.page_container.pack(fill="both", expand=True, padx=22, pady=(8, 12))

            self.pages = {}
            self.build_billing_page()
            self.build_top5_page()
            self.build_areas_page()
            self.build_errors_page()
            self.build_calculator_page()
            self.build_tests_page()

            self.status_var = tk.StringVar(value="Ready.")
            status_bar = tk.Frame(self.main_area, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER)
            status_bar.pack(fill="x", side="bottom")
            tk.Label(
                status_bar,
                textvariable=self.status_var,
                bg=CARD_BG,
                fg=TEXT_SECONDARY,
                font=("Segoe UI", 9),
                anchor="w",
            ).pack(side="left", padx=18, pady=6)

        def build_topbar(self):
            topbar = tk.Frame(self.main_area, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER)
            topbar.pack(fill="x")

            title_box = tk.Frame(topbar, bg=CARD_BG)
            title_box.pack(side="left", padx=22, pady=12)
            self.page_heading = tk.Label(
                title_box,
                text="Household Billing Records",
                bg=CARD_BG,
                fg=TEXT_PRIMARY,
                font=("Segoe UI", 16, "bold"),
            )
            self.page_heading.pack(anchor="w")

            self.file_label_var = tk.StringVar(value="Source: " + INPUT_FILE)
            tk.Label(
                title_box,
                textvariable=self.file_label_var,
                bg=CARD_BG,
                fg=TEXT_SECONDARY,
                font=("Segoe UI", 9),
            ).pack(anchor="w")

            controls = tk.Frame(topbar, bg=CARD_BG)
            controls.pack(side="right", padx=22)

            tk.Button(
                controls,
                text="📁 Select Input File",
                command=self.select_file,
                bg="#f1f5f9",
                fg=TEXT_PRIMARY,
                activebackground="#e2e8f0",
                font=("Segoe UI", 9, "bold"),
                relief="flat",
                padx=14,
                pady=8,
                cursor="hand2",
            ).pack(side="left", padx=6)

            tk.Button(
                controls,
                text="⚡ Run Billing Pipeline",
                command=self.run_processing,
                bg=EMERALD,
                fg="#ffffff",
                activebackground="#047857",
                activeforeground="#ffffff",
                font=("Segoe UI", 9, "bold"),
                relief="flat",
                padx=16,
                pady=8,
                cursor="hand2",
            ).pack(side="left", padx=6)

        def build_kpi_strip(self):
            strip = tk.Frame(self.main_area, bg=CANVAS_BG)
            strip.pack(fill="x", padx=22, pady=(16, 6))

            self.kpi_vars = {}
            metrics = [
                ("accepted", "Valid Households", EMERALD),
                ("rejected", "Rejected Rows", ROSE),
                ("total_kl", "Total Volume (kL)", SKY),
                ("average_kl", "Avg / Household", "#6366f1"),
                ("revenue", "Total Billed", AMBER),
            ]

            for idx, (key, caption, accent) in enumerate(metrics):
                card = tk.Frame(strip, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER)
                card.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 8, 0))
                strip.columnconfigure(idx, weight=1)

                inner = tk.Frame(card, bg=CARD_BG)
                inner.pack(fill="both", expand=True, padx=14, pady=12)

                tk.Label(
                    inner,
                    text=caption.upper(),
                    bg=CARD_BG,
                    fg=TEXT_SECONDARY,
                    font=("Segoe UI", 8, "bold"),
                ).pack(anchor="w")

                val_var = tk.StringVar(value="--")
                self.kpi_vars[key] = val_var
                tk.Label(
                    inner,
                    textvariable=val_var,
                    bg=CARD_BG,
                    fg=accent,
                    font=("Segoe UI", 18, "bold"),
                ).pack(anchor="w", pady=(4, 0))

        def switch_page(self, page_key):
            headings = {
                "billing": "Household Billing Records",
                "top5": "Top 5 Highest Water Consumers",
                "areas": "Consumption & Revenue by Area",
                "errors": "Rejected Records Audit Log",
                "calculator": "Interactive Progressive Tariff Simulator",
                "tests": "Automated Logic & Boundary Verification",
            }
            self.active_page = page_key
            self.page_heading.config(text=headings.get(page_key, ""))

            for key, btn in self.nav_buttons.items():
                if key == page_key:
                    btn.config(bg=SIDEBAR_ACTIVE, fg="#ffffff")
                else:
                    btn.config(bg=SIDEBAR_BG, fg="#d1d5db")

            for key, frame in self.pages.items():
                if key == page_key:
                    frame.pack(fill="both", expand=True)
                else:
                    frame.pack_forget()

            if page_key == "top5":
                self.root.after(50, self.render_top5_chart)

        def create_table(self, parent, columns, widths, alignments=None):
            wrapper = tk.Frame(parent, bg=CARD_BG)
            tree = ttk.Treeview(wrapper, columns=columns, show="headings", style="Custom.Treeview")
            for i, col in enumerate(columns):
                align = alignments[i] if alignments else "w"
                tree.heading(col, text=col, anchor=align)
                tree.column(col, width=widths[i], anchor=align)

            vsb = ttk.Scrollbar(wrapper, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            tree.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")

            for cat, color in ROW_BG.items():
                tree.tag_configure(cat, background=color)
            return wrapper, tree

        def build_billing_page(self):
            page = tk.Frame(self.page_container, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER)
            self.pages["billing"] = page

            filter_bar = tk.Frame(page, bg=CARD_BG)
            filter_bar.pack(fill="x", padx=16, pady=12)

            tk.Label(filter_bar, text="Search Meter / Name:", bg=CARD_BG, fg=TEXT_SECONDARY, font=("Segoe UI", 9, "bold")).pack(side="left")
            self.search_var = tk.StringVar()
            self.search_var.trace_add("write", lambda *_: self.update_billing_table())
            tk.Entry(
                filter_bar,
                textvariable=self.search_var,
                width=24,
                font=("Segoe UI", 10),
                relief="solid",
                bd=1,
            ).pack(side="left", padx=(6, 18))

            tk.Label(filter_bar, text="Area:", bg=CARD_BG, fg=TEXT_SECONDARY, font=("Segoe UI", 9, "bold")).pack(side="left")
            self.area_filter = tk.StringVar(value="All")
            self.area_combo = ttk.Combobox(filter_bar, textvariable=self.area_filter, state="readonly", width=16, values=["All"])
            self.area_combo.pack(side="left", padx=(6, 18))
            self.area_combo.bind("<<ComboboxSelected>>", lambda _: self.update_billing_table())

            tk.Label(filter_bar, text="Tier:", bg=CARD_BG, fg=TEXT_SECONDARY, font=("Segoe UI", 9, "bold")).pack(side="left")
            self.cat_filter = tk.StringVar(value="All")
            cat_combo = ttk.Combobox(filter_bar, textvariable=self.cat_filter, state="readonly", width=14, values=["All", "LOW", "MODERATE", "HIGH"])
            cat_combo.pack(side="left", padx=(6, 12))
            cat_combo.bind("<<ComboboxSelected>>", lambda _: self.update_billing_table())

            self.filter_count_var = tk.StringVar(value="")
            tk.Label(filter_bar, textvariable=self.filter_count_var, bg=CARD_BG, fg=TEXT_SECONDARY, font=("Segoe UI", 9)).pack(side="right")

            cols = ("Meter", "Household Name", "Area", "Prev", "Curr", "Usage (kL)", "Amount Due (R)", "Category")
            widths = (80, 180, 140, 85, 85, 95, 120, 110)
            aligns = ("w", "w", "w", "e", "e", "e", "e", "center")
            tbl_frame, self.billing_tree = self.create_table(page, cols, widths, aligns)
            tbl_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # --- PAGE 2: TOP 5 CONSUMERS
        def build_top5_page(self):
            page = tk.Frame(self.page_container, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER)
            self.pages["top5"] = page

            cols = ("Rank", "Meter", "Household Name", "Area", "Consumption (kL)", "Total Bill (R)")
            widths = (70, 90, 200, 160, 130, 130)
            aligns = ("center", "w", "w", "w", "e", "e")
            tbl_frame, self.top5_tree = self.create_table(page, cols, widths, aligns)
            self.top5_tree.configure(height=5)
            tbl_frame.pack(fill="x", padx=16, pady=(16, 10))

            self.chart_canvas = tk.Canvas(page, bg="#f8fafc", highlightthickness=1, highlightbackground=BORDER)
            self.chart_canvas.pack(fill="both", expand=True, padx=16, pady=(4, 16))
            self.chart_canvas.bind("<Configure>", lambda _: self.render_top5_chart())

        def render_top5_chart(self):
            c = self.chart_canvas
            c.delete("all")
            if not self.result or not self.result["top"]:
                return

            top = self.result["top"]
            w = c.winfo_width()
            h = c.winfo_height()
            if w < 100 or h < 100:
                return

            c.create_text(20, 20, anchor="w", text="Usage Comparison (kL)", font=("Segoe UI", 11, "bold"), fill=TEXT_PRIMARY)

            max_kl = top[0][1] if top[0][1] > 0 else 1
            left_margin = 210
            right_margin = 80
            usable_w = max(50, w - left_margin - right_margin)
            row_h = (h - 55) / len(top)
            bar_colors = ["#0284c7", "#0ea5e9", "#38bdf8", "#7dd3fc", "#bae6fd"]

            for idx, (meter, kl) in enumerate(top):
                rec = self.result["accepted"][meter]
                y0 = 46 + idx * row_h
                bar_len = usable_w * (kl / max_kl)

                c.create_text(
                    left_margin - 14,
                    y0 + row_h / 2,
                    anchor="e",
                    text=f"#{idx + 1}  {rec['name']} ({meter})",
                    font=("Segoe UI", 10, "bold" if idx == 0 else "normal"),
                    fill=TEXT_PRIMARY,
                )
                c.create_rectangle(
                    left_margin,
                    y0 + 8,
                    left_margin + bar_len,
                    y0 + row_h - 10,
                    fill=bar_colors[idx % len(bar_colors)],
                    outline="",
                )
                c.create_text(
                    left_margin + bar_len + 10,
                    y0 + row_h / 2,
                    anchor="w",
                    text=f"{kl} kL  (R{rec['charge']:,.2f})",
                    font=("Segoe UI", 10, "bold"),
                    fill=TEXT_PRIMARY,
                )

        def build_areas_page(self):
            page = tk.Frame(self.page_container, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER)
            self.pages["areas"] = page

            tk.Label(
                page,
                text="Regional Consumption & Revenue Summary",
                bg=CARD_BG,
                fg=TEXT_PRIMARY,
                font=("Segoe UI", 12, "bold"),
            ).pack(anchor="w", padx=18, pady=(16, 8))

            cols = ("Area / Suburb", "Accepted Households", "Total Consumption (kL)", "Avg kL / Household", "Total Billed Revenue (R)")
            widths = (200, 160, 180, 160, 190)
            aligns = ("w", "e", "e", "e", "e")
            tbl_frame, self.area_tree = self.create_table(page, cols, widths, aligns)
            tbl_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        def build_errors_page(self):
            page = tk.Frame(self.page_container, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER)
            self.pages["errors"] = page

            cols = ("Line #", "Raw Input Record", "Validation Failure Reason")
            widths = (80, 380, 440)
            aligns = ("center", "w", "w")
            tbl_frame, self.errors_tree = self.create_table(page, cols, widths, aligns)
            tbl_frame.pack(fill="both", expand=True, padx=16, pady=16)

        def build_calculator_page(self):
            page = tk.Frame(self.page_container, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER)
            self.pages["calculator"] = page

            container = tk.Frame(page, bg=CARD_BG)
            container.pack(pady=32, padx=32)

            tk.Label(
                container,
                text="Progressive Tariff Breakdown Simulator",
                bg=CARD_BG,
                fg=TEXT_PRIMARY,
                font=("Segoe UI", 15, "bold"),
            ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

            tk.Label(
                container,
                text="Adjust the slider or enter monthly consumption in kilolitres (kL) to preview charges.",
                bg=CARD_BG,
                fg=TEXT_SECONDARY,
                font=("Segoe UI", 10),
            ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 20))

            tk.Label(container, text="Monthly Usage (kL):", bg=CARD_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 11, "bold")).grid(row=2, column=0, sticky="w")

            self.sim_kl_var = tk.IntVar(value=25)
            slider = tk.Scale(
                container,
                from_=0,
                to=120,
                orient="horizontal",
                variable=self.sim_kl_var,
                length=320,
                bg=CARD_BG,
                highlightthickness=0,
                command=lambda _: self.update_simulator(),
            )
            slider.grid(row=2, column=1, padx=14)

            entry = tk.Entry(container, textvariable=self.sim_kl_var, width=8, font=("Segoe UI", 12, "bold"), relief="solid", bd=1, justify="center")
            entry.grid(row=2, column=2)
            entry.bind("<KeyRelease>", lambda _: self.update_simulator())

            self.sim_result_box = tk.Label(
                container,
                text="",
                bg="#f8fafc",
                fg=TEXT_PRIMARY,
                justify="left",
                font=("Consolas", 11),
                padx=20,
                pady=16,
                relief="solid",
                bd=1,
            )
            self.sim_result_box.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(22, 0))
            self.update_simulator()

        def update_simulator(self):
            try:
                kl = int(self.sim_kl_var.get())
                if kl < 0:
                    raise ValueError
            except (ValueError, tk.TclError):
                self.sim_result_box.config(text="Please enter a valid whole number (0 or greater).", fg=ROSE)
                return

            free_used = min(kl, FREE_LIMIT)
            band2_used = 0 if kl <= FREE_LIMIT else min(kl, BAND2_LIMIT) - FREE_LIMIT
            band3_used = 0 if kl <= BAND2_LIMIT else kl - BAND2_LIMIT

            cost2 = band2_used * RATE_BAND2
            cost3 = band3_used * RATE_BAND3
            total = calculate_bill(kl)
            tier = classify_consumption(kl)

            breakdown = (
                f"Band 1 (0 - {FREE_LIMIT} kL)   : {free_used:3d} kL @ R 0.00  =  R {0.0:8.2f}\n"
                f"Band 2 ({FREE_LIMIT + 1} - {BAND2_LIMIT} kL)  : {band2_used:3d} kL @ R {RATE_BAND2:4.2f}  =  R {cost2:8.2f}\n"
                f"Band 3 (> {BAND2_LIMIT} kL)    : {band3_used:3d} kL @ R{RATE_BAND3:5.2f}  =  R {cost3:8.2f}\n"
                f"----------------------------------------------------\n"
                f"Consumption Tier   : {tier}\n"
                f"TOTAL MONTHLY BILL : R {total:,.2f}"
            )
            self.sim_result_box.config(text=breakdown, fg=TEXT_PRIMARY)

        def build_tests_page(self):
            page = tk.Frame(self.page_container, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER)
            self.pages["tests"] = page

            top = tk.Frame(page, bg=CARD_BG)
            top.pack(fill="x", padx=16, pady=(14, 8))
            tk.Label(top, text="Unit & Boundary Test Suite", bg=CARD_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 12, "bold")).pack(side="left")
            tk.Button(
                top,
                text="↻ Re-run All Tests",
                command=self.execute_tests,
                bg=SKY,
                fg="#ffffff",
                font=("Segoe UI", 9, "bold"),
                relief="flat",
                padx=12,
                pady=6,
                cursor="hand2",
            ).pack(side="right")

            cols = ("Test Case", "Input", "Expected", "Actual", "Status")
            widths = (310, 170, 160, 160, 90)
            aligns = ("w", "w", "w", "w", "center")
            tbl_frame, self.tests_tree = self.create_table(page, cols, widths, aligns)
            self.tests_tree.tag_configure("PASS", background="#ecfdf5")
            self.tests_tree.tag_configure("FAIL", background="#fff1f2")
            tbl_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
            self.execute_tests()

        def execute_tests(self):
            for item in self.tests_tree.get_children():
                self.tests_tree.delete(item)

            tariff_cases = [
                (0, 0.00), (6, 0.00), (7, 8.50), (20, 119.00),
                (21, 131.00), (25, 179.00), (50, 479.00), (51, 491.00),
            ]
            for kl, exp in tariff_cases:
                act = calculate_bill(kl)
                ok = abs(act - exp) < 0.001
                self.tests_tree.insert("", "end", values=("Tariff Boundary", f"{kl} kL", f"R{exp:.2f}", f"R{act:.2f}", "PASS" if ok else "FAIL"), tags=("PASS" if ok else "FAIL",))

            class_cases = [(20, "LOW"), (21, "MODERATE"), (50, "MODERATE"), (51, "HIGH")]
            for kl, exp in class_cases:
                act = classify_consumption(kl)
                ok = act == exp
                self.tests_tree.insert("", "end", values=("Classification Tier", f"{kl} kL", exp, act, "PASS" if ok else "FAIL"), tags=("PASS" if ok else "FAIL",))

            val_cases = [
                ("M300,A,100,120,X", "", "Valid record"),
                ("M001,Dup,1,5,X", "Duplicate", "Duplicate meter"),
                ("M301,A,,5,X", "Missing", "Missing reading"),
                ("M302,A,abc,5,X", "Non-numeric", "Non-numeric reading"),
                ("M303,A,-10,5,X", "Negative", "Negative reading"),
                ("M304,A,200,100,X", "below", "Reversed reading"),
                ("M305,A,1,5,", "Missing", "Missing area"),
                ("M306,A,1", "Wrong number", "Wrong field count"),
            ]
            known = {"M001": {}}
            for raw, key, label in val_cases:
                reason = validate_record(clean_fields(raw), known)
                ok = (reason == "") if key == "" else (key in reason)
                self.tests_tree.insert("", "end", values=(f"Validation: {label}", raw, "Rejected" if key else "Accepted", "Rejected" if reason else "Accepted", "PASS" if ok else "FAIL"), tags=("PASS" if ok else "FAIL",))

            demo = {f"T{i}": {"kl": val} for i, val in enumerate([10, 90, 40, 90, 70, 5, 120, 60])}
            order = [kl for _, kl in top_five_consumers(demo)]
            ok = order == [120, 90, 90, 70, 60]
            self.tests_tree.insert("", "end", values=("Manual Top 5 Ranking", "10,90,40,90,70,5,120,60", "[120, 90, 90, 70, 60]", str(order), "PASS" if ok else "FAIL"), tags=("PASS" if ok else "FAIL",))

        # --- DATA & ACTIONS
        def select_file(self):
            chosen = filedialog.askopenfilename(
                title="Select Water Meter Readings File",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            )
            if chosen:
                self.file_path = chosen
                self.file_label_var.set("Source: " + os.path.basename(chosen))
                self.run_processing()

        def run_processing(self):
            res = run_pipeline(self.file_path, self.folder)
            if res["error"] != "":
                messagebox.showerror("Input File Error", res["error"])
                self.status_var.set("Error: " + res["error"])
                return

            self.result = res
            s = res["summary"]

            self.kpi_vars["accepted"].set(str(s["accepted"]))
            self.kpi_vars["rejected"].set(str(s["rejected"]))
            self.kpi_vars["total_kl"].set(f"{s['total_kl']:,}")
            self.kpi_vars["average_kl"].set(f"{s['average_kl']:.1f} kL")
            self.kpi_vars["revenue"].set(f"R{s['total_revenue']:,.2f}")

            area_list = ["All"] + list(s["areas"].keys())
            self.area_combo.configure(values=area_list)
            self.area_filter.set("All")

            self.update_billing_table()
            self.update_top5_table()
            self.update_areas_table()
            self.update_errors_table()

            self.status_var.set(
                f"Processed {res['lines']} lines from '{os.path.basename(self.file_path)}'  •  "
                f"{s['accepted']} accepted, {s['rejected']} rejected  •  Reports saved to {self.folder}"
            )

        def update_billing_table(self):
            if not self.result:
                return
            for item in self.billing_tree.get_children():
                self.billing_tree.delete(item)

            query = self.search_var.get().strip().lower()
            area_sel = self.area_filter.get()
            cat_sel = self.cat_filter.get()
            shown = 0

            for meter, rec in self.result["accepted"].items():
                if area_sel != "All" and rec["area"] != area_sel:
                    continue
                if cat_sel != "All" and rec["category"] != cat_sel:
                    continue
                if query and query not in meter.lower() and query not in rec["name"].lower():
                    continue

                self.billing_tree.insert(
                    "",
                    "end",
                    values=(
                        meter,
                        rec["name"],
                        rec["area"],
                        rec["previous"],
                        rec["current"],
                        rec["kl"],
                        f"{rec['charge']:,.2f}",
                        rec["category"],
                    ),
                    tags=(rec["category"],),
                )
                shown += 1

            self.filter_count_var.set(f"Showing {shown} of {self.result['summary']['accepted']} records")

        def update_top5_table(self):
            for item in self.top5_tree.get_children():
                self.top5_tree.delete(item)

            for rank, (meter, kl) in enumerate(self.result["top"], start=1):
                rec = self.result["accepted"][meter]
                self.top5_tree.insert(
                    "",
                    "end",
                    values=(rank, meter, rec["name"], rec["area"], kl, f"{rec['charge']:,.2f}"),
                )
            self.render_top5_chart()

        def update_areas_table(self):
            for item in self.area_tree.get_children():
                self.area_tree.delete(item)

            for area, stats in self.result["summary"]["areas"].items():
                avg = stats["kl"] / stats["count"] if stats["count"] > 0 else 0.0
                self.area_tree.insert(
                    "",
                    "end",
                    values=(area, stats["count"], f"{stats['kl']:,}", f"{avg:.2f}", f"{stats['revenue']:,.2f}"),
                )

        def update_errors_table(self):
            for item in self.errors_tree.get_children():
                self.errors_tree.delete(item)

            for err in self.result["rejected"]:
                self.errors_tree.insert("", "end", values=(err["line"], err["raw"], err["reason"]), tags=("HIGH",))

        def open_external_file(self, filename):
            full_path = os.path.join(self.folder, filename)
            if not os.path.exists(full_path):
                messagebox.showinfo("File Not Found", "Run the billing pipeline first to generate reports.")
                return
            try:
                if sys.platform.startswith("win"):
                    os.startfile(full_path)
                elif sys.platform == "darwin":
                    os.system(f'open "{full_path}"')
                else:
                    os.system(f'xdg-open "{full_path}"')
            except OSError as exc:
                messagebox.showerror("Unable to Open File", str(exc))

    root = tk.Tk()
    WaterBillingDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_console_version()
    else:
        launch_gui()
