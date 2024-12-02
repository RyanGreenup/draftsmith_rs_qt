from enum import IntEnum
from PySide6.QtCore import Qt


class Key(IntEnum):
    """Define key constants to satisfy type checker"""

    Key_J = Qt.Key.Key_J
    Key_K = Qt.Key.Key_K
    Key_Space = Qt.Key.Key_Space
    Key_Right = Qt.Key.Key_Right
    Key_Left = Qt.Key.Key_Left
    Key_Down = Qt.Key.Key_Down
    Key_Up = Qt.Key.Key_Up
