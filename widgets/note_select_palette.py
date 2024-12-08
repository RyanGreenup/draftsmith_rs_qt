from typing import Optional
from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtCore import Qt
from .palette_populated_with_notes import PalettePopulatedWithNotes


class NoteSelectPalette(PalettePopulatedWithNotes):
    """Popup palette for selecting notes by title"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.search_input.setPlaceholderText("Type note title...")
        self.original_note_id = None


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

    def preview_note(self, note_id: int) -> None:
        """Preview the selected note without focusing the tree"""
        if self.parent():
            self.parent()._handle_view_request(note_id)

    def hide(self) -> None:
        """Restore original note when hiding if no selection was made"""
        if not self.results_list.currentItem() and self.original_note_id and self.parent():
            # Restore original note
            self.parent()._handle_view_request(self.original_note_id)
        super().hide()
