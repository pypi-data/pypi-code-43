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


class Sonars:
    def __init__(self, memory, sharo, robot, close = 0.5, middle = 1.0 , far = 1.4 , varyFar = 1.8):
        self.memoryProxy = memory
        self.robot = robot
        self.sharo = sharo
        self.run = True
        self.close = close
        self.middle = middle
        self.far = far
        self.varyFar = varyFar
    
    def onRun(self):
        
        old_proximity = "none"
        proximity = "none"
        error = False

       

        while self.run:

            try:
                front_value = self.memoryProxy.getData("Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value")
                back_value = self.memoryProxy.getData("Device/SubDeviceList/Platform/Back/Sonar/Sensor/Value")


                if front_value < self.close:
                    proximity = "close"
                elif front_value < self.middle  and front_value > self.close:
                    proximity = "middle"
                elif front_value < self.far and front_value > self.middle : 
                    proximity = "far"
                elif front_value > self.varyFar:
                    proximity = "very far"
               
                if old_proximity == proximity:
                    pass
                else:
                    print ("Human distance: " + proximity)
                    data = {"primitive":"human_distance", "input":{proximity:1}, "robot":self.robot} 
                    self.sharo.send_json(data)
            except:
                if not error:
                    print ("Sonar problem")
                    error = True
                else:
                    pass
            old_proximity = proximity
            time.sleep(.01)