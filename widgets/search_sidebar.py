from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QKeyEvent
from widgets.right_sidebar import NavigableListWidget

SEARCH_DELAY = 200 # Delay in milliseconds for search debounce

class SearchSidebar(QWidget):
    """Widget for searching notes and displaying results"""

    note_selected = Signal(int)  # Emitted when search result is selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_search_timer()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Search input with placeholder
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search notes...")
        self.search_input.returnPressed.connect(self._handle_search_return)

        # Results list
        self.results_list = NavigableListWidget()
        self.results_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_list.setWordWrap(True)
        
        # Forward the note_selected signal
        self.results_list.note_selected.connect(self.note_selected.emit)

        layout.addWidget(self.search_input)
        layout.addWidget(self.results_list)

    def _setup_search_timer(self):
        # Debounce timer to avoid searching on every keystroke
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(SEARCH_DELAY)  # 300ms delay

    def _connect_signals(self):
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_timer.timeout.connect(self._perform_search)

    def _on_search_text_changed(self, text):
        """Restart timer on each keystroke"""
        self.search_timer.stop()
        self.search_timer.start()

    def _perform_search(self):
        """Perform the search using the notes model"""
        search_text = self.search_input.text()
        self.results_list.clear()

        if not search_text:
            item = QListWidgetItem("Type to search...")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)  # Make non-clickable
            self.results_list.addItem(item)
            return

        # Get notes model from parent widget hierarchy
        main_window = self.window()
        if not main_window or not hasattr(main_window, 'notes_model'):
            return

        try:
            results = main_window.notes_model.note_api.search_notes(search_text)
            if not results:
                item = QListWidgetItem("No results found")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                self.results_list.addItem(item)
                return

            for note in results:
                item = QListWidgetItem(note.title)
                item.setData(Qt.ItemDataRole.UserRole, note.id)
                self.results_list.addItem(item)

        except Exception as e:
            print(f"Error performing search: {e}")
            item = QListWidgetItem("Error performing search")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.results_list.addItem(item)

    def _handle_search_return(self):
        """Handle return/enter press in search input"""
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)
            self.results_list.setFocus()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard events"""
        if event.key() == Qt.Key.Key_Escape:
            self.search_input.clear()
            self.search_input.setFocus()
            event.accept()
        else:
            super().keyPressEvent(event)