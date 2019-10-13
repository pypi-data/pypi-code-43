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

class AutonomusLife:
    def __init__(self,ip, port = 9559):
        """ Define parameters for SayText function

            Parameters
            ----------

            ip : string
               IP value of the robot

        """
        self.port = int(port)
        self.ip = ip
        self.onLoad()

    def onLoad(self):
        try: 
            proxy_name ="ALAutonomousLife"
            self.proxy = ALProxy(proxy_name,self.ip,self.port)
            print ( proxy_name + " success")
        except:
            print ( proxy_name + " error")
            return False

        return True
    

    def onRun(self, input_ = "", parameters = {}, parallel = False):
        """ Run action primitive"""
        try:
            self.proxy.setState("input_") # solotary, interactive, safeguard

                
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    def onStop(self):
        try:
            if self.proxy.getState != "disabled":
                self.proxy.setState("disabled")
        except:
            print ("Autonomus life:  already disabled")

        



