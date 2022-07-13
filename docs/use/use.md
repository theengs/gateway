# Use

## Launching the gateway
```shell
python -m TheengsGateway -H "192.168.1.17" -u "username" -p "password"
```
`192.168.1.17` being your MQTT broker IP address.

Once the command launched you should see MQTT payloads appearing on the broker. To visualize these data you have to use an [MQTT client tool](../prerequisites/broker).

![mqtt](../img/TheengsGateway_mqtt_explorer.png)

Example payload received:
```json
{"name":"F35285","id":"F3:52:85","rssi":-82,"brand":"BlueMaestro","model":"TempoDisc","model_id":"BM_V23","tempc":24.1,"tempf":75.38,"hum":104.7,"dp":24.8,"volt":2.56}
```

## Details options
```shell
C:\Users\1technophile>python -m TheengsGateway -h
usage: -m [-h] [-H HOST] [-P PORT] [-u USER] [-p PWD] [-pt PUB_TOPIC]
          [-st SUB_TOPIC] [-pa PUBLISH_ALL] [-sd SCAN_DUR] [-tb TIME_BETWEEN]
          [-ll {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-Dt DISCOVERY_TOPIC] [-D DISCOVERY]
          [-Dn DISCOVERY_DEVICE_NAME] [-Df DISCOVERY_FILTER [DISCOVERY_FILTER ...]]
          [-a ADAPTER]

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  MQTT host address
  -P PORT, --port PORT  MQTT host port
  -u USER, --user USER  MQTT username
  -p PWD, --pass PWD    MQTT password
  -pt PUB_TOPIC, --pub_topic PUB_TOPIC
                        MQTT publish topic
  -st SUB_TOPIC, --sub_topic SUB_TOPIC
                        MQTT subscribe topic
  -pa PUBLISH_ALL, --publish_all PUBLISH_ALL
                        Enable(1) or disable(0) publishing of all beacons
  -sd SCAN_DUR, --scan_duration SCAN_DUR
                        BLE scan duration (seconds)
  -tb TIME_BETWEEN, --time_between TIME_BETWEEN
                        Seconds to wait between scans
  -ll {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        TheengsGateway log level
  -Dt DISCOVERY_TOPIC, --discovery-topic DISCOVERY_TOPIC
                        MQTT Discovery topic
  -D DISCOVERY, --discovery DISCOVERY
                        Enable(1) or disable(0) MQTT discovery
  -Dn DISCOVERY_DEVICE_NAME, --discovery_name DISCOVERY_DEVICE_NAME
                        Device name for Home Assistant
  -Df DISCOVERY_FILTER [DISCOVERY_FILTER ...], --discovery_filter DISCOVERY_FILTER [DISCOVERY_FILTER ...]
                        Device discovery filter list for Home Assistant
  -a ADAPTER, --adapter ADAPTER
                        Bluetooth adapter (e.g. hci1 on Linux)
```

## Publish to a 2 levels topic

```shell
python -m TheengsGateway -H "192.168.1.17" -u "username" -p "password" -pt "home/TheengsGateway"
```

## Scan every 55s

```shell
python -m TheengsGateway -H "192.168.1.17" -u "username" -p "password" -pt "home/TheengsGateway" -tb 55
```

## Configuration record
Once you have entered your credentials and parameters they are saved into a configuration file `theengsgw.conf` into your user directory and you can simply launch the gateway by using:
```shell
python -m TheengsGateway
```

## MQTTtoMQTT decoding
Messages sent to the subscribe topic can be used for decoding BLE data and will be published to the publish topic. This allows for offloading the decode operation from other devices, such as an ESP32, to enhance performance.

The data sent to the topic is expected to be formatted in JSON and MUST have at least an "id" entry.

Example message:
```
{
  "id":"54:94:5E:9F:64:C4",
  "mac_type":1,
  "manufacturerdata":"4c0010060319247bbc68",
  "rssi":-74,
  "txpower":12
}
```
If possible, the data will be decoded and published.

## Home Assistant auto discovery
If enabled (default), decoded devices will publish their configuration to Home Assistant to be discovered.
- This can be enabled/disabled with the `-D` or `--discovery` command line argument with a value of 1 (enable) or 0 (disable).
- The discovery topic can be set with the `-Dt` or `--discovery_topic` command line argument.
- The discovery name can be set wit the `-Dn` or `--discovery_name` command line argument.
- Devices can be filtered from discovery with the `-Df` or `--discovery_filter` argument which takes a list of device "model_id" to be filtered.

The `IBEACON`, `GAEN` and `MS-CDP` devices are already filtered as their addresses (id's) change over time resulting in multiple discoveries.
