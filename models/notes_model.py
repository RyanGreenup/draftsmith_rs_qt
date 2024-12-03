from typing import Optional, List, Dict, Set
from api.client import (
    NoteAPI,
    TagAPI,
    Note as APINote,
    TreeNote as APITreeNote,
    UpdateNoteRequest,
    Tag,
)
from models.note import Note
from datetime import datetime
from PySide6.QtCore import QObject, Signal


class NotesModel(QObject):
    """Model class to handle notes data and API interactions"""

    # TODO should this include tags etc? What if user adds backlink / tag etc.?
    notes_updated = Signal()  # Emitted when notes data changes
    note_selected = Signal(
        Note, List[Note], List[Note], List[Tag]
    )  # Emitted when a note is selected, includes forward links, backlinks, and tags

    def __init__(self, api_url: str):
        super().__init__()
        self.note_api: NoteAPI = NoteAPI(api_url)
        self.tag_api: TagAPI = TagAPI(api_url)
        self.notes: Dict[int, Note] = {}  # id -> Note mapping
        self.root_notes: List[Note] = []  # Top-level notes

    def refresh_notes(self) -> None:
        """Refresh notes from the server"""
        try:
            # Get the tree structure of notes
            tree_notes = self.note_api.get_notes_tree()

            # Clear existing data
            self.notes.clear()
            self.root_notes.clear()

            # Process the tree notes
            for tree_note in tree_notes:
                self._process_tree_note(tree_note)

            # Emit single update signal after all processing is complete
            self.notes_updated.emit()

        except Exception as e:
            print(f"Error refreshing notes: {e}")

    def load_notes(self) -> None:
        """Load all notes from the API"""
        self.refresh_notes()

    def _process_tree_note(
        self, api_tree_note: APITreeNote, parent: Optional[Note] = None
    ) -> Note:
        """Process a tree note and its children"""
        # Convert API note to our Note model
        note = Note.from_api_tree_note(api_tree_note)

        # Store in our lookup dictionary
        self.notes[note.id] = note

        # Handle parent-child relationship
        if parent:
            parent.add_child(note)
        else:
            self.root_notes.append(note)

        # Process children recursively
        for child_tree_note in api_tree_note.children:
            self._process_tree_note(child_tree_note, note)

        return note

    def get_note(self, note_id: int) -> Optional[Note]:
        """Get a note by its ID"""
        return self.notes.get(note_id)

    def get_forward_links(self, note_id: int) -> List[Note]:
        """Get all notes that this note links to"""
        try:
            api_notes = self.note_api.get_note_forward_links(note_id)
            return [Note.from_api_note(api_note) for api_note in api_notes]
        except Exception as e:
            print(f"Error getting forward links: {e}")
            return []

    def get_backlinks(self, note_id: int) -> List[Note]:
        """Get all notes that link to this note"""
        try:
            api_notes = self.note_api.get_note_backlinks(note_id)
            return [Note.from_api_note(api_note) for api_note in api_notes]
        except Exception as e:
            print(f"Error getting backlinks: {e}")
            return []

    def get_note_tags(self, note_id: int) -> List[Tag]:
        """Get all tags for a note"""
        try:
            # Get the note-tag relations
            relations = self.tag_api.get_note_tag_relations()
            # Filter relations for this note
            note_tag_ids = [rel.tag_id for rel in relations if rel.note_id == note_id]
            # Get all tags
            all_tags = self.tag_api.get_all_tags()
            # Filter tags for this note
            return [tag for tag in all_tags if tag.id in note_tag_ids]
        except Exception as e:
            print(f"Error getting tags for note {note_id}: {e}")
            return []

    def select_note(self, note_id: int) -> None:
        """Handle note selection and emit signals with all necessary data"""
        note = self.notes.get(note_id)
        if note:
            try:
                forward_links = self.get_forward_links(note_id)
                backlinks = self.get_backlinks(note_id)
                tags = self.get_note_tags(note_id)  # Get tags for the note
                # Update signal to include tags
                self.note_selected.emit(note, forward_links, backlinks, tags)
            except Exception as e:
                print(f"Error getting data for note {note_id}: {e}")
                self.note_selected.emit(note, [], [], [])

    def create_note(
        self, title: str, content: str, parent_id: Optional[int] = None
    ) -> Optional[Note]:
        """Create a new note"""
        try:
            api_response = self.note_api.note_create(title, content)
            # Convert API response to Note model explicitly
            api_note = APINote.model_validate(api_response)
            note = Note.from_api_note(api_note)

            self.notes[note.id] = note

            if parent_id:
                parent = self.notes.get(parent_id)
                if parent:
                    self.note_api.attach_note_to_parent(note.id, parent_id)
                    parent.add_child(note)
            else:
                self.root_notes.append(note)

            self.notes_updated.emit()
            return note

        except Exception as e:
            print(f"Error creating note: {e}")
            return None

    def update_note(
        self, note_id: int, title: Optional[str] = None, content: Optional[str] = None
    ) -> bool:
        """Update an existing note"""
        try:
            note = self.notes.get(note_id)
            if not note:
                return False

            # Create update request using the imported type
            update_data = UpdateNoteRequest(title=title, content=content)

            api_response = self.note_api.update_note(note_id, update_data)
            note.update_from_api_note(api_response)

            self.notes_updated.emit()
            return True

        except Exception as e:
            print(f"Error updating note: {e}")
            return False

    def handle_forward_link_selected(self, note_id: int) -> None:
        """Handle when a forward link is selected"""
        note = self.notes.get(note_id)
        if note:
            # Emit signal for tree selection
            self.note_selected.emit(note, self.get_forward_links(note_id))

    def delete_note(self, note_id: int) -> bool:
        """Delete a note"""
        try:
            note = self.notes.get(note_id)
            if not note:
                return False

            self.note_api.delete_note(note_id)

            # Remove from parent's children
            if note.parent_id and note.parent_id in self.notes:
                self.notes[note.parent_id].remove_child(note)

            # Remove from root notes if it's there
            if note in self.root_notes:
                self.root_notes.remove(note)

            # Remove from notes dictionary
            del self.notes[note_id]

            self.notes_updated.emit()
            return True

        except Exception as e:
            print(f"Error deleting note: {e}")
            return False
