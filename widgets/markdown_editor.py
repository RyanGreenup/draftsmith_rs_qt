import resources_rc
from PySide6.QtWebEngineCore import (
    QWebEnginePage, QWebEngineUrlScheme,
    QWebEngineUrlSchemeHandler, QWebEngineUrlRequestJob,
    QWebEngineProfile
)
from PySide6.QtWidgets import QWidget, QSplitter, QTextEdit, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QTimer, Signal, QUrl, QByteArray, QBuffer, QIODevice
import markdown
from widgets.text_edit.neovim_integration import EditorWidget
from enum import Enum
from urllib.parse import quote

class URLScheme(Enum):
    """URL schemes used in the application"""
    ASSET = "asset://local"
    NOTE = "note://local"

def make_asset_url(asset_name: str) -> str:
    """Create properly formatted asset URL

    Args:
        asset_name: The asset filename/path

    Returns:
        str: Properly formatted asset URL
    """
    # Remove any leading slashes and 'm/' prefix if present
    clean_name = asset_name.lstrip('/').removeprefix('m/')
    return f"{URLScheme.ASSET.value}/m/{quote(clean_name)}"


# Define and register the custom URL scheme for assets
asset_scheme = QWebEngineUrlScheme(b"asset")
asset_scheme.setSyntax(QWebEngineUrlScheme.Syntax.Path)
asset_scheme.setFlags(
    QWebEngineUrlScheme.LocalAccessAllowed | QWebEngineUrlScheme.CorsEnabled
)
QWebEngineUrlScheme.registerScheme(asset_scheme)


class AssetUrlSchemeHandler(QWebEngineUrlSchemeHandler):
    def __init__(self, markdown_editor):
        super().__init__()
        self.markdown_editor = markdown_editor

    def requestStarted(self, job: QWebEngineUrlRequestJob):
        url = job.requestUrl()
        path = url.path().lstrip('/')

        # Remove 'm/' prefix if present
        if path.startswith('m/'):
            path = path[2:]

        if not path:
            job.fail(QWebEngineUrlRequestJob.Error.RequestFailed)
            return

        # Emit signal to request asset data
        self.markdown_editor.asset_requested.emit(path, job)


class LinkHandler(QWebEnginePage):
    def __init__(self, markdown_editor):
        super().__init__(markdown_editor)  # Set parent
        self.markdown_editor = markdown_editor  # Store correct reference

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # Get the full URL string to check scheme
        url_str = url.toString()
        path = url.path()
        
        # Remove trailing slash if present
        if path.endswith('/'):
            path = path[:-1]
            
        # Handle note links regardless of current scheme
        if '/note/' in path:
            try:
                note_id = int(path.split('/note/')[-1])
                self.markdown_editor.note_selected.emit(note_id)
                return False
            except ValueError:
                pass
                
        return True



class MarkdownEditor(QWidget):
    save_requested = Signal()
    preview_requested = Signal()    # Pull the initial preview
    render_requested = Signal(str)  # Send up the content and get back the rendered HTML
    note_selected = Signal(int)     # Emitted when a note link is clicked
    asset_requested = Signal(str, QWebEngineUrlRequestJob)  # Emitted when an asset is requested

    def __init__(self, parent=None):
        super().__init__(parent)
        self._remote_rendering_action = None
        
        # Load CSS from resources
        css_file = QFile(":/styles/markdown.css")
        css_file.open(QFile.ReadOnly)
        self.css = css_file.readAll().data().decode()
        css_file.close()

        # Create horizontal splitter for side-by-side view
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create editor
        self.editor = EditorWidget()
        self.editor.textChanged.connect(self.on_text_changed)

        # Set up WebEngine profile and handlers
        self.profile = QWebEngineProfile.defaultProfile()
        self.scheme_handler = AssetUrlSchemeHandler(self)
        self.profile.installUrlSchemeHandler(b"asset", self.scheme_handler)

        # Create preview with custom link handling
        self.preview = QWebEngineView()
        self.preview.setPage(LinkHandler(self))
        self.preview.setHtml("", QUrl(URLScheme.ASSET.value))

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
        styled_html = f"""
        <html>
        <head>
            <style>
                {self.css}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        self.preview.setHtml(styled_html, QUrl(URLScheme.ASSET.value))


    def update_preview_local(self):
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=["fenced_code", "tables", "wikilinks", "footnotes"])
        html = md.convert(self.editor.toPlainText())

        # Add styling from resource
        styled_html = f"""
        <html>
        <head>
            <style>
                {self.css}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """

        self.preview.setHtml(styled_html, QUrl(URLScheme.ASSET.value))

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


