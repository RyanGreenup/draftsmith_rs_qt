from PySide6.QtWidgets import QApplication
import sys
from widgets.main_window import NoteApp









if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteApp()
    window.show()
    sys.exit(app.exec())
