# Contributing to PathOfBuilding-Python

## Setting up a development installation

* This project targets Python 3.10. You can install it from
[here](https://www.python.org/downloads/release/python-3100/).
* For dependency management, we use [poetry](https://python-poetry.org/).
Install it like so (Powershell):
    ```shell
    (Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py -UseBasicParsing).Content | python -
    ```
* Run this command to clone the repository:
    ```shell
    git clone -b dev https://github.com/PathOfBuildingCommunity/PathOfBuilding.git
    ```
* Afterwards, run this command to install all dependencies:
    ```shell
    poetry install
    ```

## Before submitting your PR

### Style guide

* Code: [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* Docstrings: [PEP 257](https://www.python.org/dev/peps/pep-0257/)
* Type hints: [PEP 484](https://www.python.org/dev/peps/pep-0484/)
* Formatting: [black](https://github.com/psf/black) and
[isort](https://github.com/PyCQA/isort)
* Commit message: Follow the
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) guidelines
* Branch: Pull requests must be created against the `dev` branch. It is strongly
recommended creating a new branch off of `dev` to contain your proposed changes.

Here's a primer on the specifics:
* Class/type names: `CamelCase`
* Variable/function/module/file names: `snake_case`.
* Variables with values that do not change during program execution: `UPPER_SNAKE_CASE`.
These could be literals or enum variants.
* Mark module- or class-level implementation details by prepending a single underscore,
like `_variable`, `_method`.
* Do not shadow built-ins (even `id`, `help` and the like).
Instead, append a single underscore, like `id_`, `help_.
* Likewise for reserved keywords (`class_`, `import_`, etc.
Please no `klass`, `clazz or similar!)

In case of contradictions between individual guidelines, `black` is right.

In the specific case of third-party libraries with divergent style conventions,
follow theirs. This is in line with PEP 8.


## Getting in touch with the developers

There is a [Discord](https://discordapp.com/) server, intended for active development on
this project. If you are interested in joining, send a private message to
Cinnabarit#1341.

## Keeping your fork up to date

* Add a new remote repository and name it upstream.
    ```shell
    git remote add upstream https://github.com/PathOfBuildingCommunity/PathOfBuilding.git
    ```
* Verify that adding the remote worked.
    ```shell
    git remote -v
    ```
* Fetch all branches and their commits from upstream.
    ```shell
    git fetch upstream
    ```
* Check out your local dev branch if you haven't already.
    ```shell
    git checkout dev
    ```
* Merge all changes from upstream/dev into your local dev branch.
    ```shell
    git rebase upstream/dev
    ```
* Push your updated branch to GitHub.
    ```shell
    git push -f origin dev
    ```
