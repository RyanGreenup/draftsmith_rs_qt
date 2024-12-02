from typing import Union
from PySide6.QtWidgets import QSplitter, QTreeWidgetItem, QTreeWidget
from PySide6.QtCore import Qt
from .markdown_editor import MarkdownEditor
from .left_sidebar import LeftSidebar
from .right_sidebar import RightSidebar
from models.note import Note
from api.client import TreeNote

class MainContent(QSplitter):
    def __init__(self, handle_size=20, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.left_sidebar = LeftSidebar()
        self.editor = MarkdownEditor()
        self.right_sidebar = RightSidebar(handle_size)
        
        self._setup_ui(handle_size)
        self.left_sidebar.tree.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _setup_ui(self, handle_size):
        self.setHandleWidth(handle_size)
        self.addWidget(self.left_sidebar)
        self.addWidget(self.editor)
        self.addWidget(self.right_sidebar)

    def _on_selection_changed(self):
        """Handle selection changes in the notes tree"""
        selected_items = self.left_sidebar.tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            note = item.data(0, Qt.ItemDataRole.UserRole)
            if note:
                self.editor.set_content(note.content)
            else:
                self.editor.set_content("")

    def initialize_notes_model(self, api_url: str):
        """Initialize the notes model and load data"""
        from api.client import NoteAPI
        self.api = NoteAPI(api_url)
        self._refresh_notes_tree()
        
    def _refresh_notes_tree(self):
        """Refresh the notes tree with current API data"""
        self.left_sidebar.tree.clear()
        
        # Get notes tree from API
        try:
            notes = self.api.get_notes_tree()
            # Add all root notes
            for note in notes:
                self._add_note_to_tree(note, self.left_sidebar.tree)
        except Exception as e:
            print(f"Error loading notes: {e}")
            
    def _add_note_to_tree(self, note: TreeNote, parent_item: Union[QTreeWidget, QTreeWidgetItem]) -> None:
        """Recursively add a note and its children to the tree"""
        if isinstance(parent_item, QTreeWidgetItem):
            item = QTreeWidgetItem(parent_item)
        else:  # QTreeWidget
            item = QTreeWidgetItem(parent_item)
            
        item.setText(0, note.title)
        item.setData(0, Qt.ItemDataRole.UserRole, note)
        
        # Recursively add children
        for child in note.children:
            self._add_note_to_tree(child, item)
