from typing import Optional
from PySide6.QtWidgets import QListWidgetItem, QTextEdit
from PySide6.QtCore import Qt
from .palette_populated_with_notes import PalettePopulatedWithNotes


class NoteLinkInsertPalette(PalettePopulatedWithNotes):
    """Popup palette for inserting note links into the editor"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # 3. The cursor position is not stored

        self.search_input.setPlaceholderText("Select note to link to...")
        self.original_cursor_position = None

    def on_item_activated(self, item: QListWidgetItem) -> None:
        """Handle note link insertion"""
        note = item.data(Qt.ItemDataRole.UserRole)
        if note and self.parent():
            # The parent is TabContent, which has direct access to the editor
            if hasattr(self.parent(), "editor") and hasattr(
                self.parent().editor, "editor"
            ):
                editor: QTextEdit = self.parent().editor.editor

                # Insert the note link at cursor position
                link_text = f"[[{note.id}]]"
                editor.insertPlainText(link_text)

        self.hide()

    def show_palette(self) -> None:
        """Show the palette and store the current cursor position"""

        # 1. The inserted text is injected into the last previewed note
        # So for now we simply disable this and we'll fix it later.
        self.follow_mode = False

        if self.parent():
            # The parent is TabContent, which has direct access to the editor
            if hasattr(self.parent(), "editor") and hasattr(
                self.parent().editor, "editor"
            ):
                editor: QTextEdit = self.parent().editor.editor
                self.original_cursor_position = editor.textCursor().position()

        self.populate_notes()
        super().show_palette()

    def preview_note(self, note_id: int) -> None:
        """Preview the selected note without inserting"""
        if self.parent():
            self.parent()._handle_view_request(note_id)

    def hide(self) -> None:
        """Restore cursor position if no selection was made"""
        if (
            not self.results_list.currentItem()
            and self.original_cursor_position is not None
        ):
            if self.parent():
                # The parent is TabContent, which has direct access to the editor
                if hasattr(self.parent(), "editor") and hasattr(
                    self.parent().editor, "editor"
                ):
                    editor: QTextEdit = self.parent().editor.editor
                    cursor = editor.textCursor()
                    cursor.setPosition(self.original_cursor_position)
                    editor.setTextCursor(cursor)

        super().hide()
