from PySide6.QtWidgets import QWidget, QSplitter, QTextEdit, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QTimer
import markdown

class MarkdownEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create horizontal splitter for side-by-side view
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create editor
        self.editor = QTextEdit()
        self.editor.textChanged.connect(self.on_text_changed)
        
        # Create preview
        self.preview = QWebEngineView()
        self.preview.setHtml("")
        
        # Add widgets to splitter
        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.preview)
        
        # Set up delayed update timer
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_preview)
        
        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.splitter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def on_text_changed(self):
        # Start timer to update preview
        self.update_timer.start(500)  # 500ms delay
        
    def update_preview(self):
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=['fenced_code', 'tables'])
        html = md.convert(self.editor.toPlainText())
        
        # Add some basic styling
        styled_html = f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    padding: 20px;
                    max-width: 800px;
                    margin: 0 auto;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 4px;
                    border-radius: 4px;
                }}
                pre {{
                    background-color: #f4f4f4;
                    padding: 10px;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        self.preview.setHtml(styled_html)

    def set_content(self, content: str):
        self.editor.setPlainText(content)
