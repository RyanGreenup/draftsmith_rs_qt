from PySide6.QtWidgets import QApplication
import signal
import sys
from ui.actions_manager import create_actions
from ui.menu_manager import create_file_menu, create_view_menu, create_tabs_menu
from ui.toolbar_manager import create_toolbar
from widgets.main_window import NoteApp


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteApp()

    # Allow C-c to kill app
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Load and apply the stylesheet
    with open("ui/styles/style.qss", "r") as file:
        app.setStyleSheet(file.read())

    # Create actions
    actions = create_actions(window)

    # Create menus using actions
    menubar = window.menuBar()
    file_menu = create_file_menu(menubar, actions)
    view_menu = create_view_menu(menubar, actions)
    tabs_menu = create_tabs_menu(menubar, actions)
    menubar.addMenu(file_menu)
    menubar.addMenu(view_menu)
    menubar.addMenu(tabs_menu)

    # Add toolbar using the same actions
    toolbar = create_toolbar(window, actions)
    window.addToolBar(toolbar)

    window.show()
    sys.exit(app.exec())
