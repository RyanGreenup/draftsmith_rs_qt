from PySide6.QtWidgets import QListWidget
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent


class NavigableListWidget(QListWidget):
    """Base class for list widgets with keyboard navigation"""

    note_selected = Signal(int)  # Signal emitted when a note is selected
    note_selected_with_focus = Signal(int)  # Signal emitted when a note should be selected and focused

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.itemActivated.connect(self._on_item_activated)

    def mouseReleaseEvent(self, event):
        """Handle mouse button releases"""
        if event.button() == Qt.MouseButton.MiddleButton:
            item = self.itemAt(event.pos())
            if item:
                note_id = item.data(Qt.ItemDataRole.UserRole)
                if note_id is not None and note_id != -1:
                    self.note_selected.emit(note_id)
        super().mouseReleaseEvent(event)

    def _on_item_double_clicked(self, item):
        """Handle double click on item"""
        if item:
            note_id = item.data(Qt.ItemDataRole.UserRole)
            if note_id is not None and note_id != -1:
                self.note_selected_with_focus.emit(note_id)

    def _on_item_activated(self, item):
        """Handle item activation (Enter key)"""
        if item:
            note_id = item.data(Qt.ItemDataRole.UserRole)
            if note_id is not None and note_id != -1:
                self.note_selected.emit(note_id)

    def _handle_return(self, event: QKeyEvent) -> bool:
        """Handle return key press, returns True if handled"""
        current_item = self.currentItem()
        if current_item:
            note_id = current_item.data(Qt.ItemDataRole.UserRole)
            if note_id:
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    self.note_selected_with_focus.emit(note_id)
                else:
                    self.note_selected.emit(note_id)
                return True
        return False

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard navigation"""
        if event.key() == Qt.Key.Key_Return:
            if self._handle_return(event):
                event.accept()
                return
        elif event.key() == Qt.Key.Key_J:
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

