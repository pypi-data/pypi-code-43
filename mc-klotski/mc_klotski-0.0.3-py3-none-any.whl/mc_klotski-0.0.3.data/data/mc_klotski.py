import pygame, sys, random
from pygame.locals import *
import Images
# 一些常量
WINDOWWIDTH = 500
WINDOWHEIGHT = 500
BACKGROUNDCOLOR = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
FPS = 40
 
VHNUMS = 2
MAXRANDTIME = 100
CELLNUMS = VHNUMS*VHNUMS

# 初始化
pygame.init()
mainClock = pygame.time.Clock()
 
# 加载图片
gameImage = pygame.image.load(Images.Get('1.png'))
gameRect = gameImage.get_rect()
    
 
# 设置窗口
windowSurface = None
 
cellWidth = None
cellHeight = None
 
finish = False
isMouseAroundBlank = False
isRun = False
isRand = False
isImage = False
isDrawLine = False
isMouseDown = False

myKey = []
gameBoard = None
blackCell = None
MouseDownAroundBlank = 'no'
def Init():
    global isRun
    global windowSurface
    global cellWidth
    global cellHeight

    isRun = True
    windowSurface = pygame.display.set_mode((gameRect.width, gameRect.height))
    pygame.display.set_caption('魔扣拼图')
 
    cellWidth = int(gameRect.width / VHNUMS)
    cellHeight = int(gameRect.height / VHNUMS)

# 退出
def terminate():
    pygame.quit()
    sys.exit()
def SetSide(side = 2):
    if type(side) == int:
        if side >= 1 and side <= 50:
            global VHNUMS
            global CELLNUMS 
            global cellWidth
            global cellHeight
            VHNUMS = side
            CELLNUMS = side*side

            cellWidth = int(gameRect.width / VHNUMS)
            cellHeight = int(gameRect.height / VHNUMS)
        else:
            print('棋盘每条边的格数必须大于等于2')
            terminate()
    else:
        print('每条边的格数必须是数字')
        terminate()
# 随机生成游戏盘面
def newGameBoard(level):
    board = []
    for i in range(CELLNUMS):
        board.append(i)
    blackCell = CELLNUMS-1
    board[blackCell] = -1
 
    if type(level) == int:
        if level > 0 and level < 20:
            for i in range(CELLNUMS * level):
                direction = random.randint(0, 3)
                if (direction == 0):
                    blackCell = __moveLeft(board, blackCell)
                elif (direction == 1):
                    blackCell = __moveRight(board, blackCell)
                elif (direction == 2):
                    blackCell = __moveUp(board, blackCell)
                elif (direction == 3):
                    blackCell = __moveDown(board, blackCell)
            return board, blackCell
        else:
            print('你所设定的难度范围无效')
            terminate()
    else:
        print('所设定的难度必须为数字')
        terminate()

def CreateGameBoard(level = 10):
    global gameBoard
    global blackCell
    global isRand
    gameBoard, blackCell = newGameBoard(level)
    isRand = True
    pass
# 若空白图像块不在最左边，则将空白块左边的块移动到空白块位置  
def __moveRight(board, blackCell):
    if blackCell % VHNUMS == 0:
        return blackCell
    board[blackCell-1], board[blackCell] = board[blackCell], board[blackCell-1]
    return blackCell-1
def MoveRight():
    global blackCell
    global MouseDownAroundBlank
    MouseDownAroundBlank = 'no'
    blackCell = __moveRight(gameBoard, blackCell)
# 若空白图像块不在最右边，则将空白块右边的块移动到空白块位置  
def __moveLeft(board, blackCell):
    if blackCell % VHNUMS == VHNUMS-1:
        return blackCell
    board[blackCell+1], board[blackCell] = board[blackCell], board[blackCell+1]
    return blackCell+1
def MoveLeft():
    global blackCell
    global MouseDownAroundBlank
    MouseDownAroundBlank = 'no'
    blackCell = __moveLeft(gameBoard, blackCell)
