from typing import Optional, Dict, Any, Set, List, Union
from PySide6.QtWidgets import QTreeWidget, QApplication, QTreeWidgetItem
from PySide6.QtCore import QEvent, Qt
from models.note import Note
from models.notes_model import NotesModel
from PySide6.QtGui import QKeyEvent
from utils.key_constants import Key


class NotesTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_fold_level: int = -1  # -1 means all collapsed
        self.notes_model: Optional[NotesModel] = None
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def set_model(self, model: "NotesModel"):
        """Set the notes model for this tree widget"""
        self.notes_model = model
        # Disconnect any existing connections first
        try:
            self.notes_model.notes_updated.disconnect()
        except:
            pass
        # Connect to the model's update signal
        if self.notes_model is not None:
            self.notes_model.notes_updated.connect(
                lambda: (
                    self.update_tree(self.notes_model.root_notes)
                    if self.notes_model is not None
                    else None
                )
            )

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

    def select_note_by_id(self, note_id: int) -> None:
        """Select the tree item corresponding to the given note ID"""

        def find_and_select_item(item):
            # Check current item
            note_data = item.data(0, Qt.ItemDataRole.UserRole)
            if note_data and note_data.id == note_id:
                self.setCurrentItem(item)
                self.scrollToItem(item)
                return True

            # Check children
            for i in range(item.childCount()):
                if find_and_select_item(item.child(i)):
                    return True
            return False

        # Search through top-level items
        for i in range(self.topLevelItemCount()):
            if find_and_select_item(self.topLevelItem(i)):
                break

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

    def save_state(self) -> Dict[str, Any]:
        """Save the tree state, including expanded items and selected item."""
        state = {
            "expanded_items": self._get_expanded_item_ids(),
            "selected_item_id": self._get_selected_item_id(),
        }
        return state

    def restore_state(self, state: Dict[str, Any]) -> None:
        """
        Restore expansion and selection state where possible, without modifying tree structure.
        Only expands/selects items that exist in the current tree.
        """
        if "expanded_items" in state:
            self._set_expanded_items_by_id(state["expanded_items"])

        if "selected_item_id" in state and state["selected_item_id"] is not None:
            self.select_note_by_id(state["selected_item_id"])

    def _get_expanded_item_ids(self) -> Set[int]:
        expanded_ids = set()

        def recurse(item):
            if item.isExpanded():
                note_data = item.data(0, Qt.ItemDataRole.UserRole)
                if note_data:
                    expanded_ids.add(note_data.id)
            for i in range(item.childCount()):
                recurse(item.child(i))

        for i in range(self.topLevelItemCount()):
            recurse(self.topLevelItem(i))

        return expanded_ids

    def _set_expanded_items_by_id(self, expanded_ids: Set[int]) -> None:
        """Set expansion state only for items that exist in the tree"""

        def recurse(item):
            note_data = item.data(0, Qt.ItemDataRole.UserRole)
            if note_data and note_data.id in expanded_ids:
                # Expand parents first to ensure proper expansion
                parent = item.parent()
                while parent:
                    parent.setExpanded(True)
                    parent = parent.parent()
                item.setExpanded(True)
            for i in range(item.childCount()):
                recurse(item.child(i))

        for i in range(self.topLevelItemCount()):
            recurse(self.topLevelItem(i))

    def _get_selected_item_id(self) -> Optional[int]:
        current_item = self.currentItem()
        if current_item:
            note_data = current_item.data(0, Qt.ItemDataRole.UserRole)
            if note_data:
                return note_data.id
        return None

    def update_tree(self, root_notes: List[Note]) -> None:
        """Update the tree widget to reflect the model's state"""
        # Save current state before update
        state = self.save_state()

        # Clear and rebuild tree
        self.clear()

        # Add all root notes
        for note in root_notes:
            self._add_note_to_tree(note, self)

        # Restore state after update
        self.restore_state(state)

    def _add_note_to_tree(
        self, note: Note, parent: Union[QTreeWidget, QTreeWidgetItem]
    ) -> None:
        """Add a note and its children to the tree, reflecting model structure"""
        # Create item for current note
        item = QTreeWidgetItem()
        item.setText(0, note.title)
        item.setData(0, Qt.ItemDataRole.UserRole, note)

        # Add to parent
        if isinstance(parent, QTreeWidget):
            parent.addTopLevelItem(item)
        else:
            parent.addChild(item)

        # Add children, following model's structure
        for child in note.children:
            self._add_note_to_tree(child, item)
