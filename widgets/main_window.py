from PySide6.QtWidgets import QMainWindow, QTreeWidgetItem, QStatusBar
from PySide6.QtCore import Qt
from .main_content import MainContent
from .tab_widget import NotesTabWidget
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

        # Create and setup tab widget
        self.tab_widget = NotesTabWidget(self)
        self.setCentralWidget(self.tab_widget)
        self.main_content = self.tab_widget.add_new_tab("Main")
        

        # Create menubar
        self.menubar = self.menuBar()

        # Add File menu
        from ui.menu_manager import create_file_menu, create_view_menu, create_tabs_menu
        self.file_menu, self.file_actions = create_file_menu(self)
        self.menubar.addMenu(self.file_menu)

        # Add View menu
        self.view_menu, self.view_actions = create_view_menu(self)
        self.menubar.addMenu(self.view_menu)

        # Add Tabs menu
        self.tabs_menu, self.tabs_actions = create_tabs_menu(self)
        self.menubar.addMenu(self.tabs_menu)

        # Connect tab actions
        self.tabs_actions['new_tab'].triggered.connect(self.new_tab)
        self.tabs_actions['close_tab'].triggered.connect(self.close_current_tab)
        self.tabs_actions['next_tab'].triggered.connect(self.next_tab)
        self.tabs_actions['prev_tab'].triggered.connect(self.previous_tab)

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
        if self.main_content.right_sidebar.isVisible():
            self.main_content.right_sidebar.hide()
            self.view_actions['toggle_right_sidebar'].setText("Show &Right Sidebar")
        else:
            self.main_content.right_sidebar.show()
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

    def new_tab(self):
        """Create a new tab"""
        self.tab_widget.add_new_tab()

    def close_current_tab(self):
        """Close the current tab"""
        current_index = self.tab_widget.currentIndex()
        self.tab_widget.close_tab(current_index)

    def next_tab(self):
        """Switch to next tab"""
        current = self.tab_widget.currentIndex()
        next_index = (current + 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(next_index)

    def previous_tab(self):
        """Switch to previous tab"""
        current = self.tab_widget.currentIndex()
        prev_index = (current - 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(prev_index)

