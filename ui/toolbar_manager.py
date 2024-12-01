from PySide6.QtWidgets import QToolBar, QAction

def create_toolbar(parent):
    "Create a toolbar with dummy actions"

    toolbar = QToolBar("Main Toolbar", parent)
    
    new_action = QAction("New", parent)
    new_action.setShortcut("Ctrl+N")
    toolbar.addAction(new_action)

    open_action = QAction("Open", parent)
    open_action.setShortcut("Ctrl+O")
    toolbar.addAction(open_action)

    save_action = QAction("Save", parent)
    save_action.setShortcut("Ctrl+S")
    toolbar.addAction(save_action)

    return toolbar
