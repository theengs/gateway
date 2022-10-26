**Theengs Gateway** is a multi platforms, multi devices BLE to MQTT gateway that leverages the [Theengs Decoder library](https://github.com/theengs/decoder).
It retrieves data from a wide range of [BLE sensors](https://theengs.github.io/gateway/prerequisites/devices.html); LYWSD03MMC, CGD1, CGP1W, H5072, H5075, H5102, TH1, TH2, BBQ, CGH1, CGDK2, CGPR1, RuuviTag, WS02, WS08, TPMS, MiScale, LYWSD02, LYWSDCGQ, MiFlora... translates this information into a readable JSON format and pushes those to an MQTT broker.

Enabling integration to IOT platforms or home automation controllers like [NodeRED](https://nodered.org/), [AWS IOT](https://aws.amazon.com/iot/), [Home Assistant](https://www.home-assistant.io/), [OpenHAB](https://www.openhab.org/), [FHEM](https://fhem.de/), [IOBroker](https://www.iobroker.net/) or [DomoticZ](https://domoticz.com/).

The gateway uses the bluetooth component of your Raspberry Pi, Windows, Apple desktop, laptop or server by leveraging python and multi platform libraries.

![Gateway](https://github.com/theengs/home/raw/development/docs/img/Theengs-gateway-raspberry-pi.jpg)

**Theengs Gateway** can be used as a standalone solution or as a complementary solution to [OpenMQTTGateway](https://docs.openmqttgateway.com/) as it uses the same MQTT topic structure and the same payload messages. Your OpenMQTTGateway Home Automation BLE sensors integration will work also with Theengs gateway.

The gateway will retrieve data from BLE sensors from Govee, Xiaomi, Inkbird, QingPing, ThermoBeacon, ClearGrass, Blue Maestro and many more.

Full documentation for installation and usage can be found [here](https://theengs.github.io/gateway)

## Install Theengs Gateway as a pip package
Prerequisites:
* Install [Python3](https://www.python.org/downloads/)
* Install [pip](https://pip.pypa.io/en/stable/installation/)

Command:
```shell
pip install TheengsGateway
```
You can access advanced configuration by typing:
```shell
python3 -m TheengsGateway -h
```

## Install Theengs Gateway as an Add ON in Home Assistant
1. Add the Add-on repository into the add-on store

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fmihsu81%2Faddon-theengsgw)

Or by going to Settings -> Add-ons -> Add-on store -> ⁞ (Menu) -> Repositories -> Fill in the URL `https://github.com/mihsu81/addon-theengsgw` -> Add.

2. You should now see "TheengsGateway HA Add-on" at the bottom list.
3. Click on "TheengsGateway", then click "Install".
4. Under the "Configuration" tab, change the settings appropriately (at least MQTT parameters), see [Parameters](#parameters).
5. Start the Add-on.

## Install Theengs Gateway as a snap
Theengs Gateway is also packaged as a snap in the [Snap Store](https://snapcraft.io/theengs-gateway). If you have snapd running on your Linux distribution, which is the case by default on Ubuntu, you can install the Theengs Gateway snap as:

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-white.svg)](https://snapcraft.io/theengs-gateway)

```shell
snap install theengs-gateway
```

Have a look at the [Theengs Gateway Snap](https://github.com/theengs/gateway-snap) documentation for more information about how to configure and start Theengs Gateway as a service.

## Install Theengs Gateway as a docker
Theengs Gateway is also available from docker hub thanks to [@maretodoric](https://github.com/maretodoric)

<img alt="Docker Image Size (latest by date)" src="https://img.shields.io/docker/image-size/theengs/gateway">

```shell
docker pull theengs/gateway
```
