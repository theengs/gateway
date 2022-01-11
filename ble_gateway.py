# python 3.6

import asyncio
import time
import sys
import json
import struct

from bleak import BleakScanner
from TheengsDecoder import decodeBLE as dble
from TheengsDecoder import getProperties, getAttribute
from queue import Queue
from paho.mqtt import client as mqtt_client
from threading import Thread


broker = '192.168.5.232'
port = 1883
topic = "python/mqtt"
username = ''
password = ''


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_disconnect(client, userdata,rc=0):
        print("Disconnected rc = %d\n", rc)

    global client
    client = mqtt_client.Client()
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(broker, port)


def subscribe(sub_topic = topic):
    def on_message(client_, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe(sub_topic)
    client.on_message = on_message


def publish(msg, pub_topic = topic):
    result = client.publish(pub_topic, msg)
    status = result[0]
    if status == 0:
        print(f"Sent `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def detection_callback(device, advertisement_data):
    print(device.address, "RSSI:", device.rssi, advertisement_data)
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
        if 'TxPower' in device.details:
            data_json['txpower'] = device.details['TxPower']

        data_json = dble(json.dumps(data_json))

        if data_json:
            publish(data_json)


async def scan_loop():
    scanner = BleakScanner()
    scanner.register_detection_callback(detection_callback)
    print('Starting BLE scan')
    while True:
        await asyncio.sleep(1.0)
        await scanner.start()
        await asyncio.sleep(5.0)
        await scanner.stop()


def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def run():
    connect_mqtt()
    subscribe()

    loop = asyncio.new_event_loop()
    t = Thread(target=start_background_loop, args=(loop,), daemon=True)
    t.start()

    asyncio.run_coroutine_threadsafe(scan_loop(), loop)
    client.loop_forever()


if __name__ == '__main__':
    run()

