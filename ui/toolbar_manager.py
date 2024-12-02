from PySide6.QtWidgets import QToolBar
from PySide6.QtGui import QAction
from typing import Dict


def create_toolbar(parent, actions: Dict[str, QAction]):
    "Create a toolbar using existing actions from menu"

    toolbar = QToolBar("Main Toolbar", parent)

    # Add the same actions as in menu
    toolbar.addAction(actions["new"])
    toolbar.addAction(actions["open"])
    toolbar.addAction(actions["save"])

    return toolbar
