from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QListWidgetItem,
    QComboBox,
)
from PySide6.QtCore import Qt, Signal, QTimer
from enum import Enum
from thefuzz import fuzz
from typing import List, Optional


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

        # Add filter input at top
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter results...")

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

        layout.addWidget(self.filter_input)
        layout.addWidget(self.search_type_combo)
        layout.addWidget(self.search_input)
        layout.addWidget(self.results_list)

        # Store original search results
        self._current_results: List[tuple[str, int]] = []  # [(title, note_id), ...]

    def _setup_search_timer(self):
        # Debounce timer to avoid searching on every keystroke
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(SEARCH_DELAY)  # 300ms delay

    def _connect_signals(self):
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_timer.timeout.connect(self._perform_search)
        self.results_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.filter_input.textChanged.connect(self._apply_filter)

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

    def _apply_filter(self, filter_text: str) -> None:
        """Apply fuzzy filter to current search results"""
        self._apply_results(self._current_results, filter_text)

    def _apply_results(self, results: List[tuple[str, int]], filter_text: str = "") -> None:
        """Apply any existing filter to the provided results and display them."""
        self.results_list.clear()
        
        if not results:
            return
            
        if not filter_text:
            # Show all results if no filter
            for title, note_id in results:
                item = QListWidgetItem(title)
                item.setData(Qt.ItemDataRole.UserRole, note_id)
                self.results_list.addItem(item)
            return

        # Apply fuzzy filtering
        filtered_results = []
        for title, note_id in results:
            ratio = fuzz.partial_ratio(filter_text.lower(), title.lower())
            if ratio > 60:  # Adjust threshold as needed
                filtered_results.append((title, note_id, ratio))
        
        # Sort by match quality
        filtered_results.sort(key=lambda x: x[2], reverse=True)
        
        # Update list widget
        for title, note_id, _ in filtered_results:
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, note_id)
            self.results_list.addItem(item)

    def _perform_search(self):
        """Perform the search using the selected search type"""
        search_text = self.search_input.text()
        self.results_list.clear()
        self._current_results.clear()  # Clear stored results

        if not search_text:
            # List all notes if search text is empty
            main_window = self.window()
            if not main_window or not hasattr(main_window, "notes_model"):
                return

            try:
                results = main_window.notes_model.note_api.get_all_notes()

                if not results:
                    item = QListWidgetItem("No notes found")
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                    self.results_list.addItem(item)
                    return

                # Store results and display them
                self._current_results = [(note.title, note.id) for note in results]
                
                # Apply any existing filter
                filter_text = self.filter_input.text()
                self._apply_results(self._current_results, filter_text)

            except Exception as e:
                print(f"Error fetching notes: {e}")
                item = QListWidgetItem("Error fetching notes")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
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
                item = QListWidgetItem(
                    f"{current_search_type.value} not implemented yet"
                )
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                self.results_list.addItem(item)
                return

            if not results:
                item = QListWidgetItem("No results found")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                self.results_list.addItem(item)
                return

            # Store results and display them
            self._current_results = [(note.title, note.id) for note in results]
            
            # Apply any existing filter
            filter_text = self.filter_input.text()
            self._apply_results(self._current_results, filter_text)

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
