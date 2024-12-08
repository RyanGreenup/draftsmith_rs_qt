from typing import List, Optional, Any
from PySide6.QtWidgets import QListWidgetItem, QMainWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .popup_palette import PopupPalette
from models.note import Note
from models.notes_model import NotesModel
from api.client import NoteAPI


class NoteSelectPalette(PopupPalette):
    """Popup palette for selecting notes by title"""

    def __init__(self, notes_model: NotesModel, parent: Optional[QMainWindow] = None, use_full_path: bool = False) -> None:
        super().__init__(parent)
        self.notes_model = notes_model
        self._notes: List[Note] = []
        self.search_input.setPlaceholderText("Type note title...")
        self.original_note_id = None
        # Follow mode triggers a signal that is connected in main_window.py
        # This signal updates this variable
        # In the future, notes_tree and this palette may
        # take a reference to main_window to directly inspect that variable
        # For now I've left them modular
        # To change the default just trigger the signal in main_window.py at startup
        self.follow_mode = True
        self.use_full_path = use_full_path

        # Connect selection change signal
        self.results_list.currentItemChanged.connect(self.on_selection_changed)

    def populate_notes(self) -> None:
        """Collect all notes from the model"""
        self._notes = self.notes_model.get_all_notes()

        # Clear and repopulate the results list
        self.results_list.clear()
        for note in self._notes:
            item = self.create_list_item(note)
            if item:
                self.results_list.addItem(item)

    def get_all_items(self) -> List[Note]:
        """Get all notes"""
        return self._notes

    def create_list_item(self, data: Any) -> Optional[QListWidgetItem]:
        """Create a list item from a note"""
        if not isinstance(data, Note) or not data.title:
            return None

        # Get note path from parent window's notes model
        note_path = ""
        if self.use_full_path:
            if self.parent():
                try:
                    base_url = self.parent().base_url  # type:ignore
                    note_api = NoteAPI(base_url)
                    note_path = note_api.get_note_path(data.id)
                except AttributeError:
                    print("Base URL not set for NoteSelectPalette")
            else:
                print("Parent window not set for NoteSelectPalette")

        # Create display text with path and title
        display_text = f"{note_path}"

        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, data)

        # Style the item
        font = QFont()
        font.setPointSize(11)
        item.setFont(font)

        # Store the original title for filtering
        item.setData(Qt.ItemDataRole.UserRole + 1, data.title)

        return item

    def filter_items(self, text: str) -> None:
        """Filter notes based on search text"""
        search_terms = text.lower().split()
        for note in self._notes:
            # Search in both title and full path
            note_text = note.title.lower()
            note_path = ""
            if self.parent():
                note_path = self.parent().notes_model.note_api.get_note_path(note.id).lower()

            if all(term in note_text or term in note_path for term in search_terms):
                item = self.create_list_item(note)
                if item:
                    self.results_list.addItem(item)

    def on_item_activated(self, item: QListWidgetItem) -> None:
        """Handle note selection"""
        note = item.data(Qt.ItemDataRole.UserRole)
        if note and self.parent():
            # Update the view and focus the tree item
            self.parent()._handle_view_request_with_focus(note.id)
        self.hide()

    def show_palette(self) -> None:
        """Show the palette with fresh note data"""
        # Store current note ID before showing palette
        if self.parent():
            self.original_note_id = self.parent().get_current_note_id()
        self.populate_notes()
        super().show_palette()

    def on_selection_changed(self, current: Optional[QListWidgetItem], previous: Optional[QListWidgetItem]) -> None:
        """Preview the selected note if follow mode is enabled"""
        if not current:
            if not self.parent():
                print("No current item or parent")
            return

        # Check if follow mode is enabled
        if self.follow_mode:
            note = current.data(Qt.ItemDataRole.UserRole)
            if note:
                # Update view without focusing tree
                self.parent()._handle_view_request(note.id)

    def hide(self) -> None:
        """Restore original note when hiding if no selection was made"""
        if not self.results_list.currentItem() and self.original_note_id and self.parent():
            # Restore original note
            self.parent()._handle_view_request(self.original_note_id)
        super().hide()
