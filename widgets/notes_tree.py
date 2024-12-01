from PySide6.QtWidgets import QTreeWidget, QApplication
from PySide6.QtCore import QEvent, Qt
from PySide6.QtCore import QEvent
from PySide6.QtGui import QKeyEvent
from utils.key_constants import Key





class NotesTreeWidget(QTreeWidget):
    def cycle_fold_level_of_all_items(self):
        """Cycle the fold level of all items in the tree."""
        if self.topLevelItemCount() > 0:
            index = self.indexFromItem(self.topLevelItem(0))
            current_state = self.isExpanded(index)
            for i in range(self.topLevelItemCount()):
                item = self.topLevelItem(i)
                index = self.indexFromItem(item)
                item.setExpanded(not current_state)

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
                elif event.key() == Key.Key_Space and not event.modifiers() & Qt.ShiftModifier:
                    current.setExpanded(not current.isExpanded())
                elif event.key() == Key.Key_Space and event.modifiers() & Qt.ShiftModifier:
                    self.cycle_fold_level_of_all_items()
        else:
            super().keyPressEvent(event)

