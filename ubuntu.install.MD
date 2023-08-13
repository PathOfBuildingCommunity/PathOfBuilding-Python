Ubuntu 22.10 was installed with a "minimum" install.
python 3.10 is already installed.


Add the repo for 3.11
```shell
sudo add-apt-repository ppa:deadsnakes/ppa

```shell
sudo apt install python3.11 python3-pip python3-poetry
sudo apt install git gitk
```

- get simple access to the v3.11 python, this is because /usr/bin/python3 points to python v3.10
```shell
mkdir ~/bin
ln -s /usr/bin/python3.11 ~/bin/python
```
    ```shell
    vi ~/bashrc
    export PATH="~/bin:$PATH"
    ```
- paste the export line into your shell session also

Get the code
```shell
git clone https://github.com/pHiney/PathOfBuilding-Python.git

cd PathOfBuilding-Python
git checkout python_UI
```

If there is a poetry lock version issue, remove and regenerate 
```shell
rm poetry.lock
poetry lock
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
