from PySide6.QtWidgets import QMainWindow, QTreeWidgetItem, QStatusBar
from PySide6.QtCore import Qt
from .main_content import MainContent
from PySide6.QtGui import QKeySequence, QShortcut
from models.note import Note
from .notes_tree import NotesTreeWidget
from .markdown_editor import MarkdownEditor

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

        # Create and setup main content
        self.main_content = MainContent(self.handle_size)
        self.setCentralWidget(self.main_content)
        
        # Connect selection signal
        self.main_content.left_sidebar.tree.itemSelectionChanged.connect(self.on_selection_changed)

        # Create menubar
        self.menubar = self.menuBar()

        # Add File menu
        from ui.menu_manager import create_file_menu, create_view_menu
        self.file_menu, self.file_actions = create_file_menu(self)
        self.menubar.addMenu(self.file_menu)

        # Add View menu
        self.view_menu, self.view_actions = create_view_menu(self)
        self.menubar.addMenu(self.view_menu)

        # Connect markdown view actions
        self.main_content.editor.set_view_actions(
            self.view_actions['maximize_editor'],
            self.view_actions['maximize_preview']
        )

        # Connect view actions
        self.view_actions['toggle_left_sidebar'].triggered.connect(self.toggle_left_sidebar)
        self.view_actions['toggle_right_sidebar'].triggered.connect(self.toggle_right_sidebar)
        self.view_actions['focus_next'].triggered.connect(self.focus_next_widget)
        self.view_actions['focus_previous'].triggered.connect(self.focus_previous_widget)

        # Create command palette
        from .command_palette import CommandPalette
        self.command_palette = CommandPalette(self)

        # Add shortcut for command palette
        self.command_shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        self.command_shortcut.activated.connect(self.show_command_palette)

        # Add dummy data
        self.add_dummy_data()

    def on_selection_changed(self):
        selected_items = self.main_content.left_sidebar.tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            note = item.data(0, Qt.ItemDataRole.UserRole)
            if note:
                self.main_content.editor.set_content(note.content)
            else:
                self.main_content.editor.set_content("")

    def on_tree_selection_changed(self, text):
        if text == "Notes":
            self.main_content.left_sidebar.tree.show()
            self.main_content.left_sidebar.tags_tree.hide()
            self.status_bar.showMessage("Showing Notes Tree")
        else:  # Tags
            self.main_content.left_sidebar.tree.hide()
            self.main_content.left_sidebar.tags_tree.show()
            self.status_bar.showMessage("Showing Tags Tree")

    def toggle_left_sidebar(self):
        """Toggle the visibility of the left sidebar"""
        if self.main_content.left_sidebar.isVisible():
            self.main_content.left_sidebar.hide()
            self.view_actions['toggle_left_sidebar'].setText("Show &Left Sidebar")
        else:
            self.main_content.left_sidebar.show()
            self.view_actions['toggle_left_sidebar'].setText("Hide &Left Sidebar")

    def toggle_right_sidebar(self):
        """Toggle the visibility of the right sidebar"""
        if self.right_splitter.isVisible():
            self.right_splitter.hide()
            self.view_actions['toggle_right_sidebar'].setText("Show &Right Sidebar")
        else:
            self.right_splitter.show()
            self.view_actions['toggle_right_sidebar'].setText("Hide &Right Sidebar")

    def show_command_palette(self):
        """Show the command palette and populate it with current menu actions"""
        self.command_palette.populate_actions(self.menuBar())
        self.command_palette.show_palette()

    def focus_next_widget(self):
        """Simulate Tab key press to move focus to next widget"""
        self.focusNextChild()

    def focus_previous_widget(self):
        """Simulate Shift+Tab key press to move focus to previous widget"""
        self.focusPreviousChild()

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
            parent_item = QTreeWidgetItem(self.main_content.left_sidebar.tree)
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
            parent_item = QTreeWidgetItem(self.main_content.left_sidebar.tags_tree)
            parent_item.setText(0, parent_tag.title)
            parent_item.setData(0, Qt.ItemDataRole.UserRole, parent_tag)

            for child_tag in child_tags:
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, child_tag.title)
                child_item.setData(0, Qt.ItemDataRole.UserRole, child_tag)
