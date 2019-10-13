#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

# Luis Enrique Coronado Zuniga

# You are free to use, change, or redistribute the code in any way you wish
# but please maintain the name of the original author.
# This code comes with no warranty of any kind.

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import time
import os
import sys
import copy

# Template action funtion:
"""

class name:
    def __init__(self,ip,port=9559):
        self.ip = ip
        self.port = port

    def onLoad(self):
        try: 
            proxy_name "AL.."
            self.proxy = ALProxy(proxy_name, self.ip, self.port)
            print ( proxy_name + " success")
        except:
            print ( proxy_name + " error")

    #onRun for action, onInput for peception.
    def onRun(self, input_ = "", parameters = {}, parallel = "false"):   

    def onStop(self, input_ = "", parameters = {}, parallel = "false"):


"""
# Template module:
"""

class NameModule(ALModule):
    def __init__(self, name, robot, ip  port = 9559):
        ALModule.__init__(self, name)
        self.name = name
        self.robot = robot
        self.ip = ip
        self.port = port
        try: 
            proxy_name = "AL.."
            self.proxy = ALProxy(proxy_name,self.ip,self.port)
            self.memory = ALProxy("ALMemory",self.ip, self.port)
            print ( proxy_name + " success")

            try:
                self.memory.subscribeToEvent(EventName, self.name, "EventListener")
            except():
                self.memory.unsubscribeToEvent(EventName, self.name)
                self.memory.subscribeToEvent(EventName, self.name, "EventListener")

        except:
            print ( proxy_name + " error")

    def EventListener(self, key, value, message):


"""


class Touch:

    def __init__(self, memory, sharo, robot):
        self.memoryProxy = memory
        self.robot = robot
        self.sharo = sharo
        self.run = True

    def onRun(self):
        import copy
        
        body = { "left_hand": 0,  "right_hand": 0,  "head": 0}
        old_body = copy.deepcopy(body)

        while self.run:
            
            try:
                self.Lhand_touched = self.memoryProxy.getData("Device/SubDeviceList/LHand/Touch/Back/Sensor/Value")
                self.Rhand_touched = self.memoryProxy.getData("Device/SubDeviceList/RHand/Touch/Back/Sensor/Value")
                self.Head_touched = self.memoryProxy.getData("Device/SubDeviceList/Head/Touch/Middle/Sensor/Value")

                if self.Lhand_touched > 0.4:
                    value = 1
                    if body["left_hand"] != value:
                        data = {"primitive":"touched", "input":{"left_hand":value}, "robot":self.robot}
                        self.sharo.send_json(data)
                        body["left_hand"] = value
                        print data
                else:
                    value = 0
                    if body["left_hand"] != value:
                        data = {"primitive":"touched", "input":{"left_hand":value}, "robot":self.robot}
                        self.sharo.send_json(data)
                        body["left_hand"] = value

                if self.Rhand_touched > 0.4:
                    value = 1
                    if body["right_hand"] != value:
                        data = {"primitive":"touched", "input":{"right_hand":value}, "robot":self.robot}
                        self.sharo.send_json(data)
                        body["right_hand"] = value
                        print data
                else:
                    value = 0
                    if body["right_hand"] != value:
                        data = {"primitive":"touched", "input":{"right_hand":value}, "robot":self.robot}
                        self.sharo.send_json(data)
                        body["right_hand"] = value
                    
                if self.Head_touched > 0.4:
                    value = 1
                    if body["head"] != value:
                        data = {"primitive":"touched", "input":{"head":value}, "robot":self.robot}
                        self.sharo.send_json(data)
                        body["head"] = value
                        print data
                else:
                    value = 0
                    if body["head"] != value:
                        data = {"primitive":"touched", "input":{"head":value}, "robot":self.robot}
                        self.sharo.send_json(data)
                        body["head"] = value

                old_body = copy.deepcopy(body)
            except:
                pass
            time.sleep(.01)
