from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, 
                              QListWidgetItem, QComboBox)
from PySide6.QtCore import Qt, Signal, QTimer
from enum import Enum

class SearchType(Enum):
    API = "API Search"
    TYPESENSE_HYBRID = "Typesense Hybrid"
    TYPESENSE_SEMANTIC = "Typesense Semantic" 
    TYPESENSE_STANDARD = "Typesense Standard"
from PySide6.QtGui import QKeyEvent
from widgets.right_sidebar import NavigableListWidget

SEARCH_DELAY = 200  # Delay in milliseconds for search debounce


class SearchSidebar(QWidget):
    """Widget for searching notes and displaying results"""

    note_selected = Signal(int)  # Emitted when search result is selected
    note_selected_with_focus = Signal(
        int
    )  # Emitted when search result is selected with focus

    def __init__(self, parent=None):
        super().__init__(parent)
        self.follow_mode: bool = True  # Default to true for backward compatibility
        self._setup_ui()
        self._setup_search_timer()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Search type selector
        self.search_type_combo = QComboBox()
        for search_type in SearchType:
            self.search_type_combo.addItem(search_type.value, search_type)
        
        # Search input with placeholder
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search notes...")

        # Results list
        self.results_list = NavigableListWidget()
        self.results_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.results_list.setWordWrap(True)

        # Forward the note selection signals
        self.results_list.note_selected.connect(self.note_selected.emit)
        self.results_list.note_selected_with_focus.connect(
            self.note_selected_with_focus.emit
        )

        layout.addWidget(self.search_type_combo)
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
        self.results_list.itemSelectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self):
        """Handle selection changes in results list"""
        if not self.follow_mode:
            return

        current = self.results_list.currentItem()
        if current:
            note_id = current.data(Qt.ItemDataRole.UserRole)
            if note_id:
                self.note_selected.emit(note_id)

    def _on_search_text_changed(self, text):
        """Restart timer on each keystroke"""
        self.search_timer.stop()
        self.search_timer.start()

    def _perform_search(self):
        """Perform the search using the selected search type"""
        search_text = self.search_input.text()
        self.results_list.clear()

        if not search_text:
            item = QListWidgetItem("Type to search...")
            item.setFlags(
                item.flags() & ~Qt.ItemFlag.ItemIsEnabled
            )  # Make non-clickable
            self.results_list.addItem(item)
            return

        # Get current search type
        current_search_type = self.search_type_combo.currentData()

        # Get notes model from parent widget hierarchy
        main_window = self.window()
        if not main_window or not hasattr(main_window, "notes_model"):
            return

        try:
            if current_search_type == SearchType.API:
                results = main_window.notes_model.note_api.search_notes(search_text)
            else:
                # For not implemented search types
                item = QListWidgetItem(f"{current_search_type.value} not implemented yet")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                self.results_list.addItem(item)
                return

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

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard events"""
        if event.key() == Qt.Key.Key_Escape:
            self.search_input.clear()
            self.search_input.setFocus()
            event.accept()
        else:
            super().keyPressEvent(event)
