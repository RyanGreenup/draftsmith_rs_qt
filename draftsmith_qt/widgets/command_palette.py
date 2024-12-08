from typing import List, Optional, Any
from PySide6.QtWidgets import QListWidgetItem, QMainWindow, QMenuBar, QMenu
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont, QKeyEvent
from .popup_palette import PopupPalette


class CommandPalette(PopupPalette):
    """Popup palette for executing menu commands"""

    def __init__(self, parent: Optional[QMainWindow] = None) -> None:
        super().__init__(parent)
        self._actions: List[QAction] = []
        self.search_input.setPlaceholderText("Type command...")
        self.main_window = self.get_main_window()

        # Connect selection change signal
        self.results_list.currentItemChanged.connect(self.on_selection_changed)

    def populate_actions(self, menubar: QMenuBar) -> None:
        """Collect all actions from the menubar's menus"""
        self._actions.clear()
        # Iterate through all top-level menus
        for menu in menubar.findChildren(QMenu):
            # For each menu, get its actions recursively
            self._collect_actions_from_menu(menu)

        # Clear and repopulate the results list
        self.results_list.clear()
        for action in self._actions:
            item = self.create_list_item(action)
            if item:
                self.results_list.addItem(item)

    def _collect_actions_from_menu(self, menu: QMenu) -> None:
        """Recursively collect actions from a menu and its submenus"""
        for action in menu.actions():
            if action.menu():  # If action has submenu, recurse into it
                self._collect_actions_from_menu(action.menu())
            elif (
                action.text() and action.isEnabled()
            ):  # Only add enabled actions with text
                self._actions.append(action)

    def get_all_items(self) -> List[QAction]:
        """Get all actions"""
        return [action for action in self._actions if action.text()]

    def create_list_item(self, data: Any) -> Optional[QListWidgetItem]:
        """Create a list item from an action"""
        if not isinstance(data, QAction) or not data.text():
            return None

        # Create display text with action name and description
        display_text = data.text()
        if data.statusTip():
            # Use a wider space for the action name and add a subtle separator
            display_text = f"{data.text().replace('&', ''):<30} • {data.statusTip()}"

        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, data)

        # Style the item
        font = QFont()
        font.setPointSize(11)
        item.setFont(font)

        return item

    def filter_items(self, text: str) -> None:
        """Filter actions based on search text"""
        search_terms = text.lower().split()
        for action in self._actions:
            action_text = action.text().lower()
            if all(term in action_text for term in search_terms):
                item = self.create_list_item(action)
                if item:
                    self.results_list.addItem(item)

    def get_main_window(self) -> Optional[QMainWindow]:
        """Get reference to main window"""
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, QMainWindow):
                return parent
            parent = parent.parent()
        return None

    def on_selection_changed(
        self, current: Optional[QListWidgetItem], previous: Optional[QListWidgetItem]
    ) -> None:
        """Update status bar when selection changes"""
        if current and self.main_window:
            action = current.data(Qt.ItemDataRole.UserRole)
            if action and action.statusTip():
                self.main_window.statusBar().showMessage(action.statusTip())

    def on_item_activated(self, item: QListWidgetItem) -> None:
        """Trigger the selected action"""
        action = item.data(Qt.ItemDataRole.UserRole)
        if action and action.isEnabled():
            action.trigger()
        if self.main_window:
            self.main_window.statusBar().showMessage("Ready")
        self.hide()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events"""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            current_item = self.results_list.currentItem()
            if current_item:
                self.on_item_activated(current_item)
        else:
            # Let parent class handle other keys
            super().keyPressEvent(event)
