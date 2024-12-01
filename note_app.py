from PySide6.QtWidgets import (QApplication, QMainWindow, QSplitter, 
                             QTreeWidget, QTreeWidgetItem, QTextEdit)
from PySide6.QtCore import Qt
import sys

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
        
        # Create text edit for main content
        self.text_edit = QTextEdit()
        
        # Add widgets to splitter
        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.text_edit)
        
        # Set splitter as central widget
        self.setCentralWidget(self.splitter)
        
        # Add dummy data
        self.add_dummy_data()
    
    def add_dummy_data(self):
        # Create some dummy categories and notes
        categories = {
            "Work": ["Meeting Notes", "Project Ideas", "To-Do List"],
            "Personal": ["Shopping List", "Travel Plans", "Goals"],
            "Study": ["Python Notes", "Math Notes", "History Notes"]
        }
        
        for category, notes in categories.items():
            category_item = QTreeWidgetItem(self.tree)
            category_item.setText(0, category)
            
            for note in notes:
                note_item = QTreeWidgetItem(category_item)
                note_item.setText(0, note)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteApp()
    window.show()
    sys.exit(app.exec())
