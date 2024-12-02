from PySide6.QtWidgets import QMenu, QApplication, QStyle
from PySide6.QtGui import QAction
from PySide6.QtCore import QCoreApplication, Qt
from typing import Dict, Tuple, cast


def create_tabs_menu(parent) -> Tuple[QMenu, Dict[str, QAction]]:
    """Create a tabs menu with actions"""
    tabs_menu = QMenu("&Tabs", parent)
    actions = {}

    # New tab action
    actions["new_tab"] = QAction("&New Tab", parent)
    actions["new_tab"].setShortcut("Ctrl+T")
    actions["new_tab"].setStatusTip("Create a new tab")
    tabs_menu.addAction(actions["new_tab"])

    # Close tab action
    actions["close_tab"] = QAction("&Close Tab", parent)
    actions["close_tab"].setShortcut("Ctrl+W")
    actions["close_tab"].setStatusTip("Close current tab")
    tabs_menu.addAction(actions["close_tab"])

    tabs_menu.addSeparator()

    # Next/Previous tab actions
    actions["next_tab"] = QAction("Next Tab", parent)
    actions["next_tab"].setShortcut("Ctrl+Tab")
    actions["next_tab"].setStatusTip("Switch to next tab")
    tabs_menu.addAction(actions["next_tab"])

    actions["prev_tab"] = QAction("Previous Tab", parent)
    actions["prev_tab"].setShortcut("Ctrl+Shift+Tab")
    actions["prev_tab"].setStatusTip("Switch to previous tab")
    tabs_menu.addAction(actions["prev_tab"])

    return tabs_menu, actions


def create_file_menu(parent) -> Tuple[QMenu, Dict[str, QAction]]:
    "Create a file menu with actions and return both menu and actions dictionary"

    file_menu = QMenu("&File", parent)
    actions = {}

    style = QApplication.style()

    # New action
    new_icon = style.standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder)
    actions["new"] = QAction(new_icon, "&New", parent)
    actions["new"].setShortcut("Ctrl+N")
    actions["new"].setStatusTip("Create a new note")
    actions["new"].setToolTip("Create a new note")
    file_menu.addAction(actions["new"])

    # Open action
    open_icon = style.standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton)
    actions["open"] = QAction(open_icon, "&Open", parent)
    actions["open"].setShortcut("Ctrl+O")
    actions["open"].setStatusTip("Open an existing note")
    actions["open"].setToolTip("Open an existing note")
    file_menu.addAction(actions["open"])

    # Save action
    save_icon = style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)
    actions["save"] = QAction(save_icon, "&Save", parent)
    actions["save"].setShortcut("Ctrl+S")
    actions["save"].setStatusTip("Save the current note")
    actions["save"].setToolTip("Save the current note")
    file_menu.addAction(actions["save"])

    # Exit action
    exit_icon = style.standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton)
    actions["exit"] = QAction(exit_icon, "E&xit", parent)
    actions["exit"].setShortcut("Ctrl+Q")
    actions["exit"].setStatusTip("Exit the application")
    actions["exit"].setToolTip("Exit the application")
    file_menu.addAction(actions["exit"])
    app = cast(QApplication, QCoreApplication.instance())
    actions["exit"].triggered.connect(app.quit)

    # Add separator before navigation actions
    file_menu.addSeparator()

    # Back action
    back_icon = style.standardIcon(QStyle.StandardPixmap.SP_ArrowBack)
    actions["back"] = QAction(back_icon, "Go &Back", parent)
    actions["back"].setShortcut("Alt+Left")
    actions["back"].setStatusTip("Go to previously viewed note")
    actions["back"].setEnabled(False)  # Initially disabled
    file_menu.addAction(actions["back"])

    # Forward action  
    forward_icon = style.standardIcon(QStyle.StandardPixmap.SP_ArrowForward)
    actions["forward"] = QAction(forward_icon, "Go &Forward", parent)
    actions["forward"].setShortcut("Alt+Right") 
    actions["forward"].setStatusTip("Go to next viewed note")
    actions["forward"].setEnabled(False)  # Initially disabled
    file_menu.addAction(actions["forward"])

    return file_menu, actions


def create_view_menu(parent) -> Tuple[QMenu, Dict[str, QAction]]:
    """Create a view menu with actions and return both menu and actions dictionary"""
    view_menu = QMenu("&View", parent)
    actions = {}

    # Toggle left sidebar action
    actions["toggle_left_sidebar"] = QAction("Hide &Left Sidebar", parent)
    actions["toggle_left_sidebar"].setShortcut("Ctrl+\\")
    actions["toggle_left_sidebar"].setStatusTip("Toggle left sidebar visibility")
    view_menu.addAction(actions["toggle_left_sidebar"])

    # Toggle right sidebar action
    actions["toggle_right_sidebar"] = QAction("Hide &Right Sidebar", parent)
    actions["toggle_right_sidebar"].setShortcut("Ctrl+Shift+\\")
    actions["toggle_right_sidebar"].setStatusTip("Toggle right sidebar visibility")
    view_menu.addAction(actions["toggle_right_sidebar"])

    # Add separator
    view_menu.addSeparator()

    # Navigation controls
    actions["focus_next"] = QAction("Focus &Next Widget", parent)
    actions["focus_next"].setShortcut("Ctrl+J")
    actions["focus_next"].setStatusTip("Move focus to next widget (like Tab)")
    view_menu.addAction(actions["focus_next"])

    actions["focus_previous"] = QAction("Focus &Previous Widget", parent)
    actions["focus_previous"].setShortcut("Ctrl+K")
    actions["focus_previous"].setStatusTip(
        "Move focus to previous widget (like Shift+Tab)"
    )
    view_menu.addAction(actions["focus_previous"])

    # Add separator
    view_menu.addSeparator()

    # Markdown view controls
    actions["maximize_editor"] = QAction("Ma&ximize Editor", parent)
    actions["maximize_editor"].setShortcut("Ctrl+Shift+E")
    actions["maximize_editor"].setStatusTip("Toggle maximize editor view")
    actions["maximize_editor"].setCheckable(True)
    view_menu.addAction(actions["maximize_editor"])

    actions["maximize_preview"] = QAction("Maximize &Preview", parent)
    actions["maximize_preview"].setShortcut("Ctrl+Shift+P")
    actions["maximize_preview"].setStatusTip("Toggle maximize preview")
    actions["maximize_preview"].setCheckable(True)
    view_menu.addAction(actions["maximize_preview"])

    return view_menu, actions
