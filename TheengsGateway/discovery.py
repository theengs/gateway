"""
  TheengsGateway - Decode things and devices and publish data to an MQTT broker

    Copyright: (c)Florian ROBERT

    This file is part of TheengsGateway.

    TheengsGateway is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    TheengsGateway is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# python 3.6
# encoding=utf8

import json
import re

from ._decoder import getProperties
from .ble_gateway import Gateway, logger

ha_dev_classes = [
    "battery",
    "carbon_monoxide",
    "carbon_dioxide",
    "humidity",
    "illuminance",
    "signal_strength",
    "temperature",
    "timestamp",
    "pressure",
    "power",
    "current",
    "energy",
    "power_factor",
    "voltage",
]

ha_dev_units = [
    "W",
    "kW",
    "V",
    "A",
    "W",
    "°C",
    "°F",
    "ms",
    "s",
    "hPa",
    "kg",
    "lb",
    "µS/cm",
    "lx",
    "%",
    "dB",
    "B",
]


class DiscoveryGateway(Gateway):
    """BLE to MQTT gateway class with Home Assistant MQTT discovery."""

    def __init__(
        self,
        broker,
        port,
        username,
        password,
        adapter,
        scanning_mode,
        discovery_topic,
        discovery_device_name,
        discovery_filter,
        hass_discovery,
    ):
        super().__init__(
            broker, port, username, password, adapter, scanning_mode
        )
        self.discovery_topic = discovery_topic
        self.discovery_device_name = discovery_device_name
        self.discovered_entities = []
        self.discovery_filter = discovery_filter
        self.hass_discovery = hass_discovery

    def publish_device_info(self, pub_device):
        """Publish sensor directly to Home Assistant via MQTT discovery."""
        pub_device_uuid = pub_device["id"].replace(":", "")
        device_data = json.dumps(pub_device)
        if (
            pub_device_uuid in self.discovered_entities
            or pub_device["model_id"] in self.discovery_filter
        ):
            logger.debug("Already discovered or filtered: %s", pub_device_uuid)
            self.publish(device_data, self.pub_topic + "/" + pub_device_uuid)
            return

        logger.info("publishing device `%s`", pub_device)
        pub_device["properties"] = json.loads(
            getProperties(pub_device["model_id"])
        )["properties"]

        hadevice = {}
        hadevice["identifiers"] = list({pub_device_uuid})
        hadevice["connections"] = [list(("mac", pub_device_uuid))]
        hadevice["manufacturer"] = pub_device["brand"]
        hadevice["model"] = pub_device["model_id"]
        if "name" in pub_device:
            hadevice["name"] = pub_device["name"]
        else:
            hadevice["name"] = pub_device["model"]
        hadevice["via_device"] = self.discovery_device_name

        discovery_topic = self.discovery_topic + "/" + pub_device_uuid
        state_topic = self.pub_topic + "/" + pub_device_uuid
        state_topic = re.sub(
            r".+?/", "+/", state_topic, len(re.findall(r"/", state_topic)) - 1
        )
        data = getProperties(pub_device["model_id"])
        data = json.loads(data)
        data = data["properties"]

        for k in data.keys():
            device = {}
            device["stat_t"] = state_topic
            if k in pub_device["properties"]:
                if pub_device["properties"][k]["name"] in ha_dev_classes:
                    device["dev_cla"] = pub_device["properties"][k]["name"]
                if pub_device["properties"][k]["unit"] in ha_dev_units:
                    device["unit_of_meas"] = pub_device["properties"][k][
                        "unit"
                    ]
            device["name"] = pub_device["model_id"] + "-" + k
            device["uniq_id"] = pub_device_uuid + "-" + k
            if self.hass_discovery == 1:
                device["val_tpl"] = "{{ value_json." + k + " | is_defined }}"
            else:
                device["val_tpl"] = "{{ value_json." + k + " }}"
            device["state_class"] = "measurement"
            config_topic = discovery_topic + "-" + k + "/config"
            device["device"] = hadevice
            self.publish(json.dumps(device), config_topic, True)

        self.discovered_entities.append(pub_device_uuid)
        self.publish(device_data, self.pub_topic + "/" + pub_device_uuid)
