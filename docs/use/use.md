# Use

## Launching the gateway

### For a regular installation
```shell
python -m TheengsGateway -H "<mqtt_broker_host_ip>" -u "username" -p "password"
```

### For a Docker container
To run it with minimum required parameters required:
```shell
docker run --rm \
    --network host \
    -e MQTT_HOST=<mqtt_broker_host_ip> \
    -v /var/run/dbus:/var/run/dbus \
    --name TheengsGateway \
    theengs/gateway
```

:::tip
If your mqtt broker is installed on the same instance as the gateway you can use `localhost` as the `<mqtt_broker_host_ip>`.
:::

### Checking the data published by the gateway
Once the command launched you should see MQTT payloads appearing on the broker. To visualize these data you have to use an [MQTT client tool](../prerequisites/broker).

![mqtt](../img/TheengsGateway_mqtt_explorer.png)

Example payload received:
```json
{"name":"F35285","id":"F3:52:85","rssi":-82,"brand":"BlueMaestro","model":"TempoDisc","model_id":"BM_V23","tempc":24.1,"tempf":75.38,"hum":104.7,"dp":24.8,"volt":2.56,"mfr":"Blue Maestro Limited"}
```

The `mfr` key has the company name of the manufacturer as its value in two cases:

* The advertisement of the device has been successfully decoded, its manufacturer data have a company ID compliant to the Bluetooth specification, and it's no beacon (iBeacon, Microsoft Advertising Beacon).
* The advertisement of the device can't be decoded.

Note that in the latter case, we can't guarantee that the manufacturer name is correct, as many devices are not compliant to the Bluetooth specification and encode their data in the bytes where the manufacturer ID should be.

## Details options
### For a regular installation

```shell
C:\Users\1technophile>python -m TheengsGateway -h
usage: -m [-h] [-H HOST] [-P PORT] [-u USER] [-p PWD] [-pt PUB_TOPIC]
          [-st SUB_TOPIC] [-pa PUBLISH_ALL] [-sd SCAN_DUR] [-tb TIME_BETWEEN]
          [-ll {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-Dt DISCOVERY_TOPIC] [-D DISCOVERY] [-Dh HASS_DISCOVERY]
          [-Dn DISCOVERY_DEVICE_NAME] [-Df DISCOVERY_FILTER [DISCOVERY_FILTER ...]]
          [-prt PRESENCE_TOPIC] [-pr PUBLISH_PRESENCE]
          [-a ADAPTER] [-s {active,passive}]

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
                        Publish all (1) or only decoded (0) advertisements (default:
                        1)
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
  -Dh HASS_DISCOVERY, --hass_discovery HASS_DISCOVERY
                        Enable(1) or disable(0) Home Assistant-specific MQTT
                        discovery (default: 1)                        
  -Dn DISCOVERY_DEVICE_NAME, --discovery_name DISCOVERY_DEVICE_NAME
                        Device name for Home Assistant
  -Df DISCOVERY_FILTER [DISCOVERY_FILTER ...], --discovery_filter DISCOVERY_FILTER [DISCOVERY_FILTER ...]
                        Device discovery filter list for Home Assistant
  -prt PRESENCE_TOPIC, --presence_topic PRESENCE_TOPIC
                        MQTT topic to publish presence messages
  -pr PUBLISH_PRESENCE, --presence PUBLISH_PRESENCE
                        Enable (1) or disable (0) publishing presence messages
  -a ADAPTER, --adapter ADAPTER
                        Bluetooth adapter (e.g. hci1 on Linux)
  -s {active,passive}, --scanning_mode {active,passive}
                        Scanning mode (default: active)
  -ts TIME_SYNC [TIME_SYNC ...], --time_sync TIME_SYNC [TIME_SYNC ...]
                        Addresses of Bluetooth devices to synchronize the time
  -tf TIME_FORMAT, --time_format TIME_FORMAT
                        Use 12-hour (1) or 24-hour (0) time format for clocks
                        (default: 0)
```

### For a Docker container

