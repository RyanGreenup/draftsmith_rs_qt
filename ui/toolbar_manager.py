from PySide6.QtWidgets import QToolBar, QApplication, QStyle
from PySide6.QtGui import QAction

def create_toolbar(parent):
    "Create a toolbar with dummy actions"

    toolbar = QToolBar("Main Toolbar", parent)
    
    style = QApplication.style()
    new_icon = style.standardIcon(QStyle.SP_FileDialogNewFolder)
    new_action = QAction(new_icon, "New", parent)
    new_action.setShortcut("Ctrl+N")
    toolbar.addAction(new_action)

    style = QApplication.style()
    open_icon = style.standardIcon(QStyle.SP_DialogOpenButton)
    open_action = QAction(open_icon, "Open", parent)
    open_action.setShortcut("Ctrl+O")
    toolbar.addAction(open_action)

    style = QApplication.style()
    save_icon = style.standardIcon(QStyle.SP_DialogSaveButton)
    save_action = QAction(save_icon, "Save", parent)
    save_action.setShortcut("Ctrl+S")
    toolbar.addAction(save_action)

    return toolbar
