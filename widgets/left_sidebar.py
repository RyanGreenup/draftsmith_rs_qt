from PySide6.QtWidgets import QTreeView, QWidget, QVBoxLayout, QComboBox, QMenu
from PySide6.QtCore import Qt
from .notes_tree import NotesTreeWidget
from .search_sidebar import SearchSidebar
from models.notes_tree_model import NotesTreeModel, TreeNode
from api.client import TreeNote


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
                
                # Add promote action if the item has a parent
                if node.parent and node.parent != model.root_node:
                    promote_action = menu.addAction("Promote")
                
                # Add demote action if there's a next sibling
                next_sibling = self._get_next_sibling(model, index)
                demote_action = menu.addAction("Demote")
                if not next_sibling:
                    demote_action.setEnabled(False)
                
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
            elif action == promote_action:
                self._promote_item(model, node, index)
            elif action == demote_action:
                self._demote_item(model, node, index)
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
                # Handle root-level note creation (All Notes and Untagged Notes sections)
                response = model.note_api.note_create("", "")
                tree_note = TreeNote(
                    id=response['id'],
                    title=response.get('title', ''),
                    tags=[],
                    children=[],
                    content=''
                )
                
                # Find special nodes
                all_notes_node = None
                untagged_notes_node = None
                for node in model.root_node.children:
                    if node.node_type == 'page':
                        if node.data["name"] == "All Notes":
                            all_notes_node = node
                        elif node.data["name"] == "Untagged Notes":
                            untagged_notes_node = node
                
                # Add to All Notes
                if all_notes_node:
                    new_node = TreeNode(tree_note, None, 'note')
                    new_index = model.insert_node(new_node, all_notes_node)
                
                # Add to Untagged Notes
                if untagged_notes_node:
                    new_node = TreeNode(tree_note, None, 'note')
                    new_index = model.insert_node(new_node, untagged_notes_node)
                    
                    # Focus the new note in Untagged Notes section
                    self.tags_tree.setCurrentIndex(new_index)
                    self.tags_tree.setFocus()
                
                return
                
            # Handle all other cases
            target_parent = parent_node if is_child else model.root_node
            
            if creating_note:
                response = model.note_api.note_create("", "")
                tree_note = TreeNote(
                    id=response['id'],
                    title=response.get('title', ''),
                    tags=[],
                    children=[],
                    content=''
                )
                new_node = TreeNode(tree_note, None, 'note')
                
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
                new_node = TreeNode(new_tag, None, 'tag')
                
                if parent_node and parent_node.node_type == 'tag':
                    model.tag_api.attach_tag_to_parent(
                        new_tag.id,
                        parent_node.data.id
                    )
            
            # Insert node in sorted position
            new_index = model.insert_node(new_node, target_parent)
            self.tags_tree.setCurrentIndex(new_index)
            self.tags_tree.setFocus()
                
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to create item: {str(e)}")

    def _promote_item(self, model, node, index):
        """Handle promotion of items to their grandparent level"""
        try:
            current_parent = node.parent
            grandparent = current_parent.parent if current_parent else None
            
            # First remove from current parent
            parent_index = model.parent(index)
            model.beginRemoveRows(parent_index, index.row(), index.row())
            current_parent.children.remove(node)
            model.endRemoveRows()
            
            if node.node_type == 'tag':
                # Detach from current parent
                model.tag_api.detach_tag_from_parent(node.data.id)
                
                # Attach to grandparent if it exists and is a tag
                if grandparent and grandparent != model.root_node and grandparent.node_type == 'tag':
                    model.tag_api.attach_tag_to_parent(node.data.id, grandparent.data.id)
                    new_index = model.insert_node(node, grandparent)
                else:
                    # If no valid grandparent, move to root level
                    new_index = model.insert_node(node, model.root_node)
                    
            else:  # note
                # Detach from current parent
                model.note_api.detach_note_from_parent(node.data.id)
                
                # Get current note's tags
                note_tags = node.data.tags if hasattr(node.data, 'tags') else []
                
                if grandparent and grandparent != model.root_node and grandparent.node_type == 'note':
                    # Attach to grandparent note
                    model.note_api.attach_note_to_parent(
                        node.data.id,
                        grandparent.data.id,
                        hierarchy_type="block"
                    )
                    new_index = model.insert_node(node, grandparent)
                else:
                    # If the note has tags, find the appropriate tag node(s)
                    tag_nodes = []
                    if note_tags:
                        def find_tag_nodes(search_node, tag_ids):
                            if search_node.node_type == 'tag' and hasattr(search_node.data, 'id'):
                                if search_node.data.id in tag_ids:
                                    tag_nodes.append(search_node)
                            for child in search_node.children:
                                find_tag_nodes(child, tag_ids)
                        
                        tag_ids = [tag.id for tag in note_tags]
                        find_tag_nodes(model.root_node, tag_ids)
                        
                        # Add note under each of its tag nodes
                        for tag_node in tag_nodes:
                            new_index = model.insert_node(node, tag_node)
                    
                    # Also add to "Untagged Notes" if no tags
                    if not note_tags:
                        untagged_notes_node = None
                        for child in model.root_node.children:
                            if child.node_type == 'page' and child.data["name"] == "Untagged Notes":
                                untagged_notes_node = child
                                break
                        
                        if untagged_notes_node:
                            new_index = model.insert_node(node, untagged_notes_node)
                    
                    # Always add to "All Notes" section
                    all_notes_node = None
                    for child in model.root_node.children:
                        if child.node_type == 'page' and child.data["name"] == "All Notes":
                            all_notes_node = child
                            break
                    
                    if all_notes_node:
                        new_index = model.insert_node(node, all_notes_node)
                
                # Select the promoted item in its new location
                if new_index:
                    self.tags_tree.setCurrentIndex(new_index)
                    self.tags_tree.setFocus()
            
        except Exception as e:
            # If anything fails, try to revert to original position
            if current_parent:
                new_index = model.insert_node(node, current_parent)
            raise Exception(f"Failed to promote item: {str(e)}")

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

    def _get_next_sibling(self, model, index):
        """Get the next sibling node in the tree"""
        parent = model.parent(index)
        next_row = index.row() + 1
        next_index = model.index(next_row, 0, parent)
        
        if next_index.isValid():
            return next_index.internalPointer()
        return None

    def _demote_item(self, model, node, index):
        """Handle demotion of items to become children of their next sibling"""
        try:
            # Get the next sibling
            next_sibling = self._get_next_sibling(model, index)
            if not next_sibling:
                return
            
            current_parent = node.parent
            
            # First remove from current parent
            parent_index = model.parent(index)
            model.beginRemoveRows(parent_index, index.row(), index.row())
            current_parent.children.remove(node)
            model.endRemoveRows()
            
            if node.node_type == 'tag':
                # Detach from current parent if it's a tag
                if current_parent and current_parent.node_type == 'tag':
                    model.tag_api.detach_tag_from_parent(node.data.id)
                
                # Attach to new parent (tag or note)
                model.tag_api.attach_tag_to_parent(
                    node.data.id,
                    next_sibling.data.id
                )
                new_index = model.insert_node(node, next_sibling)
                    
            else:  # note
                # Detach from current parent if it's a note
                if current_parent and current_parent.node_type == 'note':
                    model.note_api.detach_note_from_parent(node.data.id)
                
                # Attach to new parent
                model.note_api.attach_note_to_parent(
                    node.data.id,
                    next_sibling.data.id,
                    hierarchy_type="block"
                )
                new_index = model.insert_node(node, next_sibling)
            
            # Select the demoted item in its new location
            self.tags_tree.setCurrentIndex(new_index)
            self.tags_tree.setFocus()
            
        except Exception as e:
            # If anything fails, try to revert to original position
            new_index = model.insert_node(node, current_parent)
            raise Exception(f"Failed to demote item: {str(e)}")

    def focus_search(self):
        """Focus the search input and switch to search view"""
        self.tree_selector.setCurrentText("Search")
        self.search_sidebar.search_input.setFocus()
