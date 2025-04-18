"""TheengsGateway - Decode things and devices and publish data to an MQTT broker.

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

# mypy: disable-error-code=attr-defined
from __future__ import annotations

import json
import re
from time import time

from TheengsDecoder import getProperties

from .ble_gateway import DataJSONType, Gateway, TnM, logger

ha_dev_classes = [
    "battery_charging",
    "battery",
    "carbon_dioxide",
    "carbon_monoxide",
    "current",
    "data_size",
    "distance",
    "door",
    "duration",
    "energy",
    "enum",
    "gas",
    "humidity",
    "illuminance",
    "irradiance",
    "lock",
    "motion",
    "moving",
    "pm1",
    "pm10",
    "pm25",
    "power_factor",
    "power",
    "precipitation_intensity",
    "precipitation",
    "pressure",
    "problem",
    "restart",
    "signal_strength",
    "sound_pressure",
    "temperature",
    "timestamp",
    "voltage",
    "water",
    "weight",
    "wind_speed",
    "window",
]

ha_dev_units = [
    "W",
    "kW",
    "V",
    "kWh",
    "A",
    "W",
    "°C",
    "°F",
    "ms",
    "s",
    "min",
    "hPa",
    "L",
    "kg",
    "lb",
    "µS/cm",
    "ppm",
    "μg/m³",
    "m³",
    "mg/m³",
    "m/s²",
    "lx",
    "Ω",
    "%",
    "bar",
    "bpm",
    "dB",
    "dBm",
    "B",
    "UV index",
    "m/s",
    "km/h",
    "°",
    "mm",
    "mm/h",
    "cm",
]


class DiscoveryGateway(Gateway):
    """BLE to MQTT gateway class with Home Assistant MQTT discovery."""

    def __init__(self, configuration: dict) -> None:
        super().__init__(configuration)
        self.discovered_entities: list[str] = []

    def publish_device_info(self, pub_device) -> None:  # noqa: ANN001
        """Publish sensor directly to Home Assistant via MQTT discovery."""
        pub_device_uuid = pub_device["id"].replace(":", "")

        pub_device_copy = self.copy_pub_device(pub_device)

        device_data = json.dumps(pub_device_copy)
        if (
            pub_device_uuid in self.discovered_entities
            or pub_device["model_id"] in self.configuration["discovery_filter"]
        ):
            logger.debug("Already discovered or filtered: %s", pub_device_uuid)
            self.publish(
                device_data,
                self.configuration["publish_topic"] + "/" + pub_device_uuid,
            )
            if self.configuration["presence"]:
                self.publish(device_data, self.configuration["presence_topic"])
            return

        logger.info("publishing device `%s`", pub_device)
        pub_device["properties"] = json.loads(
            getProperties(pub_device["model_id"]),
        )["properties"]

        hadevice = self.prepare_hadevice(pub_device_uuid, pub_device)

        discovery_topic = self.configuration["discovery_topic"]
        state_topic = self.build_state_topic(pub_device)

        data = getProperties(pub_device["model_id"])
        data = json.loads(data)
        data = data["properties"]
        entity_type = "sensor"

        for k in data:
            device: DataJSONType = {}
            device["stat_t"] = state_topic
            # device_tracker discovery
            self.publish_device_tracker(
                pub_device_uuid,
                state_topic,
                pub_device,
                hadevice,
            )
            # If the properties key is "mac" or "device", or any of the 
            # intermediate decryption decoder properties, skip its discovery
            if k in {"mac", "device", "cipher", "ctr", "mic"}:
                continue
            if k in pub_device["properties"]:
                if pub_device["properties"][k]["name"] in ha_dev_classes:
                    device["dev_cla"] = pub_device["properties"][k]["name"]
                if pub_device["properties"][k]["unit"] in ha_dev_units:
                    device["unit_of_meas"] = pub_device["properties"][k]["unit"]
                    device["state_class"] = "measurement"
                    entity_type = "sensor"
                elif pub_device["properties"][k]["unit"] == "status":
                    entity_type = "binary_sensor"
                    device["pl_on"] = True
                    device["pl_off"] = False
            device["name"] = pub_device["model_id"] + "-" + k
            device["uniq_id"] = pub_device_uuid + "-" + k
            if k == "unlocked":
                device[
                    "val_tpl"
                ] = "{% if value_json.get('unlocked') is true -%}True{%- else -%}False{%- endif %}"  # noqa: E501
            else:
                device["val_tpl"] = "{{ value_json." + k + " | is_defined }}"

            config_topic = (
                discovery_topic
                + "/"
                + entity_type
                + "/"
                + pub_device_uuid
                + "-"
                + k
                + "/config"
            )
            device["device"] = hadevice  # type: ignore[assignment]
            self.publish(json.dumps(device), config_topic, retain=True)

        self.discovered_entities.append(pub_device_uuid)
        self.publish_device_data(
            pub_device_uuid,
            device_data,
        )

    def publish_device_data(self, uuid: str, data: str) -> None:
        """Publish device data to the configured MQTT topics."""
        self.publish(data, f"{self.configuration['publish_topic']}/{uuid}")
        if self.configuration["presence"]:
            self.publish(data, self.configuration["presence_topic"])

    def prepare_hadevice(self, uuid: str, device: dict) -> dict:
        """Prepare Home Assistant device configuration."""
        return {
            "ids": [uuid],
            "cns": [["mac", uuid]],
            "mf": device["brand"],
            "mdl": device["model_id"],
            "name": device["model"] + "-" + uuid[6:],
            "via_device": self.configuration.get(
                "discovery_device_name",
                "Unknown",
            ),
        }

    def build_state_topic(self, device: dict) -> str:
        """Build state topic."""
        state_topic = (
            self.configuration["publish_topic"] + "/" + device["id"].replace(":", "")
        )
        return re.sub(
            r".+?/",
            "+/",
            state_topic,
            count=len(re.findall(r"/", state_topic)) - 1,
        )

    def publish_device_tracker(
        self,
        pub_device_uuid: str,
        state_topic: str,
        pub_device: DataJSONType,
        hadevice: dict,
    ) -> None:
        """Publish device_tracker discovery."""
        if "track" in pub_device:
            config_topic = (
                self.configuration["discovery_topic"]
                + "/device_tracker/"
                + pub_device_uuid
                + "-tracker"
                + "/config"
            )

            tracker = {}
            tracker["stat_t"] = state_topic
            tracker["name"] = pub_device["model_id"] + "-tracker"  # type: ignore[assignment,operator]
            tracker["uniq_id"] = pub_device_uuid + "-tracker"
            tracker[
                "val_tpl"
            ] = "{% if value_json.get('rssi') -%}home{%- else -%}not_home{%- endif %}"
            tracker["source_type"] = "bluetooth_le"
            tracker["device"] = hadevice  # type: ignore[assignment]

            self.publish(json.dumps(tracker), config_topic, retain=True)

    def copy_pub_device(self, device: dict) -> dict:
        """Copy pub_device and remove "track" if publish_advdata is false."""
        # Update tracker last received time
        if "track" in device:
            self.discovered_trackers[device["id"]] = TnM(
                round(time()), device["model_id"]
            )

            # Publish trackersync message
            if self.configuration["enable_multi_gtw_sync"]:
                message = json.dumps(
                    {
                        "gatewayid": self.configuration["gateway_id"],
                        "trackerid": device["id"],
                    }
                )
                self.publish(
                    message,
                    self.configuration["trackersync_topic"],
                )

                logger.debug("      Discovered Trackers: %s", self.discovered_trackers)
        pub_device_copy = device.copy()
        # Remove "track" if PUBLISH_ADVDATA is 0
        if not self.configuration["publish_advdata"] and "track" in pub_device_copy:
            pub_device_copy.pop("track", None)

        return pub_device_copy
