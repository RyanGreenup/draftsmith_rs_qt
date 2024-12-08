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

    # file_menu.addAction(actions["new_root"])

    new_menu = QMenu("New", parent)
    new_menu.addAction(actions["new_root"])
    new_menu.addAction(actions["new_child"])
    new_menu.addAction(actions["new_sibling"])
    file_menu.addMenu(new_menu)

    file_menu.addAction(actions["open"])
    file_menu.addAction(actions["show_note_palette"])
    file_menu.addAction(actions["insert_note_link"])
    file_menu.addAction(actions["save"])
    file_menu.addAction(actions["delete_note"])
    file_menu.addAction(actions["exit"])

    file_menu.addSeparator()

    file_menu.addAction(actions["back"])
    file_menu.addAction(actions["forward"])

    return file_menu


def create_zoom_menu(parent, actions: Dict[str, QAction]) -> QMenu:
    """Create a Zoom submenu"""
    zoom_menu = QMenu("&Zoom", parent)
    zoom_menu.addAction(actions["zoom_in"])
    zoom_menu.addAction(actions["zoom_out"])
    zoom_menu.addAction(actions["zoom_reset"])
    return zoom_menu


def create_edit_menu(parent, actions: Dict[str, QAction]) -> QMenu:
    """Create an Edit menu using existing actions"""
    edit_menu = QMenu("&Edit", parent)
    edit_menu.addAction(actions["cut_note"])
    edit_menu.addAction(actions["paste_note"])
    return edit_menu

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

    # Add remote rendering toggle before the final separator and refresh
    view_menu.addSeparator()
    view_menu.addAction(actions["toggle_dark_mode"])
    view_menu.addSeparator()
    view_menu.addAction(actions["use_remote_rendering"])
    view_menu.addAction(actions["start_neovim"])

    # Add zoom menu before the final separator
    view_menu.addMenu(create_zoom_menu(parent, actions))

    # Add the Refresh action
    view_menu.addSeparator()
    view_menu.addAction(actions["refresh"])

    return view_menu
