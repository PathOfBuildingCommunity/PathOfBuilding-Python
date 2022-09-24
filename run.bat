if not exist src\PoB_Main_Window.py (
	pyside6-uic Assets\PoB_Main_Window.ui -o src\PoB_Main_Window.py
)
if not exist src\PoB_rc.py (
	pyside6-rcc Assets\PoB.qrc -o src\PoB_rc.py
)
REM Change directories as settings.xml is created in the current directory. TreeData is also referenced from there.
cd src
python PathOfBuilding.py 
cd ..
pause