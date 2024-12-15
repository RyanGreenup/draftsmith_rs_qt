from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPen, QPainter

class NotesTreeDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option, index):
        # First draw the default item
        super().paint(painter, option, index)
        
        # Check if this is marked using the model's data role
        is_marked = index.data(Qt.UserRole)
        
        if is_marked:
            # Save the painter's state
            painter.save()
            
            # Set up the pen for drawing the box
            pen = QPen(Qt.blue)  # You can change the color as needed
            pen.setWidth(2)
            pen.setStyle(Qt.SolidLine)
            painter.setPen(pen)
            
            # Draw rectangle around the item
            rect = option.rect
            margin = 2
            box_rect = QRect(
                rect.x() + margin,
                rect.y() + margin,
                rect.width() - 2*margin,
                rect.height() - 2*margin
            )
            painter.drawRect(box_rect)
            
            # Restore the painter's state
            painter.restore()
