REM Create an executable
IF "%VIRTUAL_ENV%"=="" (set pshell=poetry run) else (set pshell=)

REM Generate .ui files to .py files
%pshell% python build-ui.py

REM Create an executable 
copy /y Assets\PathOfBuilding_v2.png Assets\PathOfBuilding.png
REM --disable-console
%pshell% python -m nuitka src/PathOfBuilding.py
dir PathOfBuilding.exe
pause
