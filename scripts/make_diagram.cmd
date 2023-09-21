@echo off
REM Make a class diagram. It's not real good, don't use it.
pushd
cd "%~dp0..\src"
IF "%VIRTUAL_ENV%"=="" (set pshell=poetry run) else (set pshell=)

%pshell% pyreverse -ASkmn -o png --source-roots dialogs,PoB,widgets,windows --colorized -d ..\docs\ .
popd
pause
