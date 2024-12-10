from typing import Optional, List, Dict, Set
from api.client import (
    NoteAPI,
    TagAPI,
    Note as APINote,
    TreeNote as APITreeNote,
    UpdateNoteRequest,
    Tag,
    TreeTagWithNotes,
    TreeNote,
)
from models.note import Note
from datetime import datetime
from PySide6.QtCore import QObject, Signal


class NotesModel(QObject):
    """Model class to handle notes data and API interactions"""

    # TODO should this include tags etc? What if user adds backlink / tag etc.?
    notes_updated = Signal()  # Emitted when notes data changes
    note_selected = Signal(
        object
    )  # Emitted when a note is selected with NoteSelectionData
    note_deleted = Signal(int)  # Add this new signal - emits deleted note's ID

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
        """Process a tree note and its children, maintaining the single source of truth"""
        # Create note without processing children
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
        from models.selection_data import NoteSelectionData

        note = self.notes.get(note_id)
        if note:
            try:
                selection_data = NoteSelectionData(
                    note=note,
                    forward_links=self.get_forward_links(note_id),
                    backlinks=self.get_backlinks(note_id),
                    tags=self.get_note_tags(note_id),
                )
                self.note_selected.emit(selection_data)
            except Exception as e:
                print(f"Error getting data for note {note_id}: {e}")
                self.note_selected.emit(
                    NoteSelectionData(
                        note=note, forward_links=[], backlinks=[], tags=[]
                    )
                )

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

            self.refresh_notes()
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

            # Refresh notes but don't trigger a global re-selection
            self.refresh_notes()
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

    def get_all_notes(self) -> List[Note]:
        """Get all notes in the system"""
        return list(self.notes.values())

    def get_tags_tree(self) -> List[TreeTagWithNotes]:
        """Get the tree structure of tags with their associated notes"""
        try:
            tags_tree = self.tag_api.get_tags_tree()
            # If the API doesn't return notes with tags, we need to fetch them here
            for tag in tags_tree:
                self._populate_notes_for_tag(tag)
            print(tags_tree)
            return tags_tree
        except Exception as e:
            print(f"Error getting tags tree: {e}")
            return []

    def _populate_notes_for_tag(self, tag: TreeTagWithNotes) -> TreeTagWithNotes:
        """Recursively populate notes for a tag and its children"""
        notes = self.get_notes_for_tag(tag.id)
        updated_children = [self._populate_notes_for_tag(child) for child in tag.children]
        return TreeTagWithNotes(id=tag.id, name=tag.name, children=updated_children, notes=notes)

    def get_notes_for_tag(self, tag_id: int) -> List[TreeNote]:
        """Get all notes associated with a tag"""
        try:
            # Get the note-tag relations
            relations = self.tag_api.get_note_tag_relations()
            # Filter relations for this tag
            tag_note_ids = [rel.note_id for rel in relations if rel.tag_id == tag_id]
            # Return TreeNote objects for these note IDs
            return [TreeNote(id=note.id, title=note.title, content=note.content) 
                    for note in self.notes.values() if note.id in tag_note_ids]
        except Exception as e:
            print(f"Error getting notes for tag {tag_id}: {e}")
            return []

    def select_tag(self, tag_id: int) -> None:
        """Handle tag selection"""
        try:
            notes = self.get_notes_for_tag(tag_id)
            # You might want to emit a signal here with the selected tag and its notes
            print(f"Selected tag {tag_id} with {len(notes)} notes")
        except Exception as e:
            print(f"Error selecting tag {tag_id}: {e}")

    def create_tag(self, name: str, parent_id: Optional[int] = None) -> Optional[Tag]:
        try:
            tag = self.tag_api.create_tag(name)
            if parent_id:
                self.tag_api.attach_tag_to_parent(tag.id, parent_id)
            self.refresh_notes()  # This will trigger a tree update
            return tag
        except Exception as e:
            print(f"Error creating tag: {e}")
            return None

    def delete_tag(self, tag_id: int) -> bool:
        try:
            self.tag_api.delete_tag(tag_id)
            self.refresh_notes()  # This will trigger a tree update
            return True
        except Exception as e:
            print(f"Error deleting tag: {e}")
            return False

    def update_tag(self, tag_id: int, new_name: str) -> Optional[Tag]:
        try:
            updated_tag = self.tag_api.update_tag(tag_id, new_name)
            self.refresh_notes()  # This will trigger a tree update
            return updated_tag
        except Exception as e:
            print(f"Error updating tag: {e}")
            return None

    def get_tags_tree(self) -> List[TreeTagWithNotes]:
        """Get the tree structure of tags with their associated notes"""
        try:
            tags_tree = self.tag_api.get_tags_tree()
            updated_tags_tree = [self._populate_notes_for_tag(tag) for tag in tags_tree]
            print(updated_tags_tree)
            return updated_tags_tree
        except Exception as e:
            print(f"Error getting tags tree: {e}")
            return []

    def delete_note(self, note_id: int) -> bool:
        """Delete a note"""
        try:
            note = self.notes.get(note_id)
            if not note:
                return False

            # Delete from API
            self.note_api.delete_note(note_id)

            # Emit deletion signal
            self.note_deleted.emit(note_id)

            # Refresh internal state
            self.refresh_notes()

            return True

        except Exception as e:
            print(f"Error deleting note: {e}")
            return False

    def attach_tag_to_parent(self, child_id: int, parent_id: int) -> bool:
        """
        Attach a tag as a child of another tag

        Args:
            child_id: ID of the tag to attach as child
            parent_id: ID of the parent tag

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Use the API to attach the tag
            self.tag_api.attach_tag_to_parent(child_id, parent_id)

            # Refresh internal state and emit signal
            self.refresh_notes()  # This emits notes_updated

            return True

        except Exception as e:
            print(f"Error attaching tag {child_id} to parent {parent_id}: {e}")
            return False

    def detach_tag_from_parent(self, tag_id: int) -> bool:
        """
        Detach a tag from its parent

        Args:
            tag_id: ID of the tag to detach from its parent

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Use the API to detach the tag
            self.tag_api.detach_tag_from_parent(tag_id)

            # Refresh internal state and emit signal
            self.refresh_notes()  # This emits notes_updated

            return True

        except Exception as e:
            print(f"Error detaching tag {tag_id} from parent: {e}")
            return False

    def attach_note_to_parent(self, child_id: int, parent_id: int) -> bool:
        """
        Attach a note as a child of another note

        Args:
            child_id: ID of the note to attach as child
            parent_id: ID of the parent note

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Verify both notes exist in our model
            child = self.notes.get(child_id)
            parent = self.notes.get(parent_id)
            if not child or not parent:
                return False

            # Use the API to attach the note
            self.note_api.attach_note_to_parent(child_id, parent_id)

            # Refresh internal state and emit signal
            self.refresh_notes()  # This emits notes_updated

            return True

        except Exception as e:
            print(f"Error attaching note {child_id} to parent {parent_id}: {e}")
            return False

    def detach_note_from_parent(self, note_id: int) -> bool:
        """
        Detach a note from its parent

        Args:
            note_id: ID of the note to detach from its parent

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Verify note exists in our model
            note = self.notes.get(note_id)
            if not note:
                return False

            # Use the API to detach the note
            self.note_api.detach_note_from_parent(note_id)

            # Refresh internal state and emit signal
            self.refresh_notes()  # This emits notes_updated

            return True

        except Exception as e:
            print(f"Error detaching note {note_id} from parent: {e}")
            return False

    def attach_tag_to_note(self, note_id: int, tag_id: int) -> bool:
        """
        Attach a tag to a note

        Args:
            note_id: ID of the note
            tag_id: ID of the tag to attach

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Use the API to attach the tag to the note
            self.tag_api.attach_tag_to_note(note_id, tag_id)

            # Refresh internal state and emit signal
            self.refresh_notes()  # This emits notes_updated

            return True

        except Exception as e:
            print(f"Error attaching tag {tag_id} to note {note_id}: {e}")
            return False

    def detach_tag_from_note(self, note_id: int, tag_id: int) -> bool:
        """
        Detach a tag from a note

        Args:
            note_id: ID of the note
            tag_id: ID of the tag to detach

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Use the API to detach the tag from the note
            self.tag_api.detach_tag_from_note(note_id, tag_id)

            # Refresh internal state and emit signal
            self.refresh_notes()  # This emits notes_updated

            return True

        except Exception as e:
            print(f"Error detaching tag {tag_id} from note {note_id}: {e}")
            return False

    def detach_note_from_all_tags(self, note_id: int) -> bool:
        """
        Detach a note from all its tags

        Args:
            note_id: ID of the note to detach from all tags

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get all tags for the note
            note_tags = self.get_note_tags(note_id)
            
            # Detach the note from each tag
            for tag in note_tags:
                self.tag_api.detach_tag_from_note(note_id, tag.id)

            # Refresh internal state and emit signal
            self.refresh_notes()  # This emits notes_updated

            return True

        except Exception as e:
            print(f"Error detaching note {note_id} from all tags: {e}")
            return False
