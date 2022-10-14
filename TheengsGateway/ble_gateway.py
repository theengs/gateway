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
from datetime import datetime
import json
import struct
import sys
import logging
import platform
from random import randrange
import time

from bleak import BleakClient, BleakError, BleakScanner
from ._decoder import decodeBLE, getProperties, getAttribute
from paho.mqtt import client as mqtt_client
from threading import Thread

if platform.system() == "Linux":
    from bleak.assigned_numbers import AdvertisementDataType
    from bleak.backends.bluezdbus.advertisement_monitor import OrPattern
    from bleak.backends.bluezdbus.scanner import BlueZScannerArgs

SECONDS_IN_HOUR = 3600
SECONDS_IN_DAY = 86400

LYWSD02_TIME_UUID = "ebe0ccb7-7a0a-4b0c-8a1a-6ff2997da3a6"

logger = logging.getLogger('BLEGateway')

class gateway:
    def __init__(self, broker, port, username, password, adapter, scanning_mode):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.adapter = adapter
        self.scanning_mode = scanning_mode
        self.stopped = False
        self.lywsd02_updates = {}

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.info("Connected to MQTT Broker!")
                self.subscribe(self.sub_topic)
            else:
                logger.error(f"Failed to connect to MQTT broker %s:%d rc: %d" % (self.broker, self.port, rc))
                self.client.connect(self.broker, self.port)

        def on_disconnect(client, userdata,rc=0):
            logger.error(f"Disconnected rc = %d" % (rc))

        self.client = mqtt_client.Client()
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        try:
            self.client.connect(self.broker, self.port)
        except:
            pass

    def subscribe(self, sub_topic):
        def on_message(client_, userdata, msg):
            logger.info(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            try:
                msg_json = json.loads(str(msg.payload.decode()))
            except:
                return
            address = msg_json["id"]
            decoded_json = decodeBLE(json.dumps(msg_json))
            if decoded_json:
                if gw.discovery:
                    gw.publish_device_info(json.loads(decoded_json)) ## publish sensor data to home assistant mqtt discovery
                else:
                    gw.publish(decoded_json, gw.pub_topic + '/' + address.replace(':', ''))
            elif gw.publish_all:
                gw.publish(str(msg.payload.decode()), gw.pub_topic + '/' + address.replace(':', ''))

        self.client.subscribe(sub_topic)
        self.client.on_message = on_message
        logger.info(f"Subscribed to {sub_topic}")


    def publish(self, msg, pub_topic=None, retain=False):
        if not pub_topic:
            pub_topic = self.pub_topic

        result = self.client.publish(pub_topic, msg, 0, retain)
        status = result[0]
        if status == 0:
            logger.info(f"Sent `{msg}` to topic `{pub_topic}`")
        else:
            logger.error(f"Failed to send message to topic {pub_topic}")

    def add_lywsd02(self, address, decoded_json):
        if json.loads(decoded_json)["model_id"] == "LYWSD02":
            if address not in self.lywsd02_updates:
                # Add a random time in the last day as a starting point for the daily update.
                # This prevents the gateway from connecting to all devices at the same time.
                self.lywsd02_updates[address] = datetime.now().timestamp() - randrange(SECONDS_IN_DAY)
                logger.info(f"Found LYWSD02 device {address}, synchronizing time daily...")

    async def update_lywsd02_time(self):
        for address, timestamp in self.lywsd02_updates.copy().items():
            if datetime.now().timestamp() - timestamp > SECONDS_IN_DAY:
                logger.info(f"Synchronizing time for LYWSD02 device {address}...")
                try:
                    async with BleakClient(address) as lywsd02_client:
                        # Set timezone offset
                        if time.daylight:
                            timezone_offset = -time.altzone // SECONDS_IN_HOUR
                        else:
                            timezone_offset = -time.timezone // SECONDS_IN_HOUR

                        # Pack data for current time and timezone
                        lywsd02_time = struct.pack('Ib', int(datetime.now().timestamp()), timezone_offset)

                        # Write time and timezone to device
                        await lywsd02_client.write_gatt_char(LYWSD02_TIME_UUID, lywsd02_time)
                        logger.info(f"Synchronized time for LYWSD02 device {address}.")
                        # Reset timestamp to synchronize again in a day
                        self.lywsd02_updates[address] = datetime.now().timestamp()
                except BleakError as e:
                    logger.error(e)
                    del self.lywsd02_updates[address]
                except asyncio.exceptions.TimeoutError:
                    logger.error(f"Can't connect to LYWSD02 device {address}.")
                    del self.lywsd02_updates[address]

    async def ble_scan_loop(self):
        scanner_kwargs = {"scanning_mode": self.scanning_mode}

        # Passive scanning with BlueZ needs at least one or_pattern.
        # The following matches all devices.
        if platform.system() == "Linux" and self.scanning_mode == "passive":
            scanner_kwargs["bluez"] = BlueZScannerArgs(
                or_patterns=[
                    OrPattern(0, AdvertisementDataType.FLAGS, b"\x06"),
                    OrPattern(0, AdvertisementDataType.FLAGS, b"\x1a"),
                ]
            )

        if self.adapter:
            scanner_kwargs["adapter"] = self.adapter

        scanner = BleakScanner(**scanner_kwargs)
        scanner.register_detection_callback(self.detection_callback)
        logger.info('Starting BLE scan')
        self.running = True
        while not self.stopped:
            try:
                if self.client.is_connected():
                    await scanner.start()
                    await asyncio.sleep(self.scan_time)
                    await scanner.stop()
                    await asyncio.sleep(self.time_between_scans)

                    # Update time for all LYWSD02 devices once a day
                    await self.update_lywsd02_time()
                else:
                    await asyncio.sleep(5.0)
            except Exception as e:
                raise e

        logger.error('BLE scan loop stopped')
        self.running = False

    def detection_callback(self, device, advertisement_data):
        logger.debug("%s RSSI:%d %s" % (device.address, device.rssi, advertisement_data))
        data_json = {}

        if advertisement_data.service_data:
            dstr = list(advertisement_data.service_data.keys())[0]
            data_json['servicedatauuid'] = dstr[4:8]
            dstr = str(list(advertisement_data.service_data.values())[0].hex())
            data_json['servicedata'] = dstr

        if advertisement_data.manufacturer_data:
            dstr = str(struct.pack('<H', list(advertisement_data.manufacturer_data.keys())[0]).hex())
            dstr += str(list(advertisement_data.manufacturer_data.values())[0].hex())
            data_json['manufacturerdata'] = dstr

        if advertisement_data.local_name:
            data_json['name'] = advertisement_data.local_name

        if data_json:
            data_json['id'] = device.address
            data_json['rssi'] = device.rssi
            decoded_json = decodeBLE(json.dumps(data_json))

            if decoded_json:
                if gw.discovery:
                    gw.publish_device_info(json.loads(decoded_json)) ## publish sensor data to home assistant mqtt discovery
                else:
                    gw.publish(decoded_json, gw.pub_topic + '/' + device.address.replace(':', ''))

                # Add new LYWSD02 devices to dictionary of devices to synchronize time
                self.add_lywsd02(device.address, decoded_json)
            elif gw.publish_all:
                gw.publish(json.dumps(data_json), gw.pub_topic + '/' + device.address.replace(':', ''))

def run(arg):
    global gw

    try:
        with open(arg) as config_file:
            config = json.load(config_file)
    except:
        raise SystemExit(f"Invalid File: {sys.argv[1]}")

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

    if config['discovery']:
        from .discovery import discovery
        gw = discovery(config["host"], int(config["port"]), config["user"],
                       config["pass"], config["adapter"], config["scanning_mode"],
                       config["discovery_topic"], config["discovery_device_name"],
                       config["discovery_filter"], config["hass_discovery"])
    else:
        try:
          gw = gateway(config["host"], int(config["port"]), config["user"], config["pass"], config["adapter"], config["scanning_mode"])
        except:
          raise SystemExit(f"Missing or invalid MQTT host parameters")

    gw.discovery = config['discovery']
    gw.scan_time = config.get("ble_scan_time", 5)
    gw.time_between_scans = config.get("ble_time_between_scans", 0)
    gw.sub_topic = config.get("subscribe_topic", "gateway_sub")
    gw.pub_topic = config.get("publish_topic", "gateway_pub")
    gw.publish_all = config.get("publish_all", 5)

    logging.basicConfig()
    logger.setLevel(log_level)

    loop = asyncio.get_event_loop()
    t = Thread(target=loop.run_forever, daemon=True)
    t.start()
    asyncio.run_coroutine_threadsafe(gw.ble_scan_loop(), loop)

    gw.connect_mqtt()

    try:
        gw.client.loop_forever()
    except(KeyboardInterrupt, SystemExit):
        gw.client.disconnect()
        gw.stopped = True
        while gw.running:
            pass
        loop.call_soon_threadsafe(loop.stop)
        t.join()

if __name__ == '__main__':
    try:
        arg = sys.argv[1]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} /path/to/config_file")
    run(arg)
