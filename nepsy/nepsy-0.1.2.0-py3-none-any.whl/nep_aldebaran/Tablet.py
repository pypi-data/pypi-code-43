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
import datetime
import multiprocessing

class Tablet:
    def __init__(self,ip,port=9559):
        self.ip = ip
        self.port = int(port)
        self.onLoad()

    def onLoad(self):
        try: 
            proxy_name = "ALTabletService"
            self.proxy = ALProxy(proxy_name, self.ip, self.port)
            print ( proxy_name + " success")
        except:
            print ( proxy_name + " error")

        try:
            self.photoCaptureProxy =  ALProxy("ALPhotoCapture", self.ip, self.port)
            print ("ALPhotoCapture success")
        except:
            print ("ALPhotoCapture error")
            pass

    def showImage(self, input_, parameters = {}, parallel = False):
        self.proxy.showImage("http://198.18.0.1/apps/images/"+input_+".jpg")
        
    def showWebImage(self, input_, parameters = {}, parallel = False):
        self.proxy.showImageNoCache(input_)

    def takePhoto(self, camera = "Top"):
        self.photoCaptureProxy.setResolution(2)
        self.photoCaptureProxy.setCameraID(1) # camera ='Top': 0 or 'Bottom': 1
        self.photoCaptureProxy.setPictureFormat("jpg")
        self.photoCaptureProxy.post.takePicture("/var/persistent/home/nao/.local/share/PackageManager/apps/images/html/", self.image_name)

    def takeImage(self, input_ = "", parameters = {}, parallel = False):
        x = datetime.datetime.now()
        self.image_name = "img_" + x.strftime("%m%d%H%M%S")
        p = multiprocessing.Process(target=self.takePhoto(input_))
        p.start()
        # Wait for 10 seconds or until process finishes
        p.join(2)
        if p.is_alive():
            p.terminate()
            p.join()
        self.proxy.stopVideo()
        self.proxy.hideImage()
        time.sleep(10)
        print self.image_name
        self.proxy.showImage("http://198.18.0.1/apps/images/"+self.image_name+".jpg")

    def showWeb(self, input_, parameters = {}, parallel = False):
        self.proxy.hideImage()
        self.proxy.stopVideo()
        self.proxy.loadUrl(input_)
        self.proxy.showWebview()

    def showVideo(self, input_, parameters = {}, parallel = False):
        self.proxy.hideImage()
        self.proxy.stopVideo()
        self.proxy.enableWifi()
        path = "http://198.18.0.1/apps/videos/" + str(input_) + ".mp4"
        self.proxy.playVideo(path)

    def onReset(self, input_ = "", parameters = {}, parallel = False):
         self.proxy.resetTablet()



##  --------- Test  ------------
## Change the robot ip only
            
##robot_port = "9559"
##robot_name = "pepper"
##robot_ip = '192.168.2.27'
##import nep
##
##url = "http://" + nep.getMyIP() + ":3000/"
##
##tablet = Tablet(robot_ip, robot_port)
###tablet.showImage("gvlab")
###time.sleep(4)
##tablet.showWebImage("http://vignette.wikia.nocookie.net/animevice/images/d/d3/GochiUsa_2_End_Card_12.png")
##time.sleep(4)
####tablet.showWeb(url)
####time.sleep(10)
###tablet.showVideo("meditation")
###time.sleep(10)
###tablet.onReset()
###time.sleep(4)
###tablet.takeImage()

