from typing import Optional, List, Dict, Set
from api.client import NoteAPI, Note as APINote, TreeNote as APITreeNote, UpdateNoteRequest
from models.note import Note
from datetime import datetime
from PySide6.QtCore import QObject, Signal

class NotesModel(QObject):
    """Model class to handle notes data and API interactions"""
    
    notes_updated = Signal()  # Emitted when notes data changes
    note_selected = Signal(Note)  # Emitted when a note is selected
    
    def __init__(self, api_url: str):
        super().__init__()
        self.api = NoteAPI(api_url)
        self.notes: Dict[int, Note] = {}  # id -> Note mapping
        self.root_notes: List[Note] = []  # Top-level notes
        
    def load_notes(self) -> None:
        """Load all notes from the API"""
        try:
            # Get the tree structure of notes
            tree_notes = self.api.get_notes_tree()
            
            # Clear existing data
            self.notes.clear()
            self.root_notes.clear()
            
            # Process the tree notes
            for tree_note in tree_notes:
                self._process_tree_note(tree_note)
                
            self.notes_updated.emit()
            
        except Exception as e:
            print(f"Error loading notes: {e}")
            
    def _process_tree_note(self, api_tree_note: APITreeNote, parent: Optional[Note] = None) -> Note:
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
    
    def create_note(self, title: str, content: str, parent_id: Optional[int] = None) -> Optional[Note]:
        """Create a new note"""
        try:
            api_response = self.api.note_create(title, content)
            # Convert API response to Note model explicitly
            note = Note.from_api_note(api_response)
            
            self.notes[note.id] = note
            
            if parent_id:
                parent = self.notes.get(parent_id)
                if parent:
                    self.api.attach_note_to_parent(note.id, parent_id)
                    parent.add_child(note)
            else:
                self.root_notes.append(note)
                
            self.notes_updated.emit()
            return note
            
        except Exception as e:
            print(f"Error creating note: {e}")
            return None
    
    def update_note(self, note_id: int, title: Optional[str] = None, content: Optional[str] = None) -> bool:
        """Update an existing note"""
        try:
            note = self.notes.get(note_id)
            if not note:
                return False
                
            # Create update request using the imported type
            update_data = UpdateNoteRequest(
                title=title,
                content=content
            )
                
            api_response = self.api.update_note(note_id, update_data)
            note.update_from_api_note(api_response)
            
            self.notes_updated.emit()
            return True
            
        except Exception as e:
            print(f"Error updating note: {e}")
            return False
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note"""
        try:
            note = self.notes.get(note_id)
            if not note:
                return False
                
            self.api.delete_note(note_id)
            
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
