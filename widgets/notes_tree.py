from PySide6.QtWidgets import QTreeWidget
from PySide6.QtCore import QEvent
from PySide6.QtGui import QKeyEvent
from utils.key_constants import Key





class NotesTreeWidget(QTreeWidget):
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Key.Key_J:
            # Create a new QKeyEvent for Down key
            new_event = QKeyEvent(QEvent.Type.KeyPress, Key.Key_Down, event.modifiers())
            super().keyPressEvent(new_event)

        elif event.key() == Key.Key_K:
            # Create a new QKeyEvent for Up key
            new_event = QKeyEvent(QEvent.Type.KeyPress, Key.Key_Up, event.modifiers())
            super().keyPressEvent(new_event)

        elif event.key() in (Key.Key_Space, Key.Key_Right, Key.Key_Left):
            current = self.currentItem()
            if current:
                if event.key() == Key.Key_Left:
                    current.setExpanded(False)
                elif event.key() == Key.Key_Right:
                    current.setExpanded(True)
                elif event.key() == Key.Key_Space:
                    current.setExpanded(not current.isExpanded())
        else:
            super().keyPressEvent(event)

