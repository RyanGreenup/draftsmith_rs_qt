from PySide6.QtWidgets import (QApplication, QMainWindow, QSplitter, 
                             QTreeWidget, QTreeWidgetItem, QTextEdit)
from PySide6.QtCore import Qt
import sys

class NotesTreeWidget(QTreeWidget):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_J:
            # Get current item
            current = self.currentItem()
            if current:
                # Get index of current item
                index = self.indexOfTopLevelItem(current)
                if index == -1:  # Item is not top level
                    parent = current.parent()
                    index = parent.indexOfChild(current)
                    # Get next item
                    if index < parent.childCount() - 1:
                        self.setCurrentItem(parent.child(index + 1))
                else:  # Item is top level
                    if index < self.topLevelItemCount() - 1:
                        self.setCurrentItem(self.topLevelItem(index + 1))
    
        elif event.key() == Qt.Key_K:
            current = self.currentItem()
            if current:
                index = self.indexOfTopLevelItem(current)
                if index == -1:  # Item is not top level
                    parent = current.parent()
                    index = parent.indexOfChild(current)
                    # Get previous item
                    if index > 0:
                        self.setCurrentItem(parent.child(index - 1))
                else:  # Item is top level
                    if index > 0:
                        self.setCurrentItem(self.topLevelItem(index - 1))
    
        elif event.key() in (Qt.Key_Space, Qt.Key_Right, Qt.Key_Left):
            current = self.currentItem()
            if current:
                # Right arrow or Space expands, Left arrow collapses
                if event.key() == Qt.Key_Left:
                    current.setExpanded(False)
                elif event.key() == Qt.Key_Right:
                    current.setExpanded(True)
                elif event.key() == Qt.Key_Space:
                    current.setExpanded(not current.isExpanded())
        else:
            super().keyPressEvent(event)

class Note:
    def __init__(self, title, content=""):
        self.title = title
        self.content = content

class NoteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Note Taking App")
        self.setGeometry(100, 100, 1000, 600)

        # Create main splitter
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Create tree widget for sidebar
        self.tree = NotesTreeWidget()
        self.tree.setHeaderLabel("Notes")
        self.tree.setMinimumWidth(200)
        self.tree.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Create text edit for main content
        self.text_edit = QTextEdit()
        
        # Add widgets to splitter
        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.text_edit)
        
        # Set splitter as central widget
        self.setCentralWidget(self.splitter)
        
        # Add dummy data
        self.add_dummy_data()
    
    def on_selection_changed(self):
        selected_items = self.tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            note = item.data(0, Qt.UserRole)
            if note:
                self.text_edit.setText(note.content)
            else:
                self.text_edit.clear()

    def add_dummy_data(self):
        notes_hierarchy = {
            Note("Work", "General work-related notes and tasks"): [
                Note("Meeting Notes", "Meeting agenda:\n1. Project updates\n2. Timeline review"),
                Note("Project Ideas", "New features to implement:\n- Dark mode\n- Auto-save"),
                Note("To-Do List", "- Send report\n- Update documentation")
            ],
            Note("Personal", "My personal notes and plans"): [
                Note("Shopping List", "- Groceries\n- Household items"),
                Note("Travel Plans", "Places to visit:\n1. Paris\n2. Tokyo"),
                Note("Goals", "2024 Goals:\n1. Learn Python\n2. Exercise more")
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteApp()
    window.show()
    sys.exit(app.exec())
