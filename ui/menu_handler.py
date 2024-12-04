from PySide6.QtWidgets import QMenuBar
from PySide6.QtGui import QAction
from typing import Dict, Any


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

        # Connect file actions
        self.actions["new"].triggered.connect(self.main_window.create_new_note)

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
            self.main_window.focus_search
        )
        self.actions["toggle_follow_mode"].triggered.connect(
            self.main_window.toggle_follow_mode
        )
        self.actions["refresh"].triggered.connect(self.main_window.refresh_model)
        
        # Connect neovim action
        self.actions["start_neovim"].triggered.connect(
            self.main_window.start_neovim_server
        )
