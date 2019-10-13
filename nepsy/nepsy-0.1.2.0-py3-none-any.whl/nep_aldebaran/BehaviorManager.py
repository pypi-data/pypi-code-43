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


class BehaviorManager:
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
            proxy_name ="ALBehaviorManager"
            self.proxy = ALProxy(proxy_name,self.ip,self.port)
            print ( proxy_name + " success")
        except:
            print ( proxy_name + " error")
            return False

        return True
    

    def onRun(self, input_ = "", parameters = {}, parallel = False):
        pass

    def onStop(self):
        self.proxy.stopAllBehaviors()
        



