from typing import List, Optional, Any
from PySide6.QtWidgets import QListWidgetItem, QMainWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from thefuzz import fuzz
from .popup_palette import PopupPalette
from models.note import Note
from models.notes_model import NotesModel


class PalettePopulatedWithNotes(PopupPalette):
    """Base class for palettes that display a list of notes"""

    def __init__(
        self,
        notes_model: NotesModel,
        parent: Optional[QMainWindow] = None,
        use_full_path: bool = False,
    ) -> None:
        super().__init__(parent, min_width=800, max_height=1000)
        self.notes_model = notes_model
        self._notes: List[Note] = []
        self._note_paths: dict[int, str] = {}

        # Before this can be used, the api needs an endpoint to fetch
        # all the breadcrumbs for all notes, otherwise it will be too slow
        # Manually walking the tree will be less slow, but will add code complexity
        # that should be offloaded to the API
        self.use_full_path = use_full_path

        # Follow mode triggers a signal that is connected in main_window.py
        # This signal updates this variable
        # In the future, notes_tree and this palette may
        # take a reference to main_window to directly inspect that variable
        # For now I've left them modular
        # To change the default just trigger the signal in main_window.py at startup
        self.follow_mode = True

        # Connect selection change signal
        self.results_list.currentItemChanged.connect(self.on_selection_changed)

    def populate_notes(self) -> None:
        """Collect all notes from the model and cache their paths if needed"""
        self._notes = self.notes_model.get_all_notes()

        # Pre-fetch all note paths if using full paths
        if self.use_full_path and self.parent():
            try:
                note_api = self.parent().notes_model.note_api
                self._note_paths = {}
                for note in self._notes:
                    try:
                        breadcrumbs = note_api.get_note_breadcrumbs(note.id)
                        self._note_paths[note.id] = "/".join(
                            note.title for note in breadcrumbs
                        )
                    except Exception as e:
                        print(f"Failed to fetch breadcrumbs for note {note.id}: {e}")
                        self._note_paths[note.id] = note.title
            except Exception as e:
                print(f"Failed to fetch note paths: {e}")
                self._note_paths = {}

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

        # Get display text - either full path or just title
        if self.use_full_path:
            display_text = self._note_paths.get(data.id, data.title)
        else:
            display_text = data.title

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
        """Filter notes based on fuzzy search text"""
        self.results_list.clear()
        if not text:  # Show all items if search is empty
            for note in self._notes:
                item = self.create_list_item(note)
                if item:
                    self.results_list.addItem(item)
            return

        # Store matches with their scores for sorting
        matches = []
        for note in self._notes:
            note_text = note.title
            if self.use_full_path:
                note_text = self._note_paths.get(note.id, note.title)
            
            # Get the best match ratio using token_set_ratio (best for partial matches)
            ratio = fuzz.token_set_ratio(text.lower(), note_text.lower())
            
            # Only include matches above a certain threshold (adjust as needed)
            if ratio > 50:  # threshold of 50%
                matches.append((ratio, note))
        
        # Sort by score descending
        matches.sort(reverse=True, key=lambda x: x[0])
        
        # Add items in sorted order
        for _, note in matches:
            item = self.create_list_item(note)
            if item:
                self.results_list.addItem(item)

    def on_selection_changed(
        self, current: Optional[QListWidgetItem], previous: Optional[QListWidgetItem]
    ) -> None:
        """Preview the selected note if follow mode is enabled"""
        if not current or not self.parent():
            return

        if self.follow_mode:
            note = current.data(Qt.ItemDataRole.UserRole)
            if note:
                self.preview_note(note.id)

    def preview_note(self, note_id: int) -> None:
        """Preview the note - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement preview_note")
