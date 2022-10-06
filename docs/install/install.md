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

## Install Theengs Gateway as a snap
Theengs Gateway is also packaged as a snap in the [Snap Store](https://snapcraft.io/theengs-gateway). If you have snapd running on your Linux distribution, which is the case by default on Ubuntu, you can install the Theengs Gateway snap as:

```shell
snap install theengs-gateway
```

Have a look at the [Theengs Gateway Snap](https://github.com/theengs/gateway-snap) documentation for more information about how to configure and start Theengs Gateway as a service.

## Install Theengs Gateway as a docker
Theengs Gateway is also available from docker hub thanks to (@maretodoric)[https://github.com/maretodoric]

```shell
docker pull theengs/gateway
```

To run it with minimum required parameters required:
```shell
docker run --rm \
    --network host \
    -e MQTT_HOST=<host_ip> \
    -v /var/run/dbus:/var/run/dbus \
    --name TheengsGateway \
    theengs/gateway
```

With more parameters:
```shell
docker run --rm \
    --network host \
    -e MQTT_HOST=<host_ip> \
    -e MQTT_USERNAME=<username> \
    -e MQTT_PASSWORD=<password> \
    -e MQTT_PUB_TOPIC=home/TheengsGateway/BTtoMQTT \
    -e MQTT_SUB_TOPIC=home/TheengsGateway/commands \
    -e PUBLISH_ALL=true \
    -e TIME_BETWEEN=60 \
    -e SCAN_TIME=60 \
    -e LOG_LEVEL=DEBUG \
    -e DISCOVERY_TOPIC=homeassistant/sensor \
    -e DISCOVERY_DEVICE_NAME=TheengsGateway \
    -e DISCOVERY_FILTER="[IBEACON,GAEN,MS-CDP]" \
    -e SCANNING_MODE=active
    -e ADAPTER=hci0 \
    -v /var/run/dbus:/var/run/dbus \
    --name TheengsGateway \
    theengs/gateway
```

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
