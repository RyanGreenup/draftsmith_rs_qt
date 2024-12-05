from PySide6.QtWidgets import QWidget, QSplitter, QTextEdit, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PySide6.QtCore import Qt, QTimer, Signal
import markdown
from widgets.text_edit.neovim_integration import EditorWidget


class MarkdownEditor(QWidget):
    save_requested = Signal()
    preview_requested = Signal()    # Pull the initial preview
    render_requested = Signal(str)  # Send up the content and get back the rendered HTML
    note_selected = Signal(int)     # Emitted when a note link is clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self._remote_rendering_action = None

        # Create horizontal splitter for side-by-side view
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create editor
        self.editor = EditorWidget()
        self.editor.textChanged.connect(self.on_text_changed)

        # Create preview
        self.preview = QWebEngineView()
        self.preview.setHtml("")
        # Enable link clicking
        self.preview.page().setLinkDelegationPolicy(QWebEnginePage.LinkDelegationPolicy.DelegateAllLinks)
        self.preview.page().linkClicked.connect(self._handle_url_changed)

        # Add widgets to splitter
        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.preview)
        self.splitter.setSizes([300, 300])

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
        """
        Sync the Preview with the Editor
        """
        # When text changes, we want to send the content up for rendering
        if self._remote_rendering_action and self._remote_rendering_action.isChecked():
            self.render_requested.emit(self.editor.toPlainText())
        else:
            self.update_timer.start(0)  # Local preview update

    def update_preview(self):
        """
        Update the preview with a new note
        """
        if self._remote_rendering_action and self._remote_rendering_action.isChecked():
            self.preview_requested.emit()  # Request preview from controller
        else:
            self.update_preview_local()

    def set_preview_content(self, html: str):
        """Update preview with provided HTML content"""
        self.preview.setHtml(html)


    def update_preview_local(self):
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=["fenced_code", "tables", "wikilinks"])
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

    def maximize_editor(self, checked: bool):
        if checked:
            # Store current sizes for restoration
            self._stored_sizes = self.splitter.sizes()
            self.splitter.setSizes([1, 0])  # Show only editor
            # Uncheck preview maximize if it's checked
            self._maximize_preview_action.setChecked(False)
        else:
            # Restore previous sizes if stored
            if hasattr(self, "_stored_sizes"):
                self.splitter.setSizes(self._stored_sizes)
            else:
                self.splitter.setSizes([300, 300])

    def maximize_preview(self, checked: bool):
        if checked:
            # Store current sizes for restoration
            self._stored_sizes = self.splitter.sizes()
            self.splitter.setSizes([0, 1])  # Show only preview
            # Uncheck editor maximize if it's checked
            self._maximize_editor_action.setChecked(False)
        else:
            # Restore previous sizes if stored
            if hasattr(self, "_stored_sizes"):
                self.splitter.setSizes(self._stored_sizes)
            else:
                self.splitter.setSizes([300, 300])

    def set_view_actions(self, maximize_editor_action, maximize_preview_action, remote_rendering_action):
        """Connect view actions to the editor"""
        self._maximize_editor_action = maximize_editor_action
        self._maximize_preview_action = maximize_preview_action
        self._remote_rendering_action = remote_rendering_action
        maximize_editor_action.triggered.connect(self.maximize_editor)
        maximize_preview_action.triggered.connect(self.maximize_preview)

    def save_content(self):
        """Emit signal to request saving current content"""
        self.save_requested.emit()

    def get_content(self) -> str:
        """Get current editor content"""
        return self.editor.toPlainText()

    def get_cursor_position(self) -> int:
        """Get current cursor position in the editor"""
        return self.editor.textCursor().position()

    def set_cursor_position(self, position: int):
        """Set cursor position in the editor"""
        cursor = self.editor.textCursor()
        cursor.setPosition(position)
        self.editor.setTextCursor(cursor)

    def _handle_url_changed(self, url):
        """Handle URL changes in the preview window"""
        path = url.path()
        print(f"URL changed: {url}")
        if path.startswith('/'):
            try:
                note_id = int(path[1:])  # Remove leading slash and convert to int
                self.note_selected.emit(note_id)
            except ValueError:
                pass  # Not a valid note ID link
