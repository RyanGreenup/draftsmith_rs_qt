from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from typing import Dict


def create_tabs_menu(parent, actions: Dict[str, QAction]) -> QMenu:
    """Create a Tabs menu using existing actions"""
    tabs_menu = QMenu("&Tabs", parent)

    tabs_menu.addAction(actions["new_tab"])
    tabs_menu.addAction(actions["close_tab"])

    tabs_menu.addSeparator()

    tabs_menu.addAction(actions["next_tab"])
    tabs_menu.addAction(actions["prev_tab"])

    # Add new separator and state actions
    tabs_menu.addSeparator()
    tabs_menu.addAction(actions["save_tabs_state"])
    tabs_menu.addAction(actions["restore_tabs_state"])

    return tabs_menu


def create_file_menu(parent, actions: Dict[str, QAction]) -> QMenu:
    """Create a File menu using existing actions"""
    file_menu = QMenu("&File", parent)

    file_menu.addAction(actions["new"])
    file_menu.addAction(actions["open"])
    file_menu.addAction(actions["save"])
    file_menu.addAction(actions["exit"])

    file_menu.addSeparator()

    file_menu.addAction(actions["back"])
    file_menu.addAction(actions["forward"])

    return file_menu


def create_view_menu(parent, actions: Dict[str, QAction]) -> QMenu:
    """Create a View menu using existing actions"""
    view_menu = QMenu("&View", parent)

    view_menu.addAction(actions["toggle_left_sidebar"])
    view_menu.addAction(actions["toggle_right_sidebar"])

    view_menu.addSeparator()

    view_menu.addAction(actions["focus_next"])
    view_menu.addAction(actions["focus_previous"])
    view_menu.addAction(actions["focus_search"])

    view_menu.addSeparator()

    view_menu.addAction(actions["maximize_editor"])
    view_menu.addAction(actions["maximize_preview"])

    view_menu.addSeparator()
    view_menu.addAction(actions["toggle_follow_mode"])

    # Add Neovim action before the final separator and refresh
    view_menu.addSeparator()
    view_menu.addAction(actions["start_neovim"])
    
    # Add the Refresh action
    view_menu.addSeparator()
    view_menu.addAction(actions["refresh"])

    return view_menu
