from typing import Optional, Dict, Any, Set, List, Union
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from widgets.navigable_tree import NavigableTree
from api.client import TreeTagWithNotes, Tag, TreeNote


class TagsTreeWidget(NavigableTree):
    tag_selected = Signal(int)  # Signal emitted when a tag is selected
    note_selected = Signal(int)  # Signal emitted when a note is selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self.notes_model: Optional[Any] = None
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def set_model(self, model: Any):
        """Set the notes model for this tree widget"""
        # First disconnect from old model if it exists
        if self.notes_model is not None:
            try:
                self.notes_model.notes_updated.disconnect(self.update_tree_from_model)
            except TypeError:  # Signal wasn't connected
                pass

        # Set new model
        self.notes_model = model

        # Connect to new model if it exists
        if self.notes_model is not None:
            self.notes_model.notes_updated.connect(self.update_tree_from_model)
            # Initial update
            self.update_tree(self.notes_model.get_tags_tree())

    def update_tree_from_model(self):
        """Callback for model updates to refresh the tree"""
        if self.notes_model is not None:
            # Save state before update
            state = self.save_state()

            # Update tree
            self.update_tree(self.notes_model.get_tags_tree())

            # Restore state after update
            self.restore_state(state)

    def _on_selection_changed(self):
        """Handle selection changes and notify model"""
        current = self.currentItem()
        if current and self.notes_model:
            item_data = current.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(item_data, TreeTagWithNotes):
                self.notes_model.select_tag(item_data.id)
                self.tag_selected.emit(item_data.id)
            elif isinstance(item_data, TreeNote):
                self.notes_model.select_note(item_data.id)
                self.note_selected.emit(item_data.id)

    def update_tree(self, root_tags: List[TreeTagWithNotes]) -> None:
        """Update the tree widget to reflect the model's state"""
        # Save current state before update
        state = self.save_state()

        # Clear and rebuild tree
        self.clear()

        # Add all root tags
        for tag in root_tags:
            self._add_tag_to_tree(tag, self)

        # Restore state after update
        self.restore_state(state)

        # Expand all items to show notes
        self.expandAll()

        # Debug print
        print(f"Updated tree with {len(root_tags)} root tags")

    def _add_tag_to_tree(
        self, tag: TreeTagWithNotes, parent: Union[QTreeWidgetItem, 'TagsTreeWidget']
    ) -> None:
        """Add a tag, its children, and its notes to the tree"""
        # Create item for current tag
        tag_item = QTreeWidgetItem()
        tag_item.setText(0, tag.name)
        tag_item.setData(0, Qt.ItemDataRole.UserRole, tag)

        # Make tags bold
        font = tag_item.font(0)
        font.setBold(True)
        tag_item.setFont(0, font)

        # Add to parent
        if isinstance(parent, TagsTreeWidget):
            parent.addTopLevelItem(tag_item)
        else:
            parent.addChild(tag_item)

        # Add notes under this tag
        for note in tag.notes:
            note_item = QTreeWidgetItem(tag_item)
            note_item.setText(0, note.title)
            note_item.setData(0, Qt.ItemDataRole.UserRole, note)
            # Make notes a different color
            note_item.setForeground(0, QColor(0, 128, 0))  # Green color

        # Add children tags
        for child in tag.children:
            self._add_tag_to_tree(child, tag_item)

        # Debug print
        print(f"Added tag: {tag.name} with {len(tag.notes)} notes")

    def create_tag(self, name: str, parent_item: Optional[QTreeWidgetItem] = None):
        if self.notes_model:
            parent_id = None
            if parent_item:
                parent_tag = parent_item.data(0, Qt.ItemDataRole.UserRole)
                parent_id = parent_tag.id if parent_tag else None
            tag = self.notes_model.create_tag(name, parent_id)
            if tag:
                self.update_tree_from_model()

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
            self.select_tag_by_id(state["selected_item_id"])

    def _get_expanded_item_ids(self) -> Set[int]:
        expanded_ids = set()

        def recurse(item):
            if item.isExpanded():
                tag_data = item.data(0, Qt.ItemDataRole.UserRole)
                if tag_data:
                    expanded_ids.add(tag_data.id)
            for i in range(item.childCount()):
                recurse(item.child(i))

        for i in range(self.topLevelItemCount()):
            recurse(self.topLevelItem(i))

        return expanded_ids

    def _set_expanded_items_by_id(self, expanded_ids: Set[int]) -> None:
        """Set expansion state only for items that exist in the tree"""

        def recurse(item):
            tag_data = item.data(0, Qt.ItemDataRole.UserRole)
            if tag_data and tag_data.id in expanded_ids:
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
            tag_data = current_item.data(0, Qt.ItemDataRole.UserRole)
            if tag_data:
                return tag_data.id
        return None

    def select_tag_by_id(self, tag_id: int) -> None:
        """Select the tree item corresponding to the given tag ID"""

        def find_and_select_item(item):
            # Check current item
            tag_data = item.data(0, Qt.ItemDataRole.UserRole)
            if tag_data and tag_data.id == tag_id:
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
