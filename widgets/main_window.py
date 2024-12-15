import enum
from typing import Dict, Optional
from models.selection_data import NoteSelectionData
from PySide6.QtWidgets import QMainWindow, QStatusBar, QApplication
from PySide6.QtGui import QAction
from api.client import Tag
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import Qt
from models.note import Note
from ui.menu_handler import MenuHandler
from ui.tab_handler import TabHandler
from models.notes_model import NotesModel
from models.navigation_model import NavigationModel
from widgets.tab_content import TabContent
from widgets.note_id_link_insert import NoteLinkInsertPalette
from app_config import apply_dark_theme, apply_light_theme
from app_types import HierarchyLevel


class NoteApp(QMainWindow):
    def __init__(self, actions: Dict[str, QAction], api_url: str = "http://eir:37242"):
        super().__init__()
        self._actions = actions
        self._zoom_level = 0  # Track zoom level
        self.setup_window()
        self.api_url = api_url

        # Add notes model and load data
        self.notes_model = NotesModel(api_url)

        # Initialize navigation model
        self.navigation_model = NavigationModel()

        # Connect navigation actions directly
        self._actions["back"].triggered.connect(self.navigation_model.go_back)
        self._actions["forward"].triggered.connect(self.navigation_model.go_forward)

        # Initialize handlers
        self.menu_handler = MenuHandler(self, self._actions)

        # Initialize view actions in menu handler
        self.menu_handler.view_actions["toggle_left_sidebar"] = self._actions[
            "toggle_left_sidebar"
        ]
        self.menu_handler.view_actions["toggle_right_sidebar"] = self._actions[
            "toggle_right_sidebar"
        ]
        
        # Create dict of view actions for tabs
        self.tab_view_actions = {
            "maximize_editor": self._actions["maximize_editor"],
            "maximize_preview": self._actions["maximize_preview"],
            "use_remote_rendering": self._actions["use_remote_rendering"],
        }
        self.tab_handler = TabHandler(self, self.tab_view_actions)

        # Setup components
        self.main_content = self.tab_handler.setup_tabs()
        self.menu_handler.setup_menus()

        # Connect the model to the tree - do this before loading notes
        self.main_content.left_sidebar.tree.set_model(self.notes_model)

        # Now load the notes
        self.notes_model.load_notes()  # Load notes at startup

        # Connect note selection to right sidebar updates
        self.notes_model.note_selected.connect(self.update_right_sidebar)


        self.setup_command_palette()

    def setup_window(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.handle_size = 20
        self.setWindowTitle("Note Taking App")
        self.setGeometry(100, 100, 1000, 600)

    def setup_command_palette(self) -> None:
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
            self._actions["toggle_left_sidebar"].setText("Show &Left Sidebar")
        else:
            self.main_content.left_sidebar.show()
            self._actions["toggle_left_sidebar"].setText("Hide &Left Sidebar")

    def toggle_right_sidebar(self):
        """Toggle the visibility of the right sidebar"""
        if self.main_content.right_sidebar.isVisible():
            self.main_content.right_sidebar.hide()
            self._actions["toggle_right_sidebar"].setText("Show &Right Sidebar")
        else:
            self.main_content.right_sidebar.show()
            self._actions["toggle_right_sidebar"].setText("Hide &Right Sidebar")

    def show_command_palette(self):
        """Show the command palette and populate it with current menu actions"""
        self.command_palette.populate_actions(self.menuBar())
        self.command_palette.show_palette()

    def show_note_link_palette(self) -> None:
        """Show the note link insertion palette for the current tab"""
        current_tab = self.tab_handler.tab_widget.currentWidget()
        if isinstance(current_tab, TabContent):
            current_tab.show_note_link_palette()

    def focus_next_widget(self):
        """Simulate Tab key press to move focus to next widget"""
        self.focusNextChild()

    def focus_previous_widget(self):
        """Simulate Shift+Tab key press to move focus to previous widget"""
        self.focusPreviousChild()

    def update_right_sidebar(self, selection_data: "NoteSelectionData") -> None:
        """Update right sidebar content when a note is selected"""
        if selection_data.note:
            # Add note to navigation history
            self.navigation_model.add_to_history(selection_data.note.id)

            self.main_content.right_sidebar.update_forward_links(
                selection_data.forward_links
            )
            self.main_content.right_sidebar.update_backlinks(selection_data.backlinks)
            self.main_content.right_sidebar.update_tags(selection_data.tags)

    def new_tab(self) -> None:
        self.tab_handler.new_tab()

    def close_current_tab(self) -> None:
        self.tab_handler.close_current_tab()

    def next_tab(self) -> None:
        self.tab_handler.next_tab()

    def previous_tab(self) -> None:
        self.tab_handler.previous_tab()

    def _trigger_create_new_note(self, level: HierarchyLevel) -> None:
        """Create a new note and select it in the tree"""
        current_tab = self.tab_handler.tab_widget.currentWidget()
        if isinstance(current_tab, TabContent):
            if note := current_tab.handle_new_note_request(level):
                id = note.id
                self.status_bar.showMessage(f"Created new note: #{id}", 3000)
            else:
                self.status_bar.showMessage("Failed to create note", 3000)

    def save_current_note(self) -> None:
        """Save the current note's content"""
        current_note = self.main_content.left_sidebar.tree.currentItem()
        if current_note:
            note_data = current_note.data(0, Qt.ItemDataRole.UserRole)
            if note_data:
                content = self.main_content.editor.get_content()
                success = self.notes_model.update_note(note_data.id, content=content)

                if success:
                    self._reload_with_preserved_state()
                    self.status_bar.showMessage("Note saved successfully", 3000)
                else:
                    self.status_bar.showMessage("Failed to save note", 3000)

    def _reload_with_preserved_state(self) -> None:
        """Helper method to reload notes while preserving UI state"""
        # Store cursor position before refresh
        cursor_pos = self.main_content.editor.get_cursor_position()

        # Store current note ID and tree state
        current_item = self.main_content.left_sidebar.tree.currentItem()
        current_note_id = None
        if current_item:
            note_data = current_item.data(0, Qt.ItemDataRole.UserRole)
            if note_data:
                current_note_id = note_data.id

        # Save the tree state
        tree_state = self.main_content.left_sidebar.tree.save_state()

        # Reload notes
        self.notes_model.load_notes()

        # Restore tree state
        self.main_content.left_sidebar.tree.restore_state(tree_state)

        # If there was a selected note, reselect it and restore cursor
        if current_note_id:
            self.main_content.left_sidebar.tree.select_note_by_id(current_note_id)
            self.main_content.editor.set_cursor_position(cursor_pos)

    def refresh_model(self) -> None:
        """Refresh the notes model from the server"""
        self.notes_model.refresh_notes()
        self._reload_with_preserved_state()
        self.status_bar.showMessage("Notes refreshed from server", 3000)

    def focus_search(self) -> None:
        """Focus the search input in the left sidebar"""
        self.main_content.left_sidebar.focus_search()

    def toggle_follow_mode(self) -> None:
        """Toggle follow mode for tree and search widgets"""
        # Get new state from action
        new_state = self._actions["toggle_follow_mode"].isChecked()

        # Update all tabs
        for i in range(self.tab_handler.tab_widget.count()):
            tab = self.tab_handler.tab_widget.widget(i)
            if isinstance(tab, TabContent):
                tab.left_sidebar.tree.follow_mode = new_state
                tab.left_sidebar.search_sidebar.follow_mode = new_state
                tab.note_select_palette.follow_mode = new_state

        # Update status bar
        mode_status = "enabled" if new_state else "disabled"
        self.status_bar.showMessage(f"Follow mode {mode_status}", 3000)

    def start_neovim_server(self) -> None:
        """Start the Neovim server for the current tab's editor"""
        current_tab = self.tab_handler.tab_widget.currentWidget()
        if isinstance(current_tab, TabContent):
            current_tab.editor.editor.start_nvim_session()
            self.status_bar.showMessage("Neovim server started", 3000)

    def toggle_dark_mode(self):
        """Toggle between light and dark themes"""
        if self.is_dark_mode():
            apply_dark_theme(self._zoom_level)
        else:
            apply_light_theme(self._zoom_level)

        # Apply theme to all tabs
        for i in range(self.tab_handler.tab_widget.count()):
            tab = self.tab_handler.tab_widget.widget(i)
            if isinstance(tab, TabContent):
                tab.editor.apply_dark_theme(self.is_dark_mode())

        self.status_bar.showMessage("Theme changed", 3000)

    def is_dark_mode(self) -> bool:
        """Check if dark mode is currently enabled"""
        return self._actions["toggle_dark_mode"].isChecked()

    def zoom_in(self):
        """Increase the UI scale"""
        self._zoom_level = min(self._zoom_level + 1, 3)  # Max zoom of +3
        self._apply_current_theme()
        self.status_bar.showMessage(f"Zoom level: {self._zoom_level}", 3000)

    def zoom_out(self):
        """Decrease the UI scale"""
        self._zoom_level = max(self._zoom_level - 1, -3)  # Min zoom of -3
        self._apply_current_theme()
        self.status_bar.showMessage(f"Zoom level: {self._zoom_level}", 3000)

    def zoom_reset(self):
        """Reset the UI scale to default"""
        self._zoom_level = 0
        self._apply_current_theme()
        self.status_bar.showMessage("Zoom reset", 3000)

    def _apply_current_theme(self):
        """Apply the current theme with the current zoom level"""
        if self.is_dark_mode():
            apply_dark_theme(self._zoom_level)
        else:
            apply_light_theme(self._zoom_level)

    def _trigger_delete_current_note(self):
        """Trigger deletion of the note selected in the tree

        This does NOT delete the viewed note as users will typically work through the tree

        """
        current_tab = self.tab_handler.tab_widget.currentWidget()
        if isinstance(current_tab, TabContent):
            # Get the current note ID from the tab
            # Use the tree instead
            # note_id = current_tab.get_current_note_id()
            # This method can take note_id if I change my mind later
            current_tab._handle_note_deletion()

    def app(self):
        """Helper method to get QApplication instance"""
        return QApplication.instance()

    def _trigger_save_current_tab(self):
        """Trigger save on the currently active tab"""
        current_tab = self.tab_handler.tab_widget.currentWidget()
        if isinstance(current_tab, TabContent):
            note_id = current_tab.get_current_note_id()
            if note_id is not None:
                current_tab._handle_save_request(note_id)

    def _trigger_paste_onto_selected_tree_item(self) -> None:
        """Trigger paste onto the currently selected tree item in the active tab"""
        current_tab = self.tab_handler.tab_widget.currentWidget()
        if isinstance(current_tab, TabContent):
            current_tab.paste_onto_selected_tree_item()

    def _trigger_cut_selected_tree_item(self) -> None:
        """Trigger cut on the currently selected tree item in the active tab"""
        current_tab = self.tab_handler.tab_widget.currentWidget()
        if isinstance(current_tab, TabContent):
            current_tab.cut_selected_tree_item()

    def _trigger_promote_selected_tree_item(self) -> None:
        """Promote the currently selected tree item in the active tab"""
        current_tab = self.tab_handler.tab_widget.currentWidget()
        if isinstance(current_tab, TabContent):
            if current_tab.promote_selected_tree_item():
                self.status_bar.showMessage("Note promoted", 3000)
            else:
                self.status_bar.showMessage("Could not promote note", 3000)

    def _trigger_demote_selected_tree_item(self) -> None:
        """Demote the currently selected tree item in the active tab"""
        current_tab = self.tab_handler.tab_widget.currentWidget()
        if isinstance(current_tab, TabContent):
            if current_tab.demote_selected_tree_item():
                self.status_bar.showMessage("Note demoted", 3000)
            else:
                self.status_bar.showMessage("Could not demote note", 3000)

    def handle_filter_text(self, text: str) -> None:
        """Handle filter text entered in the current tab"""
        current_tab = self.tab_handler.tab_widget.currentWidget()
        if isinstance(current_tab, TabContent):
            current_tab.filter_sidebar(text)
