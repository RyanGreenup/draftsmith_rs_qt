from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QWidget, QStyle
from PySide6.QtCore import QCoreApplication
from typing import Dict, Optional


def create_actions(parent: Optional[QWidget] = None) -> Dict[str, QAction]:
    actions = {}
    style = QApplication.style()

    # File actions
    def make_new_action(
        display: str,
        shortcut: str,
        status_tip: str,
        key: str,
        parent: Optional[QWidget],
    ):
        actions[key] = QAction(
            style.standardIcon(QStyle.StandardPixmap.SP_FileIcon), display, parent
        )
        actions[key].setShortcut(shortcut)
        actions[key].setStatusTip(status_tip)
        actions[key].setToolTip(status_tip)

    make_new_action(
        "&New", "Ctrl+Shift+N", "Create a new note at root level", "new_root", parent
    )
    make_new_action(
        "New &Child", "Ctrl+Return", "Create a new note as child", "new_child", parent
    )
    make_new_action(
        "New &Sibling",
        "Alt+Return",
        "Create a new note as sibling",
        "new_sibling",
        parent,
    )

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

    actions["focus_search"] = QAction("Focus &Search", parent)
    actions["focus_search"].setShortcut("Ctrl+Shift+F")
    actions["focus_search"].setStatusTip("Focus the search input")

    actions["toggle_follow_mode"] = QAction("Toggle &Follow Mode", parent)
    actions["toggle_follow_mode"].setShortcut("Ctrl+F")
    actions["toggle_follow_mode"].setStatusTip(
        "Toggle automatic note preview when navigating"
    )
    actions["toggle_follow_mode"].setCheckable(True)

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
    actions["next_tab"].setShortcut("Ctrl+L")
    actions["next_tab"].setStatusTip("Switch to next tab")

    actions["prev_tab"] = QAction("Previous Tab", parent)
    actions["prev_tab"].setShortcut("Ctrl+H")
    actions["prev_tab"].setStatusTip("Switch to previous tab")

    # Add tab state actions
    actions["save_tabs_state"] = QAction("&Save Tabs State", parent)
    actions["save_tabs_state"].setShortcut("Ctrl+Alt+S")
    actions["save_tabs_state"].setStatusTip("Save the current arrangement of tabs")
    actions["save_tabs_state"].setToolTip("Save the current arrangement of tabs")

    actions["restore_tabs_state"] = QAction("&Restore Tabs State", parent)
    actions["restore_tabs_state"].setShortcut("Ctrl+Alt+R")
    actions["restore_tabs_state"].setStatusTip(
        "Restore previously saved tab arrangement"
    )
    actions["restore_tabs_state"].setToolTip("Restore previously saved tab arrangement")

    # Add refresh action
    actions["refresh"] = QAction("&Refresh", parent)
    actions["refresh"].setShortcut("F5")  # Common shortcut for refresh
    actions["refresh"].setStatusTip("Refresh notes from server")
    actions["refresh"].setToolTip("Refresh notes from server")

    # Add Neovim action
    actions["start_neovim"] = QAction("Start &Neovim Server", parent)
    actions["start_neovim"].setShortcut("Ctrl+Alt+N")
    actions["start_neovim"].setStatusTip("Start Neovim server for text editing")
    actions["start_neovim"].setToolTip("Start Neovim server for text editing")

    # Add remote rendering action
    actions["use_remote_rendering"] = QAction("Use &Remote Rendering", parent)
    actions["use_remote_rendering"].setCheckable(True)
    actions["use_remote_rendering"].setChecked(True)  # Default to remote rendering
    actions["use_remote_rendering"].setStatusTip(
        "Toggle between remote and local markdown rendering"
    )
    actions["use_remote_rendering"].setToolTip(
        "Toggle between remote and local markdown rendering"
    )

    # Add dark mode action
    actions["toggle_dark_mode"] = QAction("&Dark Mode", parent)
    actions["toggle_dark_mode"].setCheckable(True)
    actions["toggle_dark_mode"].setStatusTip("Toggle between light and dark themes")
    actions["toggle_dark_mode"].setToolTip("Toggle between light and dark themes")

    # Add zoom/scale actions
    actions["zoom_in"] = QAction("Zoom &In", parent)
    actions["zoom_in"].setShortcut("Ctrl+=")  # Common zoom in shortcut
    actions["zoom_in"].setStatusTip("Increase UI scale")
    actions["zoom_in"].setToolTip("Increase UI scale")

    actions["zoom_out"] = QAction("Zoom &Out", parent)
    actions["zoom_out"].setShortcut("Ctrl+-")  # Common zoom out shortcut
    actions["zoom_out"].setStatusTip("Decrease UI scale")
    actions["zoom_out"].setToolTip("Decrease UI scale")

    actions["zoom_reset"] = QAction("Reset &Zoom", parent)
    actions["zoom_reset"].setShortcut("Ctrl+0")  # Common zoom reset shortcut
    actions["zoom_reset"].setStatusTip("Reset UI scale to default")
    actions["zoom_reset"].setToolTip("Reset UI scale to default")

    # Add delete note action
    actions["delete_note"] = QAction("&Delete Note", parent)
    actions["delete_note"].setShortcut("Delete")  # Optional keyboard shortcut
    actions["delete_note"].setStatusTip("Delete the current note")
    actions["delete_note"].setToolTip("Delete the current note")

    # Add FZF palette action
    actions["show_note_palette"] = QAction("&Find Note...", parent)
    actions["show_note_palette"].setShortcut(
        "Ctrl+Shift+O"
    )  # Different from regular open
    actions["show_note_palette"].setStatusTip(
        "Search and open notes using fuzzy finder"
    )
    actions["show_note_palette"].setToolTip("Search and open notes using fuzzy finder")

    # Add note link insertion action
    actions["insert_note_link"] = QAction("Insert Note &Link", parent)
    actions["insert_note_link"].setShortcut(
        "Ctrl+Shift+L"
    )  # Different from Ctrl+L which is used for "next_tab"
    actions["insert_note_link"].setStatusTip("Insert a link to another note")
    actions["insert_note_link"].setToolTip("Insert a link to another note")

    # Add cut note action
    actions["cut_note"] = QAction("Cu&t Note", parent)
    actions["cut_note"].setShortcut("Ctrl+X")  # Standard cut shortcut
    actions["cut_note"].setStatusTip("Cut the selected note")
    actions["cut_note"].setToolTip("Cut the selected note")

    # Add paste note action
    actions["paste_note"] = QAction("&Paste Note", parent)
    actions["paste_note"].setShortcut("Ctrl+V")  # Standard paste shortcut
    actions["paste_note"].setStatusTip("Paste the previously cut note")
    actions["paste_note"].setToolTip("Paste the previously cut note")

    return actions
