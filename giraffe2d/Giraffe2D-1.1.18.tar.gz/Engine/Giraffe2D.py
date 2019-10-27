import contextlib
import math
import os
from struct import *

with contextlib.redirect_stdout(None):
    import pygame
    import pygame.gfxdraw
    from pygame.locals import *
    import pymunk
    import pytmx
    from pytmx.util_pygame import load_pygame
    




print("A Distribution By Saugat Siddiky Jarif")
print("A Distribution Powered By PyGame")





class App(object):
    gameDisplay = None
    def __init__(self):
        pygame.init()
        
    def RenderWindow(self, width, height):
        
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


class LevelManager():
    

    def __init__(self):
        pass

    def LoadLevel(self, LevelName):
        self.tilemap = pytmx.TiledMap(LevelName)
    def RestartLevel(self, LevelName):
        LoadLevel(LevelName)
    def StartLevel(self,LevelName):
        pytmx.load_pygame(LevelName)
        pass
    
        
        
class EventClass():
    event = None
    def __init__(self):
        pygame.init()
        self.close = False

        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                self.close = True
                pass
    
    
    
            
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
    


    
        
    
class Colour2D():
    COLOUR = None
    def __init__(self):
        self.WHITE = (255,255,255)
        self.BLACK = (0,0,0)
        self.RED = (255,0,0)
        self.GREEN = (0,255,0)
        self.BLUE = (0,0,255)
    def SetColour2D(self, colour):
        self.colour = COLOUR

    def GetColour2D(self):
        return COLOUR

        
    

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
    
    
    def __init__(self):
        self.__GRAVITY__ = 1
        self.__MASS__ = 9.8
        self.__FORCE_ = 100
        self.Object = pymunk.Space()
        
        
    def PhysicsObject2D(self,Sprite,MASS, Body, weight, distance):
        self.Sprite = Sprite
        self.Body = Body
        self.weight = weight
        self.distance = distance
        self.G = 9.8
        # F = Gm1m2 / d2
        self.calculateForce = self.MASS * (self.weight * self.weight) / self.distance 
        pass

    def SetGravity(self, Gravity):
        self.Object.gravity = Amount
        self.__GRAVITY__ = Gravity
    

        return Amount

    

class TileSet():
    def __init__(self,path, divideX, divideY):
        self.path = path
        self.divideX = divideX
        self.divideY = divideY
        gameMap = pytmx.TiledMap(path)
        pass
    


    
        
    
        
        
        

        
    
    

        
        

    
        
            
                    
    
             


     


    


