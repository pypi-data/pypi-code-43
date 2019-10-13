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

class Audio:
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
            proxy_name ="ALAudioPlayer"
            self.proxy = ALProxy(proxy_name,self.ip,self.port)
            print ( proxy_name + " success")
            
        except:
            print ( proxy_name + " error")
            return False

        return True

    def onPrintSoundSets(self): #0
        """ Display soundset infromation
        """
        lista = self.proxy.getInstalledSoundSetsList()
        print ("Soundset files installed:" + str(lista))
        for l in lista:
            print ("Sound files in soundsets " + str(l) + ": " + str(self.proxy.getSoundSetFileNames(l)))
        

        
    def onPlaySound(self,sound_name, parameters = {}, parallel = False): #2
        """ Play a SoundSet if installed in the robot
        """
        soundSet_name = "sounds"
        try:
            if parallel:
                self.proxy.post.playSoundSetFile(soundSet_name,sound_name)
            else:
                self.proxy.playSoundSetFile(soundSet_name,sound_name)
        except:
            print (sound_name + " non found in *"+ soundSet_name + "* SoundSet file in the robot")
    

    def onStop(self):
        self.proxy.stopAll()
        



