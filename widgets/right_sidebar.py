from typing import List, Optional
from PySide6.QtWidgets import (
    QSplitter, 
    QTextEdit, 
    QListWidget, 
    QListWidgetItem,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from models.note import Note
from api.client import Tag

class BacklinksWidget(QListWidget):
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

    def update_links(self, backlinks: List[Note]) -> None:
        """Update the list with new backlinks"""
        self.clear()
        if not backlinks:
            item = QListWidgetItem("No backlinks")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)  # Make non-clickable
            self.addItem(item)
            return

        for note in backlinks:
            item = QListWidgetItem(note.title)
            item.setData(Qt.ItemDataRole.UserRole, note.id)
            self.addItem(item)


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


class TagsWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemDoubleClicked.connect(self._show_not_implemented)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard navigation"""
        if event.key() in (Qt.Key.Key_J, Qt.Key.Key_K, Qt.Key.Key_Return):
            self._show_not_implemented()
            event.accept()
        else:
            super().keyPressEvent(event)

    def _show_not_implemented(self, item: Optional[QListWidgetItem] = None) -> None:
        """Show not implemented message"""
        QMessageBox.information(
            self,
            "Not Implemented",
            "Tag interaction functionality is not yet implemented.",
        )

    def update_tags(self, tags: List[Tag]) -> None:
        """Update the list with new tags"""
        self.clear()
        if not tags:
            item = QListWidgetItem("No tags")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)  # Make non-clickable
            self.addItem(item)
            return

        for tag in tags:
            item = QListWidgetItem(tag.name)
            item.setData(Qt.ItemDataRole.UserRole, tag.id)
            self.addItem(item)


class RightSidebar(QSplitter):
    def __init__(self, handle_size=20, parent=None):
        super().__init__(Qt.Orientation.Vertical, parent)
        self.backlinks = BacklinksWidget()
        self.forward_links = ForwardLinksWidget()
        self.tags = TagsWidget()
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
        self.backlinks.setMinimumHeight(100)
        self.forward_links.setMinimumHeight(100)
        self.tags.setMinimumHeight(100)
        self.text_bottom.setPlaceholderText(
            "Similar Pages (Not Yet Implemented, Don't Touch)"
        )

    def update_backlinks(self, backlinks: List[Note]) -> None:
        """Update the backlinks list with linked notes"""
        self.backlinks.update_links(backlinks)

    def update_forward_links(self, forward_links: List[Note]) -> None:
        """Update the forward links list with linked notes"""
        self.forward_links.update_links(forward_links)

    def update_tags(self, tags: List[Tag]) -> None:
        """Update the tags list"""
        self.tags.update_tags(tags)
