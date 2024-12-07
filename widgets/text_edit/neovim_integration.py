from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Signal, QTimer
import pynvim
import subprocess
import os
import asyncio
import random


SOCKET_PATH = f"/tmp/draftsmith_qt.{random.random()}.sock"


class EditorWidget(QTextEdit):
    textUpdated = Signal(str)

    def __init__(self):
        super().__init__()
        # self.setPlaceholderText("Enter your markdown here...")
        super().textChanged.connect(self.text_changed)
        self.nvim = None
        self.nvim_buffer = None
        self.is_syncing = False  # Flag to prevent recursive updates

        # Create timer for periodic Neovim checks
        self.nvim_timer = QTimer()
        self.nvim_timer.timeout.connect(self.check_nvim_changes)

    def _start_nvim_session(self):
        # Start nvim process with a socket
        socket_path = SOCKET_PATH

        # Remove existing socket if it exists
        if os.path.exists(socket_path):
            os.remove(socket_path)

        # Start nvim with socket listening and track the process
        self.nvim_process = subprocess.Popen(
            ["nvim", "--listen", socket_path, "--headless"]
        )

        # # Set filetype to markdown
        # self.nvim_process.command('set filetype=markdown')

        # Give nvim a moment to start up
        QTimer.singleShot(500, lambda: self.connect_to_nvim(socket_path))

    def connect_to_nvim(self, socket_path):
        try:
            self.nvim = pynvim.attach("socket", path=socket_path)
            self.nvim_buffer = self.nvim.current.buffer

            # Initialize nvim buffer with current text
            self.sync_to_nvim()

            # Start checking for nvim changes
            self.nvim_timer.start(20)  # Check every 20ms

            # Set filetype to markdown
            self.nvim.command(f"LspStop")
            self.nvim.command(f"set filetype=markdown")

        except Exception as e:
            print(f"Failed to connect to nvim: {e}")

    def text_changed(self):
        if not self.is_syncing:
            self.textUpdated.emit(self.toPlainText())
            self.sync_to_nvim()

    def sync_to_nvim(self):
        if self.nvim_buffer is not None:
            try:
                self.is_syncing = True
                text = self.toPlainText()
                lines = text.split("\n")
                self.nvim_buffer[:] = lines
                self.is_syncing = False
            except Exception as e:
                print(f"Failed to sync to nvim: {e}")
                self.is_syncing = False

    def cleanup_nvim(self):
        if self.nvim_timer.isActive():
            self.nvim_timer.stop()
        if self.nvim:
            try:
                self.nvim.close()
            except:
                pass

        if hasattr(self, "nvim_process"):
            try:
                self.nvim_process.terminate()
                self.nvim_process.wait(timeout=1)
            except:
                pass
            delattr(self, "nvim_process")

        self.nvim = None
        self.nvim_buffer = None
        self.is_syncing = False

        # Emit signal to update preview
        self.textUpdated.emit(self.toPlainText())

    def check_nvim_changes(self):
        if self.nvim_buffer is not None and not self.is_syncing:
            try:
                # First check if nvim process is still running
                if (
                    hasattr(self, "nvim_process")
                    and self.nvim_process.poll() is not None
                ):
                    print("Neovim process terminated")
                    self.cleanup_nvim()
                    return

                self.is_syncing = True

                # Don't do anything with an empty vim buffer
                if nvim_text := self.nvim_buffer[:]:
                    # Join with new lines
                    nvim_text = "\n".join(nvim_text)
                    # Get current text
                    current_text = self.toPlainText()

                    # Only update if different
                    if nvim_text != current_text:
                        # Update QTextEdit
                        self.setPlainText(nvim_text)

                        # Restore cursor position
                        cursor_position = self.textCursor().position()
                        cursor = self.textCursor()
                        cursor.setPosition(min(cursor_position, len(nvim_text)))
                        self.setTextCursor(cursor)

                        self.textUpdated.emit(nvim_text)

                self.is_syncing = False
            except (BrokenPipeError, ConnectionResetError):
                print("Neovim connection lost")
                self.cleanup_nvim()
            except Exception as e:
                print(f"Failed to check nvim changes: {e}")
                self.is_syncing = False

    def closeEvent(self, event):
        self.cleanup_nvim()
        super().closeEvent(event)

    def start_nvim_session(self):
        # Start nvim server
        self._start_nvim_session()

        # Start neovide
        subprocess.Popen(["neovide", "--server", SOCKET_PATH])


async def run_async_command(command):
    # Create a subprocess using asyncio
    process = await asyncio.create_subprocess_exec(
        *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    # Wait for the process to finish and collect the output
    stdout, stderr = await process.communicate()

    # Return the output and error, decoded to a string
    return stdout.decode().strip(), stderr.decode().strip()
