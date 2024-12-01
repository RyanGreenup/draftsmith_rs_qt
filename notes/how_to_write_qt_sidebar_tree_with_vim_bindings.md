# Creating a Note-Taking App with Qt: Tree Sidebar and Vim-like Navigation

This tutorial will show you how to create a note-taking application with a tree sidebar, vim-style keyboard navigation, and a text editor using Qt (PySide6).

## Prerequisites
- Python 3.x
- PySide6 (`pip install PySide6`)

## Step 1: Basic Structure

First, let's set up the basic imports and window structure:

```python
from PySide6.QtWidgets import (QApplication, QMainWindow, QSplitter,
                             QTreeWidget, QTreeWidgetItem, QTextEdit)
from PySide6.QtCore import Qt
import sys

class NoteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Note Taking App")
        self.setGeometry(100, 100, 1000, 600)
```

## Step 2: Creating the Tree Widget with Vim Bindings

Create a custom tree widget that handles keyboard navigation:

```python
class NotesTreeWidget(QTreeWidget):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_J:  # Move down
            current = self.currentItem()
            if current:
                index = self.indexOfTopLevelItem(current)
                if index == -1:  # Item is not top level
                    parent = current.parent()
                    index = parent.indexOfChild(current)
                    if index < parent.childCount() - 1:
                        self.setCurrentItem(parent.child(index + 1))
                else:  # Item is top level
                    if index < self.topLevelItemCount() - 1:
                        self.setCurrentItem(self.topLevelItem(index + 1))
        
        elif event.key() == Qt.Key_K:  # Move up
            # ... similar to Key_J but for upward movement ...
        
        elif event.key() in (Qt.Key_Space, Qt.Key_Right, Qt.Key_Left):
            current = self.currentItem()
            if current:
                if event.key() == Qt.Key_Left:
                    current.setExpanded(False)
                elif event.key() == Qt.Key_Right:
                    current.setExpanded(True)
                elif event.key() == Qt.Key_Space:
                    current.setExpanded(not current.isExpanded())
        else:
            super().keyPressEvent(event)
```

## Step 3: Setting Up the Main Window Layout

Add a splitter and the main components:

```python
def setup_ui(self):
    # Create main splitter
    self.splitter = QSplitter(Qt.Horizontal)
    
    # Create tree widget for sidebar
    self.tree = NotesTreeWidget()
    self.tree.setHeaderLabel("Notes")
    self.tree.setMinimumWidth(200)
    
    # Create text edit for main content
    self.text_edit = QTextEdit()
    
    # Add widgets to splitter
    self.splitter.addWidget(self.tree)
    self.splitter.addWidget(self.text_edit)
    
    # Set splitter as central widget
    self.setCentralWidget(self.splitter)
```

## Step 4: Creating the Note Data Structure

```python
class Note:
    def __init__(self, title, content=""):
        self.title = title
        self.content = content
```

## Step 5: Handling Note Selection

Add a method to handle tree item selection:

```python
def on_selection_changed(self):
    selected_items = self.tree.selectedItems()
    if selected_items:
        item = selected_items[0]
        note = item.data(0, Qt.UserRole)
        if note:
            self.text_edit.setText(note.content)
        else:
            self.text_edit.clear()
```

## Step 6: Adding Sample Data

```python
def add_dummy_data(self):
    notes_hierarchy = {
        Note("Work", "Work-related notes"): [
            Note("Meeting Notes", "Meeting agenda..."),
            Note("Project Ideas", "New features...")
        ],
        Note("Personal", "Personal notes"): [
            Note("Shopping List", "Items to buy..."),
            Note("Goals", "2024 Goals...")
        ]
    }

    for parent_note, child_notes in notes_hierarchy.items():
        parent_item = QTreeWidgetItem(self.tree)
        parent_item.setText(0, parent_note.title)
        parent_item.setData(0, Qt.UserRole, parent_note)

        for child_note in child_notes:
            child_item = QTreeWidgetItem(parent_item)
            child_item.setText(0, child_note.title)
            child_item.setData(0, Qt.UserRole, child_note)
```

## Step 7: Running the Application

```python
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteApp()
    window.show()
    sys.exit(app.exec())
```

## Key Features

- **Vim-style Navigation:**
  - `j`: Move down in the tree
  - `k`: Move up in the tree
  - `Space`: Toggle expand/collapse
  - `Left Arrow`: Collapse node
  - `Right Arrow`: Expand node

- **Layout:**
  - Resizable splitter between tree and editor
  - Minimum width for the tree sidebar
  - Full-height text editor

## Tips for Customization

1. **Adjust Tree Appearance:**
   ```python
   self.tree.setMinimumWidth(200)  # Change sidebar width
   self.tree.setHeaderLabel("Notes")  # Change header text
   ```

2. **Modify Splitter Behavior:**
   ```python
   self.splitter.setCollapsible(0, False)  # Prevent sidebar collapse
   self.splitter.setSizes([200, 800])  # Set initial sizes
   ```

3. **Add Text Editor Features:**
   ```python
   self.text_edit.setAcceptRichText(False)  # Plain text only
   self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
   ```

This creates a functional note-taking application with a tree sidebar for organization and a text editor for content. The vim-style navigation makes it keyboard-friendly and efficient to use.
