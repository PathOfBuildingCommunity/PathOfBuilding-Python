# Python port of Path of Building
The goal of this repository is to eventually be able to port all of
[Path of Building](https://github.com/PathOfBuildingCommunity/PathOfBuilding)
from Lua to Python. Currently, it is mostly intended for exploring ideas on how to
accomplish this.

## Install
You'll need to have `python 3.9`, `virtualenv`, `git`, and `make` installed. Start off by cloning the repository like so:
```bash
git clone -b dev https://github.com/PathOfBuildingCommunity/PathOfBuilding-Python.git
```
Setup your local development [virtual environment](https://docs.python.org/3.9/library/venv.html) or let your IDE do the plumbing for you. 
```bash
cd PathOfBuilding-Python
python3.9 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools
```
Afterwards you are ready to install dependencies and build PoB.
```bash
make install
```

## Contributing
```bash
# [1] activate your local virtualenv
source venv/bin/activate

# [2] checkout a new branch and make your changes
git checkout -b my-new-feature-branch

# [3] make your contributions

# [4] fix formatting and imports
make format
# PoB uses black to enforce formatting and isort to fix imports
# https://github.com/ambv/black, https://github.com/timothycrosley/isort

# [5] run tests and linting
make
# there are a few sub-commands in Makefile like `test`, `mypy` and `lint`
# which you might want to use, but generally just `make` should be all you need

# [6:-4] rinse and repeat from [3] until your feature is complete

# [-3] commit 
# [-2] push
# [-1] create your pull request
```

## Usage
This project is WIP and not generally useful yet, except for developers.


Pull requests are welcome! 
## Maintainers
[@ppoelzl](https://github.com/ppoelzl)

## Licence
[MIT](https://github.com/PathOfBuildingCommunity/PathOfBuilding-Python/blob/master/LICENSE.md)
