REM Create an executable 
copy /y PathOfBuilding_v2.png PathOfBuilding.png
REM --disable-console
python -m nuitka src/PathOfBuilding.py
dir PathOfBuilding.exe
copy /y PathOfBuilding.exe c:\_complete\_new  
pause
