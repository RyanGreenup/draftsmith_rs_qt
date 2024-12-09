from PySide6.QtCore import QRegularExpression
from PySide6.QtWidgets import QTextEdit
from .neovim_integration import EditorWidget
from PySide6.QtGui import QKeyEvent, QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextCursor, QTextFormat
from PySide6.QtCore import Qt, QSize
import re

BLOCK_MATH_PATTERN = re.compile(r"\$\$(.*?)\$\$", re.DOTALL)
# TODO is Dotall needed here?
INLINE_MATH_PATTERN = re.compile(r"(?<!\$)\$((?!\$).+?)(?<!\$)\$", re.DOTALL)


# This is used for Highlighting
class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Define the highlighting rules
        self.highlightingRules = []
        # If using Native re module, use this list as unicode is handled differently
        self.highlightingRules_unicode = []

        # this has false positive in code blocks
        # # Heading format
        # for i in range(1, 7):
        #     headingFormat = QTextCharFormat()
        #     headingFormat.setFontWeight(QFont.Weight.Bold)
        #     # headingFormat.setForeground(QColor("blue"))
        #     headingFormat.setFontPointSize(24 - i * 2)
        #     hashes = "#" * i
        #     self.highlightingRules.append(
        #         (QRegularExpression(f"^{hashes} .+"), headingFormat)
        #     )

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

# This provides some basic Modal Editing functionality


class VimTextEdit(EditorWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.vim_mode = False
        self.insert_mode = False
        self.visual_mode = False
        self.visual_anchor = None
        self.yanked_text = ""
        self.g_pressed = False
        self.dark_mode = False


    def update_line_highlight(self):
        if self.vim_mode and not self.insert_mode:
            self.highlight_current_line()
        else:
            self.clear_line_highlight()

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(Qt.GlobalColor.yellow)
            line_color.setAlpha(40)  # Set transparency
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def clear_line_highlight(self):
        self.setExtraSelections([])

    def keyPressEvent(self, e: QKeyEvent):
        match (self.vim_mode, self.insert_mode, self.visual_mode, e.key()):
            case (False, _, _, Qt.Key.Key_Escape):
                self.vim_mode = True
                self.insert_mode = False
                self.visual_mode = False
                self.update_line_highlight()

            case (False, _, _, _):
                super().keyPressEvent(e)

            case (True, True, _, Qt.Key.Key_Escape):
                self.insert_mode = False
                self.update_line_highlight()

            case (True, True, _, _):
                super().keyPressEvent(e)

            case (True, False, True, _):
                self.handle_visual_mode(e)

            case (True, False, False, _):
                self.handle_normal_mode(e)

    def handle_normal_mode(self, e: QKeyEvent):
        cursor = self.textCursor()
        match e.key():
            case Qt.Key.Key_H:
                cursor.movePosition(QTextCursor.MoveOperation.Left)
            case Qt.Key.Key_J:
                cursor.movePosition(QTextCursor.MoveOperation.Down)
            case Qt.Key.Key_K:
                cursor.movePosition(QTextCursor.MoveOperation.Up)
            case Qt.Key.Key_L:
                cursor.movePosition(QTextCursor.MoveOperation.Right)
            case Qt.Key.Key_I:
                self.insert_mode = True
                self.clear_line_highlight()
            # Capital A for end of line
            case Qt.Key.Key_A:
                if e.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    self.insert_mode = True
                    cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                else:
                    cursor.movePosition(QTextCursor.MoveOperation.Right)
                    self.insert_mode = True
            case Qt.Key.Key_O:
                if e.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                    cursor.insertText("\n")
                    cursor.movePosition(QTextCursor.MoveOperation.Up)
                else:
                    cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                    cursor.insertText("\n")
            case Qt.Key.Key_D:
                if e.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                    cursor.movePosition(
                        QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor
                    )
                    # Cut text instead of removing it
                    self.yank_text(cursor)
                    cursor.removeSelectedText()
            case Qt.Key.Key_Y:
                if e.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                    cursor.movePosition(
                        QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor
                    )
                    self.yank_text(cursor)
            case Qt.Key.Key_V:
                if not e.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    self.visual_mode = True
                    self.visual_anchor = cursor.position()
                else:
                    self.visual_mode = True
                    self.select_entire_line(cursor)
            case Qt.Key.Key_P:
                self.put_text(cursor)
            case Qt.Key.Key_G:
                if self.g_pressed:
                    self.move_to_top(cursor)
                    self.g_pressed = False
                else:
                    self.move_to_bottom(cursor)
            case _:
                self.g_pressed = False

        # This separate check for Key_G ensures that the `g_pressed` state is handled correctly.
        if e.key() == Qt.Key.Key_G and not self.g_pressed:
            self.g_pressed = True
        else:
            self.setTextCursor(cursor)

        self.update_line_highlight()

    def handle_visual_mode(self, e: QKeyEvent):
        cursor = self.textCursor()

        match e.key():
            case Qt.Key.Key_Escape:
                self.exit_visual_mode(cursor)
            case Qt.Key.Key_J:
                cursor.movePosition(
                    QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.KeepAnchor
                )
            case Qt.Key.Key_K:
                cursor.movePosition(
                    QTextCursor.MoveOperation.Up, QTextCursor.MoveMode.KeepAnchor
                )
            case Qt.Key.Key_H:
                cursor.movePosition(
                    QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor
                )
            case Qt.Key.Key_L:
                cursor.movePosition(
                    QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor
                )
            case Qt.Key.Key_I:
                self.insert_mode = True
                # self.exit_visual_mode(cursor)
            case Qt.Key.Key_Y:
                self.yank_text(cursor)

        self.setTextCursor(cursor)

    def exit_visual_mode(self, cursor):
        self.visual_mode = False
        cursor.clearSelection()
        self.setTextCursor(cursor)

    def yank_text(self, cursor):
        self.yanked_text = cursor.selectedText()
        self.exit_visual_mode(cursor)

    def put_text(self, cursor):
        if self.yanked_text:
            cursor.insertText(self.yanked_text)

    def select_entire_line(self, cursor):
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.movePosition(
            QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor
        )
        self.setTextCursor(
            cursor
        )  # Set the cursor to reflect the entire line selection.

    def move_to_top(self, cursor):
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.setTextCursor(cursor)

    def move_to_bottom(self, cursor):
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self.vim_mode = False
        self.insert_mode = False
        self.visual_mode = False
        self.clear_line_highlight()




class MDEditor(VimTextEdit):
    def __init__(self):
        super().__init__()
        # Initialize syntax highlighter
        self.highlighter = MarkdownHighlighter(self.document())
