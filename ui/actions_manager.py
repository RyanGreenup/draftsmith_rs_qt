from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QWidget, QStyle
from PySide6.QtCore import QCoreApplication
from typing import Dict, Optional



def create_actions(parent: Optional[QWidget] = None) -> Dict[str, QAction]:
    actions = {}
    style = QApplication.style()

    # File actions
    actions["new"] = QAction(
        style.standardIcon(QStyle.StandardPixmap.SP_FileIcon), "&New", parent
    )
    actions["new"].setShortcut("Ctrl+N")
    actions["new"].setStatusTip("Create a new note")
    actions["new"].setToolTip("Create a new note")

    actions["open"] = QAction(
        style.standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton), "&Open", parent
    )
    actions["open"].setShortcut("Ctrl+O")
    actions["open"].setStatusTip("Open an existing note")
    actions["open"].setToolTip("Open an existing note")

    actions["save"] = QAction(
        style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "&Save", parent
    )
    actions["save"].setShortcut("Ctrl+S")
    actions["save"].setStatusTip("Save the current note")
    actions["save"].setToolTip("Save the current note")

    # Exit action
    actions["exit"] = QAction(
        style.standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton), "E&xit", parent
    )
    actions["exit"].setShortcut("Ctrl+Q")
    actions["exit"].setStatusTip("Exit the application")
    actions["exit"].setToolTip("Exit the application")
    app = QApplication.instance()  # Ensure we get the QApplication instance
    if app is not None:
        actions["exit"].triggered.connect(app.quit)

    # Navigation actions
    actions["back"] = QAction(
        style.standardIcon(QStyle.StandardPixmap.SP_ArrowBack), "Go &Back", parent
    )
    actions["back"].setShortcut("Alt+Left")
    actions["back"].setStatusTip("Go to previously viewed note")
    actions["back"].setEnabled(False)  # Initially disabled

    actions["forward"] = QAction(
        style.standardIcon(QStyle.StandardPixmap.SP_ArrowForward), "Go &Forward", parent
    )
    actions["forward"].setShortcut("Alt+Right")
    actions["forward"].setStatusTip("Go to next viewed note")
    actions["forward"].setEnabled(False)  # Initially disabled

    # View actions
    actions["toggle_left_sidebar"] = QAction("Hide &Left Sidebar", parent)
    actions["toggle_left_sidebar"].setShortcut("Ctrl+\\")
    actions["toggle_left_sidebar"].setStatusTip("Toggle left sidebar visibility")

    actions["toggle_right_sidebar"] = QAction("Hide &Right Sidebar", parent)
    actions["toggle_right_sidebar"].setShortcut("Ctrl+Shift+\\")
    actions["toggle_right_sidebar"].setStatusTip("Toggle right sidebar visibility")

    actions["focus_next"] = QAction("Focus &Next Widget", parent)
    actions["focus_next"].setShortcut("Ctrl+J")
    actions["focus_next"].setStatusTip("Move focus to next widget (like Tab)")

    actions["focus_previous"] = QAction("Focus &Previous Widget", parent)
    actions["focus_previous"].setShortcut("Ctrl+K")
    actions["focus_previous"].setStatusTip(
        "Move focus to previous widget (like Shift+Tab)"
    )

    actions["maximize_editor"] = QAction("Ma&ximize Editor", parent)
    actions["maximize_editor"].setShortcut("Ctrl+Shift+E")
    actions["maximize_editor"].setStatusTip("Toggle maximize editor view")
    actions["maximize_editor"].setCheckable(True)

    actions["maximize_preview"] = QAction("Maximize &Preview", parent)
    actions["maximize_preview"].setShortcut("Ctrl+Shift+P")
    actions["maximize_preview"].setStatusTip("Toggle maximize preview")
    actions["maximize_preview"].setCheckable(True)

    # Tabs actions
    actions["new_tab"] = QAction("&New Tab", parent)
    actions["new_tab"].setShortcut("Ctrl+T")
    actions["new_tab"].setStatusTip("Create a new tab")

    actions["close_tab"] = QAction("&Close Tab", parent)
    actions["close_tab"].setShortcut("Ctrl+W")
    actions["close_tab"].setStatusTip("Close current tab")

    actions["next_tab"] = QAction("Next Tab", parent)
    actions["next_tab"].setShortcut("Ctrl+Tab")
    actions["next_tab"].setStatusTip("Switch to next tab")

    actions["prev_tab"] = QAction("Previous Tab", parent)
    actions["prev_tab"].setShortcut("Ctrl+Shift+Tab")
    actions["prev_tab"].setStatusTip("Switch to previous tab")

    # Add refresh action
    actions["refresh"] = QAction("&Refresh", parent)
    actions["refresh"].setShortcut("F5")  # Common shortcut for refresh
    actions["refresh"].setStatusTip("Refresh notes from server")
    actions["refresh"].setToolTip("Refresh notes from server")

    return actions
