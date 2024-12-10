from typing import Optional, Dict, Any, Set, List, Union
from PySide6.QtWidgets import QTreeWidgetItem, QStyle, QMenu, QMessageBox, QTreeWidget
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QIcon
from widgets.navigable_tree import NavigableTree
from api.client import TreeTagWithNotes, Tag, TreeNote


class TagsTreeWidget(NavigableTree):
    tag_selected = Signal(int)  # Signal emitted when a tag is selected
    note_selected = Signal(int)  # Signal emitted when a note is selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self.notes_model: Optional[Any] = None
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemChanged.connect(self.on_item_changed)
        self.editing_item = None
        # Enable drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)

    def edit_item_in_place(self, item, column=0):
        self.editing_item = item
        self.openPersistentEditor(item, column)
        self.editItem(item, column)
        QTimer.singleShot(0, lambda: self.setCurrentItem(item))

    def set_model(self, model: NotesModel):
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
            self.update_tree_from_model()

    def show_context_menu(self, position):
        item = self.itemAt(position)
        context_menu = QMenu(self)
        
        # Add ID label if item exists
        if item:
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(item_data, TreeTagWithNotes):
                id_label = context_menu.addAction(f"Tag ID: {item_data.id}")
            elif isinstance(item_data, TreeNote):
                id_label = context_menu.addAction(f"Note ID: {item_data.id}")
            else:
                id_label = context_menu.addAction("Unknown item type")
            id_label.setEnabled(False)  # Make the label non-clickable
            context_menu.addSeparator()  # Add a separator after the ID label
        
        create_tag_action = context_menu.addAction("Create New Tag")
        
        rename_tag_action = None
        delete_tag_action = None
        if item and isinstance(item.data(0, Qt.ItemDataRole.UserRole), TreeTagWithNotes):
            rename_tag_action = context_menu.addAction("Rename Tag")
            delete_tag_action = context_menu.addAction("Delete Tag")

        action = context_menu.exec_(self.mapToGlobal(position))
        
        if action == create_tag_action:
            self.create_new_tag(item)
        elif action == rename_tag_action:
            self.rename_tag(item)
        elif action == delete_tag_action:
            self.delete_tag(item)

    def create_new_tag(self, parent_item):
        new_item = QTreeWidgetItem(["New Tag"])
        if parent_item:
            parent_item.addChild(new_item)
            parent_item.setExpanded(True)
        else:
            self.addTopLevelItem(new_item)
        
        new_item.setData(0, Qt.ItemDataRole.UserRole, TreeTagWithNotes(id=-1, name="New Tag", children=[], notes=[]))
        self.edit_item_in_place(new_item)

    def rename_tag(self, item):
        if isinstance(item.data(0, Qt.ItemDataRole.UserRole), TreeTagWithNotes):
            self.edit_item_in_place(item)

    def on_item_changed(self, item, column):
        if item == self.editing_item:
            self.editing_item = None
            tag_data = item.data(0, Qt.ItemDataRole.UserRole)
            new_name = item.text(column)
            
            if isinstance(tag_data, TreeTagWithNotes):
                if tag_data.id == -1:  # New tag
                    created_tag = self.notes_model.create_tag(new_name, parent_id=item.parent().data(0, Qt.ItemDataRole.UserRole).id if item.parent() else None)
                    if created_tag:
                        item.setData(0, Qt.ItemDataRole.UserRole, created_tag)
                    else:
                        QMessageBox.warning(self, "Error", "Failed to create tag.")
                        self.takeTopLevelItem(self.indexOfTopLevelItem(item))
                else:  # Existing tag
                    updated_tag = self.notes_model.update_tag(tag_data.id, new_name)
                    if not updated_tag:
                        QMessageBox.warning(self, "Error", "Failed to rename tag.")
                        item.setText(column, tag_data.name)  # Revert to old name
            
            self.update_tree_from_model()

    def delete_tag(self, item):
        tag = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(tag, TreeTagWithNotes) and self.notes_model:
            reply = QMessageBox.question(self, 'Delete Tag', 
                                         f"Are you sure you want to delete the tag '{tag.name}'?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.notes_model.delete_tag(tag.id):
                    self.update_tree_from_model()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete tag.")

    def update_tree_from_model(self):
        """Callback for model updates to refresh the tree"""
        if self.notes_model is not None:
            # Save state before update
            state = self.save_state()

            # Update tree
            self.update_tree(self.notes_model.get_tags_tree())

            # Restore state after update
            self.restore_state(state)

    def dragEnterEvent(self, event):
        if event.source() == self:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.source() == self:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.source() == self:
            dragged_item = self.currentItem()
            target_item = self.itemAt(event.pos())

            if not dragged_item or dragged_item == target_item:
                event.ignore()
                return

            dragged_data = dragged_item.data(0, Qt.ItemDataRole.UserRole)
            target_data = target_item.data(0, Qt.ItemDataRole.UserRole) if target_item else None

            event.setDropAction(Qt.DropAction.IgnoreAction)
            event.accept()

            if isinstance(dragged_data, TreeTagWithNotes):
                self._handle_tag_drop(dragged_data, target_data)
            elif isinstance(dragged_data, TreeNote):
                self._handle_note_drop(dragged_data, target_data)

            self.update_tree_from_model()
        else:
            event.ignore()

    def _handle_tag_drop(self, dragged_tag: TreeTagWithNotes, target_data: Optional[Union[TreeTagWithNotes, TreeNote]]):
        if not target_data or isinstance(target_data, TreeNote):
            # Detach tag from parent if dropped on empty area or a note
            if self.notes_model:
                self.notes_model.detach_tag_from_parent(dragged_tag.id)
        elif isinstance(target_data, TreeTagWithNotes):
            # Don't allow dropping on own child
            parent = self.itemAt(self.mapFromGlobal(self.cursor().pos()))
            while parent:
                if parent.data(0, Qt.ItemDataRole.UserRole) == dragged_tag:
                    return
                parent = parent.parent()

            # Attach tag to new parent
            if self.notes_model:
                self.notes_model.attach_tag_to_parent(dragged_tag.id, target_data.id)

    def _handle_note_drop(self, dragged_note: TreeNote, target_data: Optional[Union[TreeTagWithNotes, TreeNote]]):
        if isinstance(target_data, TreeTagWithNotes):
            # Attach note to new tag
            if self.notes_model:
                self.notes_model.attach_tag_to_note(dragged_note.id, target_data.id)
        elif isinstance(target_data, TreeNote):
            # If dropped on another note, we'll ignore it
            pass
        else:
            # If dropped on empty area, detach it from all tags
            if self.notes_model:
                self.notes_model.detach_note_from_all_tags(dragged_note.id)

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

        # Set the directory icon for the tag
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        tag_item.setIcon(0, icon)

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
