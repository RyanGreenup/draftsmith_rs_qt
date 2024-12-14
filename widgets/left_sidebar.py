from PySide6.QtWidgets import QTreeView, QWidget, QVBoxLayout, QComboBox, QMenu
from PySide6.QtCore import Qt
from .notes_tree import NotesTreeWidget
from .search_sidebar import SearchSidebar
from models.notes_tree_model import NotesTreeModel, TreeNode


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
            # Existing item selected - show full menu
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
            
            # Add "New Note Under Tag" option when right-clicking a tag
            new_note_under_tag_action = None
            if node and node.node_type == 'tag':
                menu.addSeparator()
                new_note_under_tag_action = menu.addAction("New Note Under Tag")
        else:
            # No item selected - show simplified menu
            new_tag_action = menu.addAction("New Tag")
            new_note_action = menu.addAction("New Note")
        
        # Show context menu at cursor position
        action = menu.exec_(self.tags_tree.viewport().mapToGlobal(position))
        
        try:
            if not index.isValid():
                # Handle root level actions with simplified menu
                if action == new_tag_action:
                    self._create_new_item(model, None, is_child=False)
                elif action == new_note_action:
                    self._create_new_item(model, None, is_child=False, force_note=True)
                return
                
            # Handle actions for existing items
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
            elif action == new_note_under_tag_action:
                self._create_new_item(model, node, is_child=True, force_note=True)
                
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Operation failed: {str(e)}")

    def _create_new_item(self, model, parent_node, is_child, force_note=False):
        """Handle creation of new items"""
        from PySide6.QtWidgets import QInputDialog
        from PySide6.QtCore import QModelIndex
        
        creating_note = force_note or (parent_node and parent_node.node_type == 'note')
        
        title = None
        if not creating_note:
            title, ok = QInputDialog.getText(
                self,
                "New Tag",
                "Enter tag name:"
            )
            if not ok or not title.strip():
                return
                
        try:
            if creating_note and not parent_node:
                # Find "All Notes" and "Untagged Notes" nodes
                all_notes_node = None
                untagged_notes_node = None
                for i in range(model.root_node.child_count()):
                    node = model.root_node.child(i)
                    if node.node_type == 'page':
                        if node.data["name"] == "All Notes":
                            all_notes_node = node
                        elif node.data["name"] == "Untagged Notes":
                            untagged_notes_node = node

                # Create the note and convert response to TreeNote
                response = model.note_api.note_create("", "")
                tree_note = TreeNote(
                    id=response['id'],
                    title=response.get('title', ''),
                    tags=[],
                    children=[],
                    content=''
                )
                
                # Add to All Notes
                if all_notes_node:
                    insert_pos = all_notes_node.child_count()
                    parent_index = model.createIndex(all_notes_node.row(), 0, all_notes_node)
                    model.beginInsertRows(parent_index, insert_pos, insert_pos)
                    new_node = TreeNode(tree_note, all_notes_node, 'note')
                    all_notes_node.append_child(new_node)
                    model.endInsertRows()
                
                # Add to Untagged Notes
                if untagged_notes_node:
                    insert_pos = untagged_notes_node.child_count()
                    parent_index = model.createIndex(untagged_notes_node.row(), 0, untagged_notes_node)
                    model.beginInsertRows(parent_index, insert_pos, insert_pos)
                    new_node = TreeNode(tree_note, untagged_notes_node, 'note')
                    untagged_notes_node.append_child(new_node)
                    model.endInsertRows()
                    
                    # Focus the new note in Untagged Notes section
                    new_index = model.createIndex(insert_pos, 0, new_node)
                    self.tags_tree.setCurrentIndex(new_index)
                    self.tags_tree.setFocus()
                
                return

            # Handle all other cases (tags or notes with parents) as before
            target_parent = parent_node if is_child else model.root_node
            if not target_parent:
                target_parent = model.root_node
                
            parent_index = model.createIndex(target_parent.row(), 0, target_parent) if target_parent != model.root_node else QModelIndex()
            insert_position = target_parent.child_count()
            
            model.beginInsertRows(parent_index, insert_position, insert_position)
            
            if creating_note:
                response = model.note_api.note_create("", "")
                tree_note = TreeNote(
                    id=response['id'],
                    title=response.get('title', ''),
                    tags=[],
                    children=[],
                    content=''
                )
                new_node = TreeNode(tree_note, target_parent, 'note')
                
                if parent_node:
                    if parent_node.node_type == 'tag':
                        model.tag_api.attach_tag_to_note(tree_note.id, parent_node.data.id)
                    else:
                        model.note_api.attach_note_to_parent(
                            tree_note.id,
                            parent_node.data.id,
                            hierarchy_type="block"
                        )
            else:
                new_tag = model.tag_api.create_tag(title)
                new_node = TreeNode(new_tag, target_parent, 'tag')
                
                if parent_node and parent_node.node_type == 'tag':
                    model.tag_api.attach_tag_to_parent(
                        new_tag.id,
                        parent_node.data.id
                    )
            
            target_parent.append_child(new_node)
            model.endInsertRows()
            
            new_index = model.createIndex(insert_position, 0, new_node)
            self.tags_tree.setCurrentIndex(new_index)
            self.tags_tree.setFocus()
                
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
