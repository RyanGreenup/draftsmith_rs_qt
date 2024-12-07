from .neovim_integration import EditorWidget
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
import re


class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define highlighting patterns and formats
        self.highlighting_rules = []
        
        # Headers
        header_format = QTextCharFormat()
        header_format.setForeground(QColor("#569CD6"))
        header_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((re.compile(r'^#{1,6}\s.*$'), header_format))
        
        # Bold
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Bold)
        bold_format.setForeground(QColor("#C586C0"))
        self.highlighting_rules.append((re.compile(r'\*\*.*?\*\*'), bold_format))
        self.highlighting_rules.append((re.compile(r'__.*?__'), bold_format))
        
        # Italic
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        italic_format.setForeground(QColor("#9CDCFE"))
        self.highlighting_rules.append((re.compile(r'\*.*?\*'), italic_format))
        self.highlighting_rules.append((re.compile(r'_.*?_'), italic_format))
        
        # Code blocks
        code_format = QTextCharFormat()
        code_format.setForeground(QColor("#CE9178"))
        code_format.setBackground(QColor("#1E1E1E"))
        self.highlighting_rules.append((re.compile(r'`.*?`'), code_format))
        
        # Links
        link_format = QTextCharFormat()
        link_format.setForeground(QColor("#4EC9B0"))
        self.highlighting_rules.append((re.compile(r'\[.*?\]\(.*?\)'), link_format))
        
        # Lists
        list_format = QTextCharFormat()
        list_format.setForeground(QColor("#DCDCAA"))
        self.highlighting_rules.append((re.compile(r'^\s*[\-\*\+]\s'), list_format))
        self.highlighting_rules.append((re.compile(r'^\s*\d+\.\s'), list_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)


class MDEditor(EditorWidget):
    def __init__(self):
        super().__init__()
        # Initialize syntax highlighter
        self.highlighter = MarkdownHighlighter(self.document())

