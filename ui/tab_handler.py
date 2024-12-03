from widgets.tab_widget import NotesTabWidget
from typing import Dict, Any, Optional


from widgets.tab_content import TabContent

class TabHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        self.tab_widget = NotesTabWidget(main_window)
        self._last_tree_state: Optional[Dict[str, Any]] = None

    def setup_tabs(self):
        """Initialize the first tab and set up central widget"""
        self.main_window.setCentralWidget(self.tab_widget)
        return self.create_new_tab("Main")

    def new_tab(self):
        """Create a new tab with proper signal connections"""
        # Store current tree state before creating new tab
        if self.tab_widget.count() > 0:
            current_tab = self.tab_widget.currentWidget()
            if isinstance(current_tab, TabContent):
                self._last_tree_state = current_tab.left_sidebar.tree.save_state()
        
        # Create new tab and set focus
        new_tab = self.create_new_tab()
        self.tab_widget.setCurrentWidget(new_tab)
        return new_tab

    def create_new_tab(self, title: str = "New Tab") -> TabContent:
        """Create a new tab with its own view implementation"""
        # Create new tab content
        tab_content = TabContent()
        
        # Connect to model
        tab_content.set_model(self.main_window.notes_model)
        
        # Connect save signal to status updates
        tab_content.note_saved.connect(self._handle_note_saved)
        
        # Add to tab widget
        self.tab_widget.addTab(tab_content, title)
        
        # Restore tree state if available
        if self._last_tree_state is not None:
            tab_content.left_sidebar.tree.restore_state(self._last_tree_state)
        
        return tab_content

    def _handle_note_saved(self, note_id: int):
        """Update status bar when note is saved"""
        self.main_window.status_bar.showMessage(f"Note {note_id} saved successfully", 3000)

    def close_current_tab(self):
        current_index = self.tab_widget.currentIndex()
        self.tab_widget.close_tab(current_index)

    def next_tab(self):
        current = self.tab_widget.currentIndex()
        next_index = (current + 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(next_index)
        self.main_window.refresh_model()

    def previous_tab(self):
        current = self.tab_widget.currentIndex()
        prev_index = (current - 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(prev_index)
        self.main_window.refresh_model()
