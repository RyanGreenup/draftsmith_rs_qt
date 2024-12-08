from typing import List, Optional, Any
from PySide6.QtWidgets import QListWidgetItem, QMainWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .popup_palette import PopupPalette
from models.note import Note
from models.notes_model import NotesModel


class NoteSelectPalette(PopupPalette):
    """Popup palette for selecting notes by title"""

    def __init__(self, notes_model: NotesModel, parent: Optional[QMainWindow] = None) -> None:
        super().__init__(parent)
        self.notes_model = notes_model
        self._notes: List[Note] = []
        self.search_input.setPlaceholderText("Type note title...")

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

        # Create display text with just the note title
        display_text = data.title

        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, data)

        # Style the item
        font = QFont()
        font.setPointSize(11)
        item.setFont(font)

        return item

    def filter_items(self, text: str) -> None:
        """Filter notes based on search text"""
        search_terms = text.lower().split()
        for note in self._notes:
            note_text = note.title.lower()
            if all(term in note_text for term in search_terms):
                item = self.create_list_item(note)
                if item:
                    self.results_list.addItem(item)

    def on_item_activated(self, item: QListWidgetItem) -> None:
        """Handle note selection"""
        note = item.data(Qt.ItemDataRole.UserRole)
        if note and self.parent():
            # Update the view to show the selected note 
            self.notes_model.select_note(note.id)
        self.hide()

    def show_palette(self) -> None:
        """Show the palette with fresh note data"""
        self.populate_notes()
        super().show_palette()
