import pygame, sys, random
from pygame.locals import *
import Images
import time
import ogg
import Bgm

class klotski:
    def __init__(self):
        # 一些常量
        self.WINDOWWIDTH = 500
        self.WINDOWHEIGHT = 500
        self.BACKGROUNDCOLOR = (255, 255, 255)
        self.BLUE = (0, 0, 255)
        self.BLACK = (0, 0, 0)
        self.FPS = 40
        
        self.time_start = time.time()
        selftime_end = 0
        self.VHNUMS = 2
        self.MAXRANDTIME = 100
        self.CELLNUMS = self.VHNUMS*self.VHNUMS
        self.soundIndex = 1
        # 初始化
        pygame.init()
        self.mainClock = pygame.time.Clock()
 
        # 加载图片
        self.gameImage = pygame.image.load(Images.Get('1.png'))
        self.gameRect = self.gameImage.get_rect()
    
 
        # 设置窗口
        self.windowSurface = None
 
        self.cellWidth = None
        self.cellHeight = None
 
        self.finish = False
        self.isMouseAroundBlank = False
        self.isRun = False
        self.isRand = False
        self.isImage = False
        self.isDrawLine = False
        self.isMouseDown = False
        self.isKeyDown = False
        self.isRun = True
        self.isGame = False
        self.isT = True

        self.isA = False
        self.isB = False

        self.myKey = []
        self.gameBoard = None
        self.blackCell = None
        self.m = None
        self.windowSurface = pygame.display.set_mode((self.gameRect.width, self.gameRect.height))
        pygame.display.set_caption('魔扣拼图')
 
        self.cellWidth = int(self.gameRect.width / self.VHNUMS)
        self.cellHeight = int(self.gameRect.height / self.VHNUMS)
    def SetMusic(self,index = 1):
        if pygame.mixer.music.get_busy() == 1:
            pygame.mixer.music.stop()
        if type(index) == int:
            if index >=1 and index <= 8:
               pygame.mixer.music.load(Bgm.Get('bgm'+str(index)+'.mp3'))
            else:
                print('音乐的编号超出范围')
                self.terminate()
        else:
            print('音乐的编号必须是数字')
            self.terminate()
        pass
    def SetMusicVolume(self,value):
        if type(value) == int:
            if value >= 0 and value <= 100:
                pygame.mixer.music.set_volume(value / 100)
            else:
                print('音量超出范围')
                self.terminate()
        else:
            print('音量必须是数字')
            self.terminate()
    def PlayMusic(self):
        if pygame.mixer.music.get_busy() == 0:
            pygame.mixer.music.play(0)
        else:
            print('操作无效，已经播放音乐')
    def StopMusic(self):
        if pygame.mixer.music.get_busy() == 1:
            pygame.mixer.music.stop()
        else:
            print('操作无效，当前并未存在播放的音乐')
    def IsMusicPlay(self):
        if pygame.mixer.music.get_busy() == 1:
            return False
        else:
            return True
    # 退出
    def terminate(self):
        pygame.quit()
        sys.exit()
    def SetLevel(self, level = 2):
        if type(level) == int:
            if level >= 1 and level <= 50:
                self.VHNUMS = level
                self.CELLNUMS = level*level

                self.cellWidth = int(self.gameRect.width / self.VHNUMS)
                self.cellHeight = int(self.gameRect.height / self.VHNUMS)
            else:
                print('棋盘每条边的格数必须大于等于2')
                self.terminate()
        else:
            print('每条边的格数必须是数字')
            self.terminate()
    def KeyDown(self):
        pass
