REM Run the UI Designer
SET DIR=%~dp0
SET PYSIDE_DESIGNER_PLUGINS=%DIR%Assets\QTDesigner.plugin
IF "%VIRTUAL_ENV%"=="" (set pshell=poetry run) else (set pshell=)

cd "%DIR%Assets\ui_files"
%pshell% pyside6-designer

REM Generate .ui files to .py files
cd "%DIR%"
%pshell% python build-ui.py
