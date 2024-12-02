from PySide6.QtWidgets import QSplitter, QTreeWidgetItem
from PySide6.QtCore import Qt
from .markdown_editor import MarkdownEditor
from .left_sidebar import LeftSidebar
from .right_sidebar import RightSidebar
from models.note import Note

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

    def initialize_dummy_data(self):
        """Initialize this tab's dummy data"""
        self._add_notes_hierarchy()
        self._add_tags_hierarchy()

    def _add_notes_hierarchy(self):
        """Add dummy notes hierarchy to the notes tree"""
        notes_hierarchy = [
            (Note("Work", "General work-related notes and tasks"), [
                (Note("Meeting Notes", "Meeting agenda:\n1. Project updates\n2. Timeline review"), [
                    Note("Agenda Item 1", "Discuss project timeline"),
                    Note("Agenda Item 2", "Review milestones"),
                ]),
                (Note("Project Ideas", "New features to implement:\n- Dark mode\n- Auto-save"), [
                    Note("Dark Mode", "Implement dark theme for the app"),
                    Note("Auto-Save", "Add auto-save functionality"),
                ]),
                (Note("To-Do List", "- Send report\n- Update documentation"), [
                    Note("Report", "Prepare and send project report"),
                    Note("Documentation", "Update user manual"),
                ]),
            ]),
            (Note("Personal", "My personal notes and plans"), [
                (Note("Shopping List", "- Groceries\n- Household items"), [
                    Note("Groceries", "Milk, Bread, Eggs"),
                    Note("Household Items", "Cleaning supplies, Towels"),
                ]),
                (Note("Travel Plans", "Places to visit:\n1. Paris\n2. Tokyo"), [
                    Note("Paris", "Visit Eiffel Tower, Louvre Museum"),
                    Note("Tokyo", "Explore Shibuya, Visit Senso-ji Temple"),
                ]),
                (Note("Goals", "2024 Goals:\n1. Learn Python\n2. Exercise more"), [
                    Note("Learn Python", "Complete online courses and projects"),
                    Note("Exercise More", "Join a gym, Practice yoga"),
                ]),
            ]),
        ]

        for parent_note, child_notes in notes_hierarchy:
            parent_item = QTreeWidgetItem(self.left_sidebar.tree)
            parent_item.setText(0, parent_note.title)
            parent_item.setData(0, Qt.ItemDataRole.UserRole, parent_note)

            for child_note_tuple in child_notes:
                child_note, grandchild_notes = child_note_tuple
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, child_note.title)
                child_item.setData(0, Qt.ItemDataRole.UserRole, child_note)

                for grandchild_note in grandchild_notes:
                    grandchild_item = QTreeWidgetItem(child_item)
                    grandchild_item.setText(0, grandchild_note.title)
                    grandchild_item.setData(0, Qt.ItemDataRole.UserRole, grandchild_note)

    def _add_tags_hierarchy(self):
        """Add dummy tags hierarchy to the tags tree"""
        tags_hierarchy = {
            Note("Work Tags", "Tags related to work"): [
                Note("Meeting", "Notes about meetings"),
                Note("Project", "Notes about projects"),
            ],
            Note("Personal Tags", "Tags for personal notes"): [
                Note("Shopping", "Notes about shopping"),
                Note("Travel", "Notes about travel"),
            ],
        }

        for parent_tag, child_tags in tags_hierarchy.items():
            parent_item = QTreeWidgetItem(self.left_sidebar.tags_tree)
            parent_item.setText(0, parent_tag.title)
            parent_item.setData(0, Qt.ItemDataRole.UserRole, parent_tag)

            for child_tag in child_tags:
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, child_tag.title)
                child_item.setData(0, Qt.ItemDataRole.UserRole, child_tag)
