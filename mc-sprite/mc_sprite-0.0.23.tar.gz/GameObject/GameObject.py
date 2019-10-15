import pygame
from pygame.locals import *
from GameObject.Transform import Transform
from Engine.Engine import Engine
from Engine.Collider import Collider
from GameObject.Vector2 import Vector
import math
import numpy as np
class GameObject():
    id=0
    def __init__(self, image: str, priority: int):
        self.ColList=[]
        self.isMianCol=False
        self.isCol=False
        self.thisID=GameObject.id
        self.mycol=None
        GameObject.id+=1
        self.priority=priority
        
        self.transform=Transform(image)
        self.transform.parent=self
        self.__activation=True
        Engine.drawlist[str(priority)]=self
        Engine.drawSortList.append(priority)
        Engine.drawSortList.sort()
        pass
    def Add(self,image: str):
        self.transform.Add(image)
        pass
    def Set(self, id: int):
        if id <= self.transform.drawId and id >= 0:
            self.transform.Set(id)
        pass
    @property
    def active(self):
        return self.__activation
        pass
    def SetActive(self, active: bool):
        self.__activation=active
        pass
    def Draw(self):
        pass
    def AddComponent(self):
        pass
    @staticmethod
    def Find(name):
        pass
    def LookAt(self,obj):
        x = np.array((0,1))
        temp = (self.transform.position - obj.transform.position).value
        y = np.array(temp)
        print(y)
        # 两个向量
        Lx=np.sqrt(x.dot(x))
        Ly=np.sqrt(y.dot(y))
        #相当于勾股定理，求得斜线的长度
        cos_angle=x.dot(y)/(Lx*Ly)
        #求得cos_sita的值再反过来计算，绝对长度乘以cos角度为矢量长度
        angle3=np.arccos(cos_angle)
        angle=angle3*360/2/np.pi
        if temp[0]>0:
            angle*=-1
        self.transform.Rotate2(angle)
        #变为角度
        print(angle)
        pass
    def Move(self, speed):
        temp = self.transform.angle // 90
        #print(temp)
        if temp == 0:
            x = self.transform.angle/90
            y = 1-x
            self.transform.position=Vector.Move(self.transform.position,speed * y,Vector.left)
            self.transform.position=Vector.Move(self.transform.position,speed * x,Vector.up)
            pass
        elif temp == 1:
            temp = self.transform.angle - 90
            x = temp/90
            y = 1-x
            self.transform.position=Vector.Move(self.transform.position,speed * y,Vector.down)
            self.transform.position=Vector.Move(self.transform.position,speed * x,Vector.left)
            pass
        elif temp == 2:
            temp = self.transform.angle - 180
            x = temp/90
            y = 1-x
            self.transform.position=Vector.Move(self.transform.position,speed * y,Vector.right)
            self.transform.position=Vector.Move(self.transform.position,speed * x,Vector.down)
            pass
        elif temp == 3:
            temp = self.transform.angle - 270
            x = temp/90
            #print(x)
            y = 1-x
            self.transform.position=Vector.Move(self.transform.position,speed * y,Vector.up)
            self.transform.position=Vector.Move(self.transform.position,speed * x,Vector.right)
            pass
        #print(temp)
        pass