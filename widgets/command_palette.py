from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from .popup_palette import PopupPalette

class CommandPalette(PopupPalette):
    """Popup palette for executing menu commands"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.actions = []
        self.search_input.setPlaceholderText("Type command...")
        
    def populate_actions(self, menubar):
        """Collect all actions from the menubar's menus"""
        self.actions.clear()
        # Get all top-level menus
        for menu in menubar.findChildren(QAction):
            if hasattr(menu, 'menu') and menu.menu():
                # For each menu, get its actions
                for action in menu.menu().actions():
                    if action.text() and not action.menu():  # Skip empty actions and submenus
                        self.actions.append(action)
                
    def get_all_items(self):
        """Get all actions"""
        return [action for action in self.actions if action.text()]

    def create_list_item(self, action):
        """Create a list item from an action"""
        if not action.text():
            return None
            
        # Create display text with action name and description
        display_text = f"{action.text()}"
        if action.statusTip():
            display_text = f"{action.text():20} • {action.statusTip()}"
            
        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, action)
        
        # Style the item
        font = item.font()
        font.setPointSize(10)
        item.setFont(font)
        
        return item

    def filter_items(self, text):
        """Filter actions based on search text"""
        search_terms = text.lower().split()
        for action in self.actions:
            action_text = action.text().lower()
            if all(term in action_text for term in search_terms):
                item = self.create_list_item(action)
                if item:
                    self.results_list.addItem(item)
                
    def on_item_activated(self, item):
        """Trigger the selected action"""
        action = item.data(Qt.ItemDataRole.UserRole)
        if action and action.isEnabled():
            action.trigger()
        self.hide()
