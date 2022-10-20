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
1. Add the Add-on repository into the add-on store

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fmihsu81%2Faddon-theengsgw)

Or by going to Settings -> Add-ons -> Add-on store -> ⁞ (Menu) -> Repositories -> Fill in the URL `https://github.com/mihsu81/addon-theengsgw` -> Add.

2. You should now see "TheengsGateway HA Add-on" at the bottom list.
3. Click on "TheengsGateway", then click "Install".
4. Under the "Configuration" tab, change the settings appropriately (at least MQTT parameters), see [Parameters](#parameters).
5. Start the Add-on.

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
