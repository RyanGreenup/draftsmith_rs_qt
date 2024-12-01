from PySide6.QtWidgets import QMainWindow, QSplitter, QTextEdit, QTreeWidgetItem
from PySide6.QtCore import Qt
from models.note import Note
from .notes_tree import NotesTreeWidget


class NoteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.handle_size = 20
        self.setWindowTitle("Note Taking App")
        self.setGeometry(100, 100, 1000, 600)

        # Create main splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(self.handle_size)

        # Create tree widget for sidebar
        self.tree = NotesTreeWidget()
        self.tree.setHeaderLabel("Notes")
        self.tree.setMinimumWidth(100)
        self.tree.itemSelectionChanged.connect(self.on_selection_changed)

        # Create text edit for main content
        self.text_edit = QTextEdit()

        # Create tags tree widget for sidebar
        self.tags_tree = NotesTreeWidget()
        self.tags_tree.setHeaderLabel("Tags")
        self.tags_tree.setMinimumWidth(100)

        # Create additional tree widget for sidebar
        self.additional_tree = NotesTreeWidget()
        self.additional_tree.setHeaderLabel("Additional")
        self.additional_tree.setMinimumWidth(200)

        # Create a new splitter for the right sidebar
        self.right_splitter = QSplitter(Qt.Orientation.Vertical)
        self.right_splitter.setHandleWidth(self.handle_size)
        self.right_splitter.addWidget(self.tags_tree)
        self.right_splitter.addWidget(self.additional_tree)

        # Add widgets to main splitter
        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.text_edit)
        self.splitter.addWidget(self.right_splitter)

        # Set splitter as central widget
        self.setCentralWidget(self.splitter)

        # Add dummy data
        self.add_dummy_data()

    def on_selection_changed(self):
        selected_items = self.tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            note = item.data(0, Qt.ItemDataRole.UserRole)
            if note:
                self.text_edit.setText(note.content)
            else:
                self.text_edit.clear()

    def add_dummy_data(self):
        notes_hierarchy = {
            Note("Work", "General work-related notes and tasks"): [
                Note(
                    "Meeting Notes",
                    "Meeting agenda:\n1. Project updates\n2. Timeline review",
                ): [
                    Note("Agenda Item 1", "Discuss project timeline"),
                    Note("Agenda Item 2", "Review milestones"),
                ],
                Note(
                    "Project Ideas",
                    "New features to implement:\n- Dark mode\n- Auto-save",
                ): [
                    Note("Dark Mode", "Implement dark theme for the app"),
                    Note("Auto-Save", "Add auto-save functionality"),
                ],
                Note("To-Do List", "- Send report\n- Update documentation"): [
                    Note("Report", "Prepare and send project report"),
                    Note("Documentation", "Update user manual"),
                ],
            ],
            Note("Personal", "My personal notes and plans"): [
                Note("Shopping List", "- Groceries\n- Household items"): [
                    Note("Groceries", "Milk, Bread, Eggs"),
                    Note("Household Items", "Cleaning supplies, Towels"),
                ],
                Note("Travel Plans", "Places to visit:\n1. Paris\n2. Tokyo"): [
                    Note("Paris", "Visit Eiffel Tower, Louvre Museum"),
                    Note("Tokyo", "Explore Shibuya, Visit Senso-ji Temple"),
                ],
                Note("Goals", "2024 Goals:\n1. Learn Python\n2. Exercise more"): [
                    Note("Learn Python", "Complete online courses and projects"),
                    Note("Exercise More", "Join a gym, Practice yoga"),
                ],
            ],
        }

        # Add dummy data to the notes sidebar
        for parent_note, child_notes in notes_hierarchy.items():
            parent_item = QTreeWidgetItem(self.tree)
            parent_item.setText(0, parent_note.title)
            parent_item.setData(0, Qt.ItemDataRole.UserRole, parent_note)

            for child_note in child_notes:
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, child_note.title)
                child_item.setData(0, Qt.ItemDataRole.UserRole, child_note)

        # Add dummy data to the tags sidebar
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
            parent_item = QTreeWidgetItem(self.tags_tree)
            parent_item.setText(0, parent_tag.title)
            parent_item.setData(0, Qt.ItemDataRole.UserRole, parent_tag)

            for child_tag in child_tags:
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, child_tag.title)
                child_item.setData(0, Qt.ItemDataRole.UserRole, child_tag)
