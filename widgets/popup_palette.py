from typing import Optional, Any, List
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QListWidget,
    QGraphicsDropShadowEffect,
    QListWidgetItem,
    QMainWindow,
)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QKeyEvent, QColor, QPalette, QFont


class PopupPalette(QWidget):
    """Base class for popup command palettes"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent, Qt.WindowType.Popup)
        self.setObjectName("PopupPalette")
        self.setMinimumWidth(500)  # Set minimum width
        self.setMaximumHeight(400)  # Set maximum height

        # Set window background
        palette = self.palette()
        self.setPalette(palette)

        self.setup_ui()

    def setup_ui(self) -> None:
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
        layout.addWidget(self.search_input)

        # Results list styling
        self.results_list = QListWidget()
        self.results_list.itemActivated.connect(self.on_item_activated)
        layout.addWidget(self.results_list)

        self.setLayout(layout)

    def show_palette(self) -> None:
        """Show the palette and focus the search input"""
        # Add drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        # Position at top center of parent window
        parent = self.parent()
        if isinstance(parent, QWidget):
            parent_rect = parent.geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            # Position slightly below the top to give some breathing room
            y = parent_rect.y() + 50  # Adjust this value to control distance from top
            self.move(x, y)

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

    def get_all_items(self) -> List[Any]:
        """Get all items to be shown in the palette.
        To be implemented by subclasses."""
        return []

    def create_list_item(self, data: Any) -> Optional[QListWidgetItem]:
        """Create a list widget item from the data.
        To be implemented by subclasses."""
        pass

    def on_search(self, text: str) -> None:
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

    def filter_items(self, text: str) -> None:
        """Filter items based on search text.
        To be implemented by subclasses."""
        pass

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard navigation"""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            current_item = self.results_list.currentItem()
            if current_item:
                self.on_item_activated(current_item)
            event.accept()
            return
            
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

    def on_item_activated(self, item: QListWidgetItem) -> None:
        """Handle item selection"""
        # To be implemented by subclasses
        pass
