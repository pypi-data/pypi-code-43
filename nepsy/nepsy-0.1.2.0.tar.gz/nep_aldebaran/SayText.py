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

class SayText:
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
            proxy_name ="ALTextToSpeech"
            self.proxy = ALProxy(proxy_name,self.ip,self.port)
            print ( proxy_name + " success")

            proxy_name ="ALAnimatedSpeech"
            self.animatedSpeechProxy = ALProxy(proxy_name,self.ip,self.port)
            print ( proxy_name + " success")
            
        except:
            print ( proxy_name + " error")
            return False

        return True
    
    def onSetLanguage(self, input_ = "", parameters = {}, parallel = False):
        
        try:
            self.proxy.setLanguage(input_)
        except:
            print ("Language " + str(input_) + " not avaliable in this robot")


    def onRun(self, input_ = "", parameters = {}, parallel = False):
        """ Run action primitive"""
        try:
            # Encode text
            textToSay = input_.encode("utf-8")

            # Set parameters
            if "velocity" in parameters:
                value = float(parameters["velocity"])
                if value > 350:
                    value = 350
                mapped_value = 50 +  value
                self.proxy.setParameter("speed", mapped_value)
                
            if "pitch" in parameters:
                value = float(parameters["pitch"])
                if(value > 100):
                    value = 100
                if(value < 0):
                    value = 0
                mapped_value =  .5 + value*1.26/100.0  #defualt = 1.3
                self.proxy.setParameter("pitchShift", mapped_value)
                
            if "language" in parameters:
                language = parameters["language"]
                try:
                    self.proxy.setLanguage(language)
                except:
                    print ("Language" + str(language) + "not avaliable in this robot")

            if "contextual" in parameters:
                if parameters["contextual"] == True:
                    if parallel:
                        self.animatedSpeechProxy.post.say(textToSay,{"bodyLanguageMode":"contextual"})
                    else:
                        self.animatedSpeechProxy.say(textToSay,{"bodyLanguageMode":"contextual"})
                else:
                    # Running mode
                    if parallel:
                        id_ = self.proxy.post.say(textToSay)
                    else:
                        id_ = self.proxy.say(textToSay)

                return 

            else:
                # Running mode
                if parallel:
                    id_ = self.proxy.post.say(textToSay)
                else:
                    id_ = self.proxy.say(textToSay)

            
            
                
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    def onStop(self):
        self.proxy.stopAll()
        



