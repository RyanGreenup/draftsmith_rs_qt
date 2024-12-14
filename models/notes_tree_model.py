from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QStyle, QApplication
from typing import Optional, Any, List
from api.client import (
    TagAPI, NoteAPI, TreeTagWithNotes, TreeNote,
    UpdateNoteRequest
)

class TreeNode:
    def __init__(self, data, parent=None, node_type='tag'):
        self.data = data
        self.parent = parent
        self.children = []
        self.node_type = node_type  # 'tag' or 'note'

    def append_child(self, child):
        child.parent = self
        self.children.append(child)

    def child(self, row):
        if 0 <= row < len(self.children):
            return self.children[row]
        return None

    def child_count(self):
        return len(self.children)

    def row(self):
        if self.parent:
            return self.parent.children.index(self)
        return 0

class NotesTreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_node = TreeNode(None)
        # TODO: Update base URL handling
        base_url = "http://vidar:37242"
        self.tag_api = TagAPI(base_url)
        self.note_api = NoteAPI(base_url)  # Add note API
        self.complete_notes_tree = []  # Store complete notes hierarchy
        self.setup_data()

    def setup_data(self):
        try:
            # First get complete notes tree for reference
            self.complete_notes_tree = self.note_api.get_notes_tree(exclude_content=True)

            # Then get tag tree
            tags_tree: List[TreeTagWithNotes] = self.tag_api.get_tags_tree()

            # Process tag hierarchy (sort tags before processing)
            for tag in sorted(tags_tree, key=lambda x: x.name.lower()):
                self._process_tag(tag, self.root_node)

            # Add "All Notes" section
            all_notes_node = TreeNode({"name": "All Notes"}, self.root_node, 'page')
            self.root_node.append_child(all_notes_node)
            
            # Sort notes before adding them
            sorted_notes = sorted(self.complete_notes_tree, key=lambda x: x.title.lower())
            for note in sorted_notes:
                self._process_note(note, all_notes_node)

            # Add "Untagged Notes" section
            untagged_notes_node = TreeNode({"name": "Untagged Notes"}, self.root_node, 'page')
            self.root_node.append_child(untagged_notes_node)

            # Find and process untagged root notes (sort them first)
            untagged_notes = [
                note for note in self.complete_notes_tree 
                if not note.tags and not self._is_subpage(note)
            ]
            for note in sorted(untagged_notes, key=lambda x: x.title.lower()):
                if not note.tags:
                    self._process_note(note, untagged_notes_node)

        except Exception as e:
            print(f"Error loading data: {e}")

    def _find_note_in_tree(self, note_id: str, notes: List[TreeNote]) -> Optional[TreeNote]:
        """Recursively find a note by ID in the complete notes tree

        This is a work around until the API provides an endpoint to get the tags, notes and the notes subpages.

        """
        for note in notes:
            if note.id == note_id:
                return note
            if note.children:
                found = self._find_note_in_tree(note_id, note.children)
                if found:
                    return found
        return None

    def _process_tag(self, tag_data, parent_node):
        # Create tag node
        node = TreeNode(tag_data, parent_node, 'tag')
        # Use insert_node instead of append_child
        self.insert_node(node, parent_node)

        # Process child tags
        for child in sorted(tag_data.children, key=lambda x: x.name.lower()):
            self._process_tag(child, node)

        # Process notes belonging to this tag
        for note in sorted(tag_data.notes, key=lambda x: x.title.lower()):
            # Find the complete note hierarchy from notes_tree
            complete_note = self._find_note_in_tree(note.id, self.complete_notes_tree)
            if complete_note:
                self._process_note(complete_note, node)
            else:
                self._process_note(note, node)

    def _process_note(self, note_data, parent_node):
        # Create note node
        node = TreeNode(note_data, parent_node, 'note')
        # Use insert_node instead of append_child
        self.insert_node(node, parent_node)

        # Process child notes (subpages)
        for child in sorted(note_data.children, key=lambda x: x.title.lower()):
            self._process_note(child, node)

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parent_node = self.root_node if not parent.isValid() else parent.internalPointer()
        child_node = parent_node.child(row)

        if child_node:
            return self.createIndex(row, column, child_node)
        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child_node = index.internalPointer()
        parent_node = child_node.parent

        if parent_node == self.root_node:
            return QModelIndex()

        return self.createIndex(parent_node.row(), 0, parent_node)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.column() > 0:
            return 0

        parent_node = self.root_node if not parent.isValid() else parent.internalPointer()
        return parent_node.child_count()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role in (Qt.DisplayRole, Qt.EditRole):
            if node.node_type == 'tag':
                return f"{node.data.name}"
            elif node.node_type == 'page':
                return node.data["name"]  # Access dict with key
            else:  # note
                # Handle both dictionary and object cases
                if isinstance(node.data, dict):
                    return node.data.get('title', 'Untitled')
                return getattr(node.data, 'title', 'Untitled')

        elif role == Qt.DecorationRole:
            style = QApplication.style()
            if node.node_type == 'tag':
                return style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
            elif node.node_type == 'page':
                return style.standardIcon(QStyle.StandardPixmap.SP_DirLinkIcon)
            else:  # note
                return style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return "Tags"
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        # Don't allow editing of page nodes (All Notes, Untagged Notes)
        node = index.internalPointer()
        if node.node_type != 'page':
            flags |= Qt.ItemIsEditable

        return flags

    def _get_sort_key(self, node):
        """Get the key to use for sorting nodes"""
        # Special handling for page nodes (All Notes, Untagged Notes) - always at the end
        if node.node_type == 'page':
            return ('2', node.data["name"].lower())
        
        # Tags and notes are sorted by name/title
        if node.node_type == 'tag':
            return ('0', node.data.name.lower())
        else:  # note
            title = node.data.title if hasattr(node.data, 'title') else node.data.get('title', '')
            return ('1', title.lower())

    def _find_insert_position(self, parent_node, new_node):
        """Find the correct position to insert a node maintaining alphabetical order"""
        new_key = self._get_sort_key(new_node)
        
        for i, child in enumerate(parent_node.children):
            if self._get_sort_key(child) > new_key:
                return i
        return len(parent_node.children)

    def insert_node(self, new_node, parent_node):
        """Insert a node in the correct sorted position"""
        if not parent_node:
            parent_node = self.root_node
            
        # Find insert position
        insert_pos = self._find_insert_position(parent_node, new_node)
        
        # Create parent index
        parent_index = QModelIndex() if parent_node == self.root_node else \
                      self.createIndex(parent_node.row(), 0, parent_node)
        
        # Insert node
        self.beginInsertRows(parent_index, insert_pos, insert_pos)
        new_node.parent = parent_node
        parent_node.children.insert(insert_pos, new_node)
        self.endInsertRows()
        
        return self.createIndex(insert_pos, 0, new_node)

    def sort_children(self, parent_node):
        """Sort the children of a node"""
        if not parent_node.children:
            return
            
        # Create parent index
        parent_index = QModelIndex() if parent_node == self.root_node else \
                      self.createIndex(parent_node.row(), 0, parent_node)
        
        # Sort children
        self.beginResetModel()
        parent_node.children.sort(key=self._get_sort_key)
        self.endResetModel()

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if not index.isValid() or role != Qt.EditRole:
            return False

        node = index.internalPointer()
        new_name = str(value).strip()

        if not new_name:  # Don't allow empty names
            return False

        try:
            if node.node_type == 'tag':
                # Update tag name
                updated_tag = self.tag_api.update_tag(node.data.id, new_name)
                node.data.name = updated_tag.name
            elif node.node_type == 'note':
                # Update note title
                request = UpdateNoteRequest(title=new_name)
                updated_note = self.note_api.update_note(node.data.id, request)
                node.data.title = updated_note.title
            else:
                return False

            # Notify views that data has changed
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True

        except Exception as e:
            print(f"Error updating item: {e}")
            return False

    def _is_subpage(self, note: TreeNote) -> bool:
        """Check if this note is referenced as a child in the complete notes tree"""
        def check_children(parent_notes: List[TreeNote]) -> bool:
            for parent in parent_notes:
                for child in parent.children:
                    if child.id == note.id:
                        return True
                    if check_children([child]):
                        return True
            return False

        return check_children(self.complete_notes_tree)