# 若空白图像块不在最上边，则将空白块上边的块移动到空白块位置  
def __moveDown(board, blackCell):
    if blackCell < VHNUMS:
        return blackCell
    board[blackCell-VHNUMS], board[blackCell] = board[blackCell], board[blackCell-VHNUMS]
    return blackCell-VHNUMS
def MoveDown():
    global blackCell
    global MouseDownAroundBlank
    MouseDownAroundBlank = 'no'
    blackCell = __moveDown(gameBoard, blackCell)
# 若空白图像块不在最下边，则将空白块下边的块移动到空白块位置  
def __moveUp(board, blackCell):
    if blackCell >= CELLNUMS-VHNUMS:
        return blackCell
    board[blackCell+VHNUMS], board[blackCell] = board[blackCell], board[blackCell+VHNUMS]
    return blackCell+VHNUMS
def MoveUp():
    global blackCell
    global MouseDownAroundBlank
    MouseDownAroundBlank = 'no'
    blackCell = __moveUp(gameBoard, blackCell)
def KeyDown(key: str):
    global myKey
    myKey.append(key)
# 是否完成
def isFinished(board, blackCell):
    for i in range(CELLNUMS-1):
        if board[i] != i:
            return False
    return True
def SetImage(index: int):
    if type(index) == int:
        if index >= 0 and index <= 10:
            global gameImage
            global gameRect
            global isImage
            gameImage = pygame.image.load(Images.Get(str(index)+'.png'))
            gameRect = gameImage.get_rect()
            isImage = True
        else:
            print('图片编号超出范围')
            terminate()
    else:
        print('图片编号必须是数字')
        terminate()
    pass

def isAroundBlank():
    global isMouseAroundBlank
    if not isMouseAroundBlank: isMouseAroundBlank = True
    pass
def Draw():
    #print(isRun)
    if isRun:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if finish:
                continue
            if isRand:
                if event.type == KEYDOWN:
                    pass
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    global isMouseDown
                    if not isMouseDown:
                        isMouseDown = True
                        global blackCell
                        global MouseDownAroundBlank
                        x, y = pygame.mouse.get_pos()
                        col = int(x / cellWidth)
                        row = int(y / cellHeight)
                        index = col + row * VHNUMS
                        if index == blackCell-1:
                            MouseDownAroundBlank = 'right'
                        elif index == blackCell+1:
                            MouseDownAroundBlank = 'left'
                        elif index == blackCell-VHNUMS:
                            MouseDownAroundBlank = 'down'
                        elif index == blackCell+VHNUMS:
                            MouseDownAroundBlank = 'up'
                        else:
                            MouseDownAroundBlank = 'no'
                else:
                    isMouseDown = False
        windowSurface.fill(BACKGROUNDCOLOR)
        if isImage:
            if not isRand:
                windowSurface.blit(gameImage, (0,0), gameRect)
            else:
                for i in range(CELLNUMS):
                    rowDst = int(i / VHNUMS)
                    colDst = int(i % VHNUMS)
                    rectDst = pygame.Rect(colDst*cellWidth, rowDst*cellHeight, cellWidth, cellHeight)
 
                    if gameBoard[i] == -1:
                        continue
 
                    rowArea = int(gameBoard[i] / VHNUMS)
                    colArea = int(gameBoard[i] % VHNUMS)
                    rectArea = pygame.Rect(colArea*cellWidth, rowArea*cellHeight, cellWidth, cellHeight)
                    windowSurface.blit(gameImage, rectDst, rectArea)
        if isDrawLine:
            for i in range(VHNUMS+1):
                pygame.draw.line(windowSurface, BLACK, (i*cellWidth, 0), (i*cellWidth, gameRect.height))
            for i in range(VHNUMS+1):
                pygame.draw.line(windowSurface, BLACK, (0, i*cellHeight), (gameRect.width, i*cellHeight))
        pygame.display.update()
        mainClock.tick(FPS)
    pass
def DrawLine(isDraw = False):
    global isDrawLine
    if not isDrawLine: isDrawLine = True
    pass