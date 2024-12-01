from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QTextEdit,
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeyEvent
from typing import Optional, Union
from enum import IntEnum
import sys

class Key(IntEnum):
    """Define key constants to satisfy type checker"""
    Key_J = Qt.Key.Key_J
    Key_K = Qt.Key.Key_K
    Key_Space = Qt.Key.Key_Space
    Key_Right = Qt.Key.Key_Right
    Key_Left = Qt.Key.Key_Left
    Key_Down = Qt.Key.Key_Down
    Key_Up = Qt.Key.Key_Up


class NotesTreeWidget(QTreeWidget):
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Key.Key_J:
            # Create a new QKeyEvent for Down key
            new_event = QKeyEvent(QEvent.Type.KeyPress, Key.Key_Down, event.modifiers())
            super().keyPressEvent(new_event)

        elif event.key() == Key.Key_K:
            # Create a new QKeyEvent for Up key
            new_event = QKeyEvent(QEvent.Type.KeyPress, Key.Key_Up, event.modifiers())
            super().keyPressEvent(new_event)

        elif event.key() in (Key.Key_Space, Key.Key_Right, Key.Key_Left):
            current = self.currentItem()
            if current:
                if event.key() == Key.Key_Left:
                    current.setExpanded(False)
                elif event.key() == Key.Key_Right:
                    current.setExpanded(True)
                elif event.key() == Key.Key_Space:
                    current.setExpanded(not current.isExpanded())
        else:
            super().keyPressEvent(event)


class Note:
    def __init__(self, title, content=""):
        self.title = title
        self.content = content


class NoteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Note Taking App")
        self.setGeometry(100, 100, 1000, 600)

        # Create main splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create tree widget for sidebar
        self.tree = NotesTreeWidget()
        self.tree.setHeaderLabel("Notes")
        self.tree.setMinimumWidth(200)
        self.tree.itemSelectionChanged.connect(self.on_selection_changed)

        # Create text edit for main content
        self.text_edit = QTextEdit()

        # Add widgets to splitter
        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.text_edit)

        # Set splitter as central widget
        self.setCentralWidget(self.splitter)

        # Add dummy data
        self.add_dummy_data()

    def on_selection_changed(self):
        selected_items = self.tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            note = item.data(0, Qt.UserRole)
            if note:
                self.text_edit.setText(note.content)
            else:
                self.text_edit.clear()

    def add_dummy_data(self):
        notes_hierarchy = {
            Note("Work", "General work-related notes and tasks"): [
                Note(
                    "Meeting Notes",
                    "Meeting agenda:\n1. Project updates\n2. Timeline review",
                ),
                Note(
                    "Project Ideas",
                    "New features to implement:\n- Dark mode\n- Auto-save",
                ),
                Note("To-Do List", "- Send report\n- Update documentation"),
            ],
            Note("Personal", "My personal notes and plans"): [
                Note("Shopping List", "- Groceries\n- Household items"),
                Note("Travel Plans", "Places to visit:\n1. Paris\n2. Tokyo"),
                Note("Goals", "2024 Goals:\n1. Learn Python\n2. Exercise more"),
            ],
        }

        for parent_note, child_notes in notes_hierarchy.items():
            parent_item = QTreeWidgetItem(self.tree)
            parent_item.setText(0, parent_note.title)
            parent_item.setData(0, Qt.UserRole, parent_note)

            for child_note in child_notes:
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, child_note.title)
                child_item.setData(0, Qt.UserRole, child_note)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteApp()
    window.show()
    sys.exit(app.exec())
