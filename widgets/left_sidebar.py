from PySide6.QtWidgets import QTreeView, QWidget, QVBoxLayout, QComboBox, QMenu
from PySide6.QtCore import Qt
from .notes_tree import NotesTreeWidget
from .search_sidebar import SearchSidebar
from models.notes_tree_model import NotesTreeModel


class LeftSidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tree = NotesTreeWidget()
        self.tags_tree = QTreeView()
        model = NotesTreeModel(self)
        self.tags_tree.setModel(model)
        
        # Add context menu support
        self.tags_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tags_tree.customContextMenuRequested.connect(self._show_tags_context_menu)
        
        self.search_sidebar = SearchSidebar()
        self.tree_selector = QComboBox()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.tree.setHeaderLabel("Notes")
        self.tree.setMinimumWidth(100)

        self.tags_tree.setMinimumWidth(100)
        self.tags_tree.hide()  # Initially hidden

        self.search_sidebar.hide()  # Initially hidden

        self.tree_selector.addItems(["Notes", "Tags", "Search"])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tree_selector)
        layout.addWidget(self.tree)
        layout.addWidget(self.tags_tree)
        layout.addWidget(self.search_sidebar)

    def _connect_signals(self):
        self.tree_selector.currentTextChanged.connect(self._on_tree_selection_changed)

    def _on_tree_selection_changed(self, text):
        if text == "Notes":
            self.tree.show()
            self.tags_tree.hide()
            self.search_sidebar.hide()
        elif text == "Tags":
            self.tree.hide()
            self.tags_tree.show()
            self.search_sidebar.hide()
        else:  # Search
            self.tree.hide()
            self.tags_tree.hide()
            self.search_sidebar.show()

    def _show_tags_context_menu(self, position):
        index = self.tags_tree.indexAt(position)
        if not index.isValid():
            return
            
        # Get the node to check its type
        node = index.internalPointer()
        if node.node_type == 'page':
            return  # Don't show menu for special items
            
        menu = QMenu(self)
        rename_action = menu.addAction("Rename")
        delete_action = menu.addAction("Delete")
        
        # Show context menu at cursor position
        action = menu.exec_(self.tags_tree.viewport().mapToGlobal(position))
        
        if action == rename_action:
            self.tags_tree.edit(index)
        elif action == delete_action:
            model = self.tags_tree.model()
            try:
                if node.node_type == 'tag':
                    model.tag_api.delete_tag(node.data.id)
                else:  # note
                    model.note_api.delete_note(node.data.id)
                
                # Remove the item from the model
                parent_index = model.parent(index)
                model.beginRemoveRows(parent_index, index.row(), index.row())
                node.parent.children.remove(node)
                model.endRemoveRows()
                
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"Failed to delete item: {str(e)}")

    def focus_search(self):
        """Focus the search input and switch to search view"""
        self.tree_selector.setCurrentText("Search")
        self.search_sidebar.search_input.setFocus()
