REM Generate UI files to PY files
python build-ui.py

REM Change directories as settings.xml is created in the current directory. TreeData is also referenced from there.
cd src

python PathOfBuilding.py 
cd ..