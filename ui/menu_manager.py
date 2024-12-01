from PySide6.QtWidgets import QMenu, QAction

def create_file_menu(parent):
    "Create a file menu with dummy actions"

    file_menu = QMenu("File", parent)
    
    new_action = QAction("New", parent)
    new_action.setShortcut("Ctrl+N")
    file_menu.addAction(new_action)

    open_action = QAction("Open", parent)
    open_action.setShortcut("Ctrl+O")
    file_menu.addAction(open_action)

    save_action = QAction("Save", parent)
    save_action.setShortcut("Ctrl+S")
    file_menu.addAction(save_action)

    exit_action = QAction("Exit", parent)
    exit_action.setShortcut("Ctrl+Q")
    file_menu.addAction(exit_action)

    return file_menu
