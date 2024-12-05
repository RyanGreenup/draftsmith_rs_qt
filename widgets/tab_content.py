from PySide6.QtWidgets import QWidget, QSplitter
from pydantic import BaseModel, Field
from PySide6.QtCore import Signal, Qt, QBuffer, QByteArray, QIODevice
from PySide6.QtNetwork import QNetworkRequest
from PySide6.QtGui import QAction
from PySide6.QtWebEngineCore import QWebEngineUrlRequestJob
from typing import Literal, Optional, Dict

import requests
from widgets.left_sidebar import LeftSidebar
from widgets.markdown_editor import MarkdownEditor
from widgets.right_sidebar import RightSidebar
from models.notes_model import NotesModel
from models.navigation_model import NavigationModel
import api


class TabContent(QWidget):
    """A complete view implementation for a note"""

    note_saved = Signal(int)  # Emits note_id when saved

    def __init__(self, parent=None):
        super().__init__(parent)
        # Instance variables for asset streaming
        self._current_response = None
        self._current_stream_device = None
        self._asset_cache = {}  # Cache for asset responses

        self.current_note_id: Optional[int] = None
        self.notes_model: Optional[NotesModel] = None
        self.navigation_model: Optional[NavigationModel] = None
        self.view_actions: Optional[Dict[str, QAction]] = None

        # Create components
        self.left_sidebar = LeftSidebar()
        self.right_sidebar = RightSidebar()
        # Create the MarkdownEditor Region
        self.editor = MarkdownEditor()
        # NOTE this has:
        # .editor: QTextEdit
        # .preview: QWebEngineView

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the UI layout"""
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(self.left_sidebar)
        main_splitter.addWidget(self.editor)
        main_splitter.addWidget(self.right_sidebar)

        # Set default sizes
        main_splitter.setSizes([200, 600, 200])

        # Add to layout
        from PySide6.QtWidgets import QVBoxLayout

        layout = QVBoxLayout()
        layout.addWidget(main_splitter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def _connect_signals(self):
        """Connect internal signals"""
        # Editor signals
        self.editor.save_requested.connect(self._handle_save_request)

        # Connect view update signals directly to model
        self.right_sidebar.forward_links.note_selected.connect(
            self._handle_view_request
        )
        self.right_sidebar.forward_links.note_selected_with_focus.connect(
            self._handle_view_request_with_focus
        )
        self.right_sidebar.backlinks.note_selected.connect(self._handle_view_request)
        self.right_sidebar.backlinks.note_selected_with_focus.connect(
            self._handle_view_request_with_focus
        )
        self.right_sidebar.tags.note_selected.connect(self._handle_view_request)

        # Left sidebar signals
        self.left_sidebar.tree.note_selected.connect(self._handle_view_request)
        self.left_sidebar.tree.note_selected_with_focus.connect(
            self._handle_view_request_with_focus
        )
        self.left_sidebar.search_sidebar.note_selected.connect(
            self._handle_view_request
        )
        self.left_sidebar.search_sidebar.note_selected_with_focus.connect(
            self._handle_view_request_with_focus
        )

        # Connect the Preview Request signal
        # These two are needed if the preview is being loaded from the API
        # This sends the QTextEdit content to the API for rendering
        self.editor.preview_requested.connect(self._handle_preview_request)
        # This pulls the note
        self.editor.render_requested.connect(self._handle_preview_request)
        # When user follows a link, it will change the view
        self.editor.note_selected.connect(self._handle_view_request)
        # Handle asset requests from preview pane
        self.editor.asset_requested.connect(self._handle_asset_request)

    def set_model(self, notes_model: NotesModel):
        """Connect this view to the model"""
        self.notes_model = notes_model
        self.left_sidebar.tree.set_model(notes_model)
        # Connect note selection to view updates
        self.notes_model.note_selected.connect(self._update_view)

    def set_navigation_model(
        self, navigation_model: NavigationModel, actions: Dict[str, QAction]
    ):
        """Set the navigation model for this tab"""
        self.navigation_model = navigation_model

        # Connect navigation model signals
        self.navigation_model.navigation_changed.connect(self._update_navigation_state)
        self.navigation_model.note_changed.connect(self._handle_navigation_change)

        # Store actions reference
        self.navigation_actions = actions

    def _update_navigation_state(self) -> None:
        """Update navigation button states"""
        if self.navigation_model:
            self.navigation_actions["back"].setEnabled(
                self.navigation_model.can_go_back()
            )
            self.navigation_actions["forward"].setEnabled(
                self.navigation_model.can_go_forward()
            )

    def _handle_navigation_change(self, note_id: int) -> None:
        """Handle note changes from navigation"""
        if self.notes_model and note_id is not None:
            # Update tree selection without triggering signals
            self.left_sidebar.tree.select_note_by_id(note_id, emit_signal=False)
            # Request view update directly from model
            self.notes_model.select_note(note_id)
            # Update navigation state
            self._update_navigation_state()

    def _handle_view_request(self, note_id: int) -> None:
        """Handle direct view update request"""
        if self.notes_model and note_id is not None:
            # Update tree selection without triggering signals
            self.left_sidebar.tree.select_note_by_id(note_id, emit_signal=False)
            # Update navigation history
            if self.navigation_model:
                self.navigation_model.add_to_history(note_id)
            # Request view update directly from model
            self.notes_model.select_note(note_id)

    def _handle_view_request_with_focus(self, note_id: int) -> None:
        """Handle view update request with editor focus"""
        self._handle_view_request(note_id)
        self.editor.editor.setFocus()

    def _update_view(self, selection_data):
        """Update entire view when note selection changes"""
        if selection_data.note:
            self.current_note_id = selection_data.note.id
            # Update editor content
            self.editor.set_content(selection_data.note.content)
            # Update right sidebar
            self._update_right_sidebar(selection_data)

    def _handle_save_request(self):
        """Internal handler for save requests"""
        current_item = self.left_sidebar.tree.currentItem()
        if current_item:
            note_data = current_item.data(0, Qt.ItemDataRole.UserRole)
            if note_data:
                content = self.editor.get_content()
                if self.notes_model.update_note(note_data.id, content=content):
                    self.note_saved.emit(note_data.id)

    def _update_right_sidebar(self, selection_data):
        """Update right sidebar content when a note is selected"""
        if selection_data.note:
            self.current_note_id = selection_data.note.id
            self.right_sidebar.update_forward_links(selection_data.forward_links)
            self.right_sidebar.update_backlinks(selection_data.backlinks)
            self.right_sidebar.update_tags(selection_data.tags)

    def _handle_preview_request(self, content: Optional[str] = None):
        """Handle request to update preview using current note
        If send_content is true, use the provided content for rendering.
        Otherwise pull the current note HTML from server.
        """

        class RenderMarkdownRequest(BaseModel):
            """Request to render markdown content"""

            content: str
            format: Optional[Literal["text", "html", "pdf"]] = None

        self.base_url = "http://eir:37242"
        if self.notes_model and (note_id := self.current_note_id) is not None:
            format = "html"
            try:
                if content is not None:
                    # Render the provided content

                    request = RenderMarkdownRequest(content=content, format=format)

                    response = requests.post(
                        f"{self.base_url}/render/markdown",
                        headers={"Content-Type": "application/json"},
                        data=request.model_dump_json(exclude_none=True),
                    )

                    response.raise_for_status()

                    html = response.text

                    self.editor.set_preview_content(html)
                else:

                    response = requests.get(
                        f"{self.base_url}/notes/flat/{note_id}/render/{format}",
                        headers={"Content-Type": "application/json"},
                    )

                    response.raise_for_status()

                    html = response.text

                    self.editor.set_preview_content(html)

            except Exception as e:
                print(f"Error getting rendered note: {e}")
                # Fall back to local preview
                self.editor.update_preview_local()

    def get_current_note_id(self) -> Optional[int]:
        """Get the currently displayed note ID"""
        return self.current_note_id

    def set_current_note(self, note_id: int) -> None:
        """Set the current note to display"""
        if self.notes_model and note_id is not None:
            self._handle_view_request(note_id)

    def set_view_actions(self, actions: Dict[str, QAction]):
        """Set view actions for the editor"""
        self.view_actions = actions
        self.editor.set_view_actions(
            actions["maximize_editor"],
            actions["maximize_preview"],
            actions["use_remote_rendering"],
        )

    def _handle_asset_request(self, asset_name: str, job: "QWebEngineUrlRequestJob"):
        """Handle requests for assets from the preview pane with proper caching support"""
        try:
            base_url = "http://eir:37242"

            # Get the Asset from the API with streaming enabled
            endpoint = (
                f"{base_url}/assets/download/{asset_name}"
                if isinstance(asset_name, str)
                else f"{base_url}/assets/{asset_name}"
            )

            # Store response as instance variable to prevent garbage collection
            self._current_response = requests.get(endpoint, stream=True)
            self._current_response.raise_for_status()

            # Get content type and other headers
            content_type = self._current_response.headers.get(
                "Content-Type", "application/octet-stream"
            )

            # Create the QWebEngineUrlRequestJob response headers
            headers = {
                QNetworkRequest.KnownHeaders.ContentTypeHeader: content_type,
                QNetworkRequest.KnownHeaders.ContentLengthHeader: int(
                    self._current_response.headers.get("content-length", 0)
                ),
                QNetworkRequest.KnownHeaders.LastModifiedHeader: self._current_response.headers.get(
                    "last-modified"
                ),
                QNetworkRequest.KnownHeaders.ETagHeader: self._current_response.headers.get(
                    "etag"
                ),
            }

            # Add Cache-Control as a raw header since it's not in KnownHeaders
            raw_headers = {b"Cache-Control": b"public, max-age=3600"}

            # Create streaming device as child of job to manage lifetime
            class StreamDevice(QIODevice):
                def __init__(self, response, parent=None):
                    super().__init__(parent)
                    self.response = response
                    self.iterator = response.iter_content(chunk_size=8192)

                def readData(self, maxSize):
                    try:
                        chunk = next(self.iterator, None)
                        return chunk if chunk is not None else bytes()
                    except Exception:
                        return bytes()

                def writeData(self, data):
                    return -1  # Read only device

                def bytesAvailable(self):
                    return super().bytesAvailable() + (
                        int(self.response.headers.get("content-length", 0))
                        if "content-length" in self.response.headers
                        else 0
                    )

            # Create streaming device with job as parent
            self._current_stream_device = StreamDevice(
                self._current_response, parent=job
            )
            if not self._current_stream_device.open(QIODevice.ReadOnly):
                print(f"Error: Could not open stream device for asset {asset_name}")
                job.fail(QWebEngineUrlRequestJob.Error.RequestFailed)
                return

            # Create buffer for response
            buffer = QByteArray()
            buffer.append(content_type.encode())

            # Send the streaming response with headers
            job.reply(buffer, self._current_stream_device)

        except Exception as e:
            print(f"Error fetching asset {asset_name}: {e}")
            job.fail(QWebEngineUrlRequestJob.Error.RequestFailed)
