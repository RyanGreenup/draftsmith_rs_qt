from PySide6.QtWidgets import QTreeView, QMenu, QInputDialog, QMessageBox
from PySide6.QtCore import Qt, QModelIndex
from models.notes_tree_model import NotesTreeModel, TreeNode
from api.client import TreeNote

class NotesTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = NotesTreeModel(self)
        self.setModel(self.model)

        # Set the view for the model
        self.model.set_view(self)
        self.model.tagMoved.connect(self._focus_moved_tag)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeView.DragDropMode.DragDrop)

        # Add context menu support
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_tags_context_menu)

    def _show_tags_context_menu(self, position):
        index = self.indexAt(position)

        # Get the base menu from the model
        menu = self.model.create_context_menu(index)

        if index.isValid():
            node = index.internalPointer()

            # Add Note ID label if this is a note
            if node.node_type == 'note':
                note_id_action = menu.addAction(f"Note ID: {node.data.id}")
                note_id_action.setEnabled(False)  # Make it non-clickable
                menu.addSeparator()

            if node.node_type != 'page':  # Don't show edit options for special items
                rename_action = menu.addAction("Rename")

                promote_action = None
                demote_action = None

                if node.node_type != 'page':  # Don't show edit options for special items
                    rename_action = menu.addAction("Rename")
                    delete_action = menu.addAction("Delete")

                    # Add promote action if the item has a parent
                    if node.parent and node.parent != self.model.root_node:
                        promote_action = menu.addAction("Promote")

                    # Add demote action if there's a next sibling
                    next_sibling = self._get_next_sibling(index)
                    demote_action = menu.addAction("Demote")
                    if not next_sibling:
                        demote_action.setEnabled(False)

                    menu.addSeparator()

                menu.addSeparator()

            # Determine labels based on context
            if node and node.node_type == 'note':
                new_label = "New Note"
                child_label = "New Child Note"
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
        action = menu.exec_(self.viewport().mapToGlobal(position))

        # If no action was selected (e.g. Esc pressed), just return
        if action is None:
            return

        try:
            if not index.isValid():
                # Handle root level actions with simplified menu
                if action == new_tag_action:
                    self._create_new_item(None, is_child=False)
                elif action == new_note_action:
                    self._create_new_item(None, is_child=False, force_note=True)
                return

            # Handle actions for existing items
            if action == rename_action:
                self.edit(index)
            elif action == delete_action:
                self._delete_item(node, index)
            elif action == promote_action:
                self._promote_item(node, index)
            elif action == demote_action:
                self._demote_item(node, index)
            elif action == new_action:
                self._create_new_item(None, is_child=False, force_note=(node.node_type == 'note'))
            elif action == new_child_action:
                self._create_new_item(node, is_child=True)
            elif action == new_sibling_action:
                parent_node = node.parent
                self._create_new_item(parent_node, is_child=True)
            elif action == new_note_under_tag_action:
                self._create_new_item(node, is_child=True, force_note=True)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Operation failed: {str(e)}")

    def _create_new_item(self, parent_node, is_child, force_note=False):
        """Handle creation of new items"""
        creating_note = force_note or (parent_node and parent_node.node_type == 'note')


        try:
            if creating_note and not parent_node:
                # Handle root-level note creation (All Notes and Untagged Notes sections)
                response = self.model.note_api.note_create("", "")
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
                for node in self.model.root_node.children:
                    if node.node_type == 'page':
                        if node.data["name"] == "All Notes":
                            all_notes_node = node
                        elif node.data["name"] == "Untagged Notes":
                            untagged_notes_node = node

                # Add to All Notes
                if all_notes_node:
                    new_node = TreeNode(tree_note, None, 'note')
                    new_index = self.model.insert_node(new_node, all_notes_node)

                # Add to Untagged Notes
                if untagged_notes_node:
                    new_node = TreeNode(tree_note, None, 'note')
                    new_index = self.model.insert_node(new_node, untagged_notes_node)

                    # Focus the new note in Untagged Notes section
                    self.setCurrentIndex(new_index)
                    self.setFocus()

                return

            # Handle all other cases
            target_parent = parent_node if is_child else self.model.root_node

            if creating_note:
                response = self.model.note_api.note_create("", "")
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
                        self.model.tag_api.attach_tag_to_note(tree_note.id, parent_node.data.id)
                    else:
                        self.model.note_api.attach_note_to_parent(
                            tree_note.id,
                            parent_node.data.id,
                            hierarchy_type="block"
                        )
            else:
                new_tag = self.model.tag_api.create_tag("")
                new_node = TreeNode(new_tag, None, 'tag')

                if parent_node and parent_node.node_type == 'tag':
                    self.model.tag_api.attach_tag_to_parent(
                        new_tag.id,
                        parent_node.data.id
                    )

                # Use model's insert_node method for proper sorting
                target_parent = parent_node if is_child else self.model.root_node
                new_index = self.model.insert_node(new_node, target_parent)
                self.setCurrentIndex(new_index)
                self.setFocus()

                # Enter edit mode to allow the user to set the tag name
                if not creating_note:
                    self.edit(new_index)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create item: {str(e)}")

    def _promote_item(self, node, index):
        """Handle promotion of items to their grandparent level"""
        try:
            current_parent = node.parent
            grandparent = current_parent.parent if current_parent else None

            # First remove from current parent
            parent_index = self.model.parent(index)
            self.model.beginRemoveRows(parent_index, index.row(), index.row())
            current_parent.children.remove(node)
            self.model.endRemoveRows()

            if node.node_type == 'tag':
                # Detach from current parent
                self.model.tag_api.detach_tag_from_parent(node.data.id)

                # Attach to grandparent if it exists and is a tag
                if grandparent and grandparent != self.model.root_node and grandparent.node_type == 'tag':
                    self.model.tag_api.attach_tag_to_parent(node.data.id, grandparent.data.id)
                    new_index = self.model.insert_node(node, grandparent)
                else:
                    # If no valid grandparent, move to root level
                    new_index = self.model.insert_node(node, self.model.root_node)

            else:  # note
                # Detach from current parent
                self.model.note_api.detach_note_from_parent(node.data.id)

                # Get current note's tags
                note_tags = node.data.tags if hasattr(node.data, 'tags') else []

                if grandparent and grandparent != self.model.root_node and grandparent.node_type == 'note':
                    # Attach to grandparent note
                    self.model.note_api.attach_note_to_parent(
                        node.data.id,
                        grandparent.data.id,
                        hierarchy_type="block"
                    )
                    new_index = self.model.insert_node(node, grandparent)
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
                        find_tag_nodes(self.model.root_node, tag_ids)

                        # Add note under each of its tag nodes
                        for tag_node in tag_nodes:
                            new_index = self.model.insert_node(node, tag_node)

                    # Also add to "Untagged Notes" if no tags
                    if not note_tags:
                        untagged_notes_node = None
                        for child in self.model.root_node.children:
                            if child.node_type == 'page' and child.data["name"] == "Untagged Notes":
                                untagged_notes_node = child
                                break

                        if untagged_notes_node:
                            new_index = self.model.insert_node(node, untagged_notes_node)

                    # Note is already in "All Notes", no need to add it again

                # Select the promoted item in its new location
                if new_index:
                    self.setCurrentIndex(new_index)
                    self.setFocus()

        except Exception as e:
            # If anything fails, try to revert to original position
            if current_parent:
                new_index = self.model.insert_node(node, current_parent)
            raise Exception(f"Failed to promote item: {str(e)}")

    def _focus_moved_tag(self, index):
        """Focus and select a tag after it's been moved"""
        self.setCurrentIndex(index)
        self.setFocus()

    def _delete_item(self, node, index):
        """Handle deletion of items"""
        try:
            if node.node_type == 'tag':
                self.model.tag_api.delete_tag(node.data.id)
            else:  # note
                self.model.note_api.delete_note(node.data.id)

            # Remove from tree
            parent_index = self.model.parent(index)
            self.model.beginRemoveRows(parent_index, index.row(), index.row())
            node.parent.children.remove(node)
            self.model.endRemoveRows()

        except Exception as e:
            raise Exception(f"Failed to delete item: {str(e)}")

    def _get_next_sibling(self, index):
        """Get the next sibling node in the tree"""
        parent = self.model.parent(index)
        next_row = index.row() + 1
        next_index = self.model.index(next_row, 0, parent)

        if next_index.isValid():
            return next_index.internalPointer()
        return None

    def _demote_item(self, node, index):
        """Handle demotion of items to become children of their next sibling"""
        try:
            # Get the next sibling
            next_sibling = self._get_next_sibling(index)
            if not next_sibling:
                return

            current_parent = node.parent

            # First remove from current parent
            parent_index = self.model.parent(index)
            self.model.beginRemoveRows(parent_index, index.row(), index.row())
            current_parent.children.remove(node)
            self.model.endRemoveRows()

            if node.node_type == 'tag':
                # Detach from current parent if it's a tag
                if current_parent and current_parent.node_type == 'tag':
                    self.model.tag_api.detach_tag_from_parent(node.data.id)

                # Attach to new parent (tag or note)
                self.model.tag_api.attach_tag_to_parent(
                    node.data.id,
                    next_sibling.data.id
                )
                new_index = self.model.insert_node(node, next_sibling)

            else:  # note
                # Detach from current parent if it's a note
                if current_parent and current_parent.node_type == 'note':
                    self.model.note_api.detach_note_from_parent(node.data.id)

                # Attach to new parent
                self.model.note_api.attach_note_to_parent(
                    node.data.id,
                    next_sibling.data.id,
                    hierarchy_type="block"
                )
                new_index = self.model.insert_node(node, next_sibling)

            # Select the demoted item in its new location
            self.setCurrentIndex(new_index)
            self.setFocus()

        except Exception as e:
            # If anything fails, try to revert to original position
            new_index = self.model.insert_node(node, current_parent)
            raise Exception(f"Failed to demote item: {str(e)}")
