from typing import Optional
from PySide6.QtWidgets import QTreeWidget, QApplication, QTreeWidgetItem
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from utils.key_constants import Key


class NotesTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_fold_level = -1  # -1 means all collapsed
        self.notes_model = None
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def set_model(self, model: 'NotesModel'):
        """Set the notes model for this tree widget"""
        self.notes_model = model

    def _on_selection_changed(self):
        """Handle selection changes and notify model"""
        current = self.currentItem()
        if current and self.notes_model:
            note_data = current.data(0, Qt.ItemDataRole.UserRole)
            if note_data:
                self.notes_model.select_note(note_data.id)

    def set_fold_level_recursive(
        self, item: QTreeWidgetItem, current_depth: int, max_depth: int
    ):
        """Recursively set fold level of items."""
        if current_depth <= max_depth:
            item.setExpanded(True)
            for i in range(item.childCount()):
                self.set_fold_level_recursive(
                    item.child(i), current_depth + 1, max_depth
                )
        else:
            item.setExpanded(False)

    def get_max_depth(
        self, item: Optional[QTreeWidgetItem] = None, current_depth: int = 0
    ) -> int:
        """Get the maximum depth of the tree."""
        if item is None:
            max_depth = 0
            for i in range(self.topLevelItemCount()):
                depth = self.get_max_depth(self.topLevelItem(i))
                max_depth = max(max_depth, depth)
            return max_depth

        max_child_depth = current_depth
        for i in range(item.childCount()):
            depth = self.get_max_depth(item.child(i), current_depth + 1)
            max_child_depth = max(max_child_depth, depth)
        return max_child_depth

    def cycle_fold_level_of_all_items(self):
        """Cycle the fold level of all items in the tree."""
        if self.topLevelItemCount() == 0:
            return

        max_depth = self.get_max_depth()
        self.current_fold_level = (self.current_fold_level + 1) % (
            max_depth + 1
        )  # +1 for all-collapsed state

        # When we reach max_depth (fully expanded), next press should collapse all
        if self.current_fold_level == max_depth:
            self.current_fold_level = -1
            for i in range(self.topLevelItemCount()):
                self.set_fold_level_recursive(self.topLevelItem(i), 0, -1)
        else:
            for i in range(self.topLevelItemCount()):
                self.set_fold_level_recursive(
                    self.topLevelItem(i), 0, self.current_fold_level
                )

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
                elif (
                    event.key() == Key.Key_Space
                    and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier
                ):
                    current.setExpanded(not current.isExpanded())
                elif (
                    event.key() == Key.Key_Space
                    and event.modifiers() & Qt.KeyboardModifier.ShiftModifier
                ):
                    self.cycle_fold_level_of_all_items()
        else:
            super().keyPressEvent(event)
