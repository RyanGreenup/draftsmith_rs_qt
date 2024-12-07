# pyright: reportUnusedImport=false
from . import static_resources_rc  # type: ignore
from . import katex_resources_rc  # type: ignore
from . import katex_fonts_rc  # type: ignore

from PySide6.QtWebEngineCore import (
    QWebEnginePage,
    QWebEngineUrlRequestInfo,
    QWebEngineUrlRequestInterceptor,
    QWebEngineUrlScheme,
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


# Register custom schemes for the Web Engine Preview
def register_scheme(
    scheme_name: str,
    scheme_flags=(
        QWebEngineUrlScheme.Flag.LocalAccessAllowed
        | QWebEngineUrlScheme.Flag.CorsEnabled
    ),
):
    scheme = QWebEngineUrlScheme(scheme_name.encode())
    scheme.setSyntax(QWebEngineUrlScheme.Syntax.Path)
    scheme.setFlags(scheme_flags)
    QWebEngineUrlScheme.registerScheme(scheme)


register_scheme("note")
register_scheme("qrc")


class AssetUrlInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None, base_api_url=None, access_token=None):
        super().__init__(parent)
        self.base_api_url = base_api_url
        self.access_token = access_token

    def interceptRequest(self, info: QWebEngineUrlRequestInfo):
        url = info.requestUrl()
        path = url.path()

        # print(f"Intercepted URL: {url.toString()}")  # Debug print

        if path.startswith("/m/"):
            asset_path = path[3:]  # Remove /m/ prefix
            new_url = f"{self.base_api_url}/assets/download/{asset_path}"
            # print(f"Redirecting to: {new_url}")  # Debug print

            # Add Authorization header with access token
            if self.access_token:
                info.setHttpHeader(
                    b"Authorization", f"Bearer {self.access_token}".encode()
                )

            info.redirect(QUrl(new_url))


class NoteLinkPage(QWebEnginePage):
    def __init__(self, md_editor_widget, profile):
        super().__init__(profile, md_editor_widget)  # Set parent
        self.md_editor_widget = md_editor_widget  # Store correct reference

    def acceptNavigationRequest(self, url: QUrl | str, type, isMainFrame):
        if isinstance(url, str):
            url = QUrl(url)
        # print("-----------------------")
        # print(f"Navigation request: {url}")  # Debug print
        # print(f"Navigation request: {url.scheme()}")  # Debug print
        # print(f"Navigation request: {url.path()}")  # Debug print
        # print(".....................")

        if url.scheme() == "note":
            path = ""
            try:
                path = url.path().strip("/")
                note_id = int(path)
                # print(f"Emitting note_selected for ID: {note_id}")
                self.md_editor_widget.note_selected.emit(note_id)  # Use widget signal
                return False  # Prevent navigation
            except ValueError:
                print(f"Failed to parse note ID from: {path}")
                return False
        return True


class MarkdownEditor(QWidget):
    save_requested = Signal()
    preview_requested = Signal()  # Pull the initial preview
    render_requested = Signal(str)  # Send up the content and get back the rendered HTML
    note_selected = Signal(int)  # Emitted when a note link is clicked

    def __init__(self, api_url: str, parent=None):
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
        self.asset_interceptor = AssetUrlInterceptor(
            self,
            base_api_url=api_url,
            access_token=None,  # TODO Will need to be set later via a method
        )
        self.profile.setUrlRequestInterceptor(self.asset_interceptor)

        # Create preview with custom link handling
        self.preview = QWebEngineView()
        self.current_scroll_position = self.preview.page().scrollPosition()
        self.preview.setPage(
            NoteLinkPage(self, self.profile)
        )  # Pass self (MarkdownEditor) instead of preview

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

    def _get_scroll_position(self):
        self.preview.page().runJavaScript(
            "window.scrollY",
            self._update_preview_with_scroll
        )

    def _update_preview_with_scroll(self, scroll_pos):
        self._last_scroll = scroll_pos
        if self._remote_rendering_action and self._remote_rendering_action.isChecked():
            self.render_requested.emit(self.editor.toPlainText())
        else:
            self.update_preview_local()

    def on_text_changed(self):
        """
        Sync the Preview with the Editor
        """
        # Start the update timer to prevent too frequent updates
        self.update_timer.start(500)  # 500ms delay



    def update_preview(self):
        """
        Update the preview with a new note
        """
        self._get_scroll_position()  # This will trigger the update chain through _update_preview_with_scroll

    def set_preview_content(self, html: str):
        styled_html = self._apply_html_template(html)
        self.preview.loadFinished.connect(
            lambda: self.preview.page().runJavaScript(
                f"window.scrollTo(0, {getattr(self, '_last_scroll', 0)});"
            )
        )
        self.preview.setHtml(styled_html, QUrl("note:/"))

    def _get_css_resources(self) -> str:
        """Generate CSS link tags for all CSS files in resources

        If the file:

        ./static/static.qrc

        picked up the static css asset, then it will be included.

        """
        css_links = []
        it = QDirIterator(
            ":/css", QDir.Filter.Files, QDirIterator.IteratorFlag.Subdirectories
        )
        while it.hasNext():
            file_path = it.next()
            css_links.append(f'<link rel="stylesheet" href="qrc{file_path}">')

        # If needed to debug
        # print(css_links)
        # sys.exit()

        return "\n".join(css_links)

    def _apply_html_template(self, html: str) -> str:
        css_includes = self._get_css_resources()
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
        styled_html = self._apply_html_template(html)
        self.preview.loadFinished.connect(
            lambda: self.preview.page().runJavaScript(
                f"window.scrollTo(0, {getattr(self, '_last_scroll', 0)});"
            )
        )
        self.preview.setHtml(styled_html, QUrl("note:/"))

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
