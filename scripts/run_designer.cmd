@echo off
REM Run the UI Designer
pushd
cd "%~dp0.."
SET DIR=%CD%
SET PYSIDE_DESIGNER_PLUGINS=%DIR%\Assets\QTDesigner.plugin
IF "%VIRTUAL_ENV%"=="" (set pshell=poetry run) else (set pshell=)

cd "%DIR%\Assets\ui_files"
%pshell% pyside6-designer

REM Generate .ui files to .py files
cd "%~dp0\.."
%pshell% python build-ui.py
popd
