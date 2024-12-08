from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet


DARK_QT_MATERIAL_THEME = "dark_teal.xml"
LIGHT_QT_MATERIAL_THEME = "light_blue.xml"

sizes = {
    -3: "10px",
    -2: "12px",
    -1: "14px",
    0: "16px",
    1: "18px",
    2: "20px",
    3: "22px",
}


def qt_material_extra(density: int):

    return {
        "font_family": "Roboto",
        "density_scale": str(density),
        "font_size": sizes[density],
    }


def apply_theme(theme_name: str, density: int = 0):
    app = QApplication.instance()
    apply_stylesheet(
        app,
        theme=theme_name,
        extra=qt_material_extra(density),
        css_file="ui/styles/style.qss",
    )


def apply_light_theme(density: int = 0):
    apply_theme(LIGHT_QT_MATERIAL_THEME, density)


def apply_dark_theme(density: int = 0):
    apply_theme(DARK_QT_MATERIAL_THEME, density)
