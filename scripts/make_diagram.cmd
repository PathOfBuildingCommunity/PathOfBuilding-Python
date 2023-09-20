REM Make a class diagram. It's not real good, don't use it.
IF "%VIRTUAL_ENV%"=="" (set pshell=poetry run) else (set pshell=)

cd src
%pshell% pyreverse -ASkmn -o png --source-roots dialogs,PoB,widgets,windows --colorized -d ..\docs\ .
cd ..
pause
