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


class Leds:
    def __init__(self,ip,port=9559):
        self.ip = ip
        self.port = int(port)
        self.onLoad()

    def onLoad(self):
        try: 
            proxy_name = "ALLeds"
            self.proxy = ALProxy(proxy_name, self.ip, self.port)
            print ( proxy_name + " success")
        except:
            print ( proxy_name + " error")

    #onRun for action, onInput for peception.
    def onSetColor(self, input_ = "", parameters = {}, parallel = False):   

        led_g = "AllLeds"
        if input_ == "eyes":
            led_g = "FaceLeds"
            
        r = float(parameters["R"])*.1
        g = float(parameters["G"])*.1
        b = float(parameters["B"])*.1

        try:
            time_to_change = float(parameters["time"])
        except Exception as e: #Defualt value .5 seconds
            time_to_change = .5
        
        if parallel:
            self.proxy.post.fadeRGB(led_g,r,g,b,time_to_change)
            print ("Led color changed in parallel")
        else:
            self.proxy.fadeRGB(led_g,r,g,b,time_to_change)
            print ("Led color changed")

    def onReset(self, input_ = "", parameters = {}, parallel = False):

        led_g = "AllLeds"
        if input_ == "eyes":
            led_g = "FaceLeds"
        
        if parallel:
            self.proxy.post.reset(led_g)
            print ("Led color changed in parallel")
        else:
            self.proxy.reset(led_g)
            print ("Led color changed")


##  --------- Test  ------------
## Change the robot ip only
            
##robot_port = "9559"
##robot_name = "pepper"
##robot_ip = '192.168.11.37'
##middleware = "nanomsg"
##pattern = "survey"
##
##leds = Leds(robot_ip, robot_port)
##leds.onSetColor("eyes", {"R":0,"G":0,"B":255})
##time.sleep(4)
##leds.onSetColor("all", {"R":255,"G":0,"B":255})
##time.sleep(4)
##leds.onReset()
