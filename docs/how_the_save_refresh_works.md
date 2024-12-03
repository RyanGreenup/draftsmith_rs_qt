# Save and Refresh Logic in Note Taking App

## Overview

This document explains the logic behind saving a note and refreshing the UI to reflect the changes.

## Save Logic

When a user saves a note, the following steps are taken:

1. **Retrieve Current Note**: The currently selected note is retrieved from the tree widget.
2. **Save Content**: The content of the editor is saved to the notes model using `self.notes_model.update_note`.
3. **Refresh UI**:
   - If the save operation is successful, the notes are reloaded from the server.
   - The state of the tree widget is saved before saving and restored after reloading to maintain the user's view.

## Relevant Code Snippets

### Save Current Note Method

```python
def save_current_note(self):
    """Save the current note's content"""
    current_note = self.main_content.left_sidebar.tree.currentItem()
    if current_note:
        note_data = current_note.data(0, Qt.ItemDataRole.UserRole)
        if note_data:
            # Save the current tree state before saving
            tree_state = self.main_content.left_sidebar.tree.save_state()
            
            content = self.main_content.editor.get_content()
            success = self.notes_model.update_note(note_data.id, content=content)
            
            if success:
                # Reload notes and restore tree state
                self.notes_model.load_notes()
                self.main_content.left_sidebar.tree.restore_state(tree_state)
                self.status_bar.showMessage("Note saved successfully", 3000)
            else:
                self.status_bar.showMessage("Failed to save note", 3000)
```

### NotesModel Class

The `NotesModel` class handles the data and business logic. It interacts with the server to load, update, and manage notes.

```python
class NotesModel(QObject):
    note_selected = Signal(Note, List[Note], List[Note], List[Tag])

    def __init__(self, base_url: str):
        super().__init__()
        self.api_client = NoteAPI(base_url)
        self.notes = []

    def load_notes(self) -> None:
        # Load notes from the server
        pass

    def create_note(self, title: str, content: str, parent_id: Optional[int] = None) -> Note:
        # Create a new note
        pass

    def update_note(self, note_id: int, title: Optional[str] = None, content: Optional[str] = None) -> bool:
        # Update an existing note
        pass
```

### Tree Widget State Management

The tree widget state is saved before saving and restored after reloading to maintain the user's view.

```python
# Save the current tree state before saving
tree_state = self.main_content.left_sidebar.tree.save_state()

# Reload notes and restore tree state
self.notes_model.load_notes()
self.main_content.left_sidebar.tree.restore_state(tree_state)
```

## Summary

- **Save Action**: Triggered by the user.
- **Data Update**: The current note's content is saved to the model.
- **UI Refresh**: If successful, the notes are reloaded from the server, and the tree widget state is restored.
