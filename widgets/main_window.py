from typing import List, Dict
from PySide6.QtWidgets import QMainWindow, QStatusBar
from PySide6.QtGui import QAction
from api.client import Tag
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import Qt
from models.note import Note
from ui.menu_handler import MenuHandler
from ui.tab_handler import TabHandler
from models.notes_model import NotesModel
from models.navigation_model import NavigationModel

#


class NoteApp(QMainWindow):
    def __init__(self, actions: Dict[str, QAction]):
        super().__init__()
        self.actions = actions
        self.setup_window()

        # Add notes model and load data
        self.notes_model = NotesModel("http://eir:37242")

        # Initialize navigation model
        self.navigation_model = NavigationModel()

        # Initialize handlers
        self.menu_handler = MenuHandler(self, self.actions)
        self.tab_handler = TabHandler(self)

        # Setup components
        self.main_content = self.tab_handler.setup_tabs()
        self.menu_handler.setup_menus()

        # Connect the model to the tree - do this before loading notes
        self.main_content.left_sidebar.tree.set_model(self.notes_model)
        
        # Now load the notes
        self.notes_model.load_notes()  # Load notes at startup

        # Connect note selection to right sidebar updates
        self.notes_model.note_selected.connect(self.update_right_sidebar)

        # Connect forward link selection
        self.main_content.right_sidebar.forward_links.note_selected.connect(
            self.handle_forward_link_selection
        )
        # Connect backlink selection
        self.main_content.right_sidebar.backlinks.note_selected.connect(
            self.handle_forward_link_selection  # We can reuse this as it does the same thing
        )

        # Setup markdown view actions
        self.main_content.editor.set_view_actions(
            self.menu_handler.actions["maximize_editor"],
            self.menu_handler.actions["maximize_preview"],
        )

        # Connect navigation actions
        self.menu_handler.actions["back"].triggered.connect(self.navigate_back)
        self.menu_handler.actions["forward"].triggered.connect(
            self.navigate_forward
        )
        self.navigation_model.navigation_changed.connect(self.update_navigation_actions)

        # Connect save action
        self.menu_handler.actions["save"].triggered.connect(self.save_current_note)
        self.main_content.editor.save_requested.connect(self.save_current_note)

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
            self.menu_handler.view_actions["toggle_left_sidebar"].setText(
                "Show &Left Sidebar"
            )
        else:
            self.main_content.left_sidebar.show()
            self.menu_handler.view_actions["toggle_left_sidebar"].setText(
                "Hide &Left Sidebar"
            )

    def toggle_right_sidebar(self):
        """Toggle the visibility of the right sidebar"""
        if self.main_content.right_sidebar.isVisible():
            self.main_content.right_sidebar.hide()
            self.menu_handler.view_actions["toggle_right_sidebar"].setText(
                "Show &Right Sidebar"
            )
        else:
            self.main_content.right_sidebar.show()
            self.menu_handler.view_actions["toggle_right_sidebar"].setText(
                "Hide &Right Sidebar"
            )

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

    def handle_forward_link_selection(self, note_id: int) -> None:
        """Handle when a forward link is selected"""
        # Update tree selection
        self.main_content.left_sidebar.tree.select_note_by_id(note_id)
        # This will trigger the tree's selection changed signal, which will update everything else

    def navigate_back(self):
        note_id = self.navigation_model.go_back()
        if note_id != -1:
            self.main_content.left_sidebar.tree.select_note_by_id(note_id)

    def navigate_forward(self):
        note_id = self.navigation_model.go_forward()
        if note_id != -1:
            self.main_content.left_sidebar.tree.select_note_by_id(note_id)

    def update_navigation_actions(self):
        """Update the enabled state of navigation actions"""
        self.menu_handler.actions["back"].setEnabled(
            self.navigation_model.can_go_back()
        )
        self.menu_handler.actions["forward"].setEnabled(
            self.navigation_model.can_go_forward()
        )

    def update_right_sidebar(
        self,
        note: Note,
        forward_links: List[Note],
        backlinks: List[Note],
        tags: List[Tag],
    ) -> None:
        """Update right sidebar content when a note is selected"""
        if note:
            # Add note to navigation history
            self.navigation_model.add_to_history(note.id)

            self.main_content.right_sidebar.update_forward_links(forward_links)
            self.main_content.right_sidebar.update_backlinks(backlinks)
            self.main_content.right_sidebar.update_tags(tags)

    def new_tab(self):
        self.tab_handler.new_tab()

    def close_current_tab(self):
        self.tab_handler.close_current_tab()

    def next_tab(self):
        self.tab_handler.next_tab()

    def previous_tab(self):
        self.tab_handler.previous_tab()

    def create_new_note(self):
        """Create a new note and select it in the tree"""
        # Get currently selected note as parent
        current_item = self.main_content.left_sidebar.tree.currentItem()
        parent_id = None
        if current_item:
            parent_data = current_item.data(0, Qt.ItemDataRole.UserRole)
            if parent_data:
                parent_id = parent_data.id

        # Create new note
        new_note = self.notes_model.create_note(
            title="New Note",
            content="",
            parent_id=parent_id
        )
        
        if new_note:
            # Select the new note in tree
            self.main_content.left_sidebar.tree.select_note_by_id(new_note.id)
            # Focus the editor
            self.main_content.editor.setFocus()
            self.status_bar.showMessage("Created new note", 3000)
        else:
            self.status_bar.showMessage("Failed to create note", 3000)

    def save_current_note(self):
        """Save the current note's content"""
        current_note = self.main_content.left_sidebar.tree.currentItem()
        if current_note:
            note_data = current_note.data(0, Qt.ItemDataRole.UserRole)
            if note_data:
                # Save the current tree state before saving
                tree_state = self.main_content.left_sidebar.tree.save_state()
                
                content = self.main_content.editor.get_content()
                success = self.notes_model.update_note(note_data.id, content=content)
                
                if success:
                    # Reload notes and restore tree state
                    self.notes_model.load_notes()
                    self.main_content.left_sidebar.tree.restore_state(tree_state)
                    self.status_bar.showMessage("Note saved successfully", 3000)
                else:
                    self.status_bar.showMessage("Failed to save note", 3000)

    def refresh_model(self):
        """Refresh the notes model from the server"""
        # The model handles the refresh operation
        self.notes_model.refresh_notes()
        self.status_bar.showMessage("Notes refreshed from server", 3000)
