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

# mypy: disable-error-code="name-defined,attr-defined"
from __future__ import annotations

import asyncio
import json
import logging
import platform
import ssl
import struct
from contextlib import suppress
from datetime import datetime
from random import randrange
from threading import Thread
from time import time
from typing import TYPE_CHECKING, Dict, Union

from bleak import BleakError, BleakScanner
from bluetooth_clocks.exceptions import UnsupportedDeviceError
from bluetooth_clocks.scanners import find_clock
from bluetooth_numbers import company
from bluetooth_numbers.exceptions import No16BitIntegerError, UnknownCICError
from paho.mqtt import client as mqtt_client
from TheengsDecoder import decodeBLE

if TYPE_CHECKING:
    from pathlib import Path

    from bleak.backends.device import BLEDevice
    from bleak.backends.scanner import AdvertisementData

from .decryption import UnsupportedEncryptionError, create_decryptor
from .diagnose import diagnostics
from .privacy import resolve_private_address

if platform.system() == "Linux":
    from bleak.assigned_numbers import AdvertisementDataType
    from bleak.backends.bluezdbus.advertisement_monitor import OrPattern
    from bleak.backends.bluezdbus.scanner import BlueZScannerArgs

SECONDS_IN_DAY = 86400
ADVANCED_DATA = (
    "acts",
    "cidc",
    "cipher",
    "cont",
    "ctr",
    "encr",
    "manufacturerdata",
    "mic",
    "servicedata",
    "servicedatauuid",
    "track",
)

LOG_LEVEL = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

logger = logging.getLogger("BLEGateway")

DataJSONType = Dict[str, Union[str, int, float, bool]]


def get_address(data: DataJSONType) -> str:
    """Return the device address from a data JSON."""
    try:
        return data["mac"]  # type: ignore[return-value]
    except KeyError:
        return data["id"]  # type: ignore[return-value]


def add_manufacturer(
    data: DataJSONType,
    company_id: int | None,
) -> None:
    """Add the name of the manufacturer based on the company ID."""
    if company_id is not None:
        with suppress(No16BitIntegerError, UnknownCICError):
            data["mfr"] = company[company_id]


