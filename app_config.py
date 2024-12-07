from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet


DARK_QT_MATERIAL_THEME = "dark_teal.xml"
LIGHT_QT_MATERIAL_THEME = "light_blue.xml"
QT_MATERIAL_extra = {
    "font_family": "Roboto",
    "density_scale": "0",
    "font_size": "13px",
}


def apply_theme(theme_name: str):
    app = QApplication.instance()
    apply_stylesheet(
        app, theme=theme_name, extra=QT_MATERIAL_extra, css_file="ui/styles/style.qss"
    )


def apply_light_theme():
    apply_theme(LIGHT_QT_MATERIAL_THEME)


def apply_dark_theme():
    apply_theme(DARK_QT_MATERIAL_THEME)
