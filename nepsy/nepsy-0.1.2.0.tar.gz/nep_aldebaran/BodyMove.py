#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

# Luis Enrique Coronado Zuniga

# You are free to use, change, or redistribute the code in any way you wish
# but please maintain the name of the original author.
# This code comes with no warranty of any kind.

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import qi
import time
import os
import sys
import math
import time
import almath
from tinydb import TinyDB, Query

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

class BodyMove:
    def __init__(self,ip, port = 9559, robot = "pepper", animation_database_path ="animation_db.json"):
        """ Define parameters for SayText function

            Parameters
            ----------

            ip : string
               IP value of the robot

        """
        self.port = int(port)
        self.ip = ip
        self.robot = robot
        self.animation_database_path = animation_database_path
        print ("Animation path: " + str(animation_database_path))

        if self.robot == "nao":
            self.name_joints = ["LAnklePitch", "LAnkleRoll", "LHipRoll", "LHipYawPitch", "LKneePitch",\
                                    "RAnklePitch", "RAnkleRoll", "RHipRoll", "RHipYawPitch", "RKneePitch", \
                                    "LElbowRoll", "LElbowYaw", "LHand","LShoulderPitch", "LShoulderRoll", "LWristYaw", \
                                    "RElbowRoll", "RElbowYaw" , "RHand", "RShoulderPitch", "RShoulderRoll", "RWristYaw",\
                                    "HeadPitch", "HeadYaw"
                                    ]
        else:
            
            self.name_joints= ["HeadPitch","HeadYaw", "HipPitch", "HipRoll", "KneePitch", "LElbowRoll", "LElbowYaw",\
                                "LHand","LShoulderPitch", "LShoulderRoll", "LWristYaw", "RElbowRoll", "RElbowYaw" , "RHand", \
                                "RShoulderPitch", "RShoulderRoll", "RWristYaw"]
            
        self.onLoad()

    def onLoad(self):
        try: 
            proxy_name ="ALMotion"
            self.proxy = ALProxy(proxy_name,self.ip,self.port)
            self.positionErrorThresholdPos = 0.01
            self.positionErrorThresholdAng = 0.03

            self.session = qi.Session()
            self.session.connect("tcp://" + self.ip  + ":" + str(self.port))
            self.motion_service = self.session.service("ALMotion")

            if self.robot == "pepper":
                self.backgroundProxy = ALProxy("ALBackgroundMovement",self.ip,self.port)
            
            print ( proxy_name + " success")
        except:
            print ( proxy_name + " error")
            return False

        return True

    def onBreathe(self, input_ = "", parameters = {}, parallel = False):
        if input_ == "on":
            self.backgroundProxy.setEnabled(True)
        else:
            self.backgroundProxy.setEnabled(False)


    def onRunMode(self, input_ = "", parameters = {}, parallel = False):
        if input_ == "rest" or input_ == "sleep":
            self.proxy.rest()
        elif input_ == "wake_up" or input_ == "wake up":
            # Wake up robot (Turn the motors on)
            self.proxy.wakeUp()
            if self.robot == "pepper":
                self.backgroundProxy.setEnabled(True)



    def onOpenHand(self,input_ = "", parameters = {}, parallel = False):

        all_ = False

        if "all" in parameters:
            all_ = parameters["all"]

             
        if input_ == "right":

            if all_: 
                self.motion_service.setAngles("RHand", 0.98, 0.1)
            else: 
                self.motion_service.setAngles("RHand", 0.6, 0.1)

            
        elif input_ == "left":
        
            if all_: 
                self.motion_service.setAngles("LHand", 0.98, 0.1)
            else: 
                self.motion_service.setAngles("LHand", 0.6, 0.1)

        else:
            if all_: 
                self.motion_service.setAngles("LHand", 0.98, 0.1)
                self.motion_service.setAngles("RHand", 0.98, 0.1)
               
            else: 
                self.motion_service.setAngles("LHand", 0.6, 0.1)
                self.motion_service.setAngles("RHand", 0.6, 0.1)
                



    def onCloseHand(self,input_ = "", parameters = {}, parallel = False):

        if input_ == "right":
            self.motion_service.setAngles("RHand", 0.02, 0.1)
            
        elif input_ == "left":
            self.motion_service.setAngles("LHand", 0.02, 0.1)

        else:
            self.motion_service.setAngles("LHand", 0.02, 0.1)
            self.motion_service.setAngles("RHand", 0.02, 0.1)
    
    def onWalk(self, input_ = "", parameters = {}, parallel = False):

        if input_ == "position":
            try:
                x = float(parameters["x"])
                y = float(parameters["y"])
                Theta = float(parameters["angle"])
                motion_service = self.self.motion_service
        

                #####################
                ## Enable arms control by move algorithm
                #####################
                motion_service.setMoveArmsEnabled(True, True)
                #~ motion_service.setMoveArmsEnabled(False, False)

                #####################
                ## FOOT CONTACT PROTECTION
                #####################
                #~ motion_service.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION",False]])
                motion_service.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])

                #####################
                ## get robot position before move
                #####################
                initRobotPosition = almath.Pose2D(motion_service.getRobotPosition(False))
                motion_service.setMoveArmsEnabled(False, False)


                X = float(x)
                Y = float(y)
                Theta = Theta*math.pi/180

                if  parallel == True:
                    id = motion_service.post.moveTo(X, Y, Theta)
                    # wait is useful because with _async moveTo is not blocking function
                    motion_service.wait(id,0)

                    
                else:   
                    motion_service.moveTo(X, Y, Theta, _async=True)
                    # wait is useful because with _async moveTo is not blocking function
                    motion_service.waitUntilMoveIsFinished()

                #####################
                ## get robot position after move
                #####################
                endRobotPosition = almath.Pose2D(motion_service.getRobotPosition(False))

                #####################
                ## compute and print the robot motion
                #####################
                robotMove = almath.pose2DInverse(initRobotPosition)*endRobotPosition
                # return an angle between ]-PI, PI]
                robotMove.theta = almath.modulo2PI(robotMove.theta)
                print ("Robot Move:", robotMove)
                
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
            
        elif input_ == "velocity":
            x = float(parameters["x"])
            y = float(parameters["y"])
            theta = float(parameters["angle"])

            if not parallel:

                enableArms = True
                self.proxy.setMoveArmsEnabled(enableArms, enableArms)

            
                if "frequency" in parameters:
                    
                    frequency = float(parameters["frequency"])
                else:
                    frequency = 0.5
                    
                if self.robot == "nao":
                    x = float(parameters["x"])
                    y = float(parameters["y"])
                    theta = float(parameters["angle"])
                    frequency = 0.5
                    #frequency = parameters["frequency"]
                    self.proxy.setWalkTargetVelocity(x,y,theta,frequency)
                else:
                    self.proxy.moveToward(x, y, theta) 
            else:

                
                enableArms = True
                self.setMoveArmsEnabled(enableArms, enableArms)

            
                if "frequency" in parameters:
                    
                    frequency = float(parameters["frequency"])
                else:
                    frequency = 0.5
                    
                if self.robot == "nao":
                    x = float(parameters["x"])
                    y = float(parameters["y"])
                    theta = float(parameters["angle"])
                    frequency = 0.5
                    #frequency = parameters["frequency"]
                    self.proxy.post.setWalkTargetVelocity(x,y,theta,frequency)
                else:
                    self.proxy.post.moveToward(x, y, theta) 



    def onRunAnimation(self, input_ = "", parameters = {}, parallel = False):
        """ Run action primitive"""
        
        try:
            # Animation trayectory parameters              
            names = list()
            times = list()
            keys = list()
            flip = False
            reverse = False
            
            if "flip" in parameters:
                flip = parameters["flip"]
            if "reverse" in parameters:
                reverse = parameters["reverse"]
            # Get animation from database
            success, names, times, keys = self._animation_query(input_, flip, reverse)
            self.name_joints = names

            # If valid animation
            if success:

                if "time" in parameters:
                    # Set animation duration
                    times =  self._change_animation_duration(times,float(parameters["time"]))

                try:
                    if parallel:
                        self.proxy.post.angleInterpolation(names, keys, times, True)
                    else:
                        self.proxy.angleInterpolation(names, keys, times, True)
                        
                except BaseException, err:
                    print (err)
            else:
                print ('Animation execution error')
        except BaseException, err:
            print ('Animation not found in database')
                


    def onStopAnimation(self):
        self.proxy.stopAll()
        #self.proxy.killAll();


    # ------------------------------------ Animation parametrization ----------------------------------------------- 

    # Invert movement from left to rigth
    def __invert_side(self,old_keys,old_names,old_times):
        joint2negative = ["HeadYaw","HipRoll"]
        keys = old_keys
        names = old_names
        times = old_times

        for joint_name in joint2negative:
            if joint_name in names:
                index_number = names.index(joint_name)
                temp_keys = keys[index_number]
                keys[index_number] = map(lambda x: x*(-1), temp_keys)


        joints2flip = [["LElbowRoll","RElbowRoll"], ["LElbowYaw", "RElbowYaw"],["LShoulderPitch","RShoulderPitch"], ["LShoulderRoll", "RShoulderRoll"], ["LWristYaw", "RWristYaw"]]
            
        for joint_tuple in joints2flip:
            if joint_tuple[0] in names and joint_tuple[1] in names:
                index_number1 = names.index(joint_tuple[0])
                index_number2 = names.index(joint_tuple[1])

                print joint_tuple
                print keys[index_number1]
                print keys[index_number2]
                
                temp_keys1 = keys[index_number1]
                temp_keys2 = keys[index_number2]

                if joint_tuple[0] == "LShoulderPitch":
                    pass
                else:
                    temp_keys1 = map(lambda x: x*(-1), temp_keys1)
                    temp_keys2 = map(lambda y: y*(-1), temp_keys2)
                
                temp_times1 = times[index_number1]
                temp_times2 = times[index_number2]

                keys[index_number1] = temp_keys2
                keys[index_number2] = temp_keys1
                times[index_number1] = temp_times2
                times[index_number2] = temp_times1

                print keys[index_number1]
                print keys[index_number2]

            print  


        return keys,names,times

    # Invert trayectory points
    def __invert_time(self,times):
        # Invert diference between motions
        time_dif = []
        new_times = [times[0]]
        time_len = len(times)
        for t in range (time_len-1):
            time_dif.append(times[t+1]- times[t])

        new_time_dif = time_dif[::-1]
        
        for t in range (time_len-1):
            new_times.append(new_times[t]+new_time_dif[t])
        return new_times

    # Get Animation from database
    def _animation_query(self,name_animation, flip = False, reverse = False): #1
        """ Get the animation parameters (joint names, times and joint values) of a specific animation from a database"""
        db = TinyDB(self.animation_database_path)
        q = Query()
        try:
            s = db.search(q.animation == name_animation)
        except:
            print (" ERROR: Animation not found in database")
            return False,[0],[0],[0]

        names = [x.encode('UTF8') for x in s[0]['names']] # Name of the joint
        times =  s[0]['times']                            # Time index
        keys =  s[0]['keys']                              # Joint values

        if flip == True:
            keys,names,times = self.__invert_side(keys,names,times)

        if reverse == True and len(times) > 1 :
            i = 0
            for k in keys:
                temp = k[::-1]
                keys[i] = temp
                i = i + 1
            i = 0
            for time in times:
                times[i] = self.__invert_time(time)
                i = i + 1                
        return True, names, times, keys

        
    # Set animatio duration
    def _change_animation_duration(self, time_list, new_max):
        """ Change the timeline values to other specified by the user
        """
        
        l = len(time_list)
        time_base = time_list[0]
        max_time = float(time_base[-1])
        factor = float(new_max)/max_time
        for lista in time_list:
            for index, item in enumerate(lista):
                lista[index] = lista[index]*factor
        
        return time_list
        



