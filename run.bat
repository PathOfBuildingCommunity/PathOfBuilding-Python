REM Assume PoB_UI.py needs rebuilding
REM Simple way to ensure you don't forget.

pyside6-uic PoB.ui -o src/PoB_UI.py
python src/PoB.py
