Parts of this install have a depenceny on libraries from Microsoft Visual C++ Redistributable for Visual Studio 2022
If you get an error "MSVCP140.dll missing",  see bottom of this document for how to source the required files

# Install python
Download https://www.python.org/ftp/python/3.11.2/python-3.11.2-embed-amd64.zip

Extract it somewhere you can find it again. EG: c:\Python311

Add this location to your path, in Win10/11 this has been buried in settings.
- Open Settings, Click on System
- Scroll down to About. 
- On the right hand side, under "Related Settings" (Win11 is "Related Links"), select "Advanced System Settings".
    -	This will popup a system properties window, with the "Advanced" tab selected.
- Select the "Environment Variables..." button near the bottom of this window.
- Add two paths. The main python directory and the scripts directory
EG:

	C:\Python311\
	C:\Python311\Scripts\

Open a command prompt and change directory to where you cloned PathofBuilding

# Upgrade pip
```shell
python.exe -m pip install --upgrade pip
```

Install poetry and install dependencies.
```shell
pip install poetry
poetry install
```
(example output)

	Creating virtualenv pathofbuilding-python--IwoLpd0E in c:\Users\Peter\AppData\Local\pypoetry\Cache
	
	Installing dependencies from lock file

	Package operations: 22 installs, 0 updates, 0 removals
	...

Switch to the virtual environment
```shell
poetry shell
```

Run pyPoB
```shell
devel_run.cmd
```

or just it without the shell
```shell
poetry run devel_run.cmd
```


# MSVCP140.dll missing
This is the Microsoft Visual C++ Redistributable for Visual Studio 2022 (or download and install Visual Studio instead)
Download from the bottom of https://visualstudio.microsoft.com/downloads/
https://aka.ms/vs/17/release/VC_redist.x64.exe


# Creating a Windows executable.
Nuitka requires a compiler supplied by Visual Studio. Download and install the community version if you don't have a copy already
https://www.visualstudio.com/en-us/downloads/download-visual-studio-vs.aspx 
```shell
make_exe.cmd
or
poetry run make_exe.cmd
```



# Changing python versions
Whenever you change dependencies by hand in your pyproject.toml you have to take care of these points:

-    Run poetry lock --no-update afterwards. The reasons for this is, that "poetry install" takes the poetry.lock as input if it can find one and not read the pyproject.toml.

-    If you change the python version, remove the .venv before running "poetry install". 'poetry' doesn't change the python version of a .venv once it is created, because it uses the python version itself to create the virtualenv.
