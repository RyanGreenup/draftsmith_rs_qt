# Creating Tabs in PySide6

This tutorial explains how to implement tabbed interfaces in PySide6 applications, using our note-taking app as an example.

## Overview

To add tabs to a PySide6 application, you'll need to:

1. Create a custom tab widget class
2. Modify your main window to use tabs
3. Add tab-related menu items and actions
4. Handle tab operations (create, close, switch)

## Step 1: Create a Tab Widget

First, create a custom tab widget class that inherits from `QTabWidget`:

```python
from PySide6.QtWidgets import QTabWidget

class NotesTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)  # Allow tabs to be closed
        self.setMovable(True)       # Allow tabs to be reordered
        self.tabCloseRequested.connect(self.close_tab)
        
    def add_new_tab(self, title="New Tab"):
        """Create a new tab with content"""
        tab_content = YourContentWidget()  # Your main content widget
        index = self.addTab(tab_content, title)
        self.setCurrentIndex(index)
        return tab_content
        
    def close_tab(self, index):
        """Close the tab at given index"""
        if self.count() > 1:  # Keep at least one tab open
            self.removeTab(index)
```

## Step 2: Use Tabs in Main Window

Modify your main window to use the tab widget:

```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create and setup tab widget
        self.tab_widget = NotesTabWidget(self)
        self.setCentralWidget(self.tab_widget)
        
        # Create initial tab
        self.main_content = self.tab_widget.add_new_tab("Main")
```

## Step 3: Add Tab Menu Items

Create menu items for tab operations:

```python
def create_tabs_menu(parent):
    tabs_menu = QMenu("&Tabs", parent)
    actions = {}
    
    # New tab action
    actions['new_tab'] = QAction("&New Tab", parent)
    actions['new_tab'].setShortcut("Ctrl+T")
    tabs_menu.addAction(actions['new_tab'])
    
    # Close tab action
    actions['close_tab'] = QAction("&Close Tab", parent)
    actions['close_tab'].setShortcut("Ctrl+W")
    tabs_menu.addAction(actions['close_tab'])
    
    # Tab navigation
    actions['next_tab'] = QAction("Next Tab", parent)
    actions['next_tab'].setShortcut("Ctrl+Tab")
    actions['prev_tab'] = QAction("Previous Tab", parent)
    actions['prev_tab'].setShortcut("Ctrl+Shift+Tab")
    
    return tabs_menu, actions
```

## Step 4: Implement Tab Operations

Add methods to handle tab operations:

```python
def new_tab(self):
    """Create a new tab"""
    self.tab_widget.add_new_tab()

def close_current_tab(self):
    """Close the current tab"""
    current_index = self.tab_widget.currentIndex()
    self.tab_widget.close_tab(current_index)

def next_tab(self):
    """Switch to next tab"""
    current = self.tab_widget.currentIndex()
    next_index = (current + 1) % self.tab_widget.count()
    self.tab_widget.setCurrentIndex(next_index)

def previous_tab(self):
    """Switch to previous tab"""
    current = self.tab_widget.currentIndex()
    prev_index = (current - 1) % self.tab_widget.count()
    self.tab_widget.setCurrentIndex(prev_index)
```

## Step 5: Connect Actions

Connect the menu actions to their handlers:

```python
# Connect tab actions
self.tabs_actions['new_tab'].triggered.connect(self.new_tab)
self.tabs_actions['close_tab'].triggered.connect(self.close_current_tab)
self.tabs_actions['next_tab'].triggered.connect(self.next_tab)
self.tabs_actions['prev_tab'].triggered.connect(self.previous_tab)
```

## Key Features

1. **Tab Creation**: Users can create new tabs with Ctrl+T
2. **Tab Closure**: Close tabs with Ctrl+W (keeps at least one tab open)
3. **Tab Navigation**: Switch between tabs with Ctrl+Tab and Ctrl+Shift+Tab
4. **Tab Reordering**: Users can drag tabs to reorder them
5. **Independent Content**: Each tab maintains its own independent state

## Best Practices

1. Always keep at least one tab open
2. Use meaningful tab titles
3. Implement keyboard shortcuts for common operations
4. Consider tab state persistence
5. Handle tab-specific data properly

## Common Pitfalls

1. **Memory Management**: Ensure proper cleanup when closing tabs
2. **State Management**: Keep tab states independent
3. **Performance**: Be mindful of resource usage with many tabs
4. **UI Consistency**: Maintain consistent UI across tabs

## Example Usage

Here's a complete example of creating a tabbed interface:

```python
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tabbed Application")
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        
        # Set as central widget
        self.setCentralWidget(self.tabs)
        
        # Add initial tab
        self.add_new_tab()
        
    def add_new_tab(self):
        new_tab = YourContentWidget()
        self.tabs.addTab(new_tab, f"Tab {self.tabs.count() + 1}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

## Conclusion

Implementing tabs in PySide6 provides a clean way to organize content and improve user experience. The `QTabWidget` class offers built-in functionality for most common tab operations, making it straightforward to implement tabbed interfaces in your applications.

Remember to handle tab state properly and maintain good performance even with multiple tabs open. With proper implementation, tabs can greatly enhance the usability of your application.
