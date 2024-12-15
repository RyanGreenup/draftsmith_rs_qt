from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, QMimeData, QByteArray, Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtWidgets import QMenu
from typing import List
from PySide6.QtWidgets import QStyle, QApplication
from typing import Optional, Any, List
from api.client import (
    TagAPI, NoteAPI, TreeTagWithNotes, TreeNote,
    UpdateNoteRequest
)

class TreeNode:
    def __init__(self, data, parent=None, node_type='tag'):
        self.data = data
        self.parent = parent
        self.children = []
        self.node_type = node_type  # 'tag' or 'note'

    def append_child(self, child):
        child.parent = self
        self.children.append(child)

    def child(self, row):
        if 0 <= row < len(self.children):
            return self.children[row]
        return None

    def child_count(self):
        return len(self.children)

    def row(self):
        if self.parent:
            return self.parent.children.index(self)
        return 0

class NotesTreeModel(QAbstractItemModel):
    contextMenuRequested = Signal(QModelIndex, 'QMenu')
    tagMoved = Signal(QModelIndex)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_node = TreeNode(None)
        self.marked_node = None  # Store marked node for copy/paste operations
        # TODO: Update base URL handling
        base_url = "http://vidar:37242"
        self.tag_api = TagAPI(base_url)
        self.note_api = NoteAPI(base_url)  # Add note API
        self.complete_notes_tree = []  # Store complete notes hierarchy
        self._view = None  # Initialize view reference
        self.setup_data()

    def setup_data(self):
        try:
            # First get complete notes tree for reference
            self.complete_notes_tree = self.note_api.get_notes_tree(exclude_content=True)

            # Then get tag tree
            tags_tree: List[TreeTagWithNotes] = self.tag_api.get_tags_tree()

            # Process tag hierarchy (sort tags before processing)
            for tag in sorted(tags_tree, key=lambda x: x.name.lower()):
                self._process_tag(tag, self.root_node)

            # Add "All Notes" section
            all_notes_node = TreeNode({"name": "All Notes"}, self.root_node, 'page')
            self.root_node.append_child(all_notes_node)

            # Sort notes before adding them
            sorted_notes = sorted(self.complete_notes_tree, key=lambda x: x.title.lower())
            for note in sorted_notes:
                self._process_note(note, all_notes_node)

            # Add "Untagged Notes" section
            untagged_notes_node = TreeNode({"name": "Untagged Notes"}, self.root_node, 'page')
            self.root_node.append_child(untagged_notes_node)

            # Find and process untagged root notes (sort them first)
            untagged_notes = [
                note for note in self.complete_notes_tree
                if not note.tags and not self._is_subpage(note)
            ]
            for note in sorted(untagged_notes, key=lambda x: x.title.lower()):
                if not note.tags:
                    self._process_note(note, untagged_notes_node)

        except Exception as e:
            print(f"Error loading data: {e}")

    def _find_note_in_tree(self, note_id: str, notes: List[TreeNote]) -> Optional[TreeNote]:
        """Recursively find a note by ID in the complete notes tree

        This is a work around until the API provides an endpoint to get the tags, notes and the notes subpages.

        """
        for note in notes:
            if note.id == note_id:
                return note
            if note.children:
                found = self._find_note_in_tree(note_id, note.children)
                if found:
                    return found
        return None

    def _process_tag(self, tag_data, parent_node):
        # Create tag node
        node = TreeNode(tag_data, parent_node, 'tag')
        # Use insert_node instead of append_child
        self.insert_node(node, parent_node)

        # Process child tags
        for child in sorted(tag_data.children, key=lambda x: x.name.lower()):
            self._process_tag(child, node)

        # Process notes belonging to this tag
        for note in sorted(tag_data.notes, key=lambda x: x.title.lower()):
            # Find the complete note hierarchy from notes_tree
            complete_note = self._find_note_in_tree(note.id, self.complete_notes_tree)
            if complete_note:
                self._process_note(complete_note, node)
            else:
                self._process_note(note, node)

    def _process_note(self, note_data, parent_node):
        # Create note node
        node = TreeNode(note_data, parent_node, 'note')
        # Use insert_node instead of append_child
        self.insert_node(node, parent_node)

        # Process child notes (subpages)
        for child in sorted(note_data.children, key=lambda x: x.title.lower()):
            self._process_note(child, node)

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parent_node = self.root_node if not parent.isValid() else parent.internalPointer()
        child_node = parent_node.child(row)

        if child_node:
            return self.createIndex(row, column, child_node)
        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child_node = index.internalPointer()
        parent_node = child_node.parent

        if parent_node == self.root_node:
            return QModelIndex()

        return self.createIndex(parent_node.row(), 0, parent_node)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.column() > 0:
            return 0

        parent_node = self.root_node if not parent.isValid() else parent.internalPointer()
        return parent_node.child_count()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == Qt.DecorationRole:
            style = QApplication.style()
            icons = []
            
            # Add marked indicator if this is the marked node
            if node == self.marked_node:
                icons.append(style.standardIcon(QStyle.StandardPixmap.SP_DialogYesButton))
            
            # Add regular icon based on node type
            if node.node_type == 'tag':
                icons.append(style.standardIcon(QStyle.StandardPixmap.SP_DirIcon))
            elif node.node_type == 'page':
                icons.append(style.standardIcon(QStyle.StandardPixmap.SP_DirLinkIcon))
            else:  # note
                icons.append(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon))
            
            # If we have multiple icons, combine them
            if len(icons) > 1:
                # Create a pixmap to hold both icons
                combined = QPixmap(32, 16)  # Width enough for both icons
                combined.fill(Qt.transparent)
                painter = QPainter(combined)
                
                # Draw marked indicator
                icons[0].paint(painter, 0, 0, 16, 16)
                # Draw type icon
                icons[1].paint(painter, 16, 0, 16, 16)
                
                painter.end()
                return QIcon(combined)
            else:
                return icons[0]

        elif role in (Qt.DisplayRole, Qt.EditRole):
            if node.node_type == 'tag':
                return f"{node.data.name}"
            elif node.node_type == 'page':
                return node.data["name"]  # Access dict with key
            else:  # note
                # Handle both dictionary and object cases
                if isinstance(node.data, dict):
                    return node.data.get('title', 'Untitled')
                return getattr(node.data, 'title', 'Untitled')

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return "Tags"
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemIsDropEnabled  # Allow drops on the root

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        node = index.internalPointer()
        if node.node_type == 'page':  # Special nodes like "All Notes"
            return flags

        # Add drag & drop flags for notes and tags
        if node.node_type in ['note', 'tag']:
            flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsEditable

        return flags

    def supportedDropActions(self) -> Qt.DropActions:
        return Qt.MoveAction

    def mimeTypes(self) -> List[str]:
        return ['application/x-notestreemodeldata']

    def mimeData(self, indexes: List[QModelIndex]) -> QMimeData:
        if not indexes:
            return None

        mime_data = QMimeData()
        node = indexes[0].internalPointer()
        # Store the node type and ID in the mime data
        data = f"{node.node_type}:{node.data.id if hasattr(node.data, 'id') else ''}"
        mime_data.setData('application/x-notestreemodeldata', QByteArray(data.encode()))
        return mime_data

    def canDropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int,
                        column: int, parent: QModelIndex) -> bool:
        if not data.hasFormat('application/x-notestreemodeldata'):
            return False

        # Get the target node
        target_node = parent.internalPointer() if parent.isValid() else self.root_node

        # Get the source node type
        source_data = bytes(data.data('application/x-notestreemodeldata')).decode()
        source_type = source_data.split(':')[0]

        # Allow drops based on rules:
        # 1. Notes can be dropped on tags
        # 2. Notes can be dropped on other notes (to create subpages)
        # 3. Tags can be dropped on other tags
        if source_type == 'note':
            return target_node.node_type in ['tag', 'note']
        elif source_type == 'tag':
            return target_node.node_type == 'tag'

        return False

    def _find_untagged_section(self) -> QModelIndex:
        """Find the "Untagged Notes" section in the tree"""
        for i in range(self.root_node.child_count()):
            index = self.createIndex(i, 0, self.root_node.children[i])
            node = index.internalPointer()
            if (node.node_type == 'page' and
                isinstance(node.data, dict) and
                node.data.get('name') == "Untagged Notes"):
                return index
        return QModelIndex()

    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int,
                     column: int, parent: QModelIndex) -> bool:
        if not self.canDropMimeData(data, action, row, column, parent):
            return False

        source_data = bytes(data.data('application/x-notestreemodeldata')).decode()
        source_type, source_id = source_data.split(':')
        target_node = parent.internalPointer() if parent.isValid() else self.root_node

        try:
            if source_type == 'note':
                if target_node.node_type == 'tag':
                    # Convert IDs to integers
                    note_id = int(source_id)
                    tag_id = int(target_node.data.id)

                    # Perform the API call
                    self.tag_api.attach_tag_to_note(note_id, tag_id)

                    # Find the source note node
                    source_index = self._find_index_by_id(note_id, 'note')
                    if not source_index.isValid():
                        return False

                    # Get the note data
                    note_node = source_index.internalPointer()

                    # Create a new node for the note under the tag
                    insert_pos = self._find_insert_position(target_node, note_node)

                    # Insert the note node under the tag
                    self.beginInsertRows(parent, insert_pos, insert_pos)
                    new_note_node = TreeNode(note_node.data, target_node, 'note')
                    target_node.children.insert(insert_pos, new_note_node)

                    # Process child notes recursively
                    def process_children(parent_note_node, source_note_node):
                        for child in source_note_node.children:
                            child_node = TreeNode(child.data, parent_note_node, 'note')
                            parent_note_node.append_child(child_node)
                            process_children(child_node, child)

                    # Process all children of the original note
                    process_children(new_note_node, note_node)
                    self.endInsertRows()

                    # Find and remove from "Untagged Notes" if present
                    untagged_index = self._find_untagged_section()
                    if untagged_index.isValid():
                        untagged_node = untagged_index.internalPointer()
                        for i, child in enumerate(untagged_node.children):
                            if (child.node_type == 'note' and
                                hasattr(child.data, 'id') and
                                child.data.id == note_id):
                                # Remove from untagged section
                                self.beginRemoveRows(untagged_index, i, i)
                                untagged_node.children.pop(i)
                                self.endRemoveRows()
                                break

                    return True

                else:  # target is note
                    # Convert IDs to integers
                    child_note_id = int(source_id)
                    parent_note_id = int(target_node.data.id)

                    # Store the target node where the drop occurred
                    drop_target_instance = target_node

                    # Find the source note node
                    source_index = self._find_index_by_id(child_note_id, 'note')
                    if not source_index.isValid():
                        return False

                    # Get the source note node and its data
                    note_node = source_index.internalPointer()
                    note_data = note_node.data

                    # If this note was a subpage of another note, find all instances and remove it
                    old_parent = source_index.parent()
                    if old_parent.isValid():
                        old_parent_node = old_parent.internalPointer()
                        if old_parent_node.node_type == 'note':
                            old_parent_id = old_parent_node.data.id

                            # Find all instances of the old parent note
                            def find_old_parent_instances(search_node):
                                instances = []
                                if (search_node.node_type == 'note' and
                                    hasattr(search_node.data, 'id') and
                                    search_node.data.id == old_parent_id):
                                    instances.append(search_node)
                                for child in search_node.children:
                                    instances.extend(find_old_parent_instances(child))
                                return instances

                            old_parent_instances = find_old_parent_instances(self.root_node)

                            # Remove the note from each instance of the old parent
                            for parent_instance in old_parent_instances:
                                for i, child in enumerate(parent_instance.children):
                                    if (child.node_type == 'note' and
                                        hasattr(child.data, 'id') and
                                        child.data.id == child_note_id):
                                        parent_index = self.createIndex(parent_instance.row(), 0, parent_instance)
                                        self.beginRemoveRows(parent_index, i, i)
                                        parent_instance.children.pop(i)
                                        self.endRemoveRows()
                                        break
                        else:
                            # Just remove from current position if not under another note
                            row = source_index.row()
                            self.beginRemoveRows(old_parent, row, row)
                            old_parent_node.children.pop(row)
                            self.endRemoveRows()

                    # Now perform the API call to attach to new parent
                    self.note_api.attach_note_to_parent(
                        child_note_id,
                        parent_note_id,
                        hierarchy_type="block"
                    )

                    # Find all instances of the target (parent) note and add the child to each
                    def find_parent_instances(search_node):
                        instances = []
                        if (search_node.node_type == 'note' and
                            hasattr(search_node.data, 'id') and
                            search_node.data.id == parent_note_id):
                            instances.append(search_node)
                        for child in search_node.children:
                            instances.extend(find_parent_instances(child))
                        return instances

                    parent_instances = find_parent_instances(self.root_node)
                    focus_index = None

                    # Add the note to each instance of the parent
                    for parent_instance in parent_instances:
                        # Create new node for this instance
                        new_note_node = TreeNode(note_data, parent_instance, 'note')

                        # Find insert position maintaining sort order
                        insert_pos = self._find_insert_position(parent_instance, new_note_node)

                        # Insert the node
                        parent_index = self.createIndex(parent_instance.row(), 0, parent_instance)
                        self.beginInsertRows(parent_index, insert_pos, insert_pos)
                        parent_instance.children.insert(insert_pos, new_note_node)
                        self.endInsertRows()

                        # Store the index only if this is the instance where the drop occurred
                        if parent_instance is drop_target_instance:
                            focus_index = self.createIndex(insert_pos, 0, new_note_node)

                    # Focus only the instance where the drop occurred
                    if focus_index and self._view:
                        self._view.setCurrentIndex(focus_index)
                        self._view.setFocus()

                    return True
            elif source_type == 'tag':
                if target_node.node_type == 'tag':
                    # Convert IDs to integers
                    child_id = int(source_id)
                    parent_id = int(target_node.data.id)

                    # Find the source index
                    source_index = self._find_index_by_id(child_id, 'tag')
                    if not source_index.isValid():
                        return False

                    source_node = source_index.internalPointer()

                    # Store expanded states BEFORE anything else
                    expanded_states = {}
                    self._store_expanded_state(source_node, expanded_states)
                    expanded_states = {}
                    self._store_expanded_state(source_node, expanded_states)

                    # Now perform the API call
                    self.tag_api.attach_tag_to_parent(child_id, parent_id)

                    # Remove from old position
                    old_parent = source_index.parent()
                    old_parent_node = old_parent.internalPointer() if old_parent.isValid() else self.root_node
                    row = source_index.row()

                    self.beginRemoveRows(old_parent, row, row)
                    node_to_move = old_parent_node.children.pop(row)
                    self.endRemoveRows()

                    # Insert at new position
                    insert_pos = self._find_insert_position(target_node, node_to_move)
                    self.beginInsertRows(parent, insert_pos, insert_pos)
                    node_to_move.parent = target_node
                    target_node.children.insert(insert_pos, node_to_move)
                    self.endInsertRows()

                    # Create new index for the moved node
                    new_index = self.createIndex(insert_pos, 0, node_to_move)

                    # Restore expanded states after the move
                    self._restore_expanded_state(node_to_move, expanded_states)

                    # Ensure the new node is expanded if it was previously
                    if expanded_states.get(f"tag_{child_id}", False):
                        self.set_expanded(node_to_move, True)

                    self.tagMoved.emit(new_index)

                    return True

            return False

        except Exception as e:
            print(f"Error during drag and drop: {e}")
            return False

    def _get_sort_key(self, node):
        """Get the key to use for sorting nodes"""
        # Special handling for page nodes (All Notes, Untagged Notes) - always at the end
        if node.node_type == 'page':
            return ('2', node.data["name"].lower())

        # Tags and notes are sorted by name/title
        if node.node_type == 'tag':
            return ('0', node.data.name.lower())
        else:  # note
            title = node.data.title if hasattr(node.data, 'title') else node.data.get('title', '')
            return ('1', title.lower())

    def _find_insert_position(self, parent_node, new_node):
        """Find the correct position to insert a node maintaining alphabetical order"""
        new_key = self._get_sort_key(new_node)

        for i, child in enumerate(parent_node.children):
            if self._get_sort_key(child) > new_key:
                return i
        return len(parent_node.children)

    def insert_node(self, new_node, parent_node):
        """Insert a node in the correct sorted position"""
        if not parent_node:
            parent_node = self.root_node

        # Find insert position
        insert_pos = self._find_insert_position(parent_node, new_node)

        # Create parent index
        parent_index = QModelIndex() if parent_node == self.root_node else \
                      self.createIndex(parent_node.row(), 0, parent_node)

        # Insert node
        self.beginInsertRows(parent_index, insert_pos, insert_pos)
        new_node.parent = parent_node
        parent_node.children.insert(insert_pos, new_node)
        self.endInsertRows()

        return self.createIndex(insert_pos, 0, new_node)

    def sort_children(self, parent_node):
        """Sort the children of a node"""
        if not parent_node.children:
            return

        # Create parent index
        parent_index = QModelIndex() if parent_node == self.root_node else \
                      self.createIndex(parent_node.row(), 0, parent_node)

        # Sort children
        self.beginResetModel()
        parent_node.children.sort(key=self._get_sort_key)
        self.endResetModel()

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if not index.isValid() or role != Qt.EditRole:
            return False

        node = index.internalPointer()
        new_name = str(value).strip()

        if not new_name:  # Don't allow empty names
            return False

        try:
            if node.node_type == 'tag':
                # Update tag name
                updated_tag = self.tag_api.update_tag(node.data.id, new_name)
                node.data.name = updated_tag.name
            elif node.node_type == 'note':
                # Update note title
                request = UpdateNoteRequest(title=new_name)
                updated_note = self.note_api.update_note(node.data.id, request)
                node.data.title = updated_note.title
            else:
                return False

            # Notify views that data has changed
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True

        except Exception as e:
            print(f"Error updating item: {e}")
            return False

    def _find_index_by_id(self, id_to_find: int, node_type: str) -> QModelIndex:
        """Helper method to find a node's index by its ID"""
        def search(parent_index: QModelIndex) -> QModelIndex:
            rows = self.rowCount(parent_index)
            for row in range(rows):
                index = self.index(row, 0, parent_index)
                node = index.internalPointer()

                if (node.node_type == node_type and
                    hasattr(node.data, 'id') and
                    node.data.id == id_to_find):
                    return index

                # Recursively search children
                result = search(index)
                if result.isValid():
                    return result

            return QModelIndex()

        return search(QModelIndex())

    def _is_subpage(self, note: TreeNote) -> bool:
        """Check if this note is referenced as a child in the complete notes tree"""
        def check_children(parent_notes: List[TreeNote]) -> bool:
            for parent in parent_notes:
                for child in parent.children:
                    if child.id == note.id:
                        return True
                    if check_children([child]):
                        return True
            return False

        return check_children(self.complete_notes_tree)

    def create_context_menu(self, index: QModelIndex) -> QMenu:
        """Create and return a context menu for the given index"""
        menu = QMenu()

        # If no item is clicked (empty space), show refresh option
        if not index.isValid():
            refresh_action = menu.addAction("Refresh Tree")
            refresh_action.triggered.connect(self.refresh_tree)
            return menu

        node = index.internalPointer()
        if node is not None:
            # Add Mark option for notes and tags
            if node.node_type in ['note', 'tag']:
                mark_action = menu.addAction("Mark")
                mark_action.triggered.connect(lambda: self._mark_node(node))

            # Add Paste options if there's a marked node
            if self.marked_node:
                marked_type = self.marked_node.node_type
                target_type = node.node_type

                if marked_type == 'note' and target_type == 'tag':
                    # Note -> Tag options
                    menu.addSeparator()
                    attach_action = menu.addAction("Attach Marked Note Here")
                    attach_action.triggered.connect(
                        lambda: self._handle_paste(self.marked_node, node, "attach"))
                    
                    move_action = menu.addAction("Move Marked Note Here")
                    move_action.triggered.connect(
                        lambda: self._handle_paste(self.marked_node, node, "move"))

                elif marked_type == 'tag' and target_type == 'tag':
                    # Tag -> Tag option
                    menu.addSeparator()
                    move_action = menu.addAction("Move Marked Tag as Child")
                    move_action.triggered.connect(
                        lambda: self._handle_paste(self.marked_node, node, "move"))

                elif marked_type == 'note' and target_type == 'note':
                    # Note -> Note option
                    menu.addSeparator()
                    move_action = menu.addAction("Move Marked Note as Subpage")
                    move_action.triggered.connect(
                        lambda: self._handle_paste(self.marked_node, node, "move"))

            # Show detach option for notes under tags
            if (node.node_type == 'note' and
                node.parent and
                node.parent.node_type == 'tag'):
                menu.addSeparator()
                detach_action = menu.addAction("Detach from tag")
                detach_action.triggered.connect(lambda: self.detach_note_from_tag(index))

            # Show detach option for tags under other tags
            elif (node.node_type == 'tag' and
                  node.parent and
                  node.parent.node_type == 'tag'):
                menu.addSeparator()
                detach_action = menu.addAction("Detach from parent tag")
                detach_action.triggered.connect(lambda: self.detach_tag_from_parent(index))

        self.contextMenuRequested.emit(index, menu)
        return menu

    def _store_expanded_state(self, node: TreeNode, expanded_states: dict) -> None:
        """Recursively store the expanded state of a node and its children"""
        if hasattr(node.data, 'id'):
            node_id = f"{node.node_type}_{node.data.id}"
            expanded_states[node_id] = self.is_expanded(node)

        for child in node.children:
            self._store_expanded_state(child, expanded_states)

    def _restore_expanded_state(self, node: TreeNode, expanded_states: dict) -> None:
        """Recursively restore the expanded state of a node and its children"""
        if hasattr(node.data, 'id'):
            node_id = f"{node.node_type}_{node.data.id}"
            if node_id in expanded_states:
                self.set_expanded(node, expanded_states[node_id])

        for child in node.children:
            self._restore_expanded_state(child, expanded_states)

    def is_expanded(self, node: TreeNode) -> bool:
        """Check if a node is expanded in the view"""
        if not self._view:
            print("View is not set.")
            return False
        try:
            index = self.createIndex(node.row(), 0, node)
            expanded = self._view.isExpanded(index)
            return expanded
        except Exception as e:
            print(f"Error checking expanded state: {e}")
            return False

    def set_expanded(self, node: TreeNode, expanded: bool) -> None:
        """Set the expanded state of a node in the view"""
        if not self._view:
            return
        try:
            index = self.createIndex(node.row(), 0, node)
            self._view.setExpanded(index, expanded)
        except Exception:
            pass

    def set_view(self, view) -> None:
        """Set the associated view for expansion state tracking"""
        self._view = view

    def detach_tag_from_parent(self, index: QModelIndex) -> None:
        """Detach a tag from its parent tag"""
        if not index.isValid():
            return

        node = index.internalPointer()
        parent_node = node.parent

        if not (node.node_type == 'tag' and parent_node and parent_node.node_type == 'tag'):
            return

        try:
            # Store expanded states before moving
            expanded_states = {}
            self._store_expanded_state(node, expanded_states)

            # Call API to detach tag
            tag_id = int(node.data.id)
            parent_tag_id = int(parent_node.data.id)
            self.tag_api.detach_tag_from_parent(tag_id)

            # Remove tag from current position
            row = index.row()
            self.beginRemoveRows(index.parent(), row, row)
            node_to_move = parent_node.children.pop(row)
            self.endRemoveRows()

            # Move to root level, preserving all children
            insert_pos = self._find_insert_position(self.root_node, node)
            self.beginInsertRows(QModelIndex(), insert_pos, insert_pos)
            node_to_move.parent = self.root_node
            self.root_node.children.insert(insert_pos, node_to_move)
            self.endInsertRows()

            # Create new index for focusing
            new_index = self.createIndex(insert_pos, 0, node_to_move)

            # Restore expanded states
            self._restore_expanded_state(node_to_move, expanded_states)

            # Emit signal for focusing
            self.tagMoved.emit(new_index)

        except Exception as e:
            print(f"Error detaching tag from parent: {e}")

    def refresh_tree(self) -> None:
        """Rebuild the entire tree from scratch using fresh API data"""
        try:
            # Store expanded states for the entire tree before refresh
            expanded_states = {}
            self._store_expanded_state(self.root_node, expanded_states)

            # Reset and reload the entire tree
            self.beginResetModel()
            self.root_node = TreeNode(None)
            self.setup_data()
            self.endResetModel()

            # Restore expanded states after refresh
            self._restore_expanded_state(self.root_node, expanded_states)

        except Exception as e:
            print(f"Error refreshing tree: {e}")

    def delete_tag(self, index: QModelIndex) -> None:
        """Delete a tag and refresh the entire tree"""
        if not index.isValid():
            return

        node = index.internalPointer()
        if node.node_type != 'tag':
            return

        try:
            # Call API to delete tag
            tag_id = int(node.data.id)
            self.tag_api.delete_tag(tag_id)

            # Refresh the entire tree
            self.refresh_tree()

        except Exception as e:
            print(f"Error deleting tag: {e}")

    def _mark_node(self, node):
        """Mark a node for later operations"""
        self.marked_node = node
        print(f"Marked {node.node_type}: {self.data(self.createIndex(node.row(), 0, node))}")

    def _handle_paste(self, source_node, target_node, operation):
        """Handle paste operations between nodes"""
        source_type = source_node.node_type
        target_type = target_node.node_type
        
        try:
            if operation == "move" and source_type == "note" and target_type == "note":
                # Store expanded states before moving
                expanded_states = {}
                self._store_expanded_state(source_node, expanded_states)
                
                # Get source and target IDs
                source_id = int(source_node.data.id)
                target_id = int(target_node.data.id)
                
                # Call API to attach note as subpage
                self.note_api.attach_note_to_parent(source_id, target_id, hierarchy_type="block")
                
                # Remove note from current position
                source_parent = source_node.parent
                source_index = self.createIndex(source_node.row(), 0, source_node)
                source_parent_index = self.createIndex(source_parent.row(), 0, source_parent) if source_parent != self.root_node else QModelIndex()
                
                self.beginRemoveRows(source_parent_index, source_node.row(), source_node.row())
                source_parent.children.remove(source_node)
                self.endRemoveRows()
                
                # Add to new parent
                insert_pos = self._find_insert_position(target_node, source_node)
                target_index = self.createIndex(target_node.row(), 0, target_node)
                
                self.beginInsertRows(target_index, insert_pos, insert_pos)
                source_node.parent = target_node
                target_node.children.insert(insert_pos, source_node)
                self.endInsertRows()
                
                # Restore expanded states
                self._restore_expanded_state(source_node, expanded_states)
                
                # Create new index for the moved node
                new_index = self.createIndex(insert_pos, 0, source_node)
                self.tagMoved.emit(new_index)
                
            elif operation == "move" and source_type == "tag" and target_type == "tag":
                # Store expanded states before moving
                expanded_states = {}
                self._store_expanded_state(source_node, expanded_states)
                
                # Get source and target IDs
                source_id = int(source_node.data.id)
                target_id = int(target_node.data.id)
                
                # Call API to attach tag to new parent
                self.tag_api.attach_tag_to_parent(source_id, target_id)
                
                # Remove tag from current position
                source_parent = source_node.parent
                source_index = self.createIndex(source_node.row(), 0, source_node)
                source_parent_index = self.createIndex(source_parent.row(), 0, source_parent) if source_parent != self.root_node else QModelIndex()
                
                self.beginRemoveRows(source_parent_index, source_node.row(), source_node.row())
                source_parent.children.remove(source_node)
                self.endRemoveRows()
                
                # Add to new parent
                insert_pos = self._find_insert_position(target_node, source_node)
                target_index = self.createIndex(target_node.row(), 0, target_node)
                
                self.beginInsertRows(target_index, insert_pos, insert_pos)
                source_node.parent = target_node
                target_node.children.insert(insert_pos, source_node)
                self.endInsertRows()
                
                # Restore expanded states
                self._restore_expanded_state(source_node, expanded_states)
                
                # Create new index for the moved node
                new_index = self.createIndex(insert_pos, 0, source_node)
                self.tagMoved.emit(new_index)
            
            else:
                source_name = self.data(self.createIndex(source_node.row(), 0, source_node))
                target_name = self.data(self.createIndex(target_node.row(), 0, target_node))
                print(f"\nPaste Operation:")
                print(f"Source: {source_type} '{source_name}'")
                print(f"Target: {target_type} '{target_name}'")
                print(f"Operation: {operation}")
            
        except Exception as e:
            print(f"Error during paste operation: {e}")
        
        finally:
            # Clear the marked node after operation
            self.marked_node = None

    def detach_note_from_tag(self, index: QModelIndex) -> None:
        """Detach a note from its parent tag"""
        if not index.isValid():
            return

        node = index.internalPointer()
        parent_node = node.parent

        if not (node.node_type == 'note' and parent_node and parent_node.node_type == 'tag'):
            return

        try:
            # Call API to detach tag
            note_id = int(node.data.id)
            tag_id = int(parent_node.data.id)
            self.tag_api.detach_tag_from_note(note_id, tag_id)

            # Remove note from current position
            row = index.row()
            self.beginRemoveRows(index.parent(), row, row)
            parent_node.children.pop(row)
            self.endRemoveRows()

            # If note has no more tags, add it to "Untagged Notes" section
            if not node.data.tags:
                untagged_index = self._find_untagged_section()
                if untagged_index.isValid():
                    untagged_node = untagged_index.internalPointer()
                    insert_pos = self._find_insert_position(untagged_node, node)

                    self.beginInsertRows(untagged_index, insert_pos, insert_pos)
                    new_node = TreeNode(node.data, untagged_node, 'note')
                    untagged_node.children.insert(insert_pos, new_node)
                    self.endInsertRows()

        except Exception as e:
            print(f"Error detaching note from tag: {e}")
