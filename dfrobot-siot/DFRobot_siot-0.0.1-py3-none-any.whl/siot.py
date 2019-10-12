'''
# file siot.py

# brief         download into pc or raspberryPi and run the demo
# Copyright     Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
# licence       The MIT License (MIT)
# author        [LuoYufeng](yufeng.luo@dfrobot.com)
# version       V1.0
# date          2019-10-8
'''

import threading
import paho.mqtt.client as mqtt
import time

class iot:
    client = None
    timer = None

    def __init__(self, client_id, server, port=1883, user=None, password=None):
        self._host = server
        self._port = port
        self._user = user
        self._password = password
        self.client = mqtt.Client(client_id)
        self.client.on_connect = self._on_connect

    def connect(self):
        self.client.username_pw_set(self._user, self._password)
        self.client.connect(self._host, self._port, 60)

    def publish(self, topic, data):
        self.client.publish(str(topic), str(data))
      
    def subscribe(self, topic, cb):
        self.client.on_message  = cb
        self.client.subscribe(topic)
    
    def _on_connect(self, client, userdata, flags, rc):
        if str(rc)=="0":
            print("\n连接结果: 连接成功 ")
        elif str(rc)=="1":
            print("\n连接结果: 协议版本错误 ")
        elif str(rc)=="2":
            print("\n连接结果: 无效的客户端标识 ")
        elif str(rc)=="3":
            print("\n连接结果: 服务器无法使用 ")
        elif str(rc)=="4":
            print("\n连接结果: 错误的用户名或密码 ")
        else:
            print("\n连接结果: 未经授权 ") 
    def set_callback(self, cb):
        self.client.on_message = cb
    
    def getsubscribe(self, topic):
        self.client.subscribe(topic)

    def stop(self):
        self.client.disconnect()
        if self.timer != None:
            self.timer.cancel()
     
    def loop(self, timeout=None):
        thread = threading.Thread(target=self._loop, args=(timeout,))
        # thread.setDaemon(True)
        thread.start()
        
    def _loop(self, timeout=None):
        if not timeout:
            self.client.loop_forever()
        else:
            self.client.loop(timeout)
