from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QStyle, QApplication
from typing import Optional, Any, List
from api.client import TagAPI, NoteAPI, TreeTagWithNotes, TreeNote

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
        self.setup_data()

    def setup_data(self):
        try:
            # Get both tag tree and notes tree
            # TODO: In the future, the API may be updated to include inherited tags in the tag tree
            # based on user feedback. For now, we'll display both hierarchies.
            tags_tree: List[TreeTagWithNotes] = self.tag_api.get_tags_tree()
            notes_tree: List[TreeNote] = self.note_api.get_notes_tree()
            
            # Process tag hierarchy
            print(f"Received {len(tags_tree)} top-level tags")
            for tag in tags_tree:
                self._process_tag(tag, self.root_node)

            # Add root notes that aren't under any tags
            # Create a special "All Notes" node
            all_notes_node = TreeNode({"name": "All Notes"}, self.root_node, 'special')
            self.root_node.append_child(all_notes_node)
            for note in notes_tree:
                self._process_note(note, all_notes_node)

        except Exception as e:
            print(f"Error loading data: {e}")

    def _process_tag(self, tag_data, parent_node):
        # Create tag node
        node = TreeNode(tag_data, parent_node, 'tag')
        parent_node.append_child(node)

        # Process child tags
        for child in tag_data.children:
            self._process_tag(child, node)

        # Process notes belonging to this tag
        for note in tag_data.notes:
            self._process_note(note, node)

    def _process_note(self, note_data, parent_node):
        # Create note node
        node = TreeNode(note_data, parent_node, 'note')
        parent_node.append_child(node)

        # Process child notes (subpages)
        for child in note_data.children:
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

        if role == Qt.DisplayRole:
            if node.node_type == 'tag':
                return f"{node.data.name}"
            elif node.node_type == 'special':
                return node.data["name"]  # Access dict with key
            else:  # note
                return node.data.title

        elif role == Qt.DecorationRole:
            style = QApplication.style()
            if node.node_type == 'tag':
                return style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
            elif node.node_type == 'special':
                return style.standardIcon(QStyle.StandardPixmap.SP_DirLinkIcon)
            else:  # note
                return style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return "Tags"
        return None
