REM Update ui files if needed and run pyPoB
IF "%VIRTUAL_ENV%"=="" set pshell=poetry run

REM Generate .ui files to .py files
%pshell% python build-ui.py

REM Change directories as settings.xml is created in the current directory. TreeData is also referenced from there.
cd src

%pshell% python PathOfBuilding.py 
cd ..
