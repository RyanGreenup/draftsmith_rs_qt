from PySide6.QtWidgets import QApplication
import signal
import sys
from ui.actions_manager import create_actions
from ui.menu_manager import create_file_menu, create_view_menu, create_tabs_menu
from ui.toolbar_manager import create_toolbar
from widgets.main_window import NoteApp
from ui.menu_handler import MenuHandler


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create empty window first
    window = NoteApp(None)  # Temporarily pass None for actions
    
    # Now create actions using the window
    actions = create_actions(window)
    
    # Update window with the actions
    window.actions = actions
    window.menu_handler = MenuHandler(window, actions)
    window.menu_handler.setup_menus()

    # Allow C-c to kill app
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Load and apply the stylesheet
    with open("ui/styles/style.qss", "r") as file:
        app.setStyleSheet(file.read())

    # Add toolbar using actions
    toolbar = create_toolbar(window, actions)
    window.addToolBar(toolbar)

    window.show()
    sys.exit(app.exec())
