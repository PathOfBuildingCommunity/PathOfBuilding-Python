If running in a VM and poetry hangs, disable IPv6 as per https://www.suse.com/support/kb/doc/?id=000016980 and 10.2.2 of https://wiki.archlinux.org/title/IPv6 and reboot.

# openSuSE 15.4
For Tumbleweed, see further down.

Install packages
```shell
sudo zypper in python310-pip
sudo zypper in git gitk
```

Get simple access to the v3.10 python, this is because /usr/bin/python points to python v3.6
```shell
ln -s /usr/bin/python3.10 ~/bin/python
ln -s /usr/bin/pip3.10 ~/bin/pip
```

Get the code
```shell
git clone https://github.com/pHiney/PathOfBuilding-Python.git

cd PathOfBuilding-Python
git checkout python_UI
```

Install poetry and install dependencies.
pip install poetry

-  Note the path warnings, add it to the path in ~/bashrc
    ```shell
    vi ~/bashrc
    export PATH="~/.local/bin:$PATH"
    ```
- paste the export line into your shell session also

Install dependencies
```shell
poetry install
```

Switch to the poetry environent
```shell
poetry shell
```

```shell
./run
```

# Tumbleweed
The main change here is that newer versions of python are available

Find what version is available. 3.11 at the time of writing. Do not go past the recommended version. We want the same version on Windows and Linux.
```shell
sudo zypper se python3 | grep "\-pip "
```
```
#Example output
  | python39-pip                                               | A Python package management system                                              | package
i | python310-pip                                              | A Python package management system                                              | package
  | python311-pip                                              | A Python package management system                                              | package
```

Install packages
```shell
sudo zypper in python311-pip
sudo zypper in git gitk
```shell

- get simple access to the v3.11 python, this is because /usr/bin/python points to python v2.7
```shell
ln -s /usr/bin/python3.11 ~/bin/python
ln -s /usr/bin/pip3.11 ~/bin/pip
```

Get the code
```shell
cd ~
git clone https://github.com/pHiney/PathOfBuilding-Python.git

cd PathOfBuilding-Python
git checkout python_UI
```

Install poetry and install dependencies.
```shell
pip install poetry
```

Install dependencies
```shell
poetry install
```

Switch to the poetry environent
```shell
poetry shell
```

```shell
./run
```


# Tumbleweed thru WSL2 and MS App store
You will need to install some GUI components. Use one of the following to suit your preferences. xfce will have the smallest foot print.
```shell
sudo zypper in --no-recommends -t pattern xfce
sudo zypper in --no-recommends -t pattern kde
sudo zypper in --no-recommends -t pattern gnome
```
