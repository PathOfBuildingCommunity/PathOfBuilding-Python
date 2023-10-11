@echo off
REM Create an executable
pushd
cd "%~dp0.."
IF "%VIRTUAL_ENV%"=="" (set pshell=poetry run) else (set pshell=)

REM Generate .ui files to .py files
%pshell% python build-ui.py

copy /y Assets\PathOfBuilding_v2.png Assets\PathOfBuilding.png
REM --disable-console
%pshell% python -m nuitka src/PathOfBuilding.py
dir PathOfBuilding.exe
rmdir /q /s PathOfBuilding.dist PathOfBuilding.build >nul 2>&1

popd
pause
