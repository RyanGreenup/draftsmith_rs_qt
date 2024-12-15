from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QSplitter, QLineEdit
from pydantic import BaseModel, Field
from PySide6.QtCore import Signal, Qt, QBuffer, QByteArray, QIODevice
from PySide6.QtNetwork import QNetworkRequest
from PySide6.QtGui import QAction
from PySide6.QtWebEngineCore import QWebEngineUrlRequestJob
from typing import Literal, Optional, Dict
from pydantic import BaseModel

import requests
from models.note import Note
from widgets.left_sidebar import LeftSidebar
from widgets.markdown_editor import MarkdownEditor
from widgets.right_sidebar import RightSidebar
from models.notes_model import NotesModel
from models.navigation_model import NavigationModel
from widgets.note_select_palette import NoteSelectPalette
import api
from app_types import HierarchyLevel


class TabContent(QWidget):
    """A complete view implementation for a note"""

    note_saved = Signal(int)  # Emits note_id when saved
    filter_text_entered = Signal(str)  # Add this new signal

    def __init__(self, base_url: str, parent=None):
        super().__init__(parent)
        self.current_note_id: Optional[int] = None
        self.notes_model: Optional[NotesModel] = None
        self.navigation_model: Optional[NavigationModel] = None
        self.view_actions: Optional[Dict[str, QAction]] = None
        self.base_url = base_url
        self.note_select_palette = None  # Will be initialized when model is set
        self.note_link_palette = None  # Will be initialized when needed

        # Create components
        self.left_sidebar = LeftSidebar()
        self.right_sidebar = RightSidebar()
        # Create the MarkdownEditor Region
        self.editor = MarkdownEditor(self.base_url)
        # NOTE this has:
        # .editor: QTextEdit
        # .preview: QWebEngineView

        # Add the new QLineEdit
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter text...")

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the UI layout"""
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create a container for left sidebar and text input
        left_container = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self.text_input)
        left_layout.addWidget(self.left_sidebar)
        left_container.setLayout(left_layout)

        main_splitter.addWidget(left_container)
        main_splitter.addWidget(self.editor)
        main_splitter.addWidget(self.right_sidebar)

        # Set default sizes
        main_splitter.setSizes([200, 600, 200])


        layout = QVBoxLayout()
        layout.addWidget(main_splitter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def _connect_signals(self):
        """Connect internal signals"""
        # Connect text input to filtering
        self.text_input.textChanged.connect(self.filter_sidebar)

        # Add connection for note deletion
        # What to do when the user has asked to delete a note
        self.left_sidebar.tree.note_deleted.connect(self._handle_note_deletion)
        # After the note has been deleted, make sure to clear the view if needed
        if self.notes_model:
            self.notes_model.note_deleted.connect(self._handle_note_deleted_signal)

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

    def set_model(self, notes_model: NotesModel):
        """Connect this view to the model"""
        self.notes_model = notes_model
        self.left_sidebar.tree.set_model(notes_model)
        # Connect note selection to view updates, but only when this tab is active
        self.notes_model.note_selected.connect(self._filtered_update_view)
        # Connect tree model's note_updated signal to notes_model's note_updated signal
        self.left_sidebar.tags_tree.model.note_updated.connect(self.notes_model.note_updated.emit)
        # Initialize palettes with view actions
        self.note_select_palette = NoteSelectPalette(notes_model, self)
        # Initialize note link palette
        from widgets.note_id_link_insert import NoteLinkInsertPalette

        self.note_link_palette = NoteLinkInsertPalette(notes_model, self)

    def _filtered_update_view(self, selection_data):
        """Only update view if this tab is currently active"""
        tab_widget = self.parent()
        if tab_widget and tab_widget.currentWidget() == self:
            self._update_view(selection_data)

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

    def _handle_save_request(self, note_id: int):
        """Internal handler for save requests"""
        # Store current cursor position and tree state before save
        cursor = self.editor.editor.textCursor()
        cursor_position = cursor.position()
        tree_state = self.left_sidebar.tree.save_state()

        content = self.editor.get_content()
        if self.notes_model:
            # Store current note ID before save
            current_note_id = self.get_current_note_id()
            if self.notes_model.update_note(note_id, content=content):
                # After model refresh, restore UI state
                if current_note_id is not None:
                    # Restore tree state first
                    self.left_sidebar.tree.restore_state(tree_state)
                    # Then restore note selection and cursor
                    self.set_current_note(current_note_id)
                    cursor = self.editor.editor.textCursor()
                    cursor.setPosition(cursor_position)
                    self.editor.editor.setTextCursor(cursor)
                self.note_saved.emit(note_id)

    def _update_right_sidebar(self, selection_data):
        """Update right sidebar content when a note is selected"""
        if selection_data.note:
            self.current_note_id = selection_data.note.id
            self.right_sidebar.update_forward_links(selection_data.forward_links)
            self.right_sidebar.update_backlinks(selection_data.backlinks)
            self.right_sidebar.update_tags(selection_data.tags)

    def _handle_preview_request(self, content: Optional[str] = None):
        """Handle request to update preview using streaming response"""

        class RenderMarkdownRequest(BaseModel):
            """Request to render markdown content"""

            content: str
            format: Optional[Literal["text", "html", "pdf"]] = None

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
                        stream=True,  # Enable streaming
                    )
                else:
                    response = requests.get(
                        f"{self.base_url}/notes/flat/{note_id}/render/{format}",
                        headers={"Content-Type": "application/json"},
                        stream=True,  # Enable streaming
                    )

                response.raise_for_status()

                # Create a QBuffer to accumulate streamed content
                buffer = QByteArray()

                # Stream and accumulate the response content
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        buffer.append(chunk)
                        # Update preview with accumulated content so far
                        html = buffer.data().decode("utf-8")
                        self.editor.set_preview_content(html)

            except Exception as e:
                print(f"Error getting rendered note: {e}")
                # Fall back to local preview
                self.editor.update_preview_local()

    def get_current_note_id(self) -> Optional[int]:
        """Get the currently displayed note ID"""
        return self.current_note_id

    def focus_search(self):
        """Focus the search input in the left sidebar of this tab"""
        self.left_sidebar.focus_search()

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

    def _handle_note_deletion(self, maybe_note_id: Optional[int] = None):
        """Handle note deletion request

        Deletes the item in the tree unless an int is passed, then it deletes the note with that id
        """
        if maybe_note_id is None:
            current_item = self.left_sidebar.tree.currentItem()
            if not current_item:
                return
            note_id = current_item.data(0, Qt.ItemDataRole.UserRole).id
        else:
            note_id = maybe_note_id
            current_item = None

        try:
            if self.notes_model:
                # If we're deleting the currently selected item, select the one above first
                if (
                    current_item
                    and current_item.data(0, Qt.ItemDataRole.UserRole).id == note_id
                ):
                    self.left_sidebar.tree.select_item_above()
                # Delete the note through the model
                self.notes_model.delete_note(note_id)

        except Exception as e:
            print(f"Error deleting note: {e}")

    def _handle_note_deleted_signal(self, deleted_note_id: int):
        """Handle when a note is deleted by clearing view if needed"""
        # TODO this does not work and nothing is selected
        if self.current_note_id == deleted_note_id:
            # Clear the editor if this was the current note
            # (though the note_deleted signal handler should handle this)
            if self.current_note_id == deleted_note_id:
                # Get the previous item in the tree
                if (
                    item := self.left_sidebar.tree.currentItem()
                    .parent()
                    .data(0, Qt.ItemDataRole.UserRole)
                ):
                    self.current_note_id = item.id
                else:
                    self.current_note_id = None
                    self.editor.set_content("")

    def show_note_select_palette(self):
        """Show the note selection palette"""
        if self.notes_model and self.note_select_palette:
            self.note_select_palette.show_palette()

    def show_note_link_palette(self) -> None:
        """Show the note link insertion palette"""
        if self.note_link_palette:
            self.note_link_palette.show_palette()

    def cut_selected_tree_item(self) -> None:
        """Cut the currently selected item in the tree"""
        current_item = self.left_sidebar.tree.currentItem()
        if current_item:
            self.left_sidebar.tree._handle_cut(current_item)

    def paste_onto_selected_tree_item(self) -> None:
        """Paste the previously cut item onto the currently selected tree item"""
        current_item = self.left_sidebar.tree.currentItem()
        if current_item:
            self.left_sidebar.tree._handle_paste(current_item)

    def promote_selected_tree_item(self) -> bool:
        """
        Promote the currently selected item in the tree.
        Returns True if promotion was successful, False otherwise.
        """
        current_item = self.left_sidebar.tree.currentItem()
        if current_item:
            return self.left_sidebar.tree.promote_note(current_item)
        return False

    def demote_selected_tree_item(self) -> bool:
        """
        Demote the currently selected item in the tree.
        Returns True if demotion was successful, False otherwise.
        """
        current_item = self.left_sidebar.tree.currentItem()
        if current_item:
            return self.left_sidebar.tree.demote_note(current_item)
        return False

    def filter_sidebar(self, text: str) -> None:
        """Filter the sidebar tree based on entered text"""
        # Get the tree model directly from the left sidebar's tree
        tree_model = self.left_sidebar.tags_tree.model

        # If using a proxy model, get the source model
        if hasattr(tree_model, 'sourceModel') and callable(tree_model.sourceModel):
            tree_model = tree_model.sourceModel()

        if hasattr(tree_model, 'filter_tree'):
            tree_model.filter_tree(text)
        else:
            print("Warning: Tree model does not support filtering")

    def handle_new_note_request(self, level: HierarchyLevel) -> Note | None:
        # Typically, we would act on the id of the view, however
        # the user will want to rapidly create notes based on the tree but have the keybindings described in the menu
        # rather than the complexity of keybindings for the tree and the view when rarely will a user want to create a child
        # of the viewed note, usually they will want to create a child/sibling based on the item selected in the tree
        # This would be the note_id of the view:
        # note_id = self.get_current_note_id()

        parent_id = None
        match level:
            case level.ROOT:
                parent_id = None
            case level.CHILD:
                # This is the view of the UI, use the tree
                # parent_id = self.get_current_note_id()
                parent_id = (
                    self.left_sidebar.tree.currentItem()
                    .data(0, Qt.ItemDataRole.UserRole)
                    .id
                )
            case level.SIBLING:
                # Get from the tree
                parent_id = (
                    self.left_sidebar.tree.currentItem()
                    .parent()
                    .data(0, Qt.ItemDataRole.UserRole)
                    .id
                )

        # Create new note
        if self.notes_model:
            new_note = self.notes_model.create_note(
                title="New Note", content="", parent_id=parent_id
            )

            if new_note:
                # Select the new note in tree
                self.left_sidebar.tree.select_note_by_id(new_note.id)
            return new_note
