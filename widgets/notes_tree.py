from typing import Optional, Dict, Any, Set, List, Union
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu
from PySide6.QtCore import Qt, Signal, QMimeData
from models.note import Note
from models.notes_model import NotesModel
from PySide6.QtGui import QKeyEvent
from utils.key_constants import Key
from widgets.navigable_tree import NavigableTree


class NotesTreeWidget(NavigableTree):
    note_selected = Signal(int)  # Signal emitted when a note is selected
    note_selected_with_focus = Signal(
        int
    )  # Signal emitted when note should be selected and focused
    note_deleted = Signal(int)  # Signal emitted when a note should be deleted

    def __init__(self, parent=None):
        super().__init__(parent)
        # Enable drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.notes_model: Optional[NotesModel] = None
        self.follow_mode: bool = True  # Default to true for backward compatibility
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def set_model(self, model: "NotesModel"):
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
            self.update_tree(self.notes_model.root_notes)

    def update_tree_from_model(self):
        """Callback for model updates to refresh the tree"""
        if self.notes_model is not None:
            # Save state before update
            state = self.save_state()
            
            # Update tree
            self.update_tree(self.notes_model.root_notes)
            
            # Restore state after update
            self.restore_state(state)

    def _on_selection_changed(self):
        """Handle selection changes and notify model"""
        if not self.follow_mode:
            return

        current = self.currentItem()
        if current and self.notes_model:
            note_data = current.data(0, Qt.ItemDataRole.UserRole)
            if note_data:
                self.notes_model.select_note(note_data.id)

    def select_note_by_id(self, note_id: int, emit_signal: bool = True) -> None:
        """Select the tree item corresponding to the given note ID"""

        def find_and_select_item(item):
            # Check current item
            note_data = item.data(0, Qt.ItemDataRole.UserRole)
            if note_data and note_data.id == note_id:
                self.blockSignals(not emit_signal)
                self.setCurrentItem(item)
                self.scrollToItem(item)
                self.blockSignals(False)
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

    def _handle_return(self, event: QKeyEvent) -> bool:
        """Handle return key press"""
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

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # Handle Return/Ctrl+Return first
        if event.key() == Qt.Key.Key_Return:
            if self._handle_return(event):
                event.accept()
                return

        # Handle J/K navigation using base class
        elif self._handle_navigation_key(event):
            event.accept()
            return

        # Handle tree-specific keys
        elif event.key() in (Key.Key_Space, Key.Key_Right, Key.Key_Left):
            current = self.currentItem()
            if current:
                if event.key() == Key.Key_Left:
                    if current.isExpanded():
                        current.setExpanded(False)
                    elif current.parent():
                        self.setCurrentItem(current.parent())
                elif event.key() == Key.Key_Right:
                    if not current.isExpanded() and current.childCount() > 0:
                        current.setExpanded(True)
                    elif current.childCount() > 0:
                        self.setCurrentItem(current.child(0))
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
                event.accept()
                return

        # Let other keys propagate to parent
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

    def _create_context_menu(self) -> QMenu:
        """Create and return the context menu with note-specific actions"""
        menu = super()._create_context_menu()

        # Add a separator before note-specific actions
        menu.addSeparator()

        # Add delete action
        current_item = self.currentItem()
        if current_item:
            note_data = current_item.data(0, Qt.ItemDataRole.UserRole)
            if note_data:
                # Create delete action directly instead of trying to access main window
                delete_action = menu.addAction("Delete Note")
                # self.note_deleted is handled in TabContent._connect_signals
                # which is is called in main_window referring to the current tab
                delete_action.triggered.connect(
                    lambda: self.note_deleted.emit(note_data.id)
                )

        return menu

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

    def mouseDoubleClickEvent(self, event):
        """Handle double click events to focus the selected note"""
        current = self.currentItem()
        if current:
            note_data = current.data(0, Qt.ItemDataRole.UserRole)
            if note_data:
                self.note_selected_with_focus.emit(note_data.id)
                event.accept()
                return
        super().mouseDoubleClickEvent(event)

    def dropEvent(self, event):
        """Handle drop events for note reordering and detaching"""
        # Get the target item (where we're dropping)
        target = self.itemAt(event.pos())
        
        # Get the dragged item
        dragged = self.currentItem()
        if not dragged or dragged == target:
            event.ignore()
            return

        # Get dragged note data
        dragged_note = dragged.data(0, Qt.ItemDataRole.UserRole)
        if not dragged_note:
            event.ignore()
            return

        # Prevent default drop handling
        event.setDropAction(Qt.DropAction.IgnoreAction)
        event.accept()

        # If target is None, we're dropping to root level (detach)
        if not target:
            if self.notes_model:
                self.notes_model.detach_note_from_parent(dragged_note.id)
            return

        # Handle normal attachment to another note
        target_note = target.data(0, Qt.ItemDataRole.UserRole)
        if not target_note:
            event.ignore()
            return

        # Don't allow dropping on own child
        parent = target
        while parent:
            if parent == dragged:
                event.ignore()
                return
            parent = parent.parent()

        # Use the model to update the relationship
        if self.notes_model:
            success = self.notes_model.attach_note_to_parent(
                dragged_note.id, 
                target_note.id
            )
            
            if not success:
                # If the model update failed, we might want to show an error
                return

    def dragEnterEvent(self, event):
        """Accept drag events only from within the tree"""
        if event.source() == self:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move events to control where drops are allowed"""
        if event.source() == self:
            event.accept()
        else:
            event.ignore()
