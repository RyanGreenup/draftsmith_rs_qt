from PySide6.QtCore import QRegularExpression
from .neovim_integration import EditorWidget
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
import re

BLOCK_MATH_PATTERN = re.compile(r"\$\$(.*?)\$\$", re.DOTALL)
# TODO is Dotall needed here?
INLINE_MATH_PATTERN = re.compile(r"(?<!\$)\$((?!\$).+?)(?<!\$)\$", re.DOTALL)

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Define the highlighting rules
        self.highlightingRules = []
        # If using Native re module, use this list as unicode is handled differently
        self.highlightingRules_unicode = []

        # Heading format
        for i in range(1, 7):
            headingFormat = QTextCharFormat()
            headingFormat.setFontWeight(QFont.Weight.Bold)
            # headingFormat.setForeground(QColor("blue"))
            headingFormat.setFontPointSize(24 - i * 2)
            hashes = "#" * i
            self.highlightingRules.append(
                (QRegularExpression(f"^{hashes} .+"), headingFormat)
            )

        # Inline Math
        inlineMathFormat = QTextCharFormat()
        inlineMathFormat.setForeground(QColor("darkGreen"))
        # Set Background to highlight math
        inlineMathFormat.setBackground(QColor("lightGray"))
        self.highlightingRules.append(
            (QRegularExpression(INLINE_MATH_PATTERN.pattern), inlineMathFormat)
        )

        # Bold format
        boldFormat = QTextCharFormat()
        boldFormat.setFontWeight(QFont.Weight.Bold)
        self.highlightingRules.append(
            (QRegularExpression("\\*\\*(.*?)\\*\\*"), boldFormat)
        )
        self.highlightingRules.append((QRegularExpression("__(.*?)__"), boldFormat))

        # Italic format
        italicFormat = QTextCharFormat()
        italicFormat.setFontItalic(True)
        self.highlightingRules.append((QRegularExpression("\\*(.*?)\\*"), italicFormat))
        self.highlightingRules.append((QRegularExpression("_(.*?)_"), italicFormat))

        # Code format
        codeFormat = QTextCharFormat()
        # codeFormat.setFontFamily(Config().config["fonts"]["editor"]["mono"])
        codeFormat.setFontFamily("Fira Code")
        codeFormat.setForeground(QColor("darkGreen"))
        self.highlightingRules.append((QRegularExpression("`[^`]+`"), codeFormat))
        self.highlightingRules.append((QRegularExpression("^\\s*```.*"), codeFormat))

        # Link format
        linkFormat = QTextCharFormat()
        linkFormat.setForeground(QColor("darkBlue"))
        linkFormat.setFontWeight(QFont.Weight.Bold)
        self.highlightingRules.append(
            (QRegularExpression("\\[.*?\\]\\(.*?\\)"), linkFormat)
        )
        # Wikilinks
        self.highlightingRules.append(
            (QRegularExpression("\\[\\[.*?\\]\\]"), linkFormat)
        )

        # Image format
        imageFormat = QTextCharFormat()
        # imageFormat.setForeground(QColor("darkMagenta"))
        self.highlightingRules.append(
            (QRegularExpression("!\\[.*?\\]\\(.*?\\)"), imageFormat)
        )

        # List format
        listFormat = QTextCharFormat()
        # listFormat.setForeground(QColor("brown"))
        self.highlightingRules.append(
            (QRegularExpression("^\\s*([-+*])\\s+.*"), listFormat)
        )
        self.highlightingRules.append(
            (QRegularExpression("^\\s*\\d+\\.\\s+.*"), listFormat)
        )

    def highlightBlock(self, text):
        if text:
            for pattern, format in self.highlightingRules:
                iterator = pattern.globalMatch(text)
                while iterator.hasNext():
                    match = iterator.next()
                    index = match.capturedStart()
                    length = match.capturedLength()
                    self.setFormat(index, length, format)


class MDEditor(EditorWidget):
    def __init__(self):
        super().__init__()
        # Initialize syntax highlighter
        self.highlighter = MarkdownHighlighter(self.document())

