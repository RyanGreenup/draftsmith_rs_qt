from typing import Optional
from PySide6.QtWidgets import QListWidgetItem, QTextEdit, QMainWindow
from PySide6.QtCore import Qt
from .note_select_palette import NoteSelectPalette
from models.notes_model import NotesModel

class InsertLinkPalette(NoteSelectPalette):
    """Popup palette for inserting note links into the editor"""

    def __init__(self, notes_model: NotesModel, 
                 parent: Optional[QMainWindow] = None,
                 use_full_path: bool = False) -> None:
        super().__init__(notes_model, parent, use_full_path)
        self.search_input.setPlaceholderText("Select note to link to...")
        self.original_cursor_position = None
        # Disable follow mode since we don't want preview behavior
        self.follow_mode = False

    def on_item_activated(self, item: QListWidgetItem) -> None:
        """Handle note link insertion"""
        note = item.data(Qt.ItemDataRole.UserRole)
        if note and self.parent():
            # Get the current tab's editor
            if hasattr(self.parent(), 'current_tab') and hasattr(self.parent().current_tab, 'editor'):
                editor: QTextEdit = self.parent().current_tab.editor.editor
                # Insert the note link at cursor position
                link_text = f"[[{note.id}]]"
                editor.insertPlainText(link_text)
        self.hide()

    def show_palette(self) -> None:
        """Show the palette and store the current cursor position"""
        if self.parent() and hasattr(self.parent(), 'current_tab'):
            editor: QTextEdit = self.parent().current_tab.editor.editor
            self.original_cursor_position = editor.textCursor().position()
        
        self.populate_notes()
        super().show_palette()

    def hide(self) -> None:
        """Restore cursor position if no selection was made"""
        if not self.results_list.currentItem() and self.original_cursor_position is not None:
            if self.parent() and hasattr(self.parent(), 'current_tab'):
                editor: QTextEdit = self.parent().current_tab.editor.editor
                cursor = editor.textCursor()
                cursor.setPosition(self.original_cursor_position)
                editor.setTextCursor(cursor)
        
        super().hide()

    def on_selection_changed(self, current: Optional[QListWidgetItem], previous: Optional[QListWidgetItem]) -> None:
        """Override to disable preview behavior"""
        pass
