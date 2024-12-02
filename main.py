from PySide6.QtWidgets import QApplication
import signal
from PySide6.QtCore import QFile, QTextStream
import sys
from ui.menu_manager import create_file_menu, create_view_menu
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

    menubar = window.menuBar()
    actions = dict()
    actions.update(create_file_menu(menubar)[1])
    actions.update(create_view_menu(menubar)[1])

    # Add toolbar
    toolbar = create_toolbar(window, actions)
    window.addToolBar(toolbar)

    window.show()
    sys.exit(app.exec())
