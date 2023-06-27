REM Generate UI files to PY files
@echo off
del /q /s /f build >nul 2>&1

pip freeze > requirements.txt
python setup.py bdist_wheel

del /q /s /f build >nul 2>&1
