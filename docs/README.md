---
title: Theengs BLE MQTT gateway
---

<!-- vale Google.Acronyms = NO -->
# Theengs BLE MQTT gateway
<!-- vale Google.Acronyms = YES-->

**Theengs Gateway** is a multi-platform, multi devices Bluetooth Low Energy (BLE) to MQTT gateway that leverages the [Theengs Decoder library](https://github.com/theengs/decoder).
It retrieves data from a wide range of [BLE sensors](https://decoder.theengs.io/devices/devices.html), including the LYWSD03MMC, CGD1, CGP1W, H5072, H5075, H5102, TH1, TH2, CGH1, CGDK2, CGPR1, RuuviTag, WS02, WS08, TPMS, MiScale, LYWSD02, LYWSDCGQ, and MiFlora, and translates this information into a readable JSON format and pushes those to an MQTT broker.

Enabling integration to Internet of Things (IoT) platforms or home automation controllers like [NodeRED](https://nodered.org/), [AWS IoT](https://aws.amazon.com/iot/), [Home Assistant](https://www.home-assistant.io/), [OpenHAB](https://www.openhab.org/), [FHEM](https://fhem.de/), [ioBroker](https://www.iobroker.net/) or [Domoticz](https://domoticz.com/).

The gateway uses the Bluetooth Low Energy adapter of your Raspberry Pi, Windows, Apple desktop, laptop, or server by leveraging Python and multi-platform libraries.

![Gateway](https://github.com/theengs/home/raw/development/docs/img/Theengs-gateway-raspberry-pi.jpg)

You can use **Theengs Gateway** as a standalone solution or as a complementary solution to [OpenMQTTGateway](https://docs.openmqttgateway.com/), as it uses the same MQTT topic structure and the same payload messages. Your OpenMQTTGateway home automation BLE sensors integration also works with Theengs Gateway.

The gateway retrieves data from BLE sensors from Govee, Xiaomi, Inkbird, Qingping, ThermoBeacon, Blue Maestro, and many more.
