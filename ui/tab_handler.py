from widgets.tab_widget import NotesTabWidget
from typing import Dict, Any, Optional


from widgets.tab_content import TabContent

class TabHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        self.tab_widget = NotesTabWidget(main_window)
        self._last_tree_state: Optional[Dict[str, Any]] = None
        self._tab_note_ids: Dict[int, int] = {}  # Map tab index to note ID

    def setup_tabs(self):
        """Initialize the first tab and set up central widget"""
        self.main_window.setCentralWidget(self.tab_widget)
        first_tab = self.create_new_tab("Main")
        return first_tab

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

        # Connect to models
        tab_content.set_model(self.main_window.notes_model)
        tab_content.set_navigation_model(
            self.main_window.navigation_model,
            self.main_window._actions
        )

        # Connect save signal to status updates
        tab_content.note_saved.connect(self._handle_note_saved)

        # Add to tab widget
        index = self.tab_widget.addTab(tab_content, title)
        
        # Store current note ID for this tab
        if self.tab_widget.count() > 1:
            # Copy the current note ID from the active tab
            current_tab = self.tab_widget.currentWidget()
            if isinstance(current_tab, TabContent):
                current_note_id = current_tab.get_current_note_id()
                if current_note_id is not None:
                    self._tab_note_ids[index] = current_note_id
                    tab_content.set_current_note(current_note_id)

        # Restore tree state if available
        if self._last_tree_state is not None:
            tab_content.left_sidebar.tree.restore_state(self._last_tree_state)

        return tab_content

    def _handle_note_saved(self, note_id: int):
        """Update status bar when note is saved"""
        self.main_window.status_bar.showMessage(f"Note {note_id} saved successfully", 3000)

    def close_current_tab(self):
        current_index = self.tab_widget.currentIndex()
        # Remove the note ID mapping when closing the tab
        self._tab_note_ids.pop(current_index, None)
        self.tab_widget.close_tab(current_index)
        # Adjust remaining tab indices in the mapping
        new_mapping = {}
        for idx, note_id in self._tab_note_ids.items():
            if idx > current_index:
                new_mapping[idx - 1] = note_id
            else:
                new_mapping[idx] = note_id
        self._tab_note_ids = new_mapping

    def next_tab(self):
        self._store_current_tab_state()
        current = self.tab_widget.currentIndex()
        next_index = (current + 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(next_index)
        self._restore_tab_state(next_index)

    def previous_tab(self):
        self._store_current_tab_state()
        current = self.tab_widget.currentIndex()
        prev_index = (current - 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(prev_index)
        self._restore_tab_state(prev_index)

    def _store_current_tab_state(self):
        """Store the current tab's note ID"""
        current_tab = self.tab_widget.currentWidget()
        if isinstance(current_tab, TabContent):
            current_index = self.tab_widget.currentIndex()
            note_id = current_tab.get_current_note_id()
            if note_id is not None:
                self._tab_note_ids[current_index] = note_id

    def _restore_tab_state(self, index: int):
        """Restore the note ID for the given tab index"""
        if index in self._tab_note_ids:
            tab_content = self.tab_widget.widget(index)
            if isinstance(tab_content, TabContent):
                tab_content.set_current_note(self._tab_note_ids[index])
