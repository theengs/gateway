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

import asyncio
import json
import logging
import platform
import struct
import sys
from datetime import datetime
from random import randrange
from threading import Thread
from time import time

from bleak import BleakError, BleakScanner
from bluetooth_clocks.exceptions import UnsupportedDeviceError
from bluetooth_clocks.scanners import find_clock
from paho.mqtt import client as mqtt_client

from ._decoder import decodeBLE

if platform.system() == "Linux":
    from bleak.assigned_numbers import AdvertisementDataType
    from bleak.backends.bluezdbus.advertisement_monitor import OrPattern
    from bleak.backends.bluezdbus.scanner import BlueZScannerArgs

SECONDS_IN_DAY = 86400

logger = logging.getLogger("BLEGateway")


class Gateway:
    """BLE to MQTT gateway class."""

    def __init__(
        self, broker, port, username, password, adapter, scanning_mode
    ):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.adapter = adapter
        self.scanning_mode = scanning_mode
        self.stopped = False
        self.clock_updates = {}

    def connect_mqtt(self):
        """Connect to MQTT broker."""

        def on_connect(client, userdata, flags, return_code):
            if return_code == 0:
                logger.info("Connected to MQTT Broker!")
                self.subscribe(self.sub_topic)
            else:
                logger.error(
                    "Failed to connect to MQTT broker %s:%d return code: %d",
                    self.broker,
                    self.port,
                    return_code,
                )
                self.client.connect(self.broker, self.port)

        def on_disconnect(client, userdata, return_code=0):
            logger.error("Disconnected with return code = %d", return_code)

        self.client = mqtt_client.Client()
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        try:
            self.client.connect(self.broker, self.port)
        except Exception as exception:
            logger.error(exception)

    def subscribe(self, sub_topic):
        """Subscribe to MQTT topic <sub_topic>."""

        def on_message(client_, userdata, msg):
            logger.info(
                "Received `%s` from `%s` topic",
                msg.payload.decode(),
                msg.topic,
            )
            try:
                msg_json = json.loads(str(msg.payload.decode()))
            except Exception as exception:
                logger.warning(exception)
                return
            address = msg_json["id"]
            decoded_json = decodeBLE(json.dumps(msg_json))
            if decoded_json:
                if gw.discovery:
                    gw.publish_device_info(
                        json.loads(decoded_json)
                    )  # Publish sensor data to Home Assistant MQTT discovery
                else:
                    gw.publish(
                        decoded_json,
                        gw.pub_topic + "/" + address.replace(":", ""),
                    )
            elif gw.publish_all:
                gw.publish(
                    str(msg.payload.decode()),
                    gw.pub_topic + "/" + address.replace(":", ""),
                )

        self.client.subscribe(sub_topic)
        self.client.on_message = on_message
        logger.info("Subscribed to %s", sub_topic)

    def publish(self, msg, pub_topic=None, retain=False):
        """Publish <msg> to MQTT topic <pub_topic>."""

        if not pub_topic:
            pub_topic = self.pub_topic

        result = self.client.publish(pub_topic, msg, 0, retain)
        status = result[0]
        if status == 0:
            logger.info("Sent `%s` to topic `%s`", msg, pub_topic)
        else:
            logger.error("Failed to send message to topic %s", pub_topic)

    def add_clock(self, address):
        """Register clock to synchronize its time later."""
        if address in self.time_sync and address not in self.clock_updates:
            # Add a random time in the last day as a starting point
            # for the daily update.
            # This prevents the gateway from connecting to all clocks
            # at the same time.
            start_time = time() - randrange(SECONDS_IN_DAY)
            self.clock_updates[address] = start_time
            logger.info(
                "Found device %s, synchronizing time daily beginning from %s",
                address,
                datetime.fromtimestamp(start_time + SECONDS_IN_DAY).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            )

    async def update_clock_times(self):
        """Update time for all registered clocks."""
        # Make a copy of the dictionary because we're changing it in the loop.
        for address, timestamp in self.clock_updates.copy().items():
            if time() - timestamp > SECONDS_IN_DAY:
                logger.info("Synchronizing time for clock %s...", address)

                # Find clock and try to synchronize the time
                try:
                    logger.info(f"Scanning for clock {address}...")
                    clock = await find_clock(address, self.scan_time)
                    if clock:
                        logger.info(
                            f"Writing time to {clock.DEVICE_TYPE} device..."
                        )
                        await clock.set_time(ampm=self.time_format)
                        logger.info("Synchronized time")
                    else:
                        logger.info(f"Didn't find device {address}.")
                except UnsupportedDeviceError as exc:
                    logger.error(f"Unsupported clock: {exc}")
                    # There's no point in retrying for an unsupported device.
                    del self.clock_updates[address]
                    # Just continue with the next device.
                    continue
                except asyncio.exceptions.TimeoutError as exc:
                    logger.error(f"Can't connect to clock {address}: {exc}")
                except BleakError as exc:
                    logger.error(f"Can't write to clock {address}: {exc}")
                except AttributeError as exc:
                    logger.error(
                        f"Can't get attribute from clock {address}: {exc}"
                    )

                # Register current time for this address
                this_time = time()
                self.clock_updates[address] = this_time
                logger.info(
                    "Synchronizing time with %s again on %s",
                    address,
                    datetime.fromtimestamp(
                        this_time + SECONDS_IN_DAY
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                )

    async def ble_scan_loop(self):
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
                    ]
                )
            elif self.scanning_mode == "active":
                # Disable duplicate detection of advertisement data.
                # Without this parameter non-compliant devices such as the
                # TP357/8/9 return multiple keys in manufacturer data and
                # we don't know which is the most recent data, so the sensor
                # values don't update.
                scanner_kwargs["bluez"] = BlueZScannerArgs(
                    filters=dict(DuplicateData=True)
                )

        if self.adapter:
            scanner_kwargs["adapter"] = self.adapter

        scanner_kwargs["detection_callback"] = self.detection_callback
        scanner = BleakScanner(**scanner_kwargs)
        logger.info("Starting BLE scan")
        self.running = True
        while not self.stopped:
            try:
                if self.client.is_connected():
                    await scanner.start()
                    await asyncio.sleep(self.scan_time)
                    await scanner.stop()
                    await asyncio.sleep(self.time_between_scans)

                    # Update time for all clocks once a day
                    await self.update_clock_times()
                else:
                    await asyncio.sleep(5.0)
            except Exception as exception:
                raise exception

        logger.error("BLE scan loop stopped")
        self.running = False

    def detection_callback(self, device, advertisement_data):
        """Detect device in received advertisement data."""
        logger.debug(
            "%s RSSI:%d %s", device.address, device.rssi, advertisement_data
        )

        # Try to add the device to dictionary of clocks to synchronize time.
        self.add_clock(device.address)

        data_json = {}

        if advertisement_data.service_data:
            dstr = list(advertisement_data.service_data.keys())[0]
            data_json["servicedatauuid"] = dstr[4:8]
            dstr = str(list(advertisement_data.service_data.values())[0].hex())
            data_json["servicedata"] = dstr

        if advertisement_data.manufacturer_data:
            dstr = str(
                struct.pack(
                    "<H", list(advertisement_data.manufacturer_data.keys())[0]
                ).hex()
            )
            dstr += str(
                list(advertisement_data.manufacturer_data.values())[0].hex()
            )
            data_json["manufacturerdata"] = dstr

        if advertisement_data.local_name:
            data_json["name"] = advertisement_data.local_name

        if data_json:
            data_json["id"] = device.address
            data_json["rssi"] = device.rssi
            decoded_json = decodeBLE(json.dumps(data_json))

            if decoded_json:
                if gw.discovery:
                    gw.publish_device_info(
                        json.loads(decoded_json)
                    )  # Publish sensor data to Home Assistant MQTT discovery
                else:
                    gw.publish(
                        decoded_json,
                        gw.pub_topic + "/" + device.address.replace(":", ""),
                    )
            elif gw.publish_all:
                gw.publish(
                    json.dumps(data_json),
                    gw.pub_topic + "/" + device.address.replace(":", ""),
                )


