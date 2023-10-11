@echo off
REM Build a Wheel file for distribution
pushd
cd "%~dp0.."
IF "%VIRTUAL_ENV%"=="" (set pshell=poetry run) else (set pshell=)

rmdir /q /s build >nul 2>&1
%pshell% pip freeze > requirements.txt
%pshell% python setup.py bdist_wheel
rmdir /q /s build >nul 2>&1
popd
pause
