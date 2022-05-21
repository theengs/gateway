import json
from .ble_gateway import gateway, logger
from ._decoder import getProperties

ha_dev_classes = ["battery",
                  "carbon_monoxide",
                  "carbon_dioxide",
                  "humidity",
                  "illuminance",
                  "signal_strength",
                  "temperature",
                  "timestamp",
                  "pressure",
                  "power",
                  "current",
                  "energy",
                  "power_factor",
                  "voltage"]

ha_dev_units = ["W",
                "kW",
                "V",
                "A",
                "W",
                "°C",
                "°F",
                "ms",
                "s",
                "hPa",
                "kg",
                "lb",
                "µS/cm",
                "lx",
                "%",
                "dB",
                "B"]


class discovery(gateway):
    def __init__(self, broker, port, username, password, discovery,
                 discovery_topic, discovery_device_name):
        super().__init__(broker, port, username, password)
        self.discovery = discovery
        self.discovery_topic = discovery_topic
        self.discovery_device_name = discovery_device_name
        self.discovered_entities = []

    def connect_mqtt(self):
        super().connect_mqtt()

    def publish(self, msg, pub_topic):
        return super().publish(msg, pub_topic)

    # publish sensor directly to home assistant via mqtt discovery
    def publish_device_info(self, pub_device):
        pub_device_uuid = pub_device['id'].replace(':', '')
        if pub_device_uuid in self.discovered_entities:
            logger.debug("Already discovered: %s" % pub_device_uuid)
            self.publish(json.dumps(pub_device), self.pub_topic + '/' +
                         pub_device_uuid)
            return

        logger.info(f"publishing device `{pub_device}`")
        device_data = pub_device
        pub_device = pub_device
        pub_device['properties'] = json.loads(
            getProperties(pub_device['model_id']))['properties']

        hadevice = {}
        hadevice['identifiers'] = list({pub_device_uuid})
        hadevice['connections'] = [list(('mac', pub_device_uuid))]
        hadevice['manufacturer'] = pub_device['brand']
        hadevice['model'] = pub_device['model_id']
        if 'name' in pub_device:
            hadevice['name'] = pub_device['name']
        else:
            hadevice['name'] = pub_device['model']
        hadevice['via_device'] = self.discovery_device_name

        topic = self.discovery_topic + "/" + pub_device_uuid
        data = getProperties(pub_device['model_id'])
        data = json.loads(data)
        data = data['properties']

        for k in data.keys():
            device = {}
            device['stat_t'] = self.pub_topic + "/" + pub_device_uuid
            if k in pub_device['properties']:
                if pub_device['properties'][k]['name'] in ha_dev_classes:
                    device['dev_cla'] = pub_device['properties'][k]['name']
                if pub_device['properties'][k]['unit'] in ha_dev_units:
                    device['unit_of_meas'] = pub_device['properties'][k]['unit']
            device['name'] = pub_device['model_id'] + "-" + k
            device['uniq_id'] = pub_device_uuid + "-" + k
            device['val_tpl'] = "{{ value_json." + k + " | is_defined }}"
            device['state_class'] = "measurement"
            config_topic = topic + "-" + k + "/config"
            device['device'] = hadevice
            if k in pub_device:
                self.publish(json.dumps(device), config_topic)

        self.discovered_entities.append(pub_device_uuid)
        self.publish(json.dumps(device_data), topic)
