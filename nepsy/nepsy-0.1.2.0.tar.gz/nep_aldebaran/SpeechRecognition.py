#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

# Luis Enrique Coronado Zuniga

# You are free to use, change, or redistribute the code in any way you wish
# but please maintain the name of the original author.
# This code comes with no warranty of any kind.

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import nep
import threading
import time
import sys



class SpeechRecognition(ALModule):
    def __init__(self, name, ip, sharo):
        ALModule.__init__(self, name)

        self.sharo = sharo
        self.name = name
        self.ip = ip
        self.word_spotting = True # If false the robot will only understand exact expressions
        self.visualExpression = True # Led feedback
        self.port = 9559
        self.proxy_name = "ALSpeechRecognition"
        self.visualExpression = True
        self.wordSpotting = True

        try:
            self.asr = ALProxy(self.proxy_name, ip, 9559)
            print ( self.proxy_name + " success")
            #self.onLoad(vocabulary)

        except():
            print ( self.proxy_name + " error")
            #self.memory.unsubscribeToEvent("WordRecognized")
            #self.onLoad(vocabulary)

        self.word = 0

    
    def onLoad(self,vocabulary):
        self.asr.pause(True)
        self.asr.setLanguage("English")
        self.asr.setVocabulary(vocabulary, False)

        self.asr.setVisualExpression(self.visualExpression)
        self.asr.pushContexts()
        self.asr.setVocabulary(vocabulary, self.wordSpotting )

        self.memory = ALProxy("ALMemory",self.ip, self.port)
        self.memory.subscribeToEvent("WordRecognized", self.name, "onWordRecognized")
        self.asr.pause(False)

    def onSetVocabulary(self, vocabulary):
        try: 
            self.onLoad(vocabulary)
        except():
            self.memory.unsubscribeToEvent("WordRecognized")
            try: 
                print ( self.proxy_name + "restarting ..")
                self.onLoad(vocabulary)
            except():
                print ( self.proxy_name + " error")
        

    def onWordRecognized(self, key, value, message):

        print "Key: ", key
        print "Value: " , value
        #print "Message: " , message
        if (len(value) > 1 and value[1]>0.45):

            if self.wordSpotting:
                values_rest = value[0].split("<...> ")
                values_final = values_rest[1].split(" <...>")
                value  = values_final[0]
            
            
            data = {"node":"perception", "primitive":"word", "input":"add", "robot":"pepper", "parameters":[value]}
            self.sharo.send_info(data)

    def onStop(self):
        self.memory.unsubscribeToEvent("WordRecognized")



##pip   = robot_ip
##pport = int(robot_port)
##
##try:
##    # We need this broker to be able to construct
##    # NAOqi modules and subscribe to other modules
##    # The broker must stay alive until the program exists
##    myBroker = ALBroker("myBroker",
##       "0.0.0.0",   # listen to anyone
##       0,           # find a free port and use it
##       pip,         # parent broker IP
##       pport)       # parent broker port
##
##
##    SpeechEventListener = SpeechRecognition("SpeechEventListener",pip)
##    SpeechEventListener.onSetVocabulary(["picture", "gym", "weather" , "stop", "good morning", "thank you", "yes", "no"])
##    
##except Exception as e: 
##    print(e)
##    time.sleep(5)
##    sys.exit(0)
##
##try:
##    while True:
##        time.sleep(.1)
##       
##except KeyboardInterrupt:
##    print
##    print "Interrupted by user, shutting down"
##    myBroker.shutdown()
##    sys.exit(0)

