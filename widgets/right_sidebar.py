from typing import List, Optional
from PySide6.QtWidgets import QSplitter, QTextEdit, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from .notes_tree import NotesTreeWidget
from models.note import Note


class ForwardLinksWidget(QListWidget):
    note_selected = Signal(int)  # Emitted when a note is selected, passes note_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        self._select_current_note()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard navigation"""
        if event.key() == Qt.Key.Key_J:
            # Move down
            current_row = self.currentRow()
            if current_row < self.count() - 1:
                self.setCurrentRow(current_row + 1)
            event.accept()
        elif event.key() == Qt.Key.Key_K:
            # Move up
            current_row = self.currentRow()
            if current_row > 0:
                self.setCurrentRow(current_row - 1)
            event.accept()
        elif event.key() == Qt.Key.Key_Return:
            # Select current note
            self._select_current_note()
            event.accept()
        else:
            super().keyPressEvent(event)

    def _select_current_note(self) -> None:
        """Helper method to select the current note"""
        current_item = self.currentItem()
        if current_item:
            note_id = current_item.data(Qt.ItemDataRole.UserRole)
            if note_id:
                self.note_selected.emit(note_id)

    def update_links(self, forward_links: List[Note]) -> None:
        """Update the list with new forward links"""
        self.clear()
        if not forward_links:
            item = QListWidgetItem("No forward links")
            item.setFlags(
                item.flags() & ~Qt.ItemFlag.ItemIsEnabled
            )  # Make non-clickable
            self.addItem(item)
            return

        for note in forward_links:
            item = QListWidgetItem(note.title)
            item.setData(Qt.ItemDataRole.UserRole, note.id)
            self.addItem(item)


class RightSidebar(QSplitter):
    def __init__(self, handle_size=20, parent=None):
        super().__init__(Qt.Orientation.Vertical, parent)
        self.backlinks = NotesTreeWidget()
        self.forward_links = ForwardLinksWidget()
        self.tags = QTextEdit()
        self.text_bottom = QTextEdit()

        self._setup_ui(handle_size)

    def _setup_ui(self, handle_size):
        self.setHandleWidth(handle_size)

        # First add all widgets to the splitter
        self.addWidget(self.backlinks)
        self.addWidget(self.forward_links)
        self.addWidget(self.tags)
        self.addWidget(self.text_bottom)

        # Then set up their properties
        self.backlinks.setHeaderLabel("Backlinks")
        self.backlinks.setMinimumWidth(200)

        self.forward_links.setMinimumHeight(100)
        self.tags.setPlaceholderText("Tags")
        self.text_bottom.setPlaceholderText(
            "Similar Pages (Not Yet Implemented, Don't Touch)"
        )

    def update_forward_links(self, forward_links: List[Note]) -> None:
        """Update the forward links list with linked notes"""
        self.forward_links.update_links(forward_links)
