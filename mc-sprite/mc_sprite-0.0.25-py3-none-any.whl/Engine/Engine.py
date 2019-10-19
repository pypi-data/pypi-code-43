import _thread
from Timer.Time import Time
import pygame
import sys
import time as t
from Engine.Mathf import Mathf
from Engine.Collider import Collider
pygame.init()
 
class Engine(object):
    fps = 1/60
    drawlist={}
    drawSortList=[]
    screen=None
    time=None
    __isMouseDown_=False
    __isMouseUp_=True
    __isMouse=False
    colliderList=[]
    isDrawColliderRect=False
    isUseEngineCtrl=False
    @staticmethod
    def Start(screen=None):
        Engine.time=Time()
        #_thread.start_new_thread(Engine.CheckEvent,())
        if not screen==None:
            Engine.screen=screen
        pass
    @staticmethod
    def RegisterCollider(collider: Collider):
        Engine.colliderList.append(collider)
    @staticmethod
    def isMouseDown():
        return Engine.__isMouseDown_
        pass
    @staticmethod
    def isMouseClicked():
        if Engine.__isMouseDown_:
            Engine.__isMouse=True
        if Engine.__isMouseUp_:
            if Engine.__isMouse:
                Engine.__isMouse=False
                return True
        pass
    @staticmethod
    def CheckEvent():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                Engine.__isMouseDown_=True
                Engine.__isMouseUp_=False
            elif event.type == pygame.MOUSEBUTTONUP:
                Engine.__isMouseDown_=False 
                Engine.__isMouseUp_=True
    @staticmethod
    def isMouseUp():
        return Engine.__isMouseUp_
        pass
    @staticmethod
    def A():
        pass
    @staticmethod
    def SetMode(resolution=(0,0),flags=0,depth=0):
        Engine.screen=pygame.display.set_mode(resolution,flags,depth)
    @staticmethod
    def SetCaption(title: str, icontitle = None):
        if icontitle==None:
            pygame.display.set_caption(title)
        else:
            pygame.display.set_caption(title,icontitle)
    @staticmethod
    def Delete(obj):
        del Engine.drawlist[str(obj.priority)]
        Engine.drawSortList.remove(obj.priority)
        if obj.isMianCol:
            del obj.mycol
        if obj.isCol:
            for x in obj.ColList:
                x.Del(obj)
        del obj
        pass
    @staticmethod
    def Draw():
        Engine.time.CalculationDeltaTime()
        if Engine.isUseEngineCtrl:
            Engine.CheckEvent()
        #print(Engine.drawlist.keys())
        #print(Engine.drawSortList)
        for x in Engine.drawSortList:
            temp=Engine.drawlist[str(x)]
            if temp.active:
                temp.transform.UpdateRect()
                Engine.screen.blit(temp.transform.image,temp.transform.position.value,temp.transform.image.get_rect())
                #temp.transform.rect=temp.transform.rect.move(Mathf.TupSub(temp.transform.position.value,temp.transform.position.oldV))
                #Engine.screen.blit(temp.transform.image,temp.transform.position.value,temp.transform.image.get_rect(center=temp.transform.newRect.center))
                if Engine.isDrawColliderRect:
                    pygame.draw.rect(Engine.screen, (255, 0, 0), temp.transform.rect, 1)
        for i in Engine.colliderList:
            i.collision()
        
        pygame.display.update()

        