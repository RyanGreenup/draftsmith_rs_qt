from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Set
from api.client import Note as APINote, TreeNote as APITreeNote, Tag as APITag

@dataclass
class Note:
    id: int
    title: str
    content: str
    created_at: datetime
    modified_at: datetime
    
    # Relationships
    parent_id: Optional[int] = None
    children: List['Note'] = field(default_factory=list)
    tags: Set[int] = field(default_factory=set)  # Set of tag IDs
    backlinks: Set[int] = field(default_factory=set)  # Notes that link to this note
    forward_links: Set[int] = field(default_factory=set)  # Notes this note links to
    hierarchy_type: Optional[str] = None  # e.g., "block"

    @classmethod
    def from_api_note(cls, api_note: APINote) -> 'Note':
        """Create a Note instance from an API Note response"""
        return cls(
            id=api_note.id,
            title=api_note.title,
            content=api_note.content,
            created_at=api_note.created_at,
            modified_at=api_note.modified_at
        )

    @classmethod
    def from_api_tree_note(cls, api_tree_note: APITreeNote) -> 'Note':
        """Create a Note instance from an API TreeNote response"""
        # Handle optional datetime fields with a default value
        created_at = api_tree_note.created_at if api_tree_note.created_at else datetime.now()
        modified_at = api_tree_note.modified_at if api_tree_note.modified_at else datetime.now()
        
        note = cls(
            id=api_tree_note.id,
            title=api_tree_note.title,
            content=api_tree_note.content or "",
            created_at=created_at,
            modified_at=modified_at,
            hierarchy_type=api_tree_note.hierarchy_type,
            tags={tag.id for tag in api_tree_note.tags}
        )
        
        # Recursively convert child notes
        note.children = [
            cls.from_api_tree_note(child) for child in api_tree_note.children
        ]
        
        return note

    def update_from_api_note(self, api_note: APINote) -> None:
        """Update this note's properties from an API Note response"""
        self.title = api_note.title
        self.content = api_note.content
        self.modified_at = api_note.modified_at if api_note.modified_at else datetime.now()

    def add_child(self, child: 'Note') -> None:
        """Add a child note to this note"""
        child.parent_id = self.id
        if child not in self.children:
            self.children.append(child)

    def remove_child(self, child: 'Note') -> None:
        """Remove a child note from this note"""
        if child in self.children:
            child.parent_id = None
            self.children.remove(child)

    def add_tag(self, tag_id: int) -> None:
        """Add a tag to this note"""
        self.tags.add(tag_id)

    def remove_tag(self, tag_id: int) -> None:
        """Remove a tag from this note"""
        self.tags.discard(tag_id)

    def add_backlink(self, note_id: int) -> None:
        """Add a backlink to this note"""
        self.backlinks.add(note_id)

    def remove_backlink(self, note_id: int) -> None:
        """Remove a backlink from this note"""
        self.backlinks.discard(note_id)

    def add_forward_link(self, note_id: int) -> None:
        """Add a forward link from this note"""
        self.forward_links.add(note_id)

    def remove_forward_link(self, note_id: int) -> None:
        """Remove a forward link from this note"""
        self.forward_links.discard(note_id)

    def get_all_ancestors(self) -> List[int]:
        """Get all ancestor note IDs in the hierarchy"""
        ancestors = []
        current = self
        while current.parent_id is not None:
            ancestors.append(current.parent_id)
            # Note: This requires the parent note to be accessible
            # You might need to modify this based on how you maintain the note hierarchy
        return ancestors

    def get_all_descendants(self) -> List[int]:
        """Get all descendant note IDs in the hierarchy"""
        descendants = []
        for child in self.children:
            descendants.append(child.id)
            descendants.extend(child.get_all_descendants())
        return descendants
