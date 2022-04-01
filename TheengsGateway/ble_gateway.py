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
import struct
import sys
import logging

from bleak import BleakScanner
from ._decoder import decodeBLE, getProperties, getAttribute
from paho.mqtt import client as mqtt_client
from threading import Thread

logger = logging.getLogger('BLEGateway')

class gateway:
    def __init__(self, broker, port, username, password):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.stopped = False

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.info("Connected to MQTT Broker!")
                client.subscribe(self.sub_topic)
            else:
                logger.error(f"Failed to connect to MQTT broker %s:%d rc: %d" % (self.broker, self.port, rc))
                client.connect(self.broker, self.port)

        def on_disconnect(client, userdata,rc=0):
            logger.error(f"Disconnected rc = %d" % (rc))

        self.client = mqtt_client.Client()
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.connect(self.broker, self.port)

    def subscribe(self, sub_topic):
        def on_message(client_, userdata, msg):
            logger.info(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        self.client.subscribe(sub_topic)
        self.client.on_message = on_message


    def publish(self, msg, pub_topic=None):
        if not pub_topic:
            pub_topic = self.pub_topic

        result = self.client.publish(pub_topic, msg)
        status = result[0]
        if status == 0:
            logger.info(f"Sent `{msg}` to topic `{pub_topic}`")
        else:
            logger.error(f"Failed to send message to topic {pub_topic}")

    async def ble_scan_loop(self):
        scanner = BleakScanner()
        scanner.register_detection_callback(detection_callback)
        logger.info('Starting BLE scan')
        self.running = True
        while not self.stopped:
            try:
                if self.client.is_connected():
                    await scanner.start()
                    await asyncio.sleep(self.scan_time)
                    await scanner.stop()
                    await asyncio.sleep(self.time_between_scans)
                else:
                    await asyncio.sleep(5.0)
            except Exception as e:
                raise e
    
        logger.error('BLE scan loop stopped')
        self.running = False


def detection_callback(device, advertisement_data):
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
            gw.publish(decoded_json, gw.pub_topic + '/' + device.address.replace(':', ''))
        elif gw.publish_all:
            gw.publish(json.dumps(data_json), gw.pub_topic + '/' + device.address.replace(':', ''))

def run(arg):
    global gw
    try:
        with open(arg) as config_file:
            config = json.load(config_file)
    except:
        raise SystemExit(f"Invalid File: {sys.argv[1]}")

    try:
        gw = gateway(config["host"], int(config["port"]), config["user"], config["pass"])
    except:
        raise SystemExit(f"Missing or invalid MQTT host parameters")

    gw.scan_time = config.get("ble_scan_time", 5)
    gw.time_between_scans = config.get("ble_time_between_scans", 0)
    gw.sub_topic = config.get("subscribe_topic", "gateway_sub")
    gw.pub_topic = config.get("publish_topic", "gateway_pub")
    gw.publish_all = config.get("publish_all", False)

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
