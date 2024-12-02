from PySide6.QtWidgets import QMenu, QApplication, QStyle
from PySide6.QtGui import QAction
from PySide6.QtCore import QCoreApplication
from typing import Dict, Tuple

def create_file_menu(parent) -> Tuple[QMenu, Dict[str, QAction]]:
    "Create a file menu with actions and return both menu and actions dictionary"

    file_menu = QMenu("&File", parent)
    actions = {}
    
    style = QApplication.style()
    
    # New action
    new_icon = style.standardIcon(QStyle.SP_FileDialogNewFolder)
    actions['new'] = QAction(new_icon, "&New", parent)
    actions['new'].setShortcut("Ctrl+N")
    actions['new'].setStatusTip("Create a new note")
    actions['new'].setToolTip("Create a new note")
    file_menu.addAction(actions['new'])

    # Open action
    open_icon = style.standardIcon(QStyle.SP_DialogOpenButton)
    actions['open'] = QAction(open_icon, "&Open", parent)
    actions['open'].setShortcut("Ctrl+O")
    actions['open'].setStatusTip("Open an existing note")
    actions['open'].setToolTip("Open an existing note")
    file_menu.addAction(actions['open'])

    # Save action
    save_icon = style.standardIcon(QStyle.SP_DialogSaveButton)
    actions['save'] = QAction(save_icon, "&Save", parent)
    actions['save'].setShortcut("Ctrl+S")
    actions['save'].setStatusTip("Save the current note")
    actions['save'].setToolTip("Save the current note")
    file_menu.addAction(actions['save'])

    # Exit action
    exit_icon = style.standardIcon(QStyle.SP_DialogCloseButton)
    actions['exit'] = QAction(exit_icon, "E&xit", parent)
    actions['exit'].setShortcut("Ctrl+Q")
    actions['exit'].setStatusTip("Exit the application")
    actions['exit'].setToolTip("Exit the application") 
    file_menu.addAction(actions['exit'])
    actions['exit'].triggered.connect(QCoreApplication.instance().quit)

    return file_menu, actions

def create_view_menu(parent) -> Tuple[QMenu, Dict[str, QAction]]:
    """Create a view menu with actions and return both menu and actions dictionary"""
    view_menu = QMenu("&View", parent)
    actions = {}
    
    # Toggle left sidebar action
    actions['toggle_left_sidebar'] = QAction("Hide &Left Sidebar", parent)
    actions['toggle_left_sidebar'].setShortcut("Ctrl+\\")
    actions['toggle_left_sidebar'].setStatusTip("Toggle left sidebar visibility")
    view_menu.addAction(actions['toggle_left_sidebar'])
    
    # Toggle right sidebar action
    actions['toggle_right_sidebar'] = QAction("Hide &Right Sidebar", parent)
    actions['toggle_right_sidebar'].setShortcut("Ctrl+Shift+\\")
    actions['toggle_right_sidebar'].setStatusTip("Toggle right sidebar visibility")
    view_menu.addAction(actions['toggle_right_sidebar'])
    
    # Add separator
    view_menu.addSeparator()
    
    # Markdown view controls
    actions['maximize_editor'] = QAction("Ma&ximize Editor", parent)
    actions['maximize_editor'].setShortcut("Ctrl+Shift+E")
    actions['maximize_editor'].setStatusTip("Toggle maximize editor view")
    actions['maximize_editor'].setCheckable(True)
    view_menu.addAction(actions['maximize_editor'])
    
    actions['maximize_preview'] = QAction("Maximize &Preview", parent)
    actions['maximize_preview'].setShortcut("Ctrl+Shift+P")
    actions['maximize_preview'].setStatusTip("Toggle maximize preview")
    actions['maximize_preview'].setCheckable(True)
    view_menu.addAction(actions['maximize_preview'])
    
    return view_menu, actions
