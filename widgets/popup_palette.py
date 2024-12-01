from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QListWidget
from PySide6.QtCore import Qt

class PopupPalette(QWidget):
    """Base class for popup command palettes"""
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search...")
        self.search_input.textChanged.connect(self.on_search)
        layout.addWidget(self.search_input)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.itemActivated.connect(self.on_item_activated)
        layout.addWidget(self.results_list)
        
        self.setLayout(layout)
        
    def show_palette(self):
        """Show the palette and focus the search input"""
        self.show()
        self.search_input.setFocus()
        self.search_input.clear()
        self.results_list.clear()
        
    def on_search(self, text):
        """Handle search text changes"""
        # To be implemented by subclasses
        pass
        
    def on_item_activated(self, item):
        """Handle item selection"""
        # To be implemented by subclasses
        pass
