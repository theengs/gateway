![Iot](docs/img/logo-Theengs.png)

**Theengs Gateway** is a multi platforms, multi devices BLE to MQTT gateway that leverage the [Theengs Decoder library](https://github.com/theengs/decoder).
It retrieves data from a wide range of BLE sensors, translate these informations into a readable JSON format and push those to an MQTT broker.

Enabling integration to IOT platforms or home automation controllers like [NodeRED](https://nodered.org/), [AWS IOT](https://aws.amazon.com/fr/iot/), [Home Assistant](https://www.home-assistant.io/), [OpenHAB](https://www.openhab.org/), [FHEM](https://fhem.de/[), [IOBroker](https://www.iobroker.net/) or [DomoticZ](https://domoticz.com/).

The gateway uses the bluetooth component of your Raspberry Pi, Windows, Apple desktop, laptop or server by leveraging python and multi platform libraries.

**Theengs Gateway** can be used as a standalone solution or as a complementary solution to [OpenMQTTGateway](https://docs.openmqttgateway.com/) as it uses the same MQTT topic structure and the same payload messages. Your OpenMQTTGateway Home Automation BLE sensors integration will work also with Theengs gateway.

The gateway will retrieve data from BLE sensors from Govee, Xiaomi, Inkbird, QingPing, ThermoBeacon, ClearGrass, Blue Maestro and many more.