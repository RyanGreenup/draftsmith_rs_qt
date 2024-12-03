from typing import List, Optional
from PySide6.QtWidgets import (
    QSplitter,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QLabel,
    QWidget,
    QVBoxLayout,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from models.note import Note
from api.client import Tag


class NavigableListWidget(QListWidget):
    """Base class for list widgets with keyboard navigation"""
    
    note_selected = Signal(int)  # Signal emitted when a note is selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.itemActivated.connect(self._on_item_activated)

    def _on_item_double_clicked(self, item):
        """Handle double click on item"""
        self._emit_note_selected(item)

    def _on_item_activated(self, item):
        """Handle item activation (Enter key)"""
        self._emit_note_selected(item)

    def _emit_note_selected(self, item):
        """Emit note_selected signal if item has valid note_id"""
        if item:
            note_id = item.data(Qt.ItemDataRole.UserRole)
            if note_id is not None and note_id != -1:  # Ignore placeholder items
                self.note_selected.emit(note_id)

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
        else:
            super().keyPressEvent(event)


class BacklinksWidget(NavigableListWidget):
    """Widget for displaying backlinks to the current note"""
    
    def __init__(self, parent=None):
        super().__init__(parent)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        self._select_current_note()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Return:
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
            item.setFlags(
                item.flags() & ~Qt.ItemFlag.ItemIsEnabled
            )  # Make non-clickable
            self.addItem(item)
            return

        for note in backlinks:
            item = QListWidgetItem(note.title)
            item.setData(Qt.ItemDataRole.UserRole, note.id)
            self.addItem(item)


class ForwardLinksWidget(NavigableListWidget):
    """Widget for displaying forward links from the current note"""
    
    def __init__(self, parent=None):
        super().__init__(parent)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        self._select_current_note()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Return:
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


class TagsWidget(NavigableListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemDoubleClicked.connect(self._show_not_implemented)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Return:
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
            item.setFlags(
                item.flags() & ~Qt.ItemFlag.ItemIsEnabled
            )  # Make non-clickable
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

        # Create containers for each section
        backlinks_container = QWidget()
        forward_links_container = QWidget()
        tags_container = QWidget()
        similar_container = QWidget()

        # Create layouts for each container
        backlinks_layout = QVBoxLayout(backlinks_container)
        forward_links_layout = QVBoxLayout(forward_links_container)
        tags_layout = QVBoxLayout(tags_container)
        similar_layout = QVBoxLayout(similar_container)

        # Create and add labels
        backlinks_layout.addWidget(QLabel("Backlinks"))
        backlinks_layout.addWidget(self.backlinks)

        forward_links_layout.addWidget(QLabel("Forward Links"))
        forward_links_layout.addWidget(self.forward_links)

        tags_layout.addWidget(QLabel("Tags"))
        tags_layout.addWidget(self.tags)

        similar_layout.addWidget(QLabel("Similar Pages"))
        similar_layout.addWidget(self.text_bottom)

        # Remove margins to make it more compact
        for layout in (
            backlinks_layout,
            forward_links_layout,
            tags_layout,
            similar_layout,
        ):
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(2)

        # Add containers to splitter
        self.addWidget(backlinks_container)
        self.addWidget(forward_links_container)
        self.addWidget(tags_container)
        self.addWidget(similar_container)

        # Set minimum heights
        backlinks_container.setMinimumHeight(100)
        forward_links_container.setMinimumHeight(100)
        tags_container.setMinimumHeight(100)

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
