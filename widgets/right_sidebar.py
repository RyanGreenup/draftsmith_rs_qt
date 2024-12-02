from PySide6.QtWidgets import QSplitter, QTextEdit
from PySide6.QtCore import Qt
from .notes_tree import NotesTreeWidget

class RightSidebar(QSplitter):
    def __init__(self, handle_size=20, parent=None):
        super().__init__(Qt.Orientation.Vertical, parent)
        self.additional_tree = NotesTreeWidget()
        self.text_top = QTextEdit()
        self.text_mid = QTextEdit()
        self.text_bottom = QTextEdit()

        self._setup_ui(handle_size)

    def _setup_ui(self, handle_size):
        self.setHandleWidth(handle_size)

        self.additional_tree.setHeaderLabel("Backlinks")
        self.additional_tree.setMinimumWidth(200)

        self.text_top.setPlaceholderText("Forward Links")
        self.text_mid.setPlaceholderText("Tags")
        self.text_bottom.setPlaceholderText("Similar Pages (Not Yet Implemented, Don't Touch)")

        self.addWidget(self.additional_tree)
        self.addWidget(self.text_top)
        self.addWidget(self.text_mid)
        self.addWidget(self.text_bottom)
