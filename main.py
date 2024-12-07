import typer
from PySide6.QtWidgets import QApplication
import signal
import sys
from ui.actions_manager import create_actions
from ui.toolbar_manager import create_toolbar
from widgets.main_window import NoteApp
from app_config import apply_dark_theme, apply_light_theme

app = typer.Typer(pretty_exceptions_enable=False)


@app.command()
def main(
    api_url: str = typer.Option(
        "http://eir:37242", "--api-url", "-u", help="Base URL for the API server"
    ),
    theme: str = typer.Option(
        None,
        "--theme",
        "-t",
        help="Theme to use (e.g. 'dark_teal.xml', 'light_blue.xml')",
    ),
):
    """
    Launch the Notes application with specified configuration.
    """
    qt_app = QApplication(sys.argv)

    # Create actions first without a parent
    actions = create_actions()

    # Create window with actions and API URL
    window = NoteApp(actions, api_url=api_url)

    # Allow C-c to kill app
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Apply theme if specified
    apply_light_theme()
    # if theme:
    #     # Must be imported AFTER PySide6 / PyQt
    #     from qt_material import apply_stylesheet
    #
    #     apply_stylesheet(qt_app, theme=theme)
    # else:
    #     # Load and apply the default stylesheet
    #     with open("ui/styles/style.qss", "r") as file:
    #         qt_app.setStyleSheet(file.read())

    # Add toolbar using actions
    toolbar = create_toolbar(window, actions)
    window.addToolBar(toolbar)

    window.show()
    sys.exit(qt_app.exec())


if __name__ == "__main__":
    app()
