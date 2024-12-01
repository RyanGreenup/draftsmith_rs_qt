from PySide6.QtWidgets import QMenu, QApplication, QStyle
from PySide6.QtGui import QAction
from PySide6.QtCore import QCoreApplication
from typing import Dict, Tuple

def create_file_menu(parent) -> Tuple[QMenu, Dict[str, QAction]]:
    "Create a file menu with actions and return both menu and actions dictionary"

    file_menu = QMenu("File", parent)
    actions = {}
    
    style = QApplication.style()
    
    # New action
    new_icon = style.standardIcon(QStyle.SP_FileDialogNewFolder)
    actions['new'] = QAction(new_icon, "New", parent)
    actions['new'].setShortcut("Ctrl+N")
    actions['new'].setStatusTip("Create a new note")
    actions['new'].setToolTip("Create a new note")
    file_menu.addAction(actions['new'])

    # Open action
    open_icon = style.standardIcon(QStyle.SP_DialogOpenButton)
    actions['open'] = QAction(open_icon, "Open", parent)
    actions['open'].setShortcut("Ctrl+O")
    actions['open'].setStatusTip("Open an existing note")
    actions['open'].setToolTip("Open an existing note")
    file_menu.addAction(actions['open'])

    # Save action
    save_icon = style.standardIcon(QStyle.SP_DialogSaveButton)
    actions['save'] = QAction(save_icon, "Save", parent)
    actions['save'].setShortcut("Ctrl+S")
    actions['save'].setStatusTip("Save the current note")
    actions['save'].setToolTip("Save the current note")
    file_menu.addAction(actions['save'])

    # Exit action
    exit_icon = style.standardIcon(QStyle.SP_DialogCloseButton)
    actions['exit'] = QAction(exit_icon, "Exit", parent)
    actions['exit'].setShortcut("Ctrl+Q")
    actions['exit'].setStatusTip("Exit the application")
    actions['exit'].setToolTip("Exit the application") 
    file_menu.addAction(actions['exit'])
    actions['exit'].triggered.connect(QCoreApplication.instance().quit)

    return file_menu, actions
