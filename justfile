embed-assets:
    pyside6-rcc static/static.qrc                       -o widgets/static_resources_rc.py
    pyside6-rcc static/katex/dist/katex.qrc             -o widgets/katex_resources_rc.py
    # Katex looks under /fonts first, then looks relative
    # Without this Qresource pollutes the STDOUT with warnings
    # Just make a copy of them I guess
    pyside6-rcc static/katex/dist/fonts/katex_fonts.qrc -o widgets/katex_fonts_rc.py

