from typing import Optional
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QKeyEvent
from draftsmith_qt.utils.key_constants import Key


class NavigableTree(QTreeWidget):
    """Base class for tree widgets with keyboard navigation"""

    note_selected = Signal(int)  # Emitted when a note is selected
    note_selected_with_focus = Signal(
        int
    )  # Emitted when a note is selected with focus request

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_fold_level: int = -1  # -1 means all collapsed

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

            # Explicitly collapse all items at every level
            def collapse_all(item: Optional[QTreeWidgetItem] = None):
                items = []
                if item is None:
                    for i in range(self.topLevelItemCount()):
                        items.append(self.topLevelItem(i))
                else:
                    items = [item]

                for current in items:
                    current.setExpanded(False)
                    for i in range(current.childCount()):
                        collapse_all(current.child(i))

            collapse_all()
        else:
            for i in range(self.topLevelItemCount()):
                self.set_fold_level_recursive(
                    self.topLevelItem(i), 0, self.current_fold_level
                )

    def _handle_return(self, event: QKeyEvent) -> bool:
        """Handle Return/Enter key press"""
        current = self.currentItem()
        if current:
            note_data = current.data(0, Qt.ItemDataRole.UserRole)
            if note_data:
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    self.note_selected_with_focus.emit(note_data.id)
                else:
                    self.note_selected.emit(note_data.id)
                return True
        return False

    def _handle_navigation_key(self, event: QKeyEvent) -> bool:
        """Handle J/K navigation keys"""
        if event.key() == Key.Vim_Down:
            new_event = QKeyEvent(QEvent.Type.KeyPress, Key.Key_Down, event.modifiers())
            super().keyPressEvent(new_event)
            return True
        elif event.key() == Key.Vim_Up:
            new_event = QKeyEvent(QEvent.Type.KeyPress, Key.Key_Up, event.modifiers())
            super().keyPressEvent(new_event)
            return True
        return False

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard navigation"""
        if event.key() == Qt.Key.Key_Return:
            if self._handle_return(event):
                event.accept()
                return
        elif self._handle_navigation_key(event):
            event.accept()
            return
        else:
            super().keyPressEvent(event)

    def _create_context_menu(self) -> QMenu:
        """Create and return the context menu"""
        menu = QMenu(self)

        # Add basic menu items - subclasses can override this method to add more items
        expand_action = menu.addAction("Expand")
        expand_action.triggered.connect(lambda: self.currentItem().setExpanded(True))

        collapse_action = menu.addAction("Collapse")
        collapse_action.triggered.connect(lambda: self.currentItem().setExpanded(False))

        return menu

    def contextMenuEvent(self, event):
        """Handle right click events"""
        current_item = self.currentItem()
        if current_item:
            menu = self._create_context_menu()
            menu.exec(event.globalPos())
