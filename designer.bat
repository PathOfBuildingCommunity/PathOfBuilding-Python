SET DIR=%~dp0
SET PYSIDE_DESIGNER_PLUGINS=%DIR%Assets\QTDesigner.plugin  
%DIR%.venv\Lib\site-packages\PySide6\designer.exe  
REM pause
REM Generate UI files to PY files
python build-ui.py
