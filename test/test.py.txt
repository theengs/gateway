
import asyncio
import json
import struct
import sys
import logging

from bleak import BleakScanner
from threading import Thread
from TheengsDecoder import decodeBLE, getProperties, getAttribute

class test:

  
  async def ble_scan_loop(self):
          scanner = BleakScanner()
          scanner.register_detection_callback(detection_callback)
 #         logger.info('Starting BLE scan')
          running = True
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
    
#        logger.error('BLE scan loop stopped')
          running = False
def returnValues(device):
      properties = {}
      device = json.loads(device)
      print(device['model_id'])
      device = device['model_id']
      properties = getProperties(device)
      print(properties)
      properties = json.loads(properties)
      print(f"lol {properties}")
      #properties = properties['properties']
      print(f"properties: {properties['properties'].keys()}")
      print(f"properties: {properties['properties'].values()}")
      print(getAttribute(device, 'steps'))
      for p in properties['properties'].values():
         print(f"{p} is the key")
         print(getAttribute(device, p))
         

def detection_callback(device, advertisement_data):
  #    logger.debug("%s RSSI:%d %s" % (device.address, device.rssi, advertisement_data))
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
          data_json = decodeBLE(json.dumps(data_json))

          if data_json:
             print(data_json)
             dev = json.loads(data_json)
             if dev['model_id'] == "MiBand":
               data = getProperties(dev['model_id'])
               print(data)
               data = json.loads(data)
               data = data['properties']
               print(f"{device.attributes()} device")
               print(f"keys: {dev.keys()}")
               print(f"attributes: {getAttribute(dev['model_id'], 'steps')}")
            #print(data.keys())
            #print(dev.keys())
               returnValues(data_json)  

async def main():
    scanner = BleakScanner()
    scanner.register_detection_callback(detection_callback)
    await scanner.start()
    await asyncio.sleep(5.0)
    await scanner.stop()

    for d in scanner.discovered_devices:
        print(d)

asyncio.run(main())