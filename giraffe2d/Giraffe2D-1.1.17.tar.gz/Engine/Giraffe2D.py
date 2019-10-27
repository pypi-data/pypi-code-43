import contextlib
import math
import os
from test.test_turtle import Vec2D
from struct import *

with contextlib.redirect_stdout(None):
    import pygame
    import pygame.gfxdraw
    from pygame.locals import *
    import pymunk
    import pytmx
    from pytmx.util_pygame import load_pygame
    




print("Please Visit www.GiraffeGameFramework.com for more info")




class App(object):
    def __init__(self):
        pygame.init()
        
    def RenderWindow(self, width, height):
        global gameDisplay
        gameDisplay = pygame.display.set_mode((width, height))
        

    def SetAssetsFolder(self):
        self.gameFolder = os.path.dirname(__file__)
    
    
    def Update(self):
        pygame.display.update()
        pygame.display.flip()

        
    def FPS(self, amount):
        clock = pygame.time.Clock()
        clock.tick(amount)

        
    def SetTitle(self, title):
        pygame.display.set_caption(title)

        
    def Fill(self, color):
        gameDisplay.fill(color)
        
    def ShowFPS(self):
        print("FPS -> ", FPS)

    @staticmethod  
    def get_display(self):
        return gameDisplay

    def SetIcon(self, path):
        myIcon = pygame.image.load(path)
        pygame.display.set_icon(myIcon)
        
    def quit(self):
        pygame.quit()
        quit()


class Levels():
    def __init__(self, LevelName):
        self.LevelName = LevelName

    def LoadLevel(self, LevelName):
        self.tilemap = pytmx.TiledMap(LevelName)
    def RestartLevel(self, LevelName):
        LoadLevel(LevelName)
    def StartLevel(self,LevelName):
        
    
        
        
class Event():
    def __init__(self):
        pygame.init()
        self.close = False
    
        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                self.close = True
    
    
    
            
class Sprite(pygame.sprite.Sprite):
    def  __init__(self, path):
        pygame.init()
        


        
    def getPosX(self):
        return self.posX
    
    def LookAtMouse(self, spriteToRotate):
        x,y = pygame.mouse.get_pos()
        rel_x = x - self.posX
        rel_y = y - self.posY
        angle = (180 / math.pi) * math.atan2(rel_y, rel_x)
        self.image = pygame.transform.rotate(spriteToRotate, angle)
        
    def LoadImage(self, path):
        self.mainImage = pygame.image.load(path)
        
        
    
    def PlaceImage(self,image,x, y):
        self.image = image
        self.x = x
        self.y = y
        pygame.Surface.blit(App.get_display(self),self.image, (self.x, self.y))

    
        

class Draw():
    def DrawRect(self, color, sizeX , sizeY , posX, posY ):
        self.color = color
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.posX = posX
        self.posY = posY
        pygame.draw.rect(App.get_display(self), self.color, [self.posX, self.posY, self.sizeX, self.sizeY])

    def DrawCircle(self, posX, posY, color, radius):
        self.posX = posX
        self.posY = posY
        self.color = color
        self.radius = radius
        # circle(Surface, color, pos, radius, width=0) -> Rect
        pygame.draw.circle(App.get_display(self), color, [posX, posY], radius)
    def DrawPolygon(self):
        pass
    def DrawTriangle(self):
        pass
    def DrawLine(self):
        pass
    

class Keyboard():
    def __init__(self):
        self.moveRight = False
        self.moveLeft = False
        self.moveUp = False
        self.moveDown = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.moveLeft = True
        elif keys[pygame.K_RIGHT]:
            self.moveRight = True
        elif keys[pygame.K_UP]:
            self.moveUp = True
        elif keys[pygame.K_DOWN]:
            self.moveDown = True
    def CheckKey(self, key):
        pass
    def InputType(self):
        pass
    

class Vector2D(pygame.math.Vector2):
    def __init__(self, *args, **kwargs):
        pygame.math.Vector2.__init__(self, *args, **kwargs)
    def Rotate(Giraffe2D.Sprite, angle)
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        
    
        
    
class Color(object):
    def __init__(self):
        self.WHITE = (255,255,255)
        self.BLACK = (0,0,0)
        self.RED = (255,0,0)
        self.GREEN = (0,255,0)
        self.BLUE = (0,0,255)
        
    

class Sound(object):
    def __init__(self, path):
        pygame.init()
        pygame.mixer.init()
        self.sound = pygame.mixer.Sound(path)
    
    def LoadSound(self, path):
        self.sound = pygame.mixer.sound(path)
    def SetVolume(self):
        pygame.mixer.set_volume(volume)
        
    def play(self):
        pygame.mixer.sound.play(self.sound)
        
    def pause(self):
        pygame.mixer.pause()
    def unpause(self):
        pygame.mixer.unpause()

class Music():
    def __init__(self, path):
        pygame.init()
        pygame.mixer.init()
    def play(self):
        pass
    def pause(self):
        pass
    def skip(self, musicName):
        pygame.mixer.set_music(musicName)
        

class Physics2D(object):
    self.Object = pymunk.Space()
    
    def __init__(self):
        self.__GRAVITY__ = 1
        self.__MASS__ = 9.8
        self.__FORCE_ = 100
        
        
    def PhysicsObject(self,Sprite,MASS, Body, weight, distance)
        self.Sprite = Sprite
        self.Body = Body
        self.weight = weight
        self.distance = distance
        self.G = 9.8
        # F = Gm1m2 / d2
        self.calculateForce = self.MASS * (self.weight * self.weight) / self.distance 
        return Giraffe2D.PhysicsObject
    def SetGravity(self, Gravity):
        self.Object.gravity = Amount
        self.__GRAVITY__ = Gravity
    

        return Amount
    def SetForce(self, amount as int, position as Vec2D, forceMode):
        __FORCE_ = amount

class TileSet(object):
    def __init__(self,path, divideX, divideY):
        self.path = path
        self.divideX = divideX
        self.divideY = divideY
        gameMap = pytmx.TiledMap(path)
    
        
    
        
    
        
        
        

        
    
    

        
        

    
        
            
                    
    
             


     


    


