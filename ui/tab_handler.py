from widgets.tab_widget import NotesTabWidget
from typing import Dict, Any, Optional


class TabHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        self.tab_widget = NotesTabWidget(main_window)
        self._last_tree_state: Optional[Dict[str, Any]] = None

    def setup_tabs(self):
        """Initialize the first tab and set up central widget"""
        self.main_window.setCentralWidget(self.tab_widget)
        main_tab = self.tab_widget.add_new_tab("Main")
        # Connect the main tab's editor save signal
        main_tab.editor.save_requested.connect(self.main_window.save_current_note)
        return main_tab

    def new_tab(self):
        """Create a new tab with proper signal connections"""
        # Store current tree state before creating new tab
        if self.tab_widget.count() > 0:
            current_tree = self.main_window.main_content.left_sidebar.tree
            self._last_tree_state = current_tree.save_state()
        
        # Create new tab
        new_tab = self.tab_widget.add_new_tab()
        
        # Connect the new tab's editor save signal
        new_tab.editor.save_requested.connect(self.main_window.save_current_note)
        
        # Restore tree state in new tab if available
        if self._last_tree_state is not None:
            new_tree = new_tab.left_sidebar.tree
            new_tree.restore_state(self._last_tree_state)

    def close_current_tab(self):
        current_index = self.tab_widget.currentIndex()
        self.tab_widget.close_tab(current_index)

    def next_tab(self):
        current = self.tab_widget.currentIndex()
        next_index = (current + 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(next_index)

    def previous_tab(self):
        current = self.tab_widget.currentIndex()
        prev_index = (current - 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(prev_index)
