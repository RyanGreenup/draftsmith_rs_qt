from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox
from PySide6.QtCore import Qt
from .notes_tree import NotesTreeWidget

class LeftSidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tree = NotesTreeWidget()
        self.tags_tree = NotesTreeWidget()
        self.tree_selector = QComboBox()
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        self.tree.setHeaderLabel("Notes")
        self.tree.setMinimumWidth(100)
        
        self.tags_tree.setHeaderLabel("Tags")
        self.tags_tree.setMinimumWidth(100)
        self.tags_tree.hide()  # Initially hidden
        
        self.tree_selector.addItems(["Notes", "Tags"])
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tree_selector)
        layout.addWidget(self.tree)
        layout.addWidget(self.tags_tree)
    
    def _connect_signals(self):
        self.tree_selector.currentTextChanged.connect(self._on_tree_selection_changed)
    
    def _on_tree_selection_changed(self, text):
        if text == "Notes":
            self.tree.show()
            self.tags_tree.hide()
        else:  # Tags
            self.tree.hide()
            self.tags_tree.show()
