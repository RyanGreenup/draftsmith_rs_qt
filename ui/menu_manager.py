from PySide6.QtWidgets import QMenu, QApplication, QStyle
from PySide6.QtGui import QAction

def create_file_menu(parent):
    "Create a file menu with dummy actions"

    file_menu = QMenu("File", parent)
    
    style = QApplication.style()
    new_icon = style.standardIcon(QStyle.SP_FileDialogNewFolder)
    new_action = QAction(new_icon, "New", parent)
    new_action.setShortcut("Ctrl+N")
    file_menu.addAction(new_action)

    style = QApplication.style()
    open_icon = style.standardIcon(QStyle.SP_DialogOpenButton)
    open_action = QAction(open_icon, "Open", parent)
    open_action.setShortcut("Ctrl+O")
    file_menu.addAction(open_action)

    style = QApplication.style()
    save_icon = style.standardIcon(QStyle.SP_DialogSaveButton)
    save_action = QAction(save_icon, "Save", parent)
    save_action.setShortcut("Ctrl+S")
    file_menu.addAction(save_action)

    style = QApplication.style()
    exit_icon = style.standardIcon(QStyle.SP_DialogCloseButton)
    exit_action = QAction(exit_icon, "Exit", parent)
    exit_action.setShortcut("Ctrl+Q")
    file_menu.addAction(exit_action)

    return file_menu
