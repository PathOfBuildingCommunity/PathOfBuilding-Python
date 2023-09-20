REM Requires imageMagic installed (https://imagemagick.org/script/download.php#windows)
rem magick PathOfBuilding16.png PathOfBuilding24.png PathOfBuilding32.png PathOfBuilding48.png PathOfBuilding96.png PathOfBuilding256.ico -colors 256 PathOfBuilding.ico
magick PathOfBuilding256.ico -define icon:auto-resize="256,128,96,64,24,32,16" ..\PathOfBuilding.ico
pause