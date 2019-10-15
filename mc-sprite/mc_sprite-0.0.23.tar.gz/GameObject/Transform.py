from GameObject.Vector2 import Vector
import pygame
from pygame.locals import *
from Engine.Engine import Engine
from Timer.Time import Time
import _thread
class Transform(pygame.sprite.Sprite):
    def __init__(self, image: str):
        pygame.sprite.Sprite.__init__(self)
        self.__agl=0.0
        self.__nowid=0
        self.__scl=Vector(100.0,100.0)
        self.position=Vector()
        self.image=pygame.image.load(image).convert_alpha()
        self.rect=self.image.get_rect()
        self.mask=pygame.mask.from_surface(self.image)
        self.tempimage=pygame.image.load(image).convert_alpha()
        self.drawId=0
        self.imageRect=self.image.get_rect()
        self.imageRect = self.imageRect.move((0,0))
        self.newRect=self.image.get_rect()
        self.newRect=self.newRect.move((900-self.newRect.width)/2,(600-self.newRect.height)/2)
        self.__drawL={}
        self.__drawL[self.drawId]=(self.image, self.tempimage)
        self.__wid=self.image.get_size()[0]
        self.__hgt=self.image.get_size()[1]
        self.parent=None
        self.position.parent=self
        #_thread.start_new_thread(self.UpdateRect,())
        pass
    def SetParent(self,parent):
        self.parent=parent
        pass
    def GetRect():
        pass
    def Add(self,image: str):
        self.drawId+=1
        self.__drawL[self.drawId]=[pygame.image.load(image).convert_alpha(), pygame.image.load(image).convert_alpha()]
        pass
    def Set(self,id: int):
        self.image=self.__drawL[id][0]
        self.__nowid=id
        self.tempimage=self.__drawL[id][1]
        
    @property
    def width(self):
        return self.__wid*self.__scl.x/100
    @property
    def height(self):
        return self.__hgt*self.__scl.y/100
    @property
    def angle(self):
        return self.__agl
    @property
    def localScale(self):
        return Vector(self.__scl.x,self.__scl.y)
    def Translate(self,x: float,y: float):
        self.__scl.x=x
        self.__scl.y=y
        temp=self.mask.get_size()
        self.mask=self.mask.scale((int(temp[0]*(x/100)),int(temp[1]*(y/100))))
        self.__UpdateLocalScale()
        temp2 = self.__drawL[self.__nowid]
        self.__drawL[self.__nowid]=[self.image,temp2[1]]
    def __UpdateLocalScale(self):
        self.image = pygame.transform.scale(self.image,(int(self.__wid*(self.__scl.x/100)),int(self.__hgt*(self.__scl.y/100))))
        pass
    @property
    def GetRect(self):
        return self.image.get_rect()
    def Rotate(self, angle: float):
        while angle < 0:
            angle+=360
        self.__agl+=angle
        if self.__agl>360:
            self.__agl-=360
        self.image = pygame.transform.rotate(self.tempimage,self.__agl)
        for x in range(0,self.drawId+1):
            temp2 = self.__drawL[x]
            self.__drawL[x]=[self.image,temp2[1]]
            pass
        self.newRect = self.image.get_rect(center=self.tempimage.get_rect().center)
        pass
    def Rotate2(self,angle: float):#亮向量夹角
        self.__agl =90- angle
        self.image = pygame.transform.rotate(self.tempimage,self.__agl)
        for x in range(0,self.drawId+1):
            temp2 = self.__drawL[x]
            self.__drawL[x]=[self.image,temp2[1]]
            pass
        self.newRect = self.image.get_rect(center=self.tempimage.get_rect().center)
        pass
    def LookAround(setf,obj):#向量间距离=r,圆周运动
        pass
    def UpdateRect(self):
        self.rect=pygame.Rect(self.position.x,self.position.y,self.width,self.height)
        pass