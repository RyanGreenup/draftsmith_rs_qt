# How to Create a Command Palette in PySide6

This tutorial explains how to create a command palette similar to VS Code's command palette (Ctrl+Shift+P) for your Qt application using PySide6.

## Overview

A command palette provides quick keyboard access to all menu commands in your application. The implementation consists of two main classes:
- A base popup palette class that handles the UI and keyboard navigation
- A specialized command palette class that manages menu actions

## Step 1: Create the Base Popup Palette

First, create a base class that handles the common popup functionality:

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QListWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QGraphicsDropShadowEffect

class PopupPalette(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setMinimumWidth(500)
        self.setMaximumHeight(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search...")
        self.search_input.textChanged.connect(self.on_search)
        layout.addWidget(self.search_input)

        # Results list
        self.results_list = QListWidget()
        self.results_list.itemActivated.connect(self.on_item_activated)
        layout.addWidget(self.results_list)
```

## Step 2: Create the Command Palette

Next, create a specialized class for handling menu commands:

```python
from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtCore import Qt

class CommandPalette(PopupPalette):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.actions = []
        self.search_input.setPlaceholderText("Type command...")

    def populate_actions(self, menubar):
        """Collect all actions from the menubar's menus"""
        self.actions.clear()
        for menu in menubar.findChildren(QAction):
            if hasattr(menu, 'menu') and menu.menu():
                for action in menu.menu().actions():
                    if action.text() and not action.menu():
                        self.actions.append(action)
```

## Step 3: Implement Search and Filtering

Add methods to filter and display menu items:

```python
def filter_items(self, text):
    """Filter actions based on search text"""
    search_terms = text.lower().split()
    for action in self.actions:
        action_text = action.text().lower()
        if all(term in action_text for term in search_terms):
            item = self.create_list_item(action)
            if item:
                self.results_list.addItem(item)

def create_list_item(self, action):
    """Create a list item from an action"""
    if not action.text():
        return None

    display_text = f"{action.text().replace('&', ''):<30}"
    if action.statusTip():
        display_text += f" • {action.statusTip()}"

    item = QListWidgetItem(display_text)
    item.setData(Qt.ItemDataRole.UserRole, action)
    return item
```

## Step 4: Handle Item Selection and Activation

Implement the logic for executing selected commands:

```python
def on_item_activated(self, item):
    """Trigger the selected action"""
    action = item.data(Qt.ItemDataRole.UserRole)
    if action and action.isEnabled():
        action.trigger()
    self.hide()
```

## Step 5: Add Keyboard Navigation

Implement keyboard shortcuts for navigation:

```python
def keyPressEvent(self, event):
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
```

## Step 6: Integration with Main Window

Add the command palette to your main window:

```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Create command palette
        self.command_palette = CommandPalette(self)

        # Create menubar and menus
        self.create_menus()

        # Populate command palette with menu actions
        self.command_palette.populate_actions(self.menuBar())

        # Add shortcut to show command palette
        show_palette_action = QAction(self)
        show_palette_action.setShortcut("Ctrl+Shift+P")
        show_palette_action.triggered.connect(self.show_command_palette)
        self.addAction(show_palette_action)

    def show_command_palette(self):
        self.command_palette.show_palette()
```

## Minimum Working Example

```python
import sys
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt


# Step 1: Base Popup Palette
from typing import List

class PopupPalette(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setMinimumWidth(500)
        self.setMaximumHeight(400)
        self.results_list: QListWidget = QListWidget()  # Initialize results_list
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search...")
        self.search_input.textChanged.connect(self.on_search)
        layout.addWidget(self.search_input)

        # Results list
        self.results_list = QListWidget()
        self.results_list.itemActivated.connect(self.on_item_activated)
        self.results_list.currentRowChanged.connect(self.update_status_on_row_change)
        layout.addWidget(self.results_list)

    def filter_items(self, text: str) -> None:
        """Filter items based on search text"""
        pass  # Implement this method in subclasses

    def on_search(self, text):
        self.results_list.clear()
        self.filter_items(text)

    def on_item_activated(self, item: QListWidgetItem) -> None:
        """Trigger the selected action"""
        action = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(action, QAction) and action.isEnabled():
            action.trigger()
        self.hide()

    def update_status_on_row_change(self, current_row: int) -> None:
        """Update the status bar when the selected row changes"""
        pass  # Implement this method in subclasses

# Step 2: Command Palette
from typing import List

from PySide6.QtCore import Signal

class CommandPalette(PopupPalette):
    itemActivated = Signal(str)
    filterChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.palette_actions: List[QAction] = []  # Renamed to avoid overriding QWidget's actions method
        self.search_input.setPlaceholderText("Type command...")

    def populate_actions(self, menubar) -> None:
        """Collect all actions from the menubar's menus"""
        self.palette_actions.clear()
        for action in menubar.actions():
            if action.menu():
                for sub_action in action.menu().actions():
                    if sub_action.text() and not sub_action.menu():
                        self.palette_actions.append(sub_action)

    def filter_items(self, text: str) -> None:
        """Filter actions based on search text"""
        search_terms = text.lower().split()
        filtered_actions = []
        for action in self.palette_actions:
            action_text = action.text().lower()
            if all(term in action_text for term in search_terms):
                filtered_actions.append(action)

        self.results_list.clear()
        for action in filtered_actions:
            item = self.create_list_item(action)
            if item:
                self.results_list.addItem(item)

        # Select the first item if available
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)

        if filtered_actions:
            description = filtered_actions[0].statusTip() or "No description available"
        else:
            description = "No commands found"
        self.filterChanged.emit(description)

    def create_list_item(self, action: QAction) -> QListWidgetItem:
        """Create a list item from an action"""
        if not action.text():
            raise ValueError("Action must have text")

        display_text = f"{action.text().replace('&', ''):<30}"
        if action.statusTip():
            display_text += f" • {action.statusTip()}"

        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, action)
        return item

    def on_item_activated(self, item: QListWidgetItem) -> None:
        """Trigger the selected action"""
        action = item.data(Qt.ItemDataRole.UserRole)
        if action and action.isEnabled():
            description = f"Executing: {action.text()}"
            self.itemActivated.emit(description)
            action.trigger()
        self.hide()

    def update_status_on_row_change(self, current_row: int) -> None:
        """Update the status bar when the selected row changes"""
        item = self.results_list.item(current_row)
        if item:
            action = item.data(Qt.ItemDataRole.UserRole)
            description = action.statusTip() or "No description available"
            self.filterChanged.emit(description)

    def keyPressEvent(self, event) -> None:
        """Handle keyboard navigation"""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
            return

        if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            current_item = self.results_list.currentItem()
            if current_item:
                self.on_item_activated(current_item)
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

# Step 6: Integration with Main Window
from PySide6.QtWidgets import QStatusBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Command Palette Example")

        # Create command palette
        self.command_palette = CommandPalette(self)
        self.command_palette.itemActivated.connect(self.update_status_bar)
        self.command_palette.filterChanged.connect(self.update_status_bar)

        # Create menubar and menus
        self.create_menus()

        # Populate command palette with menu actions
        self.command_palette.populate_actions(self.menuBar())

        # Add shortcut to show command palette
        show_palette_action = QAction(self)
        show_palette_action.setShortcut("Ctrl+Shift+P")
        show_palette_action.triggered.connect(self.show_command_palette)
        self.addAction(show_palette_action)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def create_menus(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        open_action = QAction("Open", self)
        open_action.setStatusTip("Open a file")
        open_action.triggered.connect(lambda: print("Open triggered"))
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setStatusTip("Save the file")
        save_action.triggered.connect(lambda: print("Save triggered"))
        file_menu.addAction(save_action)

    def show_command_palette(self) -> None:
        self.command_palette.move(self.geometry().center() - self.command_palette.rect().center())
        self.command_palette.show()
        self.command_palette.search_input.setText("")  # Clear previous search
        self.command_palette.search_input.setFocus()
        self.command_palette.on_search("")  # Populate the list with all actions

    def update_status_bar(self, description: str) -> None:
        self.status_bar.showMessage(description)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())

```


## Usage

To use the command palette:

1. Press Ctrl+Shift+P to open the palette
2. Type to filter commands
3. Use Up/Down arrows or Ctrl+P/Ctrl+N to navigate
4. Press Enter to execute the selected command
5. Press Esc to close the palette

The command palette provides quick access to all menu commands without needing to navigate through menus with the mouse.



