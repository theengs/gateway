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
          [-ll {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

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
                        Publish all beacons if true
  -sd SCAN_DUR, --scan_duration SCAN_DUR
                        BLE scan duration (seconds)
  -tb TIME_BETWEEN, --time_between TIME_BETWEEN
                        Seconds to wait between scans
  -ll {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        TheengsGateway log level
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
