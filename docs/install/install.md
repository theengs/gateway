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

## Install Theengs Gateway as an Add ON in Home Assistant
1. Open Home Assistant and navigate to the "Add-on Store". Click on the 3 dots (top right) and select "Repositories".
2. Enter `https://github.com/mihsu81/addon-theengsgw` in the box and click on "Add".
3. You should now see "TheengsGateway HA Add-on" at the bottom list.
4. Click on "TheengsGateway", then click "Install".
5. Under the "Configuration" tab, change the settings appropriately (at least MQTT parameters), see [Parameters](#parameters).
6. Start the Add-on.

## Advanced users - Build and install
```
git clone https://github.com/theengs/gateway.git
cd gateway
git submodule update --init --recursive
python3 setup.py sdist
cd dist
pip3 install distribution_file_name
```
:::tip
When launching the gateway you must be outside of its source code folder to avoid errors
:::
