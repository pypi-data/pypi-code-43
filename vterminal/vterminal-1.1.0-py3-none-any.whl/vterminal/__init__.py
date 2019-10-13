import pygame, math
from pygame.locals import *
pygame.init()
pygame.font.init()

class Terminal:
    def __init__(self, width, height, tags):
        # Pygame variables.
        pygame.mouse.set_visible(False)
        pygame.key.set_repeat(1)
        
        # Screen variables.
        self.screenWidth = width
        self.screenHeight = height
        self.tags = tags
        self.caption = "vterminal"
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight), self.tags)
        pygame.display.set_caption(self.caption)
        self.width = 16
        self.height = 24
        
        # Font Variables.
        self.font = 'Courier'
        self.textFont = pygame.font.SysFont(self.font, 22)
        
        # Key variables.
        self.keys = [0 for i in range(K_EURO)] # Every key pressed. Each key press lasts for only 1 iteration of code.
        self.keysDown = pygame.key.get_pressed() # Every key whether it's pressed or not.
        self.keysPressed = [pygame.key.name(i) for i in range(len(self.keys)) if self.keys[i] == True] # The names of every key that's pressed.
        self.inputVariable = [] # Used to store text written in an input loop.
        self.shift, self.alt, self.ctrl = False, False, False # Boolean values representing if a modifier key is pressed or not.
        
        # Developer variables.
        self.gridMode = False
        
        # Grid variables.
        self.background = []
        self.foreground = []
        for y in range(45):
            self.background.append([])
            self.foreground.append([])
            for x in range(120):
                self.background[y].append((50, 50, 50) if (x+y) % 2 == 0 and self.gridMode == True else (0, 0, 0))
                self.foreground[y].append(["", (255, 255, 255)])

    def set_caption(self, caption):
        pygame.display.set_caption(caption)

    def set_mouseVisible(self, bool):
        pygame.mouse.set_visible(bool)

    def set_fontSize(self, size):
        self.textFont = pygame.font.SysFont(self.font, size)

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
        
        # Render the grid.
        for y in range(45):
            for x in range(120):
                # Render the background.
                pygame.draw.rect(self.screen, self.background[y][x], (x * self.width, y * self.height, self.width, self.height))

                # Render the foreground.
                renderedText = self.textFont.render(self.foreground[y][x][0], False, self.foreground[y][x][1])
                renderedTextRect = renderedText.get_rect()
                renderedTextRect.center = x * self.width + self.width/2, y * self.height + self.height/2
                self.screen.blit(renderedText, renderedTextRect)
        
        pygame.display.update()
    
    def input(self, x, y, mode = "alphanumeric"):
        self.out("> " + "".join(self.inputVariable) + "_", (255, 255, 255), x, y) # Display the input text in the format "> TEXT_".
        for key in self.keysPressed:
            if not self.alt and not self.ctrl:
                if key in "abcdefghijklmnopqrstuvwxyz'.," and mode in ("alpha", "alphanumeric"):
                    if self.shift: self.inputVariable += key.upper()
                    else: self.inputVariable += key
                if key in "1234567890" and mode in ("numeric", "alphanumeric"):
                    if not self.shift: self.inputVariable += key
                if key == "space": self.inputVariable += " "
                if key == "backspace" and len(self.inputVariable) > 0:
                    self.out("  ", (0, 0, 0), x + len(self.inputVariable) + 1, y)
                    self.inputVariable.pop(len(self.inputVariable)-1)
                if key == "return":
                    a = "".join(self.inputVariable)
                    self.inputVariable = []
                    return a
    
    def out(self, text, color, x, y):
        for i in range(len(text) if len(text) <= 120-x else 120-x):
            self.foreground[y][x + i] = [str(text[i]), color]

    def set(self, color, x, y):
        self.background[y][x] = color
    
    def fill(self, color, x1, y1, x2, y2):
        for ypos in range(y1, y2+1):
            for xpos in range(x1, x2+1):
                self.background[ypos][xpos] = color
    
    def image(self, text, x, y):
        # A string is passed to the function. The string is split into a 2d array, with each index containing a foreground and background value.
        # For example, "x255255255000000000,x255255255000000000\nx255255255000000000,x255255255000000000" is a string representing a 2x2 box of white "x"s with a black background.
        # Each index is split into a character, an rgb value for the character, and an rgb value for the background.
        # For example, "x255255255000000000" is split into ["x", (255, 255, 255), (0, 0, 0)].
        text = text.split("\n")
        for i in range(len(text)):
            text[i] = text[i].split(",")
        for ypos in range(0, len(text)):
            for xpos in range(0, len(text[ypos])):
                self.out(text[ypos][xpos][0], (int(text[ypos][xpos][1:4]), int(text[ypos][xpos][4:7]), int(text[ypos][xpos][7:10])), xpos, ypos)
                self.set((int(text[ypos][xpos][10:13]), int(text[ypos][xpos][13:16]), int(text[ypos][xpos][16:19])), xpos, ypos)