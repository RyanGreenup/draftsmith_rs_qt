from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, QTimer

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
        self.results_list = QListWidget()
        self.results_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_list.setWordWrap(True)

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
        """Placeholder for search implementation"""
        search_text = self.search_input.text()

        # TODO: Implement actual search logic
        # TODO: Search should include:
        #       - Note titles
        #       - Note content
        #       - Tags
        #       - Consider fuzzy matching

        self.results_list.clear()

        # Dummy implementation for UI testing
        if search_text:
            dummy_item = QListWidgetItem(f"Search results for: {search_text}")
            dummy_item.setData(Qt.ItemDataRole.UserRole, -1)  # Placeholder note ID
            self.results_list.addItem(dummy_item)

    def _on_result_selected(self, item):
        """Handle result selection"""
        # TODO: Implement proper note selection
        note_id = item.data(Qt.ItemDataRole.UserRole)
        if note_id is not None:
            self.note_selected.emit(note_id)
