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
        model = self.tags_tree.model()
        
        menu = QMenu(self)
        node = None
        
        if index.isValid():
            node = index.internalPointer()
            if node.node_type != 'page':  # Don't show edit options for special items
                rename_action = menu.addAction("Rename")
                delete_action = menu.addAction("Delete")
                menu.addSeparator()
        
        # Determine labels based on context
        if node and node.node_type == 'note':
            new_label = "New Note"
            child_label = "New Subpage"
            sibling_label = "New Sibling Page"
        else:
            new_label = "New Tag"
            child_label = "New Child Tag"
            sibling_label = "New Sibling Tag"
        
        new_action = menu.addAction(new_label)
        new_child_action = menu.addAction(child_label)
        new_sibling_action = menu.addAction(sibling_label)
        
        # Show context menu at cursor position
        action = menu.exec_(self.tags_tree.viewport().mapToGlobal(position))
        
        try:
            if not index.isValid():
                # Handle root level actions
                if action == new_action:
                    self._create_new_item(model, None, is_child=False)
                return
                
            if action == rename_action:
                self.tags_tree.edit(index)
            elif action == delete_action:
                self._delete_item(model, node, index)
            elif action == new_action:
                self._create_new_item(model, None, is_child=False)
            elif action == new_child_action:
                self._create_new_item(model, node, is_child=True)
            elif action == new_sibling_action:
                parent_node = node.parent
                self._create_new_item(model, parent_node, is_child=True)
                
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Operation failed: {str(e)}")

    def _create_new_item(self, model, parent_node, is_child):
        """Handle creation of new items"""
        from PySide6.QtWidgets import QInputDialog
        
        # Determine if we're creating a note or tag based on parent context
        creating_note = parent_node and parent_node.node_type == 'note'
        
        title, ok = QInputDialog.getText(
            self,
            f"New {'Note' if creating_note else 'Tag'}", 
            f"Enter {'note' if creating_note else 'tag'} name:"
        )
        
        if not ok or not title.strip():
            return
            
        try:
            if creating_note:
                # Create new note
                response = model.note_api.note_create(title, "")
                new_id = response['id']
                
                if parent_node:
                    model.note_api.attach_note_to_parent(
                        new_id,
                        parent_node.data.id,
                        hierarchy_type="block"
                    )
            else:
                # Create new tag
                new_tag = model.tag_api.create_tag(title)
                new_id = new_tag.id
                
                if parent_node and parent_node.node_type == 'tag':
                    model.tag_api.attach_tag_to_parent(
                        new_id,
                        parent_node.data.id
                    )
            
            # Refresh the model to show new items
            model.setup_data()
            
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to create item: {str(e)}")

    def _delete_item(self, model, node, index):
        """Handle deletion of items"""
        try:
            if node.node_type == 'tag':
                model.tag_api.delete_tag(node.data.id)
            else:  # note
                model.note_api.delete_note(node.data.id)
            
            parent_index = model.parent(index)
            model.beginRemoveRows(parent_index, index.row(), index.row())
            node.parent.children.remove(node)
            model.endRemoveRows()
            
        except Exception as e:
            raise Exception(f"Failed to delete item: {str(e)}")

    def focus_search(self):
        """Focus the search input and switch to search view"""
        self.tree_selector.setCurrentText("Search")
        self.search_sidebar.search_input.setFocus()
