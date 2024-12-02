from PySide6.QtWidgets import QMainWindow, QStatusBar
from PySide6.QtGui import QKeySequence, QShortcut
from ui.menu_handler import MenuHandler
from ui.tab_handler import TabHandler

#

class NoteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_window()
        
        # Initialize handlers
        self.menu_handler = MenuHandler(self)
        self.tab_handler = TabHandler(self)
        
        # Setup components
        self.main_content = self.tab_handler.setup_tabs()
        self.menu_handler.setup_menus()
        
        # Setup markdown view actions
        self.main_content.editor.set_view_actions(
            self.menu_handler.view_actions['maximize_editor'],
            self.menu_handler.view_actions['maximize_preview']
        )
        
        self.setup_command_palette()
        
    def setup_window(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        self.handle_size = 20
        self.setWindowTitle("Note Taking App")
        self.setGeometry(100, 100, 1000, 600)
        
    def setup_command_palette(self):
        from .command_palette import CommandPalette
        self.command_palette = CommandPalette(self)
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
        self.tab_handler.new_tab()
        
    def close_current_tab(self): 
        self.tab_handler.close_current_tab()
        
    def next_tab(self): 
        self.tab_handler.next_tab()
        
    def previous_tab(self): 
        self.tab_handler.previous_tab()

