from typing import Optional
from PySide6.QtWidgets import QListWidgetItem, QTextEdit
from PySide6.QtCore import Qt
from .palette_populated_with_notes import PalettePopulatedWithNotes


class NoteLinkInsertPalette(PalettePopulatedWithNotes):
    """Popup palette for inserting note links into the editor"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.search_input.setPlaceholderText("Select note to link to...")
        self.original_cursor_position = None

    def on_item_activated(self, item: QListWidgetItem) -> None:
        """Handle note link insertion"""
        note = item.data(Qt.ItemDataRole.UserRole)
        if note and self.parent():
            # Get the current tab's editor
            current_tab = self.parent().get_current_tab()
            if current_tab and hasattr(current_tab, 'editor') and hasattr(current_tab.editor, 'editor'):
                editor: QTextEdit = current_tab.editor.editor
                
                # Insert the note link at cursor position
                link_text = f"[[{note.id}]]"
                editor.insertPlainText(link_text)
                
        self.hide()

    def show_palette(self) -> None:
        """Show the palette and store the current cursor position"""
        if self.parent():
            current_tab = self.parent().get_current_tab()
            if current_tab and hasattr(current_tab, 'editor') and hasattr(current_tab.editor, 'editor'):
                editor: QTextEdit = current_tab.editor.editor
                self.original_cursor_position = editor.textCursor().position()
                
        self.populate_notes()
        super().show_palette()

    def preview_note(self, note_id: int) -> None:
        """Preview the selected note without inserting"""
        if self.parent():
            self.parent()._handle_view_request(note_id)

    def hide(self) -> None:
        """Restore cursor position if no selection was made"""
        if not self.results_list.currentItem() and self.original_cursor_position is not None:
            if self.parent():
                current_tab = self.parent().get_current_tab()
                if current_tab and hasattr(current_tab, 'editor') and hasattr(current_tab.editor, 'editor'):
                    editor: QTextEdit = current_tab.editor.editor
                    cursor = editor.textCursor()
                    cursor.setPosition(self.original_cursor_position)
                    editor.setTextCursor(cursor)
        
        super().hide()
