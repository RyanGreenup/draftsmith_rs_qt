from PySide6.QtWidgets import QMenuBar
from PySide6.QtGui import QAction
from typing import Dict, Any
from app_types import HierarchyLevel


class MenuHandler:
    def __init__(self, main_window, actions: Dict[str, QAction]):
        self.main_window = main_window
        self.menubar = main_window.menuBar()
        self.actions = actions
        self.file_menu = None
        self.view_menu = None
        self.tabs_menu = None
        self.view_actions = {}  # Initialize view_actions dictionary

    def setup_menus(self):
        from ui.menu_manager import create_file_menu, create_view_menu, create_tabs_menu

        # Setup File menu
        self.file_menu = create_file_menu(self.main_window, self.actions)
        self.menubar.addMenu(self.file_menu)

        # Setup View menu
        self.view_menu = create_view_menu(self.main_window, self.actions)
        self.menubar.addMenu(self.view_menu)

        # Setup Tabs menu
        self.tabs_menu = create_tabs_menu(self.main_window, self.actions)
        self.menubar.addMenu(self.tabs_menu)

        self._connect_actions()

    def _connect_actions(self):
        # Connect tab actions
        self.actions["new_tab"].triggered.connect(self.main_window.new_tab)
        self.actions["close_tab"].triggered.connect(self.main_window.close_current_tab)
        self.actions["next_tab"].triggered.connect(self.main_window.next_tab)
        self.actions["prev_tab"].triggered.connect(self.main_window.previous_tab)

        # Connect save action to current tab
        self.actions["save"].triggered.connect(
            self.main_window._trigger_save_current_tab
        )

        # Add connection for delete action
        self.actions["delete_note"].triggered.connect(
            self.main_window._trigger_delete_current_note
        )

        # Connect file actions
        self.actions["new_root"].triggered.connect(
            lambda: self.main_window._trigger_create_new_note(HierarchyLevel.ROOT)
        )

        self.actions["new_child"].triggered.connect(
            lambda: self.main_window._trigger_create_new_note(HierarchyLevel.CHILD)
        )

        self.actions["new_sibling"].triggered.connect(
            lambda: self.main_window._trigger_create_new_note(HierarchyLevel.SIBLING)
        )

        # Connect view actions
        self.actions["toggle_left_sidebar"].triggered.connect(
            self.main_window.toggle_left_sidebar
        )
        self.actions["toggle_right_sidebar"].triggered.connect(
            self.main_window.toggle_right_sidebar
        )
        self.actions["focus_next"].triggered.connect(self.main_window.focus_next_widget)
        self.actions["focus_previous"].triggered.connect(
            self.main_window.focus_previous_widget
        )
        self.actions["focus_search"].triggered.connect(
            lambda: (
                self.main_window.tab_handler.tab_widget.currentWidget().focus_search()
                if self.main_window.tab_handler.tab_widget.currentWidget()
                else None
            )
        )
        self.actions["toggle_follow_mode"].triggered.connect(
            self.main_window.toggle_follow_mode
        )
        self.actions["refresh"].triggered.connect(self.main_window.refresh_model)

        # Connect neovim action
        self.actions["start_neovim"].triggered.connect(
            self.main_window.start_neovim_server
        )

        # Connect dark mode action
        self.actions["toggle_dark_mode"].triggered.connect(
            self.main_window.toggle_dark_mode
        )

        # Connect zoom actions
        self.actions["zoom_in"].triggered.connect(self.main_window.zoom_in)
        self.actions["zoom_out"].triggered.connect(self.main_window.zoom_out)
        self.actions["zoom_reset"].triggered.connect(self.main_window.zoom_reset)

        # Connect tab state actions
        self.actions["save_tabs_state"].triggered.connect(
            self.main_window.tab_handler.save_tabs_state
        )
        self.actions["restore_tabs_state"].triggered.connect(
            self.main_window.tab_handler.restore_tabs_state
        )

        # Connect note palette action
        self.actions["show_note_palette"].triggered.connect(
            lambda: (
                self.main_window.tab_handler.tab_widget.currentWidget().show_note_select_palette()
                if self.main_window.tab_handler.tab_widget.currentWidget()
                else None
            )
        )

        # Connect link palette action
        self.actions["show_link_palette"].triggered.connect(
            lambda: (
                self.main_window.tab_handler.tab_widget.currentWidget().show_link_insert_palette()
                if self.main_window.tab_handler.tab_widget.currentWidget()
                else None
            )
        )
