
import asyncio
import json
import struct
import sys
import logging
from .ble_gateway import gateway
from TheengsDecoder import getProperties, getAttribute

class discovery(gateway):
    def __init__(self, broker, port, username, password, discovery, discovery_topic):
      super().__init__(broker, port, username, password)
      self.discovery = discovery
      self.discovery_topic = discovery_topic

    def connect_mqtt(self):
        super().connect_mqtt()
    
    def publish(self, msg, pub_topic):
        return super().publish(msg, pub_topic)
    
    def publish_device_info(self, pub_device):  ##publish sensor directly to home assistant via mqtt discovery
        print(f"publishing device `{pub_device}`")
        pub_device = pub_device
        pub_device['properties'] = json.loads(getProperties(pub_device['model_id']))
        pub_device['properties'] = pub_device['properties']['properties']
        print(type(pub_device))
        print(pub_device['properties'].keys())

        hadevice = {}
        if 'name' in pub_device:
          hadevice['name'] = pub_device['name']
        else: 
          hadevice['name'] = pub_device['id'].replace(':', '')
        hadevice['ids'] = pub_device['id'].replace(':', '')
        hadevice['manufacturer'] = pub_device['brand']
        ha = hadevice
        device = {}
        ##setup HA device
        
        pub_device_uuid = pub_device['id']
        pub_device_uuid = pub_device_uuid.replace(':', '')
        
        topic = self.discovery_topic + "/" + pub_device_uuid + "/"

        #setup entities:
        #for p in pub_device['properties']:
          
         # print(f"p: {p}")
        print(pub_device['properties'])
        data = getProperties(pub_device['model_id'])
        data = json.loads(data)
        data = data['properties']  ##attributes  
        for k in data.keys():
           print(data)
           print(f"k: {k}, type: {type(k)}")
           device['unique_id'] = pub_device['id'] + k
           device['name'] = str(pub_device['properties'][k]['name'])
           state_topic = topic + k +"/state"
           config_topic = topic + k + "/config"
           attr_topic = topic + k + "/attributes"#k = json.loads(k)                    
           device['device'] = ha
           device['schema'] = "json"
           device['state_topic'] = state_topic                     
           attributes = {}      
           attributes['rssi'] = pub_device['rssi']
           attributes['brand'] = pub_device['brand']
           attributes['id'] = pub_device['id']
           attributes['model'] = pub_device['model']
           attributes['model_id'] = pub_device['model_id']
           device['state_topic'] = state_topic
           attributes = json.dumps(attributes)
           device['json_attr_t'] = attr_topic
           if k in pub_device:
                  #if k['name']:
                    print(f"property: {k}: {pub_device[k]} {k}")
                  #attributes['unit_of_meas'] = pub_device['attributes']
                    msg = pub_device[k]
                    print(config_topic)
                    self.publish(msg, state_topic) 
                    self.publish(attributes, attr_topic) ##attribute
                    payload = json.dumps(device)
                    msg = payload
                    self.publish(msg, config_topic) ##overall device