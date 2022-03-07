# Install

## Install prerequisites
* Install [Python3](https://www.python.org/downloads/)
* Install [pip](https://pip.pypa.io/en/stable/installation/)

## Install Theengs Gateway
Doing so is simple as 1 command:
```shell
pip3 install TheengsGateway
```

You can access advanced configuration by typing:
```shell
python3 -m TheengsGateway -h
```

## Advanced users - Build and install
```
git clone https://github.com/theengs/gateway.git
cd gateway
git submodule update --init --recursive
python3 setup.py sdist
cd sdist
pip3 install distribution_file_name
```
:::tip
When launching the gateway you must be outside of its source code folder to avoid errors
:::