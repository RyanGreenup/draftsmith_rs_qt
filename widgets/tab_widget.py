from PySide6.QtWidgets import QTabWidget
from .main_content import MainContent


class NotesTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)

    def add_new_tab(self, title="New Tab"):
        """Create a new tab with MainContent"""
        tab_content = MainContent(handle_size=20)
        index = self.addTab(tab_content, title)
        self.setCurrentIndex(index)
        
        # Initialize models
        tab_content.initialize_notes_model("http://eir:37242")
        
        # Get navigation model from main window
        main_window = self.window()
        if main_window and hasattr(main_window, 'navigation_model'):
            tab_content.set_navigation_model(main_window.navigation_model)
            
        tab_content.left_sidebar.tree.setFocus()
        return tab_content

    def close_tab(self, index):
        """Close the tab at given index"""
        if self.count() > 1:  # Keep at least one tab open
            self.removeTab(index)
