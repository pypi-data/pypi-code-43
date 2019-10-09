# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 19:12:24 2019

@author: Win10 Pro x64
"""
import cv2


class CV2Cam:
    def __init__(self, camIF=0):
        self.camIF = camIF
        self.cam = cv2.VideoCapture(camIF)
        if self.cam is None or not self.cam.isOpened():
            raise RuntimeError("Keine CV2 kompatible Kamera an Interface %d gefunden"%camIF)

    def probe(self):
        ok = True
        desc = ""
        if self.cam is None or not self.cam.isOpened():
            ok = False
            desc = "Keine CV2 kompatible Kamera an Interface %d gefunden"%self.camIF
        else:
            self.cam.release()
        return ok, desc
        
    def set(self, key, val):
        self.cam.set(key, val)
        
    def read(self):
        return self.cam.read()

    @staticmethod
    def listAvailable():
        ifs = []
        idx = 0
        while True:
            cam = cv2.VideoCapture(idx)
            if cam is None or not cam.isOpened():
                break
            else:
                cam.release()
                ifs.append(idx)
            idx+=1
        return ifs