class Gateway:
    """BLE to MQTT gateway class."""

    def __init__(
        self,
        configuration: dict,
    ) -> None:
        self.configuration = configuration
        self.stopped = False
        self.clock_updates: dict[str, float] = {}
        self.published_messages = 0

    def connect_mqtt(self) -> None:
        """Connect to MQTT broker."""

        def on_connect(
            client,  # noqa: ANN001
            userdata,  # noqa: ANN001,ARG001
            flags,  # noqa: ANN001,ARG001
            return_code,  # noqa: ANN001
        ) -> None:
            if return_code == 0:
                logger.info("Connected to MQTT Broker!")
                client.publish(
                    self.configuration["lwt_topic"],
                    "online",
                    qos=0,
                    retain=True,
                )
                self.subscribe(self.configuration["subscribe_topic"])
            else:
                logger.error(
                    "Failed to connect to MQTT broker %s:%d return code: %d",
                    self.configuration["host"],
                    self.configuration["port"],
                    return_code,
                )
                self.client.connect(
                    self.configuration["host"],
                    self.configuration["port"],
                )

        def on_disconnect(
            client,  # noqa: ANN001,ARG001
            userdata,  # noqa: ANN001,ARG001
            return_code=0,  # noqa: ANN001
        ) -> None:
            logger.error("Disconnected with return code = %d", return_code)

        if self.configuration["enable_websocket"]:
            self.client = mqtt_client.Client(transport="websockets")
        else:
            self.client = mqtt_client.Client()

        if self.configuration["enable_tls"]:
            self.client.tls_set(
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLS,
            )

        self.client.username_pw_set(
            self.configuration["user"],
            self.configuration["pass"],
        )
        self.client.will_set(
            self.configuration["lwt_topic"],
            "offline",
            qos=0,
            retain=True,
        )
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        try:
            self.client.connect(
                self.configuration["host"],
                self.configuration["port"],
            )
        except Exception:
            logger.exception("Connection error")

    def disconnect_mqtt(self) -> None:
        """Disconnect from the MQTT broker."""
        self.client.publish(
            self.configuration["lwt_topic"],
            "offline",
            qos=0,
            retain=True,
        )
        self.client.disconnect()

    def subscribe(self, sub_topic: str) -> None:
        """Subscribe to MQTT topic <sub_topic>."""

        def on_message(client, userdata, msg) -> None:  # noqa: ANN001,ARG001
            logger.info(
                "Received `%s` from `%s` topic",
                msg.payload.decode(),
                msg.topic,
            )
            try:
                msg_json = json.loads(msg.payload.decode())
            except (json.JSONDecodeError, UnicodeDecodeError) as exception:
                logger.warning(exception)
                return
            decoded_json = decodeBLE(json.dumps(msg_json))

            if decoded_json:
                decoded_json = json.loads(decoded_json)
                if self.configuration["presence"]:
                    self.hass_presence(decoded_json)
                if self.configuration["discovery"]:
                    self.publish_device_info(
                        decoded_json,
                    )  # Publish sensor data to Home Assistant MQTT discovery
                else:
                    self.publish_json(decoded_json, decoded=True)
            elif self.configuration["publish_all"]:
                self.publish_json(msg_json, decoded=False)

        self.client.subscribe(sub_topic)
        self.client.on_message = on_message
        logger.info("Subscribed to %s", sub_topic)

    def hass_presence(self, decoded_json) -> None:  # noqa: ANN001
        """Add presence information to the decoded JSON."""
        rssi = decoded_json.get("rssi", 0)
        if not rssi:
            return
        txpower = decoded_json.get("txpower", 0)
        if txpower >= 0:
            txpower = (
                -59
            )  # if tx power is not found we set a default calibration value
        logger.debug("rssi: %d, txpower: %d", rssi, txpower)
        ratio = rssi / txpower
        if ratio < 1.0:  # noqa: PLR2004
            distance = pow(ratio, 10)
        else:
            distance = 0.89976 * pow(ratio, 7.7095) + 0.111
        decoded_json["distance"] = distance

    def publish(
        self,
        msg,  # noqa: ANN001
        pub_topic=None,  # noqa: ANN001
        retain=False,  # noqa: ANN001,FBT002
    ) -> None:
        """Publish <msg> to MQTT topic <pub_topic>."""
        if not pub_topic:
            pub_topic = self.configuration["publish_topic"]

        result = self.client.publish(pub_topic, msg, 0, retain)
        status = result[0]
        if status == 0:
            logger.debug("Sent `%s` to topic `%s`", msg, pub_topic)
            self.published_messages = self.published_messages + 1
        else:
            logger.error("Failed to send message to topic %s", pub_topic)

    def add_clock(self, address: str) -> None:
        """Register clock to synchronize its time later."""
        if (
            address in self.configuration["time_sync"]
            and address not in self.clock_updates
        ):
            # Add a random time in the last day as a starting point
            # for the daily update.
            # This prevents the gateway from connecting to all clocks
            # at the same time.
            start_time = time() - randrange(SECONDS_IN_DAY)  # noqa: S311
            self.clock_updates[address] = start_time
            logger.info(
                "Found device %s, synchronizing time daily beginning from %s",
                address,
                datetime.fromtimestamp(  # noqa: DTZ006
                    start_time + SECONDS_IN_DAY,
                ).strftime(
                    "%Y-%m-%d %H:%M:%S",
                ),
            )

    async def update_clock_times(self) -> None:
        """Update time for all registered clocks."""
        # Make a copy of the dictionary because we're changing it in the loop.
        for address, timestamp in self.clock_updates.copy().items():
            if time() - timestamp > SECONDS_IN_DAY:
                logger.info("Synchronizing time for clock %s...", address)

                # Find clock and try to synchronize the time
                try:
                    logger.info("Scanning for clock %s...", address)
                    clock = await find_clock(
                        address,
                        self.configuration["ble_scan_time"],
                    )
                    if clock:
                        logger.info(
                            "Writing time to %s device...",
                            clock.DEVICE_TYPE,
                        )
                        await clock.set_time(
                            ampm=bool(self.configuration["time_format"]),
                        )
                        logger.info("Synchronized time")
                    else:
                        logger.warning("Didn't find device %s.", address)
                except UnsupportedDeviceError:
                    logger.exception("Unsupported clock")
                    # There's no point in retrying for an unsupported device.
                    del self.clock_updates[address]
                    # Just continue with the next device.
                    continue
                except asyncio.exceptions.TimeoutError:
                    logger.exception("Can't connect to clock %s.", address)
                except BleakError:
                    logger.exception("Can't write to clock %s.", address)
                except AttributeError:
                    logger.exception(
                        "Can't get attribute from clock %s.",
                        address,
                    )

                # Register current time for this address
                this_time = time()
                self.clock_updates[address] = this_time
                logger.info(
                    "Synchronizing time with %s again on %s",
                    address,
                    datetime.fromtimestamp(  # noqa: DTZ006
                        this_time + SECONDS_IN_DAY,
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                )

    async def ble_scan_loop(self) -> None:
        """Scan for BLE devices."""
        scanner_kwargs = {"scanning_mode": self.configuration["scanning_mode"]}

        if platform.system() == "Linux":
            if self.configuration["scanning_mode"] == "passive":
                # Passive scanning with BlueZ needs at least one or_pattern.
                # The following matches all devices.
                scanner_kwargs["bluez"] = BlueZScannerArgs(
                    or_patterns=[
                        OrPattern(0, AdvertisementDataType.FLAGS, b"\x06"),
                        OrPattern(0, AdvertisementDataType.FLAGS, b"\x1a"),
                    ],
                )  # type: ignore[assignment]
            elif self.configuration["scanning_mode"] == "active":
                # Disable duplicate detection of advertisement data.
                # Without this parameter non-compliant devices such as the
                # TP357/8/9 return multiple keys in manufacturer data and
                # we don't know which is the most recent data, so the sensor
                # values don't update.
                scanner_kwargs["bluez"] = BlueZScannerArgs(
                    filters={"DuplicateData": True},
                )  # type: ignore[assignment]

        if self.configuration["adapter"]:
            scanner_kwargs["adapter"] = self.configuration["adapter"]

        scanner_kwargs["detection_callback"] = self.detection_callback  # type: ignore[assignment] # noqa: E501
        scanner = BleakScanner(**scanner_kwargs)  # type: ignore[arg-type]
        logger.info("Starting BLE scan")
        self.running = True
        while not self.stopped:
            if self.client.is_connected():
                self.published_messages = 0
                try:
                    await scanner.start()
                    await asyncio.sleep(self.configuration["ble_scan_time"])
                    await scanner.stop()
                except BleakError as error:
                    logger.exception(error)  # noqa: TRY401
                    self.stopped = True
                logger.info(
                    "Sent %s messages to MQTT",
                    self.published_messages,
                )
                await asyncio.sleep(
                    self.configuration["ble_time_between_scans"],
                )

                # Update time for all clocks once a day
                await self.update_clock_times()
            else:
                await asyncio.sleep(5.0)

        logger.error("BLE scan loop stopped")
        self.running = False

    def detection_callback(
        self,
        device: BLEDevice,
        advertisement_data: AdvertisementData,
    ) -> None:
        """Detect device in received advertisement data."""
        logger.debug("%s:%s", device.address, advertisement_data)

        # Try to resolve private addresses with known IRKs
        address = device.address
        for identity, irk in self.configuration["identities"].items():
            if resolve_private_address(address, irk):
                address = identity
                logger.debug(
                    "Using identity address %s instead of random private address %s",
                    address,
                    device.address,
                )
                break

        # Try to add the device to dictionary of clocks to synchronize time.
        self.add_clock(address)

        data_json: DataJSONType = {}
        company_id = None

        if advertisement_data.manufacturer_data:
            # Only look at the first manufacturer data in the advertisement
            company_id = list(  # noqa: RUF015
                advertisement_data.manufacturer_data.keys(),
            )[0]
            manufacturer_data = list(  # noqa: RUF015
                advertisement_data.manufacturer_data.values(),
            )[0]
            dstr = str(struct.pack("<H", company_id).hex())
            dstr += str(manufacturer_data.hex())
            data_json["manufacturerdata"] = dstr

        if advertisement_data.local_name:
            data_json["name"] = advertisement_data.local_name

        if advertisement_data.service_data:
            data_json["id"] = address
            data_json["rssi"] = advertisement_data.rssi
            # Try to decode advertisement with service data for each UUID separately.
            for uuid, data in advertisement_data.service_data.items():
                # Copy data JSON because it gets manipulated while decoding
                data_json_copy = data_json.copy()
                data_json_copy["servicedatauuid"] = uuid[4:8]
                data_json_copy["servicedata"] = data.hex()
                self.decode_advertisement(data_json_copy, company_id)
        elif data_json:
            data_json["id"] = address
            data_json["rssi"] = advertisement_data.rssi
            self.decode_advertisement(data_json, company_id)

    def decode_advertisement(
        self,
        data_json: DataJSONType,
        company_id: int | None,
    ) -> None:
        """Decode device from data JSON."""
        decoded_json = decodeBLE(json.dumps(data_json))

        if decoded_json:
            decoded_json = json.loads(decoded_json)
            # Only process if the device is not a random mac address
            if decoded_json["type"] != "RMAC":
                # Only add manufacturer if device is compliant and no beacon
                if (
                    decoded_json.get("cidc", True)
                    and decoded_json.get("type", "UNIQ") != "BCON"
                ):
                    add_manufacturer(data_json, company_id)

                if self.configuration["presence"]:
                    self.hass_presence(decoded_json)

                # Handle encrypted payload
                if decoded_json.get("encr", 0) > 0:
                    decoded_json = self.handle_encrypted_advertisement(
                        data_json,
                        decoded_json,
                    )

                # Remove advanced data
                if not self.configuration["publish_advdata"]:
                    for key in ADVANCED_DATA:
                        decoded_json.pop(key, None)

                if self.configuration["discovery"]:
                    self.publish_device_info(
                        decoded_json,
                    )  # Publish sensor data to Home Assistant MQTT discovery
                else:
                    self.publish_json(decoded_json, decoded=True)
        elif self.configuration["publish_all"]:
            add_manufacturer(data_json, company_id)
            self.publish_json(data_json, decoded=False)

    def publish_json(
        self,
        data_json: DataJSONType,
        decoded: bool,  # noqa: FBT001
    ) -> None:
        """Publish JSON data to MQTT."""
        message = json.dumps(data_json)
        self.publish(
            message,
            self.configuration["publish_topic"]
            + "/"
            + get_address(data_json).replace(":", ""),
        )
        if decoded and self.configuration["presence"]:
            self.publish(
                message,
                self.configuration["presence_topic"],
            )

    def handle_encrypted_advertisement(
        self,
        data_json: DataJSONType,
        decoded_json: DataJSONType,
    ) -> DataJSONType:
        """Handle encrypted advertisement."""
        try:
            bindkey = bytes.fromhex(
                self.configuration["bindkeys"][get_address(decoded_json)],
            )
            decryptor = create_decryptor(
                decoded_json["encr"],  # type: ignore[arg-type]
            )
            decrypted_data = decryptor.decrypt(
                bindkey,
                get_address(decoded_json),
                decoded_json,
            )
            decryptor.replace_encrypted_data(
                decrypted_data,
                data_json,
                decoded_json,
            )

            # Keep encrypted properties
            cipher = decoded_json["cipher"]
            mic = decoded_json["mic"]
            ctr = decoded_json["ctr"]

            # Re-decode advertisement, this time unencrypted
            decoded_json = decodeBLE(json.dumps(data_json))
            if decoded_json:
                decoded_json = json.loads(decoded_json)  # type: ignore[arg-type]
            else:
                logger.exception(
                    "Decrypted payload not supported: `%s`",
                    data_json["servicedata"],
                )

            # Re-add encrypted properties
            decoded_json["cipher"] = cipher
            decoded_json["mic"] = mic
            decoded_json["ctr"] = ctr
        except KeyError:
            logger.exception(
                "Can't find bindkey for %s.",
                get_address(decoded_json),
            )
        except UnsupportedEncryptionError:
            logger.exception(
                "Unsupported encrypted device %s of model %s",
                get_address(decoded_json),
                decoded_json["model_id"],
            )
        except ValueError:
            logger.exception("Decryption failed")
        finally:
            return decoded_json  # noqa: B012


def run(configuration: dict, config_path: Path) -> None:
    """Run BLE gateway."""
    if configuration["discovery"]:
        from .discovery import DiscoveryGateway

        gw = DiscoveryGateway(configuration)
    else:
        gw = Gateway(configuration)  # type: ignore[assignment]

    logging.basicConfig()
    log_level = LOG_LEVEL[configuration["log_level"].upper()]
    logger.setLevel(log_level)

    loop = asyncio.get_event_loop()

    if log_level == logging.DEBUG:
        asyncio.run(diagnostics(config_path))
    thread = Thread(target=loop.run_forever, daemon=True)
    thread.start()
    asyncio.run_coroutine_threadsafe(gw.ble_scan_loop(), loop)

    gw.connect_mqtt()

    try:
        gw.client.loop_forever()
    except (KeyboardInterrupt, SystemExit):
        gw.disconnect_mqtt()
        gw.stopped = True
        while gw.running:
            pass
        loop.call_soon_threadsafe(loop.stop)
        thread.join()
