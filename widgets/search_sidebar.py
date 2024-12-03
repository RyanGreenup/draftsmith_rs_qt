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

        # Results list
        self.results_list = NavigableListWidget()
        self.results_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_list.setWordWrap(True)
        self.results_list.itemDoubleClicked.connect(self._on_result_selected)

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
        self.results_list.itemClicked.connect(self._on_result_selected)

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

    def _on_result_selected(self, item):
        """Handle result selection"""
        note_id = item.data(Qt.ItemDataRole.UserRole)
        if note_id is not None and note_id != -1:  # Ignore placeholder items
            self.note_selected.emit(note_id)
