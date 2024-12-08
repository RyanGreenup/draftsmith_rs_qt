from dataclasses import dataclass
from typing import List
from draftsmith_qt.api.client import Tag
from draftsmith_qt.models.note import Note


@dataclass
class NoteSelectionData:
    note: Note
    forward_links: List[Note]
    backlinks: List[Note]
    tags: List[Tag]
