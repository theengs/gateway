# Broker
The broker acts as an intermediary between TheengsGateway and your [controller](/prerequisites/controller). Consider it as a centralized hub at the heart of your home automation system. It carries on messages following a publish/subscribe mechanism.

All the events or commands could pass by the broker.

There are many choices of brokers, here are some of the most popular:
* [Mosquitto](https://mosquitto.org/) (open source)
* [Moquette](https://moquette-io.github.io/moquette/) (open source)
* [HiveMQ](https://www.hivemq.com/hivemq/features/)
* Embedded MQTT brokers (Home Assistant and openHAB)

This [comparison of MQTT implementations](https://en.wikipedia.org/wiki/Comparison_of_MQTT_implementations) on Wikipedia gives you more details about the different choices you have.
This [list of brokers](https://github.com/mqtt/mqtt.github.io/wiki/brokers) on GitHub seems to be the most exhaustive ones.
Here is also a [list of criteria for selecting a MQTT broker](https://www.hivemq.com/blog/top-10-mqtt-broker-criteria/) from HiveMQ.

Once you've installed your broker, it can be interesting to see the traffic passing to it and to publish data. There are several tools available to do this:
* [MQTT Explorer](http://mqtt-explorer.com/)
* [HiveMQ MQTT web client](https://github.com/hivemq/hivemq-mqtt-web-client)
* [MQTT FX](https://mqttfx.jensd.de/)
