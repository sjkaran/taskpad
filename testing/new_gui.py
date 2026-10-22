"""Marada 9x9 Planner — a local-first task and goal manager.

Requirements: Python 3.10+ and CustomTkinter
Install:     python -m pip install customtkinter
Run:         python marada_planner.py

Data is saved locally in ~/.marada_planner/marada.db (SQLite).
Each of the 81 cells stores one task or goal. This is a flexible 9x9 planner
interface; it does not encode any unspecified rules of a separate "Marada method".
"""

from __future__ import annotations

import csv
import sqlite3
import tkinter as tk
from datetime import date, datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

APP_NAME = "Marada Planner"
DB_DIR = Path.home() / ".marada_planner"
DB_PATH = DB_DIR / "marada.db"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG = "#0b1020"
PANEL = "#111a2e"
PANEL_ALT = "#17233b"
BORDER = "#263653"
TEXT = "#e8eef9"
MUTED = "#93a4c2"
ACCENT = "#6c8cff"
GREEN = "#2fba87"
AMBER = "#e6a84b"
RED = "#ed6a78"


class Store:
    """Small SQLite persistence layer for the 81 planner slots."""

    def __init__(self, path: Path = DB_PATH):
        DB_DIR.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slot INTEGER NOT NULL UNIQUE CHECK(slot BETWEEN 0 AND 80),
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                entry_type TEXT NOT NULL DEFAULT 'Task',
                priority TEXT NOT NULL DEFAULT 'Medium',
                due_date TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Active',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def all(self):
        return self.conn.execute("SELECT * FROM entries ORDER BY slot").fetchall()

    def get(self, slot: int):
        return self.conn.execute("SELECT * FROM entries WHERE slot = ?", (slot,)).fetchone()

    def save(self, slot: int, title: str, description: str, entry_type: str,
             priority: str, due_date: str, status: str):
        now = datetime.now().isoformat(timespec="seconds")
        old = self.get(slot)
        if old:
            self.conn.execute("""UPDATE entries SET title=?, description=?, entry_type=?,
                priority=?, due_date=?, status=?, updated_at=? WHERE slot=?""",
                (title, description, entry_type, priority, due_date, status, now, slot))
        else:
            self.conn.execute("""INSERT INTO entries
                (slot, title, description, entry_type, priority, due_date, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (slot, title, description, entry_type, priority, due_date, status, now, now))
        self.conn.commit()

    def delete(self, slot: int):
        self.conn.execute("DELETE FROM entries WHERE slot = ?", (slot,))
        self.conn.commit()

    def close(self):
        self.conn.close()


class MaradaPlanner(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Marada Planner | Tasks & Goals")
        self.geometry("1320x900")
        self.minsize(1120, 780)
        self.configure(fg_color=BG)
        self.store = Store()
        self.selected_slot = 0
        self.entries_by_slot = {}
        self.filter_mode = "All"
        self.search_var = tk.StringVar()
        self._build_ui()
        self.refresh()
        self.select_slot(0)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=26, pady=(22, 14))
        header.grid_columnconfigure(0, weight=1)
        title_area = ctk.CTkFrame(header, fg_color="transparent")
        title_area.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(title_area, text="MARADA", text_color=ACCENT,
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(title_area, text="Tasks & Goals", text_color=TEXT,
                     font=ctk.CTkFont(size=29, weight="bold")).pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(title_area, text="An 81-slot workspace for planning, tracking, and reviewing your work.",
                     text_color=MUTED, font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(3, 0))
        header_actions = ctk.CTkFrame(header, fg_color="transparent")
        header_actions.grid(row=0, column=1, sticky="e", padx=(12, 0))
        ctk.CTkButton(header_actions, text="Export CSV", width=112, height=38,
                      fg_color=PANEL_ALT, hover_color=BORDER, command=self.export_csv).pack(side="left", padx=(0, 8))
        ctk.CTkButton(header_actions, text="＋  New entry", width=130, height=38,
                      command=self.new_entry).pack(side="left")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=26, pady=(0, 22))
        body.grid_columnconfigure(0, weight=6, uniform="main")
        body.grid_columnconfigure(1, weight=5, uniform="main")
        body.grid_rowconfigure(1, weight=1)

        # Summary cards
        stats = ctk.CTkFrame(body, fg_color="transparent")
        stats.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        for i in range(4):
            stats.grid_columnconfigure(i, weight=1, uniform="stats")
        self.stat_values = {}
        for i, (key, label, accent) in enumerate([
            ("total", "TOTAL ENTRIES", ACCENT), ("active", "ACTIVE", AMBER),
            ("done", "COMPLETED", GREEN), ("overdue", "OVERDUE", RED)
        ]):
            card = ctk.CTkFrame(stats, fg_color=PANEL, border_width=1, border_color=BORDER, corner_radius=14)
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 7, 0 if i == 3 else 7))
            ctk.CTkLabel(card, text=label, text_color=MUTED,
                         font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=15, pady=(13, 2))
            val = ctk.CTkLabel(card, text="0", text_color=accent,
                               font=ctk.CTkFont(size=27, weight="bold"))
            val.pack(anchor="w", padx=15, pady=(0, 12))
            self.stat_values[key] = val

        # Grid panel
        left = ctk.CTkFrame(body, fg_color=PANEL, border_width=1, border_color=BORDER, corner_radius=16)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        left.grid_columnconfigure(0, weight=1)
        # Give the board viewport the remaining panel height. The 9x9 grid
        # lives inside a scrollable frame so all 81 cells remain reachable
        # on shorter displays and at higher display scaling settings.
        left.grid_rowconfigure(3, weight=1)
        ctk.CTkLabel(left, text="Your 9 × 9 board", text_color=TEXT,
                     font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(17, 2))
        ctk.CTkLabel(left, text="Select a cell to create or edit its task or goal.", text_color=MUTED,
                     font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 12))

        legend = ctk.CTkFrame(left, fg_color="transparent")
        legend.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 9))
        for label, color in [("Empty", BORDER), ("Active", ACCENT), ("Completed", GREEN), ("Overdue", RED)]:
            item = ctk.CTkFrame(legend, fg_color="transparent")
            item.pack(side="left", padx=(3, 9))
            ctk.CTkFrame(item, fg_color=color, width=8, height=8, corner_radius=4).pack(side="left", padx=(0, 5))
            ctk.CTkLabel(item, text=label, text_color=MUTED, font=ctk.CTkFont(size=10)).pack(side="left")

        board = ctk.CTkScrollableFrame(
            left,
            height=480,
            fg_color="transparent",
            corner_radius=10,
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=ACCENT,
        )
        board.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 12))
        board.grid_columnconfigure(tuple(range(9)), weight=1, uniform="board-columns")
        self.cell_buttons = []
        for slot in range(81):
            r, col = divmod(slot, 9)
            btn = ctk.CTkButton(board, text=f"{slot + 1:02}", width=61, height=57,
                                corner_radius=8, border_width=1, border_color=BORDER,
                                fg_color="#131d32", hover_color="#243453",
                                text_color=MUTED, font=ctk.CTkFont(size=11, weight="bold"),
                                command=lambda s=slot: self.select_slot(s))
            btn.grid(row=r, column=col, padx=2, pady=2, sticky="nsew")
            self.cell_buttons.append(btn)

        board_footer = ctk.CTkFrame(left, fg_color="transparent")
        board_footer.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 15))
        ctk.CTkLabel(board_footer, text="81 slots · Local SQLite storage", text_color=MUTED,
                     font=ctk.CTkFont(size=11)).pack(side="left")
        self.board_progress = ctk.CTkLabel(board_footer, text="0 / 81 occupied", text_color=TEXT,
                                           font=ctk.CTkFont(size=11, weight="bold"))
        self.board_progress.pack(side="right")

        # Editor panel
        right = ctk.CTkFrame(body, fg_color=PANEL, border_width=1, border_color=BORDER, corner_radius=16)
        right.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        right.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(right, text="Entry editor", text_color=TEXT,
                     font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=20, pady=(17, 2))
        self.slot_label = ctk.CTkLabel(right, text="SLOT 01  /  ROW 1, COLUMN 1", text_color=ACCENT,
                                       font=ctk.CTkFont(size=11, weight="bold"))
        self.slot_label.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.grid(row=2, column=0, sticky="nsew", padx=20)
        form.grid_columnconfigure(0, weight=1)

        self.title_var = tk.StringVar()
        self.type_var = tk.StringVar(value="Task")
        self.priority_var = tk.StringVar(value="Medium")
        self.due_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Active")

        self._field_label(form, "TITLE", 0)
        self.title_entry = ctk.CTkEntry(form, textvariable=self.title_var, height=40,
                                        placeholder_text="e.g. Finish probability assignment")
        self.title_entry.grid(row=1, column=0, sticky="ew", pady=(5, 13))

        self._field_label(form, "DESCRIPTION / NOTES", 2)
        self.description = ctk.CTkTextbox(form, height=110, corner_radius=9,
                                          fg_color="#0d1527", border_width=1, border_color=BORDER,
                                          text_color=TEXT, font=ctk.CTkFont(size=12), wrap="word")
        self.description.grid(row=3, column=0, sticky="ew", pady=(5, 13))

        choices = ctk.CTkFrame(form, fg_color="transparent")
        choices.grid(row=4, column=0, sticky="ew")
        choices.grid_columnconfigure((0, 1), weight=1, uniform="choices")
        self._field_label(choices, "ENTRY TYPE", 0, 0)
        self.type_menu = ctk.CTkOptionMenu(choices, variable=self.type_var,
                                           values=["Task", "Goal"], height=36)
        self.type_menu.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(5, 13))
        self._field_label(choices, "PRIORITY", 0, 1)
        self.priority_menu = ctk.CTkOptionMenu(choices, variable=self.priority_var,
                                               values=["Low", "Medium", "High", "Critical"], height=36)
        self.priority_menu.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(5, 13))
        self._field_label(choices, "DUE DATE (YYYY-MM-DD)", 2, 0)
        self.due_entry = ctk.CTkEntry(choices, textvariable=self.due_var, height=36,
                                      placeholder_text="Optional")
        self.due_entry.grid(row=3, column=0, sticky="ew", padx=(0, 6), pady=(5, 13))
        self._field_label(choices, "STATUS", 2, 1)
        self.status_menu = ctk.CTkOptionMenu(choices, variable=self.status_var,
                                             values=["Active", "Completed"], height=36)
        self.status_menu.grid(row=3, column=1, sticky="ew", padx=(6, 0), pady=(5, 13))

        ctk.CTkLabel(form, text="Tip: leave the due date blank if this entry has no deadline.",
                     text_color=MUTED, font=ctk.CTkFont(size=10), wraplength=360,
                     justify="left").grid(row=5, column=0, sticky="w", pady=(0, 12))

        actions = ctk.CTkFrame(right, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", padx=20, pady=(3, 8))
        actions.grid_columnconfigure((0, 1), weight=1, uniform="actions")
        ctk.CTkButton(actions, text="Save entry", height=42, command=self.save_entry).grid(
            row=0, column=0, sticky="ew", padx=(0, 5), pady=(0, 8))
        ctk.CTkButton(actions, text="Mark complete", height=42, fg_color="#176e55",
                      hover_color="#208466", command=self.mark_complete).grid(
            row=0, column=1, sticky="ew", padx=(5, 0), pady=(0, 8))
        ctk.CTkButton(actions, text="Clear form", height=36, fg_color=PANEL_ALT,
                      hover_color=BORDER, command=self.clear_form).grid(
            row=1, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(actions, text="Delete entry", height=36, fg_color="#6f2938",
                      hover_color="#913448", command=self.delete_entry).grid(
            row=1, column=1, sticky="ew", padx=(5, 0))

        # Search and filters below the main panels
        bottom = ctk.CTkFrame(body, fg_color=PANEL, border_width=1, border_color=BORDER, corner_radius=14)
        bottom.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        bottom.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(bottom, text="FIND ENTRIES", text_color=MUTED,
                     font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=0, padx=(15, 10), pady=12)
        search = ctk.CTkEntry(bottom, textvariable=self.search_var, height=34,
                              placeholder_text="Search titles and descriptions…")
        search.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=12)
        self.search_var.trace_add("write", lambda *_: self.refresh())
        self.filter_segment = ctk.CTkSegmentedButton(bottom, values=["All", "Active", "Completed", "Overdue"],
                                                     command=self.change_filter)
        self.filter_segment.set("All")
        self.filter_segment.grid(row=0, column=2, padx=(0, 15), pady=12)

        self.status_line = ctk.CTkLabel(self, text=f"Saved locally · {DB_PATH}", text_color=MUTED,
                                        font=ctk.CTkFont(size=10), anchor="w")
        self.status_line.grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 8))

    def _field_label(self, parent, text, row, column=0):
        ctk.CTkLabel(parent, text=text, text_color=MUTED,
                     font=ctk.CTkFont(size=10, weight="bold")).grid(
            row=row, column=column, sticky="w", padx=(0, 6) if column == 0 else (6, 0))

    @staticmethod
    def is_overdue(entry):
        if not entry or entry["status"] == "Completed" or not entry["due_date"]:
            return False
        try:
            return date.fromisoformat(entry["due_date"]) < date.today()
        except ValueError:
            return False

    def select_slot(self, slot: int):
        self.selected_slot = slot
        row, col = divmod(slot, 9)
        self.slot_label.configure(text=f"SLOT {slot + 1:02}  /  ROW {row + 1}, COLUMN {col + 1}")
        entry = self.store.get(slot)
        self.title_var.set(entry["title"] if entry else "")
        self.type_var.set(entry["entry_type"] if entry else "Task")
        self.priority_var.set(entry["priority"] if entry else "Medium")
        self.due_var.set(entry["due_date"] if entry else "")
        self.status_var.set(entry["status"] if entry else "Active")
        self.description.delete("1.0", "end")
        if entry:
            self.description.insert("1.0", entry["description"])
        self.refresh()
        self.title_entry.focus_set()

    def new_entry(self):
        empty = next((slot for slot in range(81) if self.store.get(slot) is None), None)
        if empty is None:
            messagebox.showinfo("Board is full", "All 81 slots are occupied. Delete an entry or export your board before making room.")
            return
        self.select_slot(empty)
        self.status_line.configure(text=f"New entry in slot {empty + 1:02}. Fill the form and choose Save entry.")

    def clear_form(self):
        self.title_var.set("")
        self.type_var.set("Task")
        self.priority_var.set("Medium")
        self.due_var.set("")
        self.status_var.set("Active")
        self.description.delete("1.0", "end")
        self.status_line.configure(text="Form cleared. Existing saved data is unchanged until you save or delete.")

    def save_entry(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Title required", "Enter a title before saving.")
            self.title_entry.focus_set()
            return
        due = self.due_var.get().strip()
        if due:
            try:
                date.fromisoformat(due)
            except ValueError:
                messagebox.showwarning("Invalid due date", "Use the date format YYYY-MM-DD, for example 2026-12-31.")
                self.due_entry.focus_set()
                return
        existing = self.store.get(self.selected_slot)
        if existing is None and not title:
            return
        self.store.save(self.selected_slot, title, self.description.get("1.0", "end-1c").strip(),
                        self.type_var.get(), self.priority_var.get(), due, self.status_var.get())
        self.refresh()
        self.status_line.configure(text=f"Saved {self.type_var.get().lower()} to slot {self.selected_slot + 1:02} · {datetime.now().strftime('%H:%M:%S')}")

    def mark_complete(self):
        entry = self.store.get(self.selected_slot)
        title = self.title_var.get().strip()
        if not title and not entry:
            messagebox.showinfo("No entry selected", "Create and save an entry before marking it complete.")
            return
        self.status_var.set("Completed")
        self.save_entry()

    def delete_entry(self):
        entry = self.store.get(self.selected_slot)
        if not entry:
            self.clear_form()
            return
        if not messagebox.askyesno("Delete entry", f"Delete '{entry['title']}' from slot {self.selected_slot + 1:02}? This cannot be undone."):
            return
        self.store.delete(self.selected_slot)
        self.clear_form()
        self.refresh()
        self.status_line.configure(text=f"Deleted slot {self.selected_slot + 1:02}.")

    def change_filter(self, value):
        self.filter_mode = value
        self.refresh()

    def refresh(self):
        entries = self.store.all()
        self.entries_by_slot = {entry["slot"]: entry for entry in entries}
        total = len(entries)
        done = sum(entry["status"] == "Completed" for entry in entries)
        active = sum(entry["status"] == "Active" for entry in entries)
        overdue = sum(self.is_overdue(entry) for entry in entries)
        self.stat_values["total"].configure(text=str(total))
        self.stat_values["active"].configure(text=str(active))
        self.stat_values["done"].configure(text=str(done))
        self.stat_values["overdue"].configure(text=str(overdue))
        self.board_progress.configure(text=f"{total} / 81 occupied · {round(total / 81 * 100)}%")

        query = self.search_var.get().strip().casefold() if hasattr(self, "search_var") else ""
        for slot, btn in enumerate(self.cell_buttons):
            entry = self.entries_by_slot.get(slot)
            selected = slot == self.selected_slot
            visible = True
            if entry:
                if self.filter_mode == "Active":
                    visible = entry["status"] == "Active"
                elif self.filter_mode == "Completed":
                    visible = entry["status"] == "Completed"
                elif self.filter_mode == "Overdue":
                    visible = self.is_overdue(entry)
                if query:
                    visible = visible and (query in entry["title"].casefold() or query in entry["description"].casefold())
            elif self.filter_mode != "All" or query:
                visible = False

            if not entry:
                label, color, text_color = f"{slot + 1:02}", "#131d32", MUTED
            else:
                title = entry["title"]
                short = title[:8] + ("…" if len(title) > 8 else "")
                marker = "✓" if entry["status"] == "Completed" else ("!" if self.is_overdue(entry) else "•")
                label = f"{slot + 1:02}\n{marker} {short}"
                color = GREEN if entry["status"] == "Completed" else (RED if self.is_overdue(entry) else ACCENT)
                text_color = "#ffffff"
            if not visible:
                color = "#0d1321"
                text_color = "#3b4962"
            btn.configure(text=label, fg_color=color if entry and visible else ("#1c2a44" if selected else color),
                          text_color=text_color, border_color="#ffffff" if selected else BORDER,
                          border_width=2 if selected else 1, hover_color="#2a3c5f")

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            title="Export planner entries", defaultextension=".csv",
            filetypes=[("CSV spreadsheet", "*.csv")], initialfile="marada_planner_export.csv")
        if not path:
            return
        fields = ["slot", "row", "column", "title", "description", "entry_type", "priority",
                  "due_date", "status", "created_at", "updated_at"]
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.DictWriter(file, fieldnames=fields)
                writer.writeheader()
                for entry in self.store.all():
                    row, col = divmod(entry["slot"], 9)
                    record = dict(entry)
                    record["slot"] = entry["slot"] + 1
                    record["row"] = row + 1
                    record["column"] = col + 1
                    writer.writerow(record)
            self.status_line.configure(text=f"Exported {len(self.store.all())} entries to {path}")
            messagebox.showinfo("Export complete", f"Your entries were exported to:\n{path}")
        except OSError as exc:
            messagebox.showerror("Export failed", f"Could not write the CSV file.\n\n{exc}")

    def on_close(self):
        self.store.close()
        self.destroy()


if __name__ == "__main__":
    app = MaradaPlanner()
    app.mainloop()
