from PySide6.QtWidgets import QWidget, QSplitter
from PySide6.QtCore import Signal, Qt
from typing import Optional
from widgets.left_sidebar import LeftSidebar
from widgets.markdown_editor import MarkdownEditor
from widgets.right_sidebar import RightSidebar
from models.notes_model import NotesModel

class TabContent(QWidget):
    """A complete view implementation for a note"""
    note_saved = Signal(int)  # Emits note_id when saved

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_note_id: Optional[int] = None
        self.notes_model: Optional[NotesModel] = None
        
        # Create components
        self.left_sidebar = LeftSidebar()
        self.editor = MarkdownEditor()
        self.right_sidebar = RightSidebar()
        
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the UI layout"""
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(self.left_sidebar)
        main_splitter.addWidget(self.editor)
        main_splitter.addWidget(self.right_sidebar)
        
        # Set default sizes
        main_splitter.setSizes([200, 600, 200])
        
        # Add to layout
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout()
        layout.addWidget(main_splitter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def _connect_signals(self):
        """Connect internal signals"""
        self.editor.save_requested.connect(self._handle_save_request)
        
    def set_model(self, notes_model: NotesModel):
        """Connect this view to the model"""
        self.notes_model = notes_model
        self.left_sidebar.tree.set_model(notes_model)
        # Connect note selection to right sidebar updates
        self.notes_model.note_selected.connect(self._update_right_sidebar)

    def _handle_save_request(self):
        """Internal handler for save requests"""
        current_item = self.left_sidebar.tree.currentItem()
        if current_item:
            note_data = current_item.data(0, Qt.ItemDataRole.UserRole)
            if note_data:
                content = self.editor.get_content()
                if self.notes_model.update_note(note_data.id, content=content):
                    self.note_saved.emit(note_data.id)

    def _update_right_sidebar(self, selection_data):
        """Update right sidebar content when a note is selected"""
        if selection_data.note:
            self.current_note_id = selection_data.note.id
            self.right_sidebar.update_forward_links(selection_data.forward_links)
            self.right_sidebar.update_backlinks(selection_data.backlinks)
            self.right_sidebar.update_tags(selection_data.tags)
