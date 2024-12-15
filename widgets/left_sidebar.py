from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Qt
from .notes_tree import NotesTreeWidget
from .search_sidebar import SearchSidebar
from .notes_tree_view import NotesTreeView  # Import the new class


class LeftSidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tree = NotesTreeWidget()
        self.tags_tree = NotesTreeView()  # Use the new NotesTreeView class
        self.search_sidebar = SearchSidebar()
        self.tab_widget = QTabWidget()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.tree.setHeaderLabel("Notes")
        self.tree.setMinimumWidth(100)

        self.tags_tree.setMinimumWidth(100)
        self.tags_tree.hide()  # Initially hidden

        self.search_sidebar.hide()  # Initially hidden

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.tree, "Notes")
        self.tab_widget.addTab(self.tags_tree, "Tags")
        self.tab_widget.addTab(self.search_sidebar, "Search")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tab_widget)

    def _connect_signals(self):
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        if index == 0:  # Notes
            self.tree.show()
            self.tags_tree.hide()
            self.search_sidebar.hide()
        elif index == 1:  # Tags
            self.tree.hide()
            self.tags_tree.show()
            self.search_sidebar.hide()
        else:  # Search
            self.tree.hide()
            self.tags_tree.hide()
            self.search_sidebar.show()

    def focus_search(self):
        """Focus the search input and switch to search view"""
        self.tab_widget.setCurrentIndex(2)
        self.search_sidebar.search_input.setFocus()
