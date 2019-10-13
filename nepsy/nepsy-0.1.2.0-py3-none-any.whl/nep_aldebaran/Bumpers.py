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

class Bumpers:
    def __init__(self, memory, sharo, robot):
        self.memoryProxy = memory
        self.robot = robot
        self.sharo = sharo
        self.run = True
    
    def onRun(self):
        
        import copy
        old_proximity = "none"
        proximity = "none"
        error = False
        body = { "left": 0,  "right": 0,  "back": 0}
        old_body = copy.deepcopy(body)

        while self.run:

            try:
                r_value = memoryProxy.getData("Device/SubDeviceList/Platform/FrontRight/Bumper/Sensor/Value")
                l_value = memoryProxy.getData("Device/SubDeviceList/Platform/FrontLeft/Bumper/Sensor/Value")
                b_value = memoryProxy.getData("Device/SubDeviceList/Platform/Back/Bumper/Sensor/Value")


                if l_value > 0.4:
                    value = 1
                    if body["left"] != value:
                        data = {"primitive":"bumpers", "input":{"left":value}, "robot":self.robot}  
                        self.sharo.send_json(data)
                        body["left"] = value
                        print data

                else:
                    value = 0
                    if body["left"] != value:
                        data = {"primitive":"bumpers", "input":{"left":value}, "robot":self.robot} 
                        self.sharo.send_json(data)
                        body["left"] = value

                if r_value > 0.4:
                    value = 1
                    if body["right"] != value:
                        data = {"primitive":"bumpers", "input":{"right":value}, "robot":self.robot} 
                        self.sharo.send_json(data)
                        body["right"] = value
                        print data

                else:
                    value = 0
                    if body["right"] != value:
                        data = {"primitive":"bumpers", "input":{"right":value}, "robot":self.robot} 
                        self.sharo.send_json(data)
                        body["right"] = value

                if b_value > 0.4:
                    value = 1
                    if body["back"] != value:
                        data = {"primitive":"bumpers", "input":{"back":value}, "robot":self.robot} 
                        self.sharo.send_json(data)
                        body["back"] = value
                        print data

                else:
                    value = 0
                    if body["back"] != value:
                        data = {"primitive":"bumpers", "input":{"back":value}, "robot":self.robot}
                        self.sharo.send_json(data)
                        body["back"] = value

                old_body = copy.deepcopy(body)
            
            except:
                pass
                        
            time.sleep(.01)