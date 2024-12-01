from PySide6.QtWidgets import QApplication
import sys
from ui.menu_manager import create_file_menu
from ui.toolbar_manager import create_toolbar
from widgets.main_window import NoteApp









if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteApp()

    # Add file menu
    file_menu = create_file_menu(window.menuBar())
    window.menuBar().addMenu(file_menu)

    # Add toolbar
    toolbar = create_toolbar(window)
    window.addToolBar(toolbar)

    window.show()
    sys.exit(app.exec())
