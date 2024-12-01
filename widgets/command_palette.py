from PySide6.QtWidgets import QListWidgetItem, QAction
from .popup_palette import PopupPalette

class CommandPalette(PopupPalette):
    """Popup palette for executing menu commands"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.actions = []
        self.search_input.setPlaceholderText("Type command...")
        
    def populate_actions(self, menubar):
        """Collect all actions from the menubar"""
        self.actions.clear()
        for menu in menubar.findChildren(QAction):
            if menu.text():  # Skip empty actions
                self.actions.append(menu)
                
    def on_search(self, text):
        """Filter actions based on search text"""
        self.results_list.clear()
        search_terms = text.lower().split()
        
        for action in self.actions:
            action_text = action.text().lower()
            if all(term in action_text for term in search_terms):
                item = QListWidgetItem(action.text())
                item.setData(Qt.ItemDataRole.UserRole, action)
                self.results_list.addItem(item)
                
    def on_item_activated(self, item):
        """Trigger the selected action"""
        action = item.data(Qt.ItemDataRole.UserRole)
        if action and action.isEnabled():
            action.trigger()
        self.hide()
