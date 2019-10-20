import pygame, math
from pygame.locals import *
pygame.init()
pygame.font.init()

class Terminal:
    def __init__(self, screenWidth, screenHeight, tags, width = 16, height = 24):
        # Pygame variables.
        pygame.mouse.set_visible(False)
        pygame.key.set_repeat(1)
        
        # Screen variables.
        self.screenWidth, self.screenHeight = screenWidth, screenHeight
        self.tags = tags
        self.caption = "vterminal"
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight), self.tags)
        pygame.display.set_caption(self.caption)
        self.width, self.height = width, height
        self.widthBoxes, self.heightBoxes = int(self.screenWidth/self.width), int(self.screenHeight/self.height)
        
        # Font Variables.
        self.font = 'Courier'
        self.fontSize = 22
        self.textFont = pygame.font.SysFont(self.font, self.fontSize)
        
        # Key variables.
        self.keys = [0 for i in range(K_EURO)] # Every key pressed. Each key press lasts for only 1 iteration of code.
        self.keysDown = pygame.key.get_pressed() # Every key whether it's pressed or not.
        self.keysPressed = [pygame.key.name(i) for i in range(len(self.keys)) if self.keys[i] == True] # The names of every key that's pressed.
        self.inputText = [] # Used to store text written in an input loop.
        self.shift, self.alt, self.ctrl = False, False, False
        
        # Grid variables.
        self.background = []
        self.foreground = []
        for y in range(self.heightBoxes):
            self.background.append([])
            self.foreground.append([])
            for x in range(self.widthBoxes):
                self.background[y].append((0, 0, 0))
                self.foreground[y].append(["", (255, 255, 255)])

    def set_caption(self, caption):
        pygame.display.set_caption(caption)

    def set_mouseVisible(self, bool):
        pygame.mouse.set_visible(bool)

    def update(self):
        # If a key is on, set it to a middleman state so that the key is only on for 1 frame.
        for i in range(len(self.keys)):
            if self.keys[i] == 1: self.keys[i] = 2
        
        # Update events.
        for event in pygame.event.get():
            if event.type == QUIT: sys.exit()
            if event.type == KEYDOWN:
                if self.keys[event.key] == 0: self.keys[event.key] = 1
            if event.type == KEYUP:
                self.keys[event.key] = 0
        
        # Update various key functions.
        self.keysDown = pygame.key.get_pressed()
        self.keysPressed = [pygame.key.name(i) for i in range(len(self.keys)) if self.keys[i] == 1]
        self.shift = True if self.keysDown[K_LSHIFT] or self.keysDown[K_RSHIFT] else False
        self.alt = True if self.keysDown[K_LALT] or self.keysDown[K_RALT] else False
        self.ctrl = True if self.keysDown[K_LCTRL] or self.keysDown[K_RCTRL] else False
        
        # Update variables.
        self.textFont = pygame.font.SysFont(self.font, self.fontSize)
        
        
        # Render the grid.
        for y in range(self.heightBoxes):
            for x in range(self.widthBoxes):
                # Render the background.
                pygame.draw.rect(self.screen, self.background[y][x], (x * self.width, y * self.height, self.width, self.height))

                # Render the foreground.
                renderedText = self.textFont.render(self.foreground[y][x][0], False, self.foreground[y][x][1])
                renderedTextRect = renderedText.get_rect()
                renderedTextRect.center = x * self.width + self.width/2, y * self.height + self.height/2
                self.screen.blit(renderedText, renderedTextRect)
        
        pygame.display.update()
    
    def input(self, x, y, mode = "alphanumeric"):
        self.out("> " + "".join(self.inputText) + "_", (255, 255, 255), x, y) # Display the input text in the format "> TEXT_".
        for key in self.keysPressed:
            if not self.alt and not self.ctrl:
                if key in "abcdefghijklmnopqrstuvwxyz'.," and mode in ("alpha", "alphanumeric"):
                    if self.shift: self.inputText += key.upper()
                    else: self.inputText += key
                if key in "1234567890" and mode in ("numeric", "alphanumeric"):
                    if not self.shift: self.inputText += key
                if key == "space": self.inputText += " "
                if key == "backspace" and len(self.inputText) > 0:
                    self.out("  ", (0, 0, 0), x + len(self.inputText) + 1, y)
                    self.inputText.pop(len(self.inputText)-1)
                if key == "return":
                    a = "".join(self.inputText)
                    self.inputText = []
                    return a
        return False
    
    def out(self, text, color, x, y):
        for i in range(len(text) if len(text) <= self.widthBoxes-x else self.widthBoxes-x):
            self.foreground[y][x + i] = [str(text[i]), color]

    def set(self, text, color, x, y):
        for i in range(len(text) if len(text) <= self.widthBoxes-x else self.widthBoxes-x):
            if text[i] == "1": self.background[y][x + i] = color
    
    def fill(self, color, x1, y1, x2, y2):
        for ypos in range(y1, y2+1):
            for xpos in range(x1, x2+1):
                self.background[ypos][xpos] = color

    def clear(self):
        for y in range(self.heightBoxes):
            self.background.append([])
            self.foreground.append([])
            for x in range(self.widthBoxes):
                self.background[y].append((0, 0, 0))
                self.foreground[y].append(["", (255, 255, 255)])