# 随机生成游戏盘面
    def newGameBoard(self,level):
        board = []
        for i in range(self.CELLNUMS):
            board.append(i)
        blackCell = self.CELLNUMS-1
        board[blackCell] = -1
 
        if type(level) == int:
            if level > 0 and level < 20:
                for i in range(self.CELLNUMS//2 * level):
                    direction = random.randint(0, 3)
                    if (direction == 0):
                        blackCell = self.__moveLeft(board, blackCell)
                    elif (direction == 1):
                        blackCell = self.__moveRight(board, blackCell)
                    elif (direction == 2):
                        blackCell = self.__moveUp(board, blackCell)
                    elif (direction == 3):
                        blackCell = self.__moveDown(board, blackCell)
                return board, blackCell
            else:
                print('你所设定的难度范围无效')
                self.terminate()
        else:
            print('所设定的难度必须为数字')
            self.terminate()

    def CreateGameBoard(self,level = 10):
        self.gameBoard, self.blackCell = self.newGameBoard(level)
        self.isRand = True
        pass
    # 若空白图像块不在最左边，则将空白块左边的块移动到空白块位置  
    def __moveRight(self,board, blackCell):
        if blackCell % self.VHNUMS == 0:
            return blackCell
        board[blackCell-1], board[blackCell] = board[blackCell], board[blackCell-1]
        return blackCell-1
    def MoveRight(self):
        self.MouseDownAroundBlank = 'no'
        self.blackCell = self.__moveRight(self.gameBoard, self.blackCell)
    # 若空白图像块不在最右边，则将空白块右边的块移动到空白块位置  
    def __moveLeft(self,board, blackCell):
        if blackCell % self.VHNUMS == self.VHNUMS-1:
            return blackCell
        board[blackCell+1], board[blackCell] = board[blackCell], board[blackCell+1]
        return blackCell+1
    def MoveLeft(self):
        self.MouseDownAroundBlank = 'no'
        self.blackCell = self.__moveLeft(self.gameBoard, self.blackCell)
    # 若空白图像块不在最上边，则将空白块上边的块移动到空白块位置  
    def __moveDown(self,board, blackCell):
        if blackCell < self.VHNUMS:
            return blackCell
        board[blackCell-self.VHNUMS], board[blackCell] = board[blackCell], board[blackCell-self.VHNUMS]
        return blackCell-self.VHNUMS
    def MoveDown(self):
        self.MouseDownAroundBlank = 'no'
        self.blackCell = self.__moveDown(self.gameBoard, self.blackCell)
    # 若空白图像块不在最下边，则将空白块下边的块移动到空白块位置  
    def __moveUp(self,board, blackCell):
        if blackCell >= self.CELLNUMS-self.VHNUMS:
            return blackCell
        board[blackCell+self.VHNUMS], board[blackCell] = board[blackCell], board[blackCell+self.VHNUMS]
        return blackCell+self.VHNUMS
    def MoveUp(self):
        self.MouseDownAroundBlank = 'no'
        self.blackCell = self.__moveUp(self.gameBoard, self.blackCell)
    # 是否完成
    def isFinished(self,board, blackCell):
        for i in range(self.CELLNUMS-1):
            if board[i] != i:
                return False
        return True
    def SetImage(self,index: int):
        if type(index) == int:
            if index >= 0 and index <= 10:
                self.gameImage = pygame.image.load(Images.Get(str(index)+'.png'))
                self.gameRect = self.gameImage.get_rect()
                self.isImage = True
            else:
                print('图片编号超出范围')
                self.terminate()
        else:
            print('图片编号必须是数字')
            self.terminate()
        pass
    def SetSound(self,index = 1):
        if type(index) == int:
            if index >= 1 and index <= 6:
                self.soundIndex = index
                self.m = pygame.mixer.Sound(ogg.Get(str(index)+'.ogg'))
            else:
                print('音效编号超出范围')
                self.terminate()
        else:
            print('音效编号必须是数字')
            self.terminate()
        pass
    def PlayerSound(self):
        self.m.play(0)
    def isKey(self):
        if self.isKeyDown or self.isMouseDown:
            self.isKeyDown = self.isMouseDown = False
            return True
        else:
            return False
    def isAroundBlank(self):
        if not self.isMouseAroundBlank: self.isMouseAroundBlank = True
        pass
    def IsGameWin(self):
        return self.finish
    def RestoreImage(self):
        self.gameBoard[self.blackCell] = self.CELLNUMS-1
    def Draw(self):
        if self.isRun:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.terminate()
                if self.isRand:
                    if event.type == KEYDOWN:
                        if not self.isKeyDown and not self.isA:
                            self.isKeyDown = True
                        if not self.isA:
                            isA=True
                        if event.key == K_LEFT or event.key == ord('a'):
                            self.blackCell = self.__moveLeft(self.gameBoard, self.blackCell)
                        if event.key == K_RIGHT or event.key == ord('d'):
                            self.blackCell = self.__moveRight(self.gameBoard, self.blackCell)
                        if event.key == K_UP or event.key == ord('w'):
                            self.blackCell = self.__moveUp(self.gameBoard, self.blackCell)
                        if event.key == K_DOWN or event.key == ord('s'):
                            self.blackCell = self.__moveDown(self.gameBoard, self.blackCell)
                    else:
                        self.isKeyDown = False
                        isA=False
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        if not self.isMouseDown and not self.isB:
                            self.isMouseDown = True
                        if not self.isB:
                            isB=True
                        x, y = pygame.mouse.get_pos()
                        col = int(x / self.cellWidth)
                        row = int(y / self.cellHeight)
                        index = col + row * self.VHNUMS
                        if (index == self.blackCell-1 or index == self.blackCell+1 or index == self.blackCell-self.VHNUMS or index == self.blackCell+self.VHNUMS):
                            self.gameBoard[self.blackCell], self.gameBoard[index] = self.gameBoard[index], self.gameBoard[self.blackCell]
                            self.blackCell = index
                    else:
                        isB=False
                        self.isMouseDown = False
            if (self.isFinished(self.gameBoard, self.blackCell)):
                self.finish = True
        

            self.windowSurface.fill(self.BACKGROUNDCOLOR)
            if self.isImage:
                if not self.isRand:
                    self.windowSurface.blit(self.gameImage, (0,0), self.gameRect)
                else:
                    for i in range(self.CELLNUMS):
                        rowDst = int(i / self.VHNUMS)
                        colDst = int(i % self.VHNUMS)
                        rectDst = pygame.Rect(colDst*self.cellWidth, rowDst*self.cellHeight, self.cellWidth, self.cellHeight)
 
                        if self.gameBoard[i] == -1:
                            continue
 
                        rowArea = int(self.gameBoard[i] / self.VHNUMS)
                        colArea = int(self.gameBoard[i] % self.VHNUMS)
                        rectArea = pygame.Rect(colArea*self.cellWidth, rowArea*self.cellHeight, self.cellWidth, self.cellHeight)
                        self.windowSurface.blit(self.gameImage, rectDst, rectArea)
            if self.isDrawLine:
                for i in range(self.VHNUMS+1):
                    pygame.draw.line(self.windowSurface, self.BLACK, (i*self.cellWidth, 0), (i*self.cellWidth, self.gameRect.height))
                for i in range(self.VHNUMS+1):
                    pygame.draw.line(self.windowSurface, self.BLACK, (0, i*self.cellHeight), (self.gameRect.width, i*self.cellHeight))
            pygame.display.update()
            self.mainClock.tick(self.FPS)
        pass
    def DrawLine(self,isDraw = False):
        self.isDrawLine = isDraw
        pass
    def GameRunTime(self):
        if self.isT:
            self.time_end=time.time()
            sec = self.time_end - self.time_start
            min = 0
            hour = 0
            while sec>60:
                min += 1
                sec -= 60
            while min > 60:
                hour += 1
                min -= 60
            print('一共用时 '+str(int(hour))+' 小时 '+str(int(min))+' 分钟 '+str(int(sec//1))+' 秒')
            self.isT = False
        pass

def Init():
    return klotski()
    pass
    
