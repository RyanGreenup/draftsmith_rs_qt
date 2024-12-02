from widgets.tab_widget import NotesTabWidget

class TabHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        self.tab_widget = NotesTabWidget(main_window)
        
    def setup_tabs(self):
        self.main_window.setCentralWidget(self.tab_widget)
        return self.tab_widget.add_new_tab("Main")
        
    def new_tab(self):
        self.tab_widget.add_new_tab()
        
    def close_current_tab(self):
        current_index = self.tab_widget.currentIndex()
        self.tab_widget.close_tab(current_index)
        
    def next_tab(self):
        current = self.tab_widget.currentIndex()
        next_index = (current + 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(next_index)
        
    def previous_tab(self):
        current = self.tab_widget.currentIndex()
        prev_index = (current - 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(prev_index)
