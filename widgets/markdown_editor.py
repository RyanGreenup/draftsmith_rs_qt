from . import static_resources_rc  # pyright:ignore
from . import katex_resources_rc  # pyright:ignore
from PySide6.QtWebEngineCore import (
    QWebEnginePage,
    QWebEngineUrlRequestInfo,
    QWebEngineUrlRequestInterceptor,
    QWebEngineUrlScheme,
    QWebEngineUrlSchemeHandler,
    QWebEngineUrlRequestJob,
    QWebEngineProfile,
)

from PySide6.QtWidgets import QWidget, QSplitter, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import (
    Qt,
    QTimer,
    Signal,
    QUrl,
    QFile,
    QDirIterator,
    QDir,
)
import markdown
from markdown.extensions.wikilinks import WikiLinkExtension
from widgets.text_edit.neovim_integration import EditorWidget
from enum import Enum
from urllib.parse import urlparse, urlunparse


class AssetUrlInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None, base_api_url=None):
        super().__init__(parent)
        self.base_api_url = base_api_url

    def interceptRequest(self, info: QWebEngineUrlRequestInfo):
        url = info.requestUrl()
        path = url.path()

        print(f"Intercepted URL: {url.toString()}")  # Debug print

        if path.startswith("/m/"):
            asset_path = path[3:]  # Remove /m/ prefix
            new_url = f"{self.base_api_url}/assets/download/{asset_path}"
            print(f"Redirecting to: {new_url}")  # Debug print
            info.redirect(QUrl(new_url))


# Define and register the QRC scheme
note_scheme = QWebEngineUrlScheme(b"qrc")
note_scheme.setSyntax(QWebEngineUrlScheme.Syntax.Path)
note_scheme.setFlags(
    QWebEngineUrlScheme.LocalAccessAllowed | QWebEngineUrlScheme.CorsEnabled
)
QWebEngineUrlScheme.registerScheme(note_scheme)

# Register the note scheme for local links
note_scheme = QWebEngineUrlScheme(b"note")
note_scheme.setSyntax(QWebEngineUrlScheme.Syntax.Path)
note_scheme.setFlags(
    QWebEngineUrlScheme.LocalAccessAllowed | QWebEngineUrlScheme.CorsEnabled
)
QWebEngineUrlScheme.registerScheme(note_scheme)


def _resource_to_string(qrc_path: str) -> str:
    qrc_file = QFile(qrc_path)
    qrc_file.open(QFile.ReadOnly)
    content = qrc_file.readAll().data().decode()
    qrc_file.close()
    return content


class MarkdownEditor(QWidget):
    save_requested = Signal()
    preview_requested = Signal()  # Pull the initial preview
    render_requested = Signal(str)  # Send up the content and get back the rendered HTML
    note_selected = Signal(int)  # Emitted when a note link is clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self._remote_rendering_action = None

        # Create horizontal splitter for side-by-side view
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create editor
        self.editor = EditorWidget()
        self.editor.textChanged.connect(self.on_text_changed)

        # Set up WebEngine profile and handlers
        self.profile = QWebEngineProfile.defaultProfile()

        # Add asset URL interceptor
        self.asset_interceptor = AssetUrlInterceptor(self, "http://eir:37242")
        self.profile.setUrlRequestInterceptor(self.asset_interceptor)

        # Create preview with custom link handling
        self.preview = QWebEngineView()
        self.preview.setPage(
            QWebEnginePage(self.profile, self.preview)
        )  # Use our profile with interceptor
        self.preview.settings().setAttribute(
            self.preview.settings().WebAttribute.JavascriptEnabled, True
        )
        self.preview.settings().setAttribute(
            self.preview.settings().WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        self.preview.settings().setAttribute(
            self.preview.settings().WebAttribute.LocalContentCanAccessFileUrls, True
        )

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
        # html = self.replace_asset_links(html)
        styled_html = self._apply_html_template(html)
        self.preview.setHtml(styled_html, QUrl("note://"))

    def _get_css_resources(self) -> str:
        """Generate CSS link tags for all CSS files in resources

        If the file:

        ./static/static.qrc

        picked up the static css asset, then it will be included.

        """
        css_links = []
        it = QDirIterator(":/css", QDir.Files, QDirIterator.Subdirectories)
        while it.hasNext():
            file_path = it.next()
            css_links.append(f'<link rel="stylesheet" href="qrc{file_path}">')

        # If needed to debug
        # print(css_links)
        # sys.exit()

        return "\n".join(css_links)

    def _apply_html_template(self, html: str) -> str:
        css_includes = self._get_css_resources()
        # print(html)
        return f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            <link rel="stylesheet" href="qrc:/katex/katex.min.css">
            {css_includes}
        </head>
        <body><div class="markdown">
            {html}
            </div>
            <script src="qrc:/katex/katex.min.js"></script>
            <script src="qrc:/katex/contrib/auto-render.min.js"></script>
            <script src="qrc:/katex/config.js"></script>
        </body>
        </html>
        """

    def update_preview_local(self):
        # Convert markdown to HTML
        md = markdown.Markdown(
            extensions=[
                "fenced_code",
                "tables",
                "footnotes",
                WikiLinkExtension(
                    base_url=""
                ),  # TODO this is inconsistent, consider using scheme handler and prefixing with a url
            ]
        )

        html = md.convert(self.editor.toPlainText())
        # html = self.replace_asset_links(html)
        styled_html = self._apply_html_template(html)
        self.preview.setHtml(styled_html, QUrl("note://"))

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

    def set_view_actions(
        self, maximize_editor_action, maximize_preview_action, remote_rendering_action
    ):
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
