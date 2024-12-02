from PySide6.QtWidgets import (QMainWindow, QSplitter, QTextEdit, QTreeWidgetItem, 
                              QStatusBar, QComboBox, QVBoxLayout, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from models.note import Note
from .notes_tree import NotesTreeWidget

#

class NoteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Create and set status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

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

        # Create tags tree widget for sidebar
        self.tags_tree = NotesTreeWidget()
        self.tags_tree.setHeaderLabel("Tags")
        self.tags_tree.setMinimumWidth(100)

        # Create combo box for tree selection
        self.tree_selector = QComboBox()
        self.tree_selector.addItems(["Notes", "Tags"])
        self.tree_selector.currentTextChanged.connect(self.on_tree_selection_changed)

        # Create a container widget for the combo box and current tree
        self.left_sidebar = QWidget()
        self.left_layout = QVBoxLayout(self.left_sidebar)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.addWidget(self.tree_selector)
        self.left_layout.addWidget(self.tree)
        self.left_layout.addWidget(self.tags_tree)

        # Initially hide tags tree
        self.tags_tree.hide()

        # Create text edit for main content
        self.text_edit = QTextEdit()

        # Create additional tree widget for sidebar
        self.additional_tree = NotesTreeWidget()
        self.additional_tree.setHeaderLabel("Additional")
        self.additional_tree.setMinimumWidth(200)

        # Create a new splitter for the right sidebar
        self.right_splitter = QSplitter(Qt.Orientation.Vertical)
        self.right_splitter.setHandleWidth(self.handle_size)
        self.right_splitter.addWidget(self.additional_tree)

        # Add widgets to main splitter
        self.splitter.addWidget(self.left_sidebar)
        self.splitter.addWidget(self.text_edit)
        self.splitter.addWidget(self.right_splitter)

        # Set splitter as central widget
        self.setCentralWidget(self.splitter)

        # Create command palette
        from .command_palette import CommandPalette
        self.command_palette = CommandPalette(self)

        # Add shortcut for command palette
        self.command_shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        self.command_shortcut.activated.connect(self.show_command_palette)

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

    def on_tree_selection_changed(self, text):
        if text == "Notes":
            self.tree.show()
            self.tags_tree.hide()
            self.status_bar.showMessage("Showing Notes Tree")
        else:  # Tags
            self.tree.hide()
            self.tags_tree.show()
            self.status_bar.showMessage("Showing Tags Tree")

    def show_command_palette(self):
        """Show the command palette and populate it with current menu actions"""
        self.command_palette.populate_actions(self.menuBar())
        self.command_palette.show_palette()

    def add_dummy_data(self):
        notes_hierarchy = [
            (Note("Work", "General work-related notes and tasks"), [
                (Note(
                    "Meeting Notes",
                    "Meeting agenda:\n1. Project updates\n2. Timeline review",
                ), [
                    Note("Agenda Item 1", "Discuss project timeline"),
                    Note("Agenda Item 2", "Review milestones"),
                ]),
                (Note(
                    "Project Ideas",
                    "New features to implement:\n- Dark mode\n- Auto-save",
                ), [
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

        # Add dummy data to the notes sidebar
        for parent_note, child_notes in notes_hierarchy:
            parent_item = QTreeWidgetItem(self.tree)
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
