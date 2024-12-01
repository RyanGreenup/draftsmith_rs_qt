from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QListWidget, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QColor, QPalette, QFont

class PopupPalette(QWidget):
    """Base class for popup command palettes"""
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setMinimumWidth(500)  # Set minimum width
        self.setMaximumHeight(400)  # Set maximum height
        
        # Set window background
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.Base, QColor(60, 60, 60))
        palette.setColor(QPalette.ColorRole.Text, QColor(200, 200, 200))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(130, 130, 130))
        self.setPalette(palette)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Search input styling
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search...")
        self.search_input.textChanged.connect(self.on_search)
        search_font = QFont()
        search_font.setPointSize(12)
        self.search_input.setFont(search_font)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: none;
                border-radius: 4px;
                background-color: #404040;
                color: #E0E0E0;
            }
            QLineEdit:focus {
                background-color: #454545;
            }
        """)
        layout.addWidget(self.search_input)
        
        # Results list styling
        self.results_list = QListWidget()
        self.results_list.itemActivated.connect(self.on_item_activated)
        self.results_list.setStyleSheet("""
            QListWidget {
                border: none;
                border-radius: 4px;
                background-color: #404040;
                color: #E0E0E0;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #2979ff;
                color: white;
            }
            QListWidget::item:hover:!selected {
                background-color: #505050;
            }
        """)
        layout.addWidget(self.results_list)
        
        self.setLayout(layout)
        
    def show_palette(self):
        """Show the palette and focus the search input"""
        # Add drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # Center the palette on screen
        screen = self.screen().geometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2
        )
        
        self.show()
        self.search_input.setFocus()
        self.search_input.clear()
        self.results_list.clear()
        
        # Show all items initially
        for item_data in self.get_all_items():
            list_item = self.create_list_item(item_data)
            if list_item:
                self.results_list.addItem(list_item)
        
        # Select first item by default
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)
        
    def get_all_items(self):
        """Get all items to be shown in the palette.
        To be implemented by subclasses."""
        return []

    def create_list_item(self, data):
        """Create a list widget item from the data.
        To be implemented by subclasses."""
        pass

    def on_search(self, text):
        """Handle search text changes"""
        self.results_list.clear()
        
        if not text.strip():  # Show all items when search is empty
            for item_data in self.get_all_items():
                list_item = self.create_list_item(item_data)
                if list_item:
                    self.results_list.addItem(list_item)
        else:
            self.filter_items(text)
            
        # Select first item if any exist
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)
    
    def filter_items(self, text):
        """Filter items based on search text.
        To be implemented by subclasses."""
        pass
        
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard navigation"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            current_row = self.results_list.currentRow()
            
            if event.key() == Qt.Key.Key_N:  # Next item
                if current_row < self.results_list.count() - 1:
                    self.results_list.setCurrentRow(current_row + 1)
                event.accept()
                return
                
            elif event.key() == Qt.Key.Key_P:  # Previous item
                if current_row > 0:
                    self.results_list.setCurrentRow(current_row - 1)
                event.accept()
                return
                
        super().keyPressEvent(event)
        
    def on_item_activated(self, item):
        """Handle item selection"""
        # To be implemented by subclasses
        pass
