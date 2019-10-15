import pygame
from pygame.locals import *
from GameObject.Transform import Transform
from Engine.Engine import Engine
from Engine.Collider import Collider
from GameObject.Vector2 import Vector
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
    def Move(self, speed):
        temp = self.transform.angle // 90
        print(temp)
        if temp == 0:
            x = self.transform.angle/90
            y = 1-x
            self.transform.position=Vector.Move(self.transform.position,speed * x,Vector.left)
            self.transform.position=Vector.Move(self.transform.position,speed * y,Vector.up)
            pass
        elif temp == 1:
            temp = self.transform.angle - 90
            x = temp/90
            y = 1-x
            self.transform.position=Vector.Move(self.transform.position,speed * x,Vector.down)
            self.transform.position=Vector.Move(self.transform.position,speed * y,Vector.left)
            pass
        elif temp == 2:
            temp = self.transform.angle - 180
            x = temp/90
            y = 1-x
            self.transform.position=Vector.Move(self.transform.position,speed * x,Vector.right)
            self.transform.position=Vector.Move(self.transform.position,speed * y,Vector.down)
            pass
        elif temp == 3:
            temp = self.transform.angle - 270
            x = temp/90
            y = 1-x
            self.transform.position=Vector.Move(self.transform.position,speed * x,Vector.up)
            self.transform.position=Vector.Move(self.transform.position,speed * y,Vector.right)
            pass
        #print(temp)
        pass