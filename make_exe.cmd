REM Generate UI files to PY files
python build-ui.py

REM Create an executable 
copy /y PathOfBuilding_v2.png PathOfBuilding.png
REM --disable-console
python -m nuitka src/PathOfBuilding.py
dir PathOfBuilding.exe
pause
