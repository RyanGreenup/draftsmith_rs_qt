from PySide6.QtWidgets import QSplitter
from PySide6.QtCore import Qt
from .markdown_editor import MarkdownEditor
from .left_sidebar import LeftSidebar
from .right_sidebar import RightSidebar

class MainContent(QSplitter):
    def __init__(self, handle_size=20, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.left_sidebar = LeftSidebar()
        self.editor = MarkdownEditor()
        self.right_sidebar = RightSidebar(handle_size)
        
        self._setup_ui(handle_size)
    
    def _setup_ui(self, handle_size):
        self.setHandleWidth(handle_size)
        self.addWidget(self.left_sidebar)
        self.addWidget(self.editor)
        self.addWidget(self.right_sidebar)
