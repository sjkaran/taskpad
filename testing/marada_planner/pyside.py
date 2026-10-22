"""Marada Planner — premium PySide6 edition.

Requirements: Python 3.10+ and PySide6
Install:     python -m pip install PySide6
Run:         python marada_planner_pyside6.py

Data is stored in ~/.marada_planner/marada.db, using the same SQLite schema
as the CustomTkinter edition so existing entries can be reused.
"""
from __future__ import annotations

import csv
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QScrollArea, QGridLayout,
    QVBoxLayout, QHBoxLayout, QFormLayout, QSplitter, QMessageBox,
    QFileDialog, QButtonGroup, QSizePolicy, QSpacerItem
)

APP_NAME = "Marada Planner"
DB_DIR = Path.home() / ".marada_planner"
DB_PATH = DB_DIR / "marada.db"

# Palette: deep navy surfaces, subtle borders, restrained indigo accent.
BG = "#0A0F1C"
SIDEBAR = "#0D1424"
PANEL = "#111A2D"
PANEL_HOVER = "#192641"
BORDER = "#263550"
TEXT = "#EDF2FC"
MUTED = "#91A1BD"
ACCENT = "#8095FF"
ACCENT_DARK = "#5368D8"
GREEN = "#35C59A"
AMBER = "#F2B75D"
RED = "#F27483"

STYLESHEET = f"""
QMainWindow, QWidget#root {{ background: {BG}; color: {TEXT}; }}
QWidget {{ color: {TEXT}; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 13px; }}
QFrame#sidebar {{ background: {SIDEBAR}; border-right: 1px solid {BORDER}; }}
QFrame#panel, QFrame#statCard {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 16px; }}
QFrame#statCard {{ border-radius: 13px; }}
QLabel#eyebrow {{ color: {ACCENT}; font-size: 10px; font-weight: 800; letter-spacing: 2px; }}
QLabel#pageTitle {{ color: {TEXT}; font-size: 28px; font-weight: 750; }}
QLabel#sectionTitle {{ color: {TEXT}; font-size: 17px; font-weight: 700; }}
QLabel#muted {{ color: {MUTED}; }}
QLabel#statValue {{ font-size: 27px; font-weight: 750; }}
QLineEdit, QTextEdit, QComboBox, QDateEdit {{
  background: #0B1323; border: 1px solid {BORDER}; border-radius: 9px;
  padding: 9px 11px; selection-background-color: {ACCENT_DARK};
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {{ border: 1px solid {ACCENT}; }}
QComboBox::drop-down, QDateEdit::drop-down {{ border: 0; width: 25px; }}
QComboBox QAbstractItemView {{ background: {PANEL}; border: 1px solid {BORDER}; selection-background-color: {ACCENT_DARK}; }}
QPushButton {{ background: {ACCENT_DARK}; color: white; border: 1px solid transparent; border-radius: 9px; padding: 10px 14px; font-weight: 650; }}
QPushButton:hover {{ background: #6378E8; }}
QPushButton:pressed {{ background: #4559C2; }}
QPushButton#secondary {{ background: #1A2740; border-color: {BORDER}; color: {TEXT}; }}
QPushButton#secondary:hover {{ background: #263755; }}
QPushButton#danger {{ background: #512532; border-color: #713344; color: #FFDDE2; }}
QPushButton#danger:hover {{ background: #713344; }}
QPushButton#success {{ background: #155541; border-color: #1E7659; color: #D7FFF2; }}
QPushButton#success:hover {{ background: #1B6B50; }}
QPushButton#nav {{ text-align: left; background: transparent; color: {MUTED}; padding: 11px 12px; border-radius: 8px; font-weight: 600; }}
QPushButton#nav:hover, QPushButton#nav:checked {{ background: #1A2740; color: {TEXT}; }}
QPushButton#filter {{ background: transparent; color: {MUTED}; border: 1px solid transparent; padding: 8px 13px; }}
QPushButton#filter:checked {{ background: #27365A; color: white; border-color: #485E9C; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{ background: #0D1526; width: 10px; margin: 3px; border-radius: 5px; }}
QScrollBar::handle:vertical {{ background: #344463; min-height: 28px; border-radius: 5px; }}
QScrollBar::handle:vertical:hover {{ background: #52658B; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ background: #0D1526; height: 10px; margin: 3px; border-radius: 5px; }}
QScrollBar::handle:horizontal {{ background: #344463; min-width: 28px; border-radius: 5px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
"""


