from PySide6.QtWidgets import QToolBar
from PySide6.QtGui import QAction
from typing import Dict


def create_toolbar(parent, actions: Dict[str, QAction]) -> QToolBar:
    """Create a toolbar using existing actions"""
    toolbar = QToolBar("Main Toolbar", parent)

    toolbar.addAction(actions["new_child"])
    toolbar.addAction(actions["open"])
    toolbar.addAction(actions["save"])

    return toolbar