```shell
docker run --rm \
    --network host \
    -e MQTT_HOST=<host_ip> \
    -e MQTT_USERNAME=<username> \
    -e MQTT_PASSWORD=<password> \
    -e MQTT_PUB_TOPIC=home/TheengsGateway/BTtoMQTT \
    -e MQTT_SUB_TOPIC=home/+/BTtoMQTT/undecoded \
    -e PUBLISH_ALL=true \
    -e TIME_BETWEEN=60 \
    -e SCAN_TIME=60 \
    -e LOG_LEVEL=DEBUG \
    -e HAAS_DISCOVERY=true \
    -e DISCOVERY=true \
    -e DISCOVERY_TOPIC=homeassistant/sensor \
    -e DISCOVERY_DEVICE_NAME=TheengsGateway \
    -e DISCOVERY_FILTER="[IBEACON,GAEN,MS-CDP]" \
    -e SCANNING_MODE=active
    -e ADAPTER=hci0 \
    -v /var/run/dbus:/var/run/dbus \
    --name TheengsGateway \
    theengs/gateway
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

[OpenMQTTGateway](https://docs.openmqttgateway.com/), proposes a [web upload](https://docs.openmqttgateway.com/upload/web-install.html) binary `esp32dev-ble-mqtt-undecoded` that will publish directly to 'home/<gateway name>/BTtoMQTT` making it directly compatible with Theengs Gateway MQTTtoMQTT decoding feature.

:::tip
By default Theengs Gateway will listen to `home/+/BTtoMQTT/undecoded`, if you have several ESP32 gateways with OpenMQTTGateway undecoded, Theengs will pickup all of them and centralize the decoded BT sensor data in one place.
:::

## Home Assistant auto discovery
If enabled (default), decoded devices will publish their configuration to Home Assistant to be discovered.
- This can be enabled/disabled with the `-D` or `--discovery` command line argument with a value of 1 (enable) or 0 (disable).
- If you want to use Home Assistant discovery with other home automation gateways such as openHAB, set `-Dh` or `--hass_discovery` to 0 (disable).
- The discovery topic can be set with the `-Dt` or `--discovery_topic` command line argument.
- The discovery name can be set wit the `-Dn` or `--discovery_name` command line argument.
- Devices can be filtered from discovery with the `-Df` or `--discovery_filter` argument which takes a list of device "model_id" to be filtered.

The `IBEACON`, `GAEN` and `MS-CDP` devices are already filtered as their addresses (id's) change over time resulting in multiple discoveries.

## Passive scanning
Passive scanning (`-s passive` or `--scanning_mode passive`) only works on Windows or Linux kernel >= 5.10 and BlueZ >= 5.56 with experimental features enabled.

To enable experimental features in BlueZ on a Linux distribution that uses systemd, run the following command:

```shell
sudo systemctl edit bluetooth.service
```

Then add the following lines:

```
[Service]
ExecStart=
ExecStart=/usr/lib/bluetooth/bluetoothd --experimental
```

Save and close the file and then run the following commands:

```
sudo systemctl daemon-reload
sudo systemctl restart bluetooth.service
```

## Time synchronization
If you have specified the MAC addresses of [supported Bluetooth clocks](https://bluetooth-clocks.readthedocs.io/en/latest/devices.html) with the `--time_sync` argument, Theengs Gateway automatically synchronizes their time once a day. Therefore, make sure that your gateway's time is set correctly.

Some Bluetooth clocks let you choose between 12-hour (AM/PM) and 24-hour format to show their time. Use the argument `--time_format 0` (default) for 24-hour format and `--time_format 1` for 12-hour format.

Note that the first time synchronization of each specified clock will happen at a random time in the next day. This way the connections to these devices will be spaced out in time. After this first time synchronization, Theengs Gateway will synchronize its time every 24 hours.

If a device isn't recognized as a supported clock, Theengs Gateway won't try to synchronize its time ever. But if there are other errors, such as connection errors or write errors (which could be temporary), the device will still be tried every 24 hours.

If you want to know which of your devices are supported by Theengs Gateway's time synchronization feature, run the following command:

```
bluetooth-clocks discover
```

The `bluetooth-clocks` command is installed as part of Theengs Gateway.
