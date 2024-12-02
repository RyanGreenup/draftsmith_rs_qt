from typing import List
from PySide6.QtCore import QObject, Signal


class NavigationModel(QObject):
    """Model to manage navigation history of notes"""

    navigation_changed = Signal()  # Emitted when history changes

    def __init__(self):
        super().__init__()
        self._history: List[int] = []  # List of note IDs
        self._current_index: int = -1

    def can_go_back(self) -> bool:
        return self._current_index > 0

    def can_go_forward(self) -> bool:
        return self._current_index < len(self._history) - 1

    def go_back(self) -> int:
        """Move back in history and return the note ID"""
        if self.can_go_back():
            self._current_index -= 1
            self.navigation_changed.emit()
            return self._history[self._current_index]
        return -1

    def go_forward(self) -> int:
        """Move forward in history and return the note ID"""
        if self.can_go_forward():
            self._current_index += 1
            self.navigation_changed.emit()
            return self._history[self._current_index]
        return -1

    def add_to_history(self, note_id: int):
        """Add a new note to history"""
        # Don't add if it's the same as current
        if (
            self._history
            and self._current_index >= 0
            and self._history[self._current_index] == note_id
        ):
            return

        # Remove any forward history when adding new note
        if self._current_index < len(self._history) - 1:
            self._history = self._history[: self._current_index + 1]

        self._history.append(note_id)
        self._current_index = len(self._history) - 1
        self.navigation_changed.emit()
