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


import asyncio
import json
import logging
import platform
import ssl
import struct
import sys
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from random import randrange
from threading import Thread
from time import time
from typing import Dict, Optional, Union

from bleak import BleakError, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from bluetooth_clocks.exceptions import UnsupportedDeviceError
from bluetooth_clocks.scanners import find_clock
from bluetooth_numbers import company
from bluetooth_numbers.exceptions import No16BitIntegerError, UnknownCICError
from paho.mqtt import client as mqtt_client
from TheengsDecoder import decodeBLE

from .decryption import UnsupportedEncryptionError, create_decryptor
from .diagnose import diagnostics

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
    company_id: Optional[int],
) -> None:
    """Add the name of the manufacturer based on the company ID."""
    if company_id is not None:
        with suppress(No16BitIntegerError, UnknownCICError):
            data["mfr"] = company[company_id]


class Gateway:
    """BLE to MQTT gateway class."""

    def __init__(
        self,
        broker: str,
        port: int,
        username: str,
        password: str,
        adapter: str,
        scanning_mode: str,
        enable_tls: bool,
        enable_websockets: bool,
    ) -> None:
        self.broker = broker
        self.port = port
        self.enable_tls = enable_tls
        self.enable_websockets = enable_websockets
        self.username = username
        self.password = password
        self.adapter = adapter
        self.scanning_mode = scanning_mode
        self.stopped = False
        self.clock_updates: Dict[str, float] = {}
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
                client.publish(self.lwt_topic, "online", 0, True)
                self.subscribe(self.sub_topic)
            else:
                logger.error(
                    "Failed to connect to MQTT broker %s:%d return code: %d",
                    self.broker,
                    self.port,
                    return_code,
                )
                self.client.connect(self.broker, self.port)

        def on_disconnect(
            client,  # noqa: ANN001,ARG001
            userdata,  # noqa: ANN001,ARG001
            return_code=0,  # noqa: ANN001
        ) -> None:
            logger.error("Disconnected with return code = %d", return_code)

        if self.enable_websockets:
            self.client = mqtt_client.Client(transport="websockets")
        else:
            self.client = mqtt_client.Client()

        if self.enable_tls:
            self.client.tls_set(
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLS,
            )

        self.client.username_pw_set(self.username, self.password)
        self.client.will_set(self.lwt_topic, "offline", 0, True)
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        try:
            self.client.connect(self.broker, self.port)
        except Exception:
            logger.exception("Connection error")

    def disconnect_mqtt(self) -> None:
        """Disconnect from the MQTT broker."""
        self.client.publish(self.lwt_topic, "offline", 0, True)
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
                if gw.presence:
                    self.hass_presence(decoded_json)
                if gw.discovery:
                    gw.publish_device_info(
                        decoded_json,
                    )  # Publish sensor data to Home Assistant MQTT discovery
                else:
                    self.publish_json(decoded_json, decoded=True)
            elif gw.publish_all:
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
        if ratio < 1.0:
            distance = pow(ratio, 10)
        else:
            distance = 0.89976 * pow(ratio, 7.7095) + 0.111
        decoded_json["distance"] = distance

    def publish(
        self,
        msg,  # noqa: ANN001
        pub_topic=None,  # noqa: ANN001
        retain=False,  # noqa: ANN001
    ) -> None:
        """Publish <msg> to MQTT topic <pub_topic>."""
        if not pub_topic:
            pub_topic = self.pub_topic

        result = self.client.publish(pub_topic, msg, 0, retain)
        status = result[0]
        if status == 0:
            logger.debug("Sent `%s` to topic `%s`", msg, pub_topic)
            self.published_messages = self.published_messages + 1
        else:
            logger.error("Failed to send message to topic %s", pub_topic)

    def add_clock(self, address: str) -> None:
        """Register clock to synchronize its time later."""
        if address in self.time_sync and address not in self.clock_updates:
            # Add a random time in the last day as a starting point
            # for the daily update.
            # This prevents the gateway from connecting to all clocks
            # at the same time.
            start_time = time() - randrange(SECONDS_IN_DAY)  # noqa: S311
            self.clock_updates[address] = start_time
            logger.info(
                "Found device %s, synchronizing time daily beginning from %s",
                address,
                datetime.fromtimestamp(start_time + SECONDS_IN_DAY).strftime(
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
                    clock = await find_clock(address, self.scan_time)
                    if clock:
                        logger.info(
                            "Writing time to %s device...",
                            clock.DEVICE_TYPE,
                        )
                        await clock.set_time(ampm=self.time_format)
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
                    datetime.fromtimestamp(
                        this_time + SECONDS_IN_DAY,
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                )

    async def ble_scan_loop(self) -> None:
        """Scan for BLE devices."""
        scanner_kwargs = {"scanning_mode": self.scanning_mode}

        if platform.system() == "Linux":
            if self.scanning_mode == "passive":
                # Passive scanning with BlueZ needs at least one or_pattern.
                # The following matches all devices.
                scanner_kwargs["bluez"] = BlueZScannerArgs(
                    or_patterns=[
                        OrPattern(0, AdvertisementDataType.FLAGS, b"\x06"),
                        OrPattern(0, AdvertisementDataType.FLAGS, b"\x1a"),
                    ],
                )  # type: ignore[assignment]
            elif self.scanning_mode == "active":
                # Disable duplicate detection of advertisement data.
                # Without this parameter non-compliant devices such as the
                # TP357/8/9 return multiple keys in manufacturer data and
                # we don't know which is the most recent data, so the sensor
                # values don't update.
                scanner_kwargs["bluez"] = BlueZScannerArgs(
                    filters={"DuplicateData": True},
                )  # type: ignore[assignment]

        if self.adapter:
            scanner_kwargs["adapter"] = self.adapter

        scanner_kwargs["detection_callback"] = self.detection_callback  # type: ignore[assignment] # noqa: E501
        scanner = BleakScanner(**scanner_kwargs)  # type: ignore[arg-type]
        logger.info("Starting BLE scan")
        self.running = True
        while not self.stopped:
            try:
                if self.client.is_connected():
                    self.published_messages = 0
                    await scanner.start()
                    await asyncio.sleep(self.scan_time)
                    await scanner.stop()
                    logger.info(
                        "Sent %s messages to MQTT",
                        self.published_messages,
                    )
                    await asyncio.sleep(self.time_between_scans)

                    # Update time for all clocks once a day
                    await self.update_clock_times()
                else:
                    await asyncio.sleep(5.0)
            except Exception:
                raise

        logger.error("BLE scan loop stopped")
        self.running = False

    def detection_callback(
        self,
        device: BLEDevice,
        advertisement_data: AdvertisementData,
    ) -> None:
        """Detect device in received advertisement data."""
        logger.debug("%s:%s", device.address, advertisement_data)

        # Try to add the device to dictionary of clocks to synchronize time.
        self.add_clock(device.address)

        data_json: DataJSONType = {}
        company_id = None

        if advertisement_data.manufacturer_data:
            # Only look at the first manufacturer data in the advertisement
            company_id = list(advertisement_data.manufacturer_data.keys())[0]
            manufacturer_data = list(
                advertisement_data.manufacturer_data.values(),
            )[0]
            dstr = str(struct.pack("<H", company_id).hex())
            dstr += str(manufacturer_data.hex())
            data_json["manufacturerdata"] = dstr

        if advertisement_data.local_name:
            data_json["name"] = advertisement_data.local_name

        if advertisement_data.service_data:
            data_json["id"] = device.address
            data_json["rssi"] = advertisement_data.rssi
            # Try to decode advertisement with service data for each UUID separately.
            for uuid, data in advertisement_data.service_data.items():
                # Copy data JSON because it gets manipulated while decoding
                data_json_copy = data_json.copy()
                data_json_copy["servicedatauuid"] = uuid[4:8]
                data_json_copy["servicedata"] = data.hex()
                self.decode_advertisement(data_json_copy, company_id)
        elif data_json:
            data_json["id"] = device.address
            data_json["rssi"] = advertisement_data.rssi
            self.decode_advertisement(data_json, company_id)

    def decode_advertisement(
        self,
        data_json: DataJSONType,
        company_id: Optional[int],
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

                if gw.presence:
                    self.hass_presence(decoded_json)

                # Handle encrypted payload
                if decoded_json.get("encr", False):
                    self.handle_encrypted_advertisement(
                        data_json,
                        decoded_json,
                    )

                # Remove advanced data
                if not gw.pubadvdata:
                    for key in ADVANCED_DATA:
                        decoded_json.pop(key, None)

                if gw.discovery:
                    gw.publish_device_info(
                        decoded_json,
                    )  # Publish sensor data to Home Assistant MQTT discovery
                else:
                    self.publish_json(decoded_json, decoded=True)
        elif gw.publish_all:
            add_manufacturer(data_json, company_id)
            self.publish_json(data_json, decoded=False)

    def publish_json(self, data_json: DataJSONType, decoded: bool) -> None:
        """Publish JSON data to MQTT."""
        message = json.dumps(data_json)
        gw.publish(
            message,
            gw.pub_topic + "/" + get_address(data_json).replace(":", ""),
        )
        if decoded and gw.presence:
            gw.publish(
                message,
                gw.presence_topic,
            )

    def handle_encrypted_advertisement(
        self,
        data_json: DataJSONType,
        decoded_json: DataJSONType,
    ) -> None:
        """Handle encrypted advertisement."""
        try:
            bindkey = bytes.fromhex(
                gw.bindkeys[get_address(decoded_json)],
            )
            decryptor = create_decryptor(
                decoded_json["model_id"],  # type: ignore[arg-type]
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


def run(conf_path: Path) -> None:
    """Run BLE gateway."""
    global gw

    try:
        with conf_path.open(encoding="utf-8") as config_file:
            config = json.load(config_file)
    except (json.JSONDecodeError, OSError) as exception:
        msg = f"Invalid File: {sys.argv[1]}"
        raise SystemExit(msg) from exception  # noqa: TRY003

    log_level = config.get("log_level", "WARNING").upper()
    if log_level == "DEBUG":
        log_level = logging.DEBUG
    elif log_level == "INFO":
        log_level = logging.INFO
    elif log_level == "WARNING":
        log_level = logging.WARNING
    elif log_level == "ERROR":
        log_level = logging.ERROR
    elif log_level == "CRITICAL":
        log_level = logging.CRITICAL
    else:
        log_level = logging.WARNING

    if config["discovery"]:
        from .discovery import DiscoveryGateway

        gw = DiscoveryGateway(
            config["host"],
            int(config["port"]),
            config["user"],
            config["pass"],
            config["adapter"],
            config["scanning_mode"],
            config["discovery_topic"],
            config["discovery_device_name"],
            config["discovery_filter"],
            config["hass_discovery"],
            config["enable_tls"],
            config["enable_websockets"],
        )
    else:
        try:
            gw = Gateway(
                config["host"],
                int(config["port"]),
                config["user"],
                config["pass"],
                config["adapter"],
                config["scanning_mode"],
                config["enable_tls"],
                config["enable_websockets"],
            )
        except Exception as exception:  # noqa: BLE001
            msg = "Missing or invalid MQTT host parameters"
            raise SystemExit(msg) from exception  # noqa: TRY003

    gw.discovery = config["discovery"]
    gw.scan_time = config.get("ble_scan_time", 5)
    gw.time_between_scans = config.get("ble_time_between_scans", 0)
    gw.sub_topic = config.get("subscribe_topic", "gateway_sub")
    gw.pub_topic = config.get("publish_topic", "gateway_pub")
    gw.lwt_topic = config["lwt_topic"]
    gw.presence_topic = config["presence_topic"]
    gw.presence = config["presence"]
    gw.publish_all = config["publish_all"]
    gw.time_sync = config["time_sync"]
    gw.time_format = bool(config["time_format"])
    gw.pubadvdata = bool(config["publish_advdata"])
    gw.bindkeys = config["bindkeys"]

    logging.basicConfig()
    logger.setLevel(log_level)

    loop = asyncio.get_event_loop()

    if log_level == logging.DEBUG:
        asyncio.run(diagnostics(conf_path))
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