def run(arg):
    """Run BLE gateway."""
    global gw

    try:
        with open(arg, encoding="utf-8") as config_file:
            config = json.load(config_file)
    except Exception as exception:
        raise SystemExit(f"Invalid File: {sys.argv[1]}") from exception

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
            )
        except Exception as exception:
            raise SystemExit(
                "Missing or invalid MQTT host parameters"
            ) from exception

    gw.discovery = config["discovery"]
    gw.scan_time = config.get("ble_scan_time", 5)
    gw.time_between_scans = config.get("ble_time_between_scans", 0)
    gw.sub_topic = config.get("subscribe_topic", "gateway_sub")
    gw.pub_topic = config.get("publish_topic", "gateway_pub")
    gw.publish_all = config.get("publish_all", 5)
    gw.time_sync = config["time_sync"]
    gw.time_format = bool(config["time_format"])

    logging.basicConfig()
    logger.setLevel(log_level)

    loop = asyncio.get_event_loop()
    thread = Thread(target=loop.run_forever, daemon=True)
    thread.start()
    asyncio.run_coroutine_threadsafe(gw.ble_scan_loop(), loop)

    gw.connect_mqtt()

    try:
        gw.client.loop_forever()
    except (KeyboardInterrupt, SystemExit):
        gw.client.disconnect()
        gw.stopped = True
        while gw.running:
            pass
        loop.call_soon_threadsafe(loop.stop)
        thread.join()