class Store:
    """SQLite storage compatible with the CustomTkinter edition."""
    def __init__(self, path: Path = DB_PATH):
        DB_DIR.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS entries (
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
        )""")
        self.conn.commit()

    def all(self):
        return self.conn.execute("SELECT * FROM entries ORDER BY slot").fetchall()

    def get(self, slot: int):
        return self.conn.execute("SELECT * FROM entries WHERE slot=?", (slot,)).fetchone()

    def save(self, slot, title, description, entry_type, priority, due_date, status):
        now = datetime.now().isoformat(timespec="seconds")
        old = self.get(slot)
        if old:
            self.conn.execute("""UPDATE entries SET title=?, description=?, entry_type=?, priority=?,
                due_date=?, status=?, updated_at=? WHERE slot=?""",
                (title, description, entry_type, priority, due_date, status, now, slot))
        else:
            self.conn.execute("""INSERT INTO entries
                (slot,title,description,entry_type,priority,due_date,status,created_at,updated_at)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (slot,title,description,entry_type,priority,due_date,status,now,now))
        self.conn.commit()

    def delete(self, slot):
        self.conn.execute("DELETE FROM entries WHERE slot=?", (slot,))
        self.conn.commit()

    def close(self):
        self.conn.close()


class StatCard(QFrame):
    def __init__(self, label: str, color: str):
        super().__init__()
        self.setObjectName("statCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(17, 13, 17, 14)
        layout.setSpacing(5)
        self.caption = QLabel(label.upper())
        self.caption.setStyleSheet(f"color:{MUTED}; font-size:10px; font-weight:800; letter-spacing:1px; border:none;")
        self.value = QLabel("0")
        self.value.setObjectName("statValue")
        self.value.setStyleSheet(f"color:{color}; border:none;")
        layout.addWidget(self.caption)
        layout.addWidget(self.value)


class MaradaPlanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Marada Planner — Tasks & Goals")
        self.resize(1480, 940)
        self.setMinimumSize(1080, 720)
        self.store = Store()
        self.selected_slot = 0
        self.filter_mode = "All"
        self.entries_by_slot = {}
        self.cell_buttons: list[QPushButton] = []
        self._build_ui()
        self.refresh()
        self.select_slot(0)

    @staticmethod
    def label(text, object_name=None):
        item = QLabel(text)
        if object_name:
            item.setObjectName(object_name)
        return item

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(218)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(18, 24, 18, 20)
        side.setSpacing(8)
        brand_row = QHBoxLayout()
        mark = QLabel("M")
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setFixedSize(38, 38)
        mark.setStyleSheet(f"background:{ACCENT_DARK}; color:white; border-radius:11px; font-size:20px; font-weight:800;")
        brand_text = QVBoxLayout()
        brand_text.setSpacing(1)
        brand_text.addWidget(self.label("MARADA", "sectionTitle"))
        brand_text.addWidget(self.label("PERSONAL WORKSPACE", "muted"))
        brand_row.addWidget(mark)
        brand_row.addLayout(brand_text)
        brand_row.addStretch()
        side.addLayout(brand_row)
        side.addSpacing(30)
        side.addWidget(self.label("WORKSPACE", "eyebrow"))
        self.nav_board = QPushButton("▦    Planning board")
        self.nav_board.setObjectName("nav")
        self.nav_board.setCheckable(True)
        self.nav_board.setChecked(True)
        self.nav_board.clicked.connect(lambda: self.search.setFocus())
        side.addWidget(self.nav_board)
        self.nav_all = QPushButton("◷    All entries")
        self.nav_all.setObjectName("nav")
        self.nav_all.clicked.connect(lambda: self.set_filter("All"))
        side.addWidget(self.nav_all)
        self.nav_active = QPushButton("◉    Active tasks")
        self.nav_active.setObjectName("nav")
        self.nav_active.clicked.connect(lambda: self.set_filter("Active"))
        side.addWidget(self.nav_active)
        self.nav_done = QPushButton("✓    Completed")
        self.nav_done.setObjectName("nav")
        self.nav_done.clicked.connect(lambda: self.set_filter("Completed"))
        side.addWidget(self.nav_done)
        self.nav_overdue = QPushButton("!    Overdue")
        self.nav_overdue.setObjectName("nav")
        self.nav_overdue.clicked.connect(lambda: self.set_filter("Overdue"))
        side.addWidget(self.nav_overdue)
        side.addStretch(1)
        tip = QFrame()
        tip.setStyleSheet(f"background:#141F35; border:1px solid {BORDER}; border-radius:12px;")
        tip_layout = QVBoxLayout(tip)
        tip_layout.setContentsMargins(12, 12, 12, 12)
        tip_layout.addWidget(self.label("YOUR SYSTEM", "eyebrow"))
        tip_layout.addWidget(self.label("81 focused slots.\nOne local database.\nYour work stays yours.", "muted"))
        side.addWidget(tip)
        side.addSpacing(8)
        side.addWidget(self.label("LOCAL STORAGE · SQLITE", "muted"))
        outer.addLayout(side)

        # Main area
        main = QWidget()
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(26, 23, 26, 16)
        main_layout.setSpacing(16)
        outer.addWidget(main, 1)

        header = QHBoxLayout()
        heading = QVBoxLayout()
        heading.setSpacing(4)
        heading.addWidget(self.label("YOUR PERSONAL SYSTEM", "eyebrow"))
        heading.addWidget(self.label("Tasks & Goals", "pageTitle"))
        heading.addWidget(self.label("Plan deliberately. Track progress. Keep the important work visible.", "muted"))
        header.addLayout(heading, 1)
        self.export_btn = QPushButton("↧  Export CSV")
        self.export_btn.setObjectName("secondary")
        self.export_btn.clicked.connect(self.export_csv)
        header.addWidget(self.export_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        self.new_btn = QPushButton("＋  New entry")
        self.new_btn.clicked.connect(self.new_entry)
        header.addWidget(self.new_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        main_layout.addLayout(header)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(11)
        self.stats = {
            "total": StatCard("Total entries", ACCENT),
            "active": StatCard("Active", AMBER),
            "done": StatCard("Completed", GREEN),
            "overdue": StatCard("Overdue", RED),
        }
        for card in self.stats.values():
            stats_row.addWidget(card, 1)
        main_layout.addLayout(stats_row)

        # Split board/editor area. ScrollArea provides both vertical and horizontal scrolling.
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(8)
        main_layout.addWidget(splitter, 1)

        board_panel = QFrame()
        board_panel.setObjectName("panel")
        board_layout = QVBoxLayout(board_panel)
        board_layout.setContentsMargins(17, 16, 17, 14)
        board_layout.setSpacing(10)
        board_header = QHBoxLayout()
        board_header.addWidget(self.label("Planning board", "sectionTitle"))
        board_header.addStretch()
        self.occupied_label = self.label("0 / 81", "muted")
        board_header.addWidget(self.occupied_label)
        board_layout.addLayout(board_header)
        board_layout.addWidget(self.label("Select a cell to create or edit its task or goal.", "muted"))
        legend = QHBoxLayout()
        legend.setSpacing(13)
        for name, color in [("Empty", BORDER), ("Active", ACCENT), ("Completed", GREEN), ("Overdue", RED)]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{color}; border:none; font-size:10px;")
            txt = QLabel(name)
            txt.setObjectName("muted")
            legend.addWidget(dot)
            legend.addWidget(txt)
        legend.addStretch()
        board_layout.addLayout(legend)

        self.board_scroll = QScrollArea()
        self.board_scroll.setObjectName("boardScroll")
        self.board_scroll.setWidgetResizable(True)
        self.board_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.board_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.board_scroll.setMinimumHeight(220)
        board_widget = QWidget()
        board_widget.setStyleSheet("background:transparent;")
        self.board_grid = QGridLayout(board_widget)
        self.board_grid.setContentsMargins(3, 3, 8, 3)
        self.board_grid.setHorizontalSpacing(7)
        self.board_grid.setVerticalSpacing(7)
        for col in range(9):
            self.board_grid.setColumnMinimumWidth(col, 76)
        for row in range(9):
            self.board_grid.setRowMinimumHeight(row, 72)
        for slot in range(81):
            r, c = divmod(slot, 9)
            btn = QPushButton(f"{slot + 1:02}")
            btn.setMinimumSize(QSize(76, 72))
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setCheckable(False)
            btn.clicked.connect(lambda checked=False, s=slot: self.select_slot(s))
            self.board_grid.addWidget(btn, r, c)
            self.cell_buttons.append(btn)
        self.board_scroll.setWidget(board_widget)
        board_layout.addWidget(self.board_scroll, 1)
        board_footer = QHBoxLayout()
        board_footer.addWidget(self.label("81 slots · autosaved locally when you save", "muted"))
        board_footer.addStretch()
        self.board_percent = self.label("0% occupied", "muted")
        board_footer.addWidget(self.board_percent)
        board_layout.addLayout(board_footer)
        splitter.addWidget(board_panel)

        # Entry editor panel
        editor = QFrame()
        editor.setObjectName("panel")
        editor.setMinimumWidth(340)
        editor_layout = QVBoxLayout(editor)
        editor_layout.setContentsMargins(20, 17, 20, 18)
        editor_layout.setSpacing(13)
        editor_layout.addWidget(self.label("Entry editor", "sectionTitle"))
        self.slot_label = self.label("SLOT 01  /  ROW 1, COLUMN 1", "eyebrow")
        editor_layout.addWidget(self.slot_label)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(8)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g. Finish probability assignment")
        form.addRow("TITLE", self.title_input)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Add context, next actions, or notes…")
        self.description_input.setMinimumHeight(115)
        self.description_input.setMaximumHeight(180)
        form.addRow("DESCRIPTION", self.description_input)
        self.type_input = QComboBox()
        self.type_input.addItems(["Task", "Goal"])
        form.addRow("ENTRY TYPE", self.type_input)
        self.priority_input = QComboBox()
        self.priority_input.addItems(["Low", "Medium", "High", "Critical"])
        form.addRow("PRIORITY", self.priority_input)
        self.due_input = QLineEdit()
        self.due_input.setPlaceholderText("Optional · YYYY-MM-DD")
        form.addRow("DUE DATE", self.due_input)
        self.status_input = QComboBox()
        self.status_input.addItems(["Active", "Completed"])
        form.addRow("STATUS", self.status_input)
        editor_layout.addLayout(form)
        editor_layout.addWidget(self.label("Leave the due date blank if there is no deadline.", "muted"))

        save_row = QHBoxLayout()
        self.save_btn = QPushButton("Save entry")
        self.save_btn.clicked.connect(self.save_entry)
        self.complete_btn = QPushButton("✓  Mark complete")
        self.complete_btn.setObjectName("success")
        self.complete_btn.clicked.connect(self.mark_complete)
        save_row.addWidget(self.save_btn, 1)
        save_row.addWidget(self.complete_btn, 1)
        editor_layout.addLayout(save_row)
        actions = QHBoxLayout()
        self.clear_btn = QPushButton("Clear form")
        self.clear_btn.setObjectName("secondary")
        self.clear_btn.clicked.connect(self.clear_form)
        self.delete_btn = QPushButton("Delete entry")
        self.delete_btn.setObjectName("danger")
        self.delete_btn.clicked.connect(self.delete_entry)
        actions.addWidget(self.clear_btn, 1)
        actions.addWidget(self.delete_btn, 1)
        editor_layout.addLayout(actions)
        editor_layout.addStretch(1)
        splitter.addWidget(editor)
        splitter.setSizes([740, 470])

        # Search and filters
        search_panel = QFrame()
        search_panel.setObjectName("panel")
        search_layout = QHBoxLayout(search_panel)
        search_layout.setContentsMargins(13, 10, 13, 10)
        search_layout.setSpacing(10)
        search_layout.addWidget(self.label("SEARCH", "eyebrow"))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search titles and descriptions…")
        self.search.textChanged.connect(self.refresh)
        search_layout.addWidget(self.search, 1)
        self.filter_buttons = {}
        for value in ["All", "Active", "Completed", "Overdue"]:
            button = QPushButton(value)
            button.setObjectName("filter")
            button.setCheckable(True)
            button.setChecked(value == "All")
            button.clicked.connect(lambda checked=False, v=value: self.set_filter(v))
            self.filter_buttons[value] = button
            search_layout.addWidget(button)
        main_layout.addWidget(search_panel)

        self.status_line = self.label(f"Ready · Local database: {DB_PATH}", "muted")
        self.status_line.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        main_layout.addWidget(self.status_line)

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
        self.slot_label.setText(f"SLOT {slot + 1:02}  /  ROW {row + 1}, COLUMN {col + 1}")
        entry = self.store.get(slot)
        self.title_input.setText(entry["title"] if entry else "")
        self.description_input.setPlainText(entry["description"] if entry else "")
        self.type_input.setCurrentText(entry["entry_type"] if entry else "Task")
        self.priority_input.setCurrentText(entry["priority"] if entry else "Medium")
        self.due_input.setText(entry["due_date"] if entry else "")
        self.status_input.setCurrentText(entry["status"] if entry else "Active")
        self.refresh()

    def new_entry(self):
        empty = next((slot for slot in range(81) if self.store.get(slot) is None), None)
        if empty is None:
            QMessageBox.information(self, "Board is full", "All 81 slots are occupied. Delete an entry or export your board before making room.")
            return
        self.select_slot(empty)
        self.title_input.setFocus()
        self.status_line.setText(f"New entry in slot {empty + 1:02}. Fill in the form and select Save entry.")

    def clear_form(self):
        self.title_input.clear()
        self.description_input.clear()
        self.type_input.setCurrentText("Task")
        self.priority_input.setCurrentText("Medium")
        self.due_input.clear()
        self.status_input.setCurrentText("Active")
        self.status_line.setText("Form cleared. Saved data is unchanged until you save or delete.")

    def save_entry(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Title required", "Enter a title before saving.")
            self.title_input.setFocus()
            return
        due = self.due_input.text().strip()
        if due:
            try:
                date.fromisoformat(due)
            except ValueError:
                QMessageBox.warning(self, "Invalid due date", "Use YYYY-MM-DD, for example 2026-12-31.")
                self.due_input.setFocus()
                return
        self.store.save(self.selected_slot, title, self.description_input.toPlainText().strip(),
                        self.type_input.currentText(), self.priority_input.currentText(), due,
                        self.status_input.currentText())
        self.refresh()
        self.status_line.setText(f"Saved to slot {self.selected_slot + 1:02} · {datetime.now().strftime('%H:%M:%S')}")

    def mark_complete(self):
        if not self.title_input.text().strip() and self.store.get(self.selected_slot) is None:
            QMessageBox.information(self, "No entry selected", "Create and save an entry before marking it complete.")
            return
        self.status_input.setCurrentText("Completed")
        self.save_entry()

    def delete_entry(self):
        entry = self.store.get(self.selected_slot)
        if not entry:
            self.clear_form()
            return
        answer = QMessageBox.question(self, "Delete entry",
            f"Delete '{entry['title']}' from slot {self.selected_slot + 1:02}? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.store.delete(self.selected_slot)
        self.clear_form()
        self.refresh()
        self.status_line.setText(f"Deleted slot {self.selected_slot + 1:02}.")

    def set_filter(self, value):
        self.filter_mode = value
        for key, button in self.filter_buttons.items():
            button.setChecked(key == value)
        self.refresh()

    def refresh(self, *_):
        entries = self.store.all()
        self.entries_by_slot = {entry["slot"]: entry for entry in entries}
        total = len(entries)
        done = sum(e["status"] == "Completed" for e in entries)
        active = sum(e["status"] == "Active" for e in entries)
        overdue = sum(self.is_overdue(e) for e in entries)
        for key, value in [("total", total), ("active", active), ("done", done), ("overdue", overdue)]:
            self.stats[key].value.setText(str(value))
        self.occupied_label.setText(f"{total} / 81 occupied")
        self.board_percent.setText(f"{round(total / 81 * 100)}% occupied")
        query = self.search.text().strip().casefold() if hasattr(self, "search") else ""
        for slot, button in enumerate(self.cell_buttons):
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
                label, fill, fg = f"{slot + 1:02}\nEMPTY", "#121D31", MUTED
            else:
                title = entry["title"]
                short = title[:11] + ("…" if len(title) > 11 else "")
                marker = "✓" if entry["status"] == "Completed" else ("!" if self.is_overdue(entry) else "•")
                label = f"{slot + 1:02}  {marker}\n{short}"
                fill = GREEN if entry["status"] == "Completed" else (RED if self.is_overdue(entry) else ACCENT_DARK)
                fg = "#FFFFFF"
            if not visible:
                fill, fg = "#0D1422", "#4A5870"
            if selected:
                border = f"2px solid {ACCENT};"
            else:
                border = f"1px solid {BORDER};"
            button.setText(label)
            button.setStyleSheet(f"QPushButton {{ background:{fill}; color:{fg}; border:{border} border-radius:10px; padding:5px; font-size:11px; font-weight:650; text-align:center; }} QPushButton:hover {{ background:{PANEL_HOVER}; border:1px solid {ACCENT}; color:{TEXT}; }}")
            button.setToolTip(f"Slot {slot + 1:02}" + (f"\n{entry['title']}\n{entry['status']} · {entry['priority']}" if entry else "\nEmpty slot"))

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export planner entries", str(Path.home() / "marada_planner_export.csv"), "CSV files (*.csv)")
        if not path:
            return
        if not path.lower().endswith(".csv"):
            path += ".csv"
        fields = ["slot", "row", "column", "title", "description", "entry_type", "priority", "due_date", "status", "created_at", "updated_at"]
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
            self.status_line.setText(f"Exported {len(self.store.all())} entries to {path}")
            QMessageBox.information(self, "Export complete", f"Entries exported to:\n{path}")
        except OSError as exc:
            QMessageBox.critical(self, "Export failed", f"Could not write the CSV file.\n\n{exc}")

    def closeEvent(self, event):
        self.store.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    app.setFont(QFont("Segoe UI", 10))
    window = MaradaPlanner()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
