from PySide6.QtWidgets import (QApplication, QMainWindow, QSplitter, 
                             QTreeWidget, QTreeWidgetItem, QTextEdit)
from PySide6.QtCore import Qt
import sys

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
        self.tree = QTreeWidget()
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
        categories = {
            "Work": [
                Note("Meeting Notes", "Meeting agenda:\n1. Project updates\n2. Timeline review"),
                Note("Project Ideas", "New features to implement:\n- Dark mode\n- Auto-save"),
                Note("To-Do List", "- Send report\n- Update documentation")
            ],
            "Personal": [
                Note("Shopping List", "- Groceries\n- Household items"),
                Note("Travel Plans", "Places to visit:\n1. Paris\n2. Tokyo"),
                Note("Goals", "2024 Goals:\n1. Learn Python\n2. Exercise more")
            ]
        }
        
        for category, notes in categories.items():
            category_item = QTreeWidgetItem(self.tree)
            category_item.setText(0, category)
            
            for note in notes:
                note_item = QTreeWidgetItem(category_item)
                note_item.setText(0, note.title)
                note_item.setData(0, Qt.UserRole, note)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteApp()
    window.show()
    sys.exit(app.exec())
