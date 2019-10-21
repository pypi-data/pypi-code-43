import zmq
import json
import asyncio
from ..lib.kernel import GK
from ..lib.aiomqtthelper import AioMqttHelper
from ..lib.kontext import Kontext

import paho.mqtt.client as mqtt
import socket

from datetime import datetime as dt  # this
from datetime import timedelta as td # is
from datetime import timezone as tz  # madness

class GMqttBridge(GK, AioMqttHelper):
    def __init__(self, *args, **kwargs):
        GK.__init__(self, *args, **kwargs)

    def on_connect(self, client, userdata, flags, rc):
        print("Connecting")
    
    def on_message(self, client, userdata, message):
        #if not self.got_message:
        #    self.glog.debug("Got unexpected message: {}".format(msg.decode()))
        #else:
        #    self.got_message.set_result(json.loads(message.payload.decode()))
        self.got_message.set_result(message)

    def on_disconnect(self, client, userdata, rc):
        self.disconnected.set_result(rc)

    async def paho_loop(self):
        with open(f'/etc/gilgamesh/mqtt.secret', 'r') as raw:
            cfg = json.load(raw)

        self.disconnected = self.loop.create_future()
        self.got_message = None

        self.client = mqtt.Client()
        self.client.username_pw_set(cfg['username'], cfg['password'])
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        aioh = AioMqttHelper(self.loop, self.client)

        # fixme -> get all from config
        self.client.connect(cfg['hostname'], 1883, 60)
        self.client.socket().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
        self.client.subscribe(f'gilgamesh/data_in/#')

        del cfg

        while True:
            await asyncio.sleep(1)
            self.got_message = self.loop.create_future()
            msg = await self.got_message
            self.got_message = None

            try:
                topic = msg.topic.split('/')
                topic.pop(0)
                dev_id = topic.pop(0)
                coll = topic.pop(0)
                payload = msg.payload.decode()
            except Exception as e:
                self.glog.error(f'got a bad mqtt message: {e}')

            print(dev_id, coll)
            print(payload)
            #tags = None
            #data = {}
            #tmst = dt.timestamp(dt.utcfromtimestamp(float(msg["time"]) + float(msg["msec"])/1000))
            #self.send_data(dev_id, res_name, data, unit, tags, tmst)

def mqtt_bridge_process(kcfg):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    kcfg['context'] = Kontext()
    kcfg['loop'] = loop

    bri = GMqttBridge(**kcfg)
    loop.create_task(bri.paho_loop())
    bri.start()
