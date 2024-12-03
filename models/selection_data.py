from dataclasses import dataclass
from typing import List
from api.client import Tag
from models.note import Note

@dataclass
class NoteSelectionData:
    note: Note
    forward_links: List[Note]
    backlinks: List[Note]
    tags: List[Tag]
