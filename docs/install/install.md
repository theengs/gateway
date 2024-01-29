# Install
Several methods are available to install the gateway:

## Install Theengs Gateway as a pip package
Prerequisites:
* Install [Python3](https://www.python.org/downloads/)
* Install [pip](https://pip.pypa.io/en/stable/installation/)

Make sure to have the latest version of pip if it's already installed:

```shell
pip install --upgrade pip
```

Then install Theengs Gateway with:

```shell
pip install TheengsGateway
```

You can access advanced configuration by typing:

```shell
python3 -m TheengsGateway -h
```

## Install Theengs Gateway as a pip package in a Python virtual environment

Recent versions of Python may prevent you from installing pip packages outside a Python virtual environment. For example, this is the case in Debian 12 ("bookworm"). Install Theengs Gateway then in a virtual environment.

First install pip and the `venv` module for Python:

```shell
sudo apt update
sudo apt install python3-pip python3-venv
```

Then create a virtual environment called `theengs` and activate it:

```shell
python3 -m venv theengs
source theengs/bin/activate
```

The command prompt is then preceded by `(theengs)` to show you're working in the virtual environment. Now you can install the Theengs Gateway package:

```shell
pip install TheengsGateway
```

After this, you can access advanced configuration by typing:

```shell
python3 -m TheengsGateway -h
```

If you want to run Theengs Gateway again in another shell session, don't forget to activate the virtual environment first.

## Install Theengs Gateway as an Add ON in Home Assistant
1. Add the Add-on repository into the add-on store

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fmihsu81%2Faddon-theengsgw)

Or by going to Settings -> Add-ons -> Add-on store -> ⁞ (Menu) -> Repositories -> Fill in the URL `https://github.com/mihsu81/addon-theengsgw` -> Add.

2. You should now see **TheengsGateway HA Add-on** at the bottom list.
3. Click on **TheengsGateway**, then click **Install**.
4. Under the **Configuration** tab, change the settings appropriately (at least MQTT parameters), see [Parameters](https://github.com/mihsu81/addon-theengsgw/blob/main/theengsgateway/DOCS.md#parameters).
5. Start the Add-on.

## Install Theengs Gateway as a snap
Theengs Gateway is also packaged as a snap in the [Snap Store](https://snapcraft.io/theengs-gateway). If you have `snapd` running on your Linux distribution, which is the case by default on Ubuntu, you can install the Theengs Gateway snap as:

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

## Advanced users - Build and install

Make sure to have the latest version of pip: 

```shell
pip install --upgrade pip
```

Then clone the repository:

```
git clone https://github.com/theengs/gateway.git
cd gateway
```

Then build and install the package:

```
pip install .
```

:::tip
When launching the gateway you must be outside of its source code folder to avoid errors
:::
