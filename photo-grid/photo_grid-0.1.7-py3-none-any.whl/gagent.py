# basic imports
import numpy as np

# 3rd party imports
from PyQt5.QtCore import QRect

# self imports
from .lib import *
from .dir import Dir


class GAgent():
    
    def __init__(self):
        """
        ----------
        Parameters
        ----------
        """

        self.agents = []
        self.img = None
        self.shape = (0, 0)
        self.imgH, self.imgW = self.shape
        self.nRow, self.nCol = 0, 0
        self.rowFake, self.colFake = -1, -1
        self.coef = 0

    def setup(self, gmap, img):
        """
        ----------
        Parameters
        ----------
        """

        self.agents = []
        self.img = img
        self.shape = self.img.shape
        self.imgH, self.imgW = self.shape
        self.nRow, self.nCol = gmap.nRow, gmap.nCol
        dt = gmap.dt
        fr, fc = [], []

        for row in range(self.nRow):
            lsAgentsRow = [] 
            for col in range(self.nCol):
                try:
                    entry = dt[(dt.row == row) & (dt.col == col)].iloc[0]                
                    ptX, ptY = entry["pt"]
                    name = entry["name"]
                except:
                    # handle inconsistant # of rows/cols
                    fr.append(row)
                    fc.append(col)
                    ptX, ptY = (-1, -1)
                    name = "_FAKE"
                agent = Agent(name=name, row=row, col=col)
                self.setCoordinate(agent=agent, x=ptX, y=ptY)
                lsAgentsRow.append(agent) 
            self.agents.append(lsAgentsRow)

        # determine fake plots
        if len(fr) > 1 and np.array(fr).var() == 0:
            self.rowFake = fr[0]
        elif len(fc) > 1 and np.array(fc).var()==0:
            self.colFake = fc[0]

    def get(self, row, col):
        """
        ----------
        Parameters
        ----------
        """

        if row < 0 or col < 0:
            # negative index
            return False
        else:
            try:
                return self.agents[row][col]
            except:
                # outside frame
                return False
    
    def getNeib(self, row, col, dir):
        """
        ----------
        Parameters
        ----------
        """

        if dir == Dir.EAST:
            agent = self.get(row, col+1)
            if not agent:
                # outside image
                return False            
            elif (col+1 == self.colFake):
                # on fake line
                return agent
            elif agent.isFake():
                return self.get(row-1, col+1)
            else:
                return agent
        elif dir == Dir.SOUTH:
            agent = self.get(row+1, col)
            if not agent:
                # outside image
                return False
            elif (row+1 == self.rowFake):
                # on fake line
                return agent
            elif agent.isFake():
                return self.get(row+1, col-1)
            else:
                return agent
        elif dir == Dir.WEST:
            agent = self.get(row, col-1)
            if not agent:
                # outside image
                return False
            elif agent.isFake():
                return self.get(row-1, col-1)
            else:
                return agent
        elif dir == Dir.NORTH:
            agent = self.get(row-1, col)
            if not agent:
                # outside image
                return False
            elif agent.isFake():
                return self.get(row+1, col-1)
            else:
                return agent
                
    def cpuPreDim(self, tol=5):
        """
        ----------
        Parameters
        ----------
        """
        
        for row in range(self.nRow):
            for col in range(self.nCol):
                agentSelf = self.get(row, col)
                agentSelf.resetBorderHard()
                if not agentSelf or agentSelf.isFake():
                    continue
                rgTemp = dict()
                for axis in [0, 1]:
                    # extract direction info and 1dImg
                    dir1 = Dir(axis) # axis:0, return N(0) and S(2)
                    dir2 = Dir(axis+2) # axis:1, return W(1) and E(3)
                    axisRev = (not axis)*1
                    img1d = self.img[agentSelf.y,
                                     :] if axis else self.img[:, agentSelf.x]
                    # extract agents info
                    ptSelf = agentSelf.getCoordinate()[axisRev]
                    agentNeig1 = self.getNeib(row, col, dir1)
                    agentNeig2 = self.getNeib(row, col, dir2)
                    # if both neighbors exists
                    if (agentNeig1 != 0) and (agentNeig2 != 0) and (not agentNeig1.isFake()) and (not agentNeig2.isFake()):
                        ptNeig1 = agentNeig1.getCoordinate()[axisRev]
                        ptNeig2 = agentNeig2.getCoordinate()[axisRev]
                        ptMid = int((ptNeig1+ptNeig2)/2)
                        ptBd1 = int((ptNeig1+ptMid)/2)
                        ptBd2 = int((ptNeig2+ptMid)/2)
                    # if only left/up side exist
                    elif agentNeig1:
                        ptNeig1 = agentNeig1.getCoordinate()[axisRev]
                        ptBd1 = int((ptSelf+ptNeig1)/2)
                        ptBd2 = self.img.shape[axis]
                        self.setBorder(agentSelf, dir2, ptBd2)
                    # if only right/down side exist
                    elif agentNeig2:
                        ptNeig2 = agentNeig2.getCoordinate()[axisRev]
                        ptBd1 = 0
                        ptBd2 = int((ptSelf+ptNeig2)/2)
                        self.setBorder(agentSelf, dir1, ptBd1)
                    # if neither side exist
                    elif self.nRow==1 or self.nCol==1:
                        ptBd1 = 0
                        ptBd2 = self.img.shape[axis]
                        self.setBorder(agentSelf, dir1, ptBd1)
                        self.setBorder(agentSelf, dir2, ptBd2)

                    # get predim
                    ## negative side (neighber 1)
                    pt_cur = ptSelf
                    tol_cur = 0
                    while (tol_cur < tol) & (pt_cur > ptBd1):
                        try:
                            img_val = img1d[pt_cur]
                        except:
                            break
                        tol_cur += 1 if img_val==0 else -tol_cur #else reset to 0
                        pt_cur -= 1
                    rgTemp[dir1.name] = pt_cur
                    ## positive side (neighber 2)
                    pt_cur = ptSelf
                    tol_cur = 0
                    while (tol_cur < tol) & (ptBd2 > pt_cur):
                        try:
                            img_val = img1d[pt_cur]
                        except:
                            break
                        tol_cur += 1 if img_val==0 else -tol_cur #else reset to 0
                        pt_cur += 1
                    rgTemp[dir2.name] = pt_cur
                agentSelf.setPreDim(rgTemp)

    def autoSeg(self, coefGrid=.2):
        """
        ----------
        Parameters
        ----------
        """
        self.coef = coefGrid
        
        # reset the border first
        self.resetBorder()
        bugmsg(self.get(1, 3).getBorder(Dir.EAST), "row 1 col 3 DIR EAST")
        # loop over rows and cols
        for row in range(self.nRow):
            for col in range(self.nCol):
                agentSelf = self.get(row, col)
                for dir in list([Dir.EAST, Dir.SOUTH]):
                    agentNeib = self.getNeib(row, col, dir)
                    dirNeib = list(Dir)[(dir.value+2) %
                                         4]  # reverse the direction
                    if not agentSelf or agentSelf.isFake() or not agentNeib or agentNeib.isFake():
                        continue
                    # reset agent border
                    agentSelf.border[dir.name] = agentSelf.border_reset[dir.name]
                    agentNeib.border[dirNeib.name] = agentNeib.border_reset[dirNeib.name]
                    # calculate border
                    dist_agents = abs(
                        agentSelf.x-agentNeib.x) if dir == Dir.EAST else abs(agentSelf.y-agentNeib.y)
                    while abs(agentSelf.getBorder(dir)-agentNeib.getBorder(dirNeib)) > 1:
                        scASelf = agentSelf.getScoreArea(
                            dir, self.img)
                        scGSelf = agentSelf.getScoreGrid(
                            dir)/dist_agents
                        scANeib = agentNeib.getScoreArea(
                            dirNeib, self.img)
                        scGNeib = agentNeib.getScoreGrid(
                            dirNeib)/dist_agents
                        # except Exception as e:
                        scoreSelf = scASelf - (scGSelf*coefGrid)
                        scoreNeib = scANeib - (scGNeib*coefGrid)
                        if scoreSelf > scoreNeib:                            
                            self.updateBorder(agentSelf, dir, 1)
                        elif scoreSelf < scoreNeib:
                            self.updateBorder(agentNeib, dirNeib, -1)
                        else:
                            self.updateBorder(agentSelf, dir, 1)
                            self.updateBorder(agentNeib, dirNeib, -1)
        
        # rescue plots on fake line
        if self.rowFake!=-1:
            for col in range(1, self.nCol):
                agent = self.get(self.rowFake, col)
                if not agent.isFake():
                    agentNeig = self.get(self.rowFake-1, col-1)
                    agent.setBorder(Dir.WEST, agentNeig.getBorder(Dir.EAST))
        elif self.colFake!=-1:
            for row in range(1, self.nRow):
                agent = self.get(row, self.colFake)
                if not agent.isFake():
                    agentNeig = self.get(row-1, self.colFake-1)
                    agent.setBorder(Dir.NORTH, agentNeig.getBorder(Dir.SOUTH))

    def fixSeg(self, width, length):
        w_unit = (self.imgW/self.nCol)/100
        l_unit = (self.imgH/self.nRow)/100
        w_side = round(width/2*w_unit)
        l_side = round(length/2*l_unit)
        for row in range(self.nRow):
            for col in range(self.nCol):
                agent = self.get(row, col)
                if not agent or agent.isFake():
                    continue
                agent.resetBorder()
                # set border
                if (row == (self.nRow-1)) & (length == 100):
                    self.setBorder(agent, Dir.SOUTH, self.imgH)
                else:
                    self.setBorder(agent, Dir.SOUTH, agent.y+l_side)
                if (row == 0) & (length == 100):
                    self.setBorder(agent, Dir.NORTH, 0)
                else:
                    self.setBorder(agent, Dir.NORTH, agent.y-l_side)
                if (col == (self.nCol-1)) & (width == 100):
                    self.setBorder(agent, Dir.EAST, self.imgW)
                else:
                    self.setBorder(agent, Dir.EAST, agent.x+w_side)
                if (col == 0) & (width == 100):
                    self.setBorder(agent, Dir.WEST, 0)
                else:
                    self.setBorder(agent, Dir.WEST, agent.x-w_side)

    def setCoordinate(self, agent, x, y):
        agent.setCoordinate(x, y)
        self.checkBorder(agent)

    def updateCoordinate(self, agent, value, axis):
        agent.updateCoordinate(value, axis)
        self.checkBorder(agent)

    def setBorder(self, agent, dir, value):
        agent.setBorder(dir, value)
        self.checkBorder(agent)
    
    def updateBorder(self, agent, dir, value):
        agent.updateBorder(dir, value)
        self.checkBorder(agent)

    def resetCoordinate(self):
        for row in range(self.nRow):
            for col in range(self.nCol):
                try:
                    self.get(row=row, col=col).resetCoordinate()
                except:
                    None

    def resetBorder(self):
        for row in range(self.nRow):
            for col in range(self.nCol):
                try:
                    self.get(row=row, col=col).resetBorder()
                except:
                    None

    def checkBorder(self, agent):
        if agent.border[Dir.NORTH.name] < 0:
            agent.border[Dir.NORTH.name] = 0
        if agent.border[Dir.WEST.name] < 0:
            agent.border[Dir.WEST.name] = 0
        if agent.border[Dir.SOUTH.name] >= self.imgH:
            agent.border[Dir.SOUTH.name] = self.imgH-1
        if agent.border[Dir.EAST.name] >= self.imgW:
            agent.border[Dir.EAST.name] = self.imgW-1

    def align(self, method, axis=0):
        '''
        '''
        if method == 0:
            # None
            for row in range(self.nRow):
                for col in range(self.nCol):
                    agent = self.get(row=row, col=col)
                    if not agent or agent.isFake():
                        continue
                    if axis == 0:
                        dist = agent.y_reset - agent.y
                    elif axis == 1:
                        dist = agent.x_reset - agent.x
                    self.updateCoordinate(agent, dist, axis=axis)
        elif method == 1:
            # Top/Left
            if axis == 0:
                for row in range(self.nRow):
                    val = 1e10
                    for col in range(self.nCol):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        val_temp = agent.y
                        val = val_temp if val_temp < val else val
                    for col in range(self.nCol):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        dist = val - agent.y
                        self.updateCoordinate(agent, dist, axis=axis)
            elif axis == 1:
                for col in range(self.nCol):
                    val = 1e10
                    for row in range(self.nRow):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        val_temp = agent.x
                        val = val_temp if val_temp < val else val
                    for row in range(self.nRow):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        dist = val - agent.x
                        self.updateCoordinate(agent, dist, axis=axis)
        elif method == 3:
            # Bottom/Right
            if axis == 0:
                for row in range(self.nRow):
                    val = -1
                    for col in range(self.nCol):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        val_temp = agent.y
                        val = val_temp if val_temp > val else val
                    for col in range(self.nCol):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        dist = val - agent.y
                        self.updateCoordinate(agent, dist, axis=axis)
            elif axis == 1:
                for col in range(self.nCol):
                    val = -1
                    for row in range(self.nRow):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        val_temp = agent.x
                        val = val_temp if val_temp > val else val
                    for row in range(self.nRow):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        dist = val - agent.x
                        self.updateCoordinate(agent, dist, axis=axis)
        elif method == 2:
            # Middle/Center
            if axis == 0:
                for row in range(self.nRow):
                    val = 0
                    for col in range(self.nCol):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        val += agent.y
                    val = int(val/(self.nCol))
                    for col in range(self.nCol):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        dist = val - agent.y
                        self.updateCoordinate(agent, dist, axis=axis)
            elif axis == 1:
                for col in range(self.nCol):
                    val = 0
                    for row in range(self.nRow):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        val += agent.x
                    val = int(val/(self.nRow))
                    for row in range(self.nRow):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        dist = val - agent.x
                        self.updateCoordinate(agent, dist, axis=axis)

    def pan(self, axis, target, value):
        if axis == 0:
            for col in range(self.nCol):
                agent = self.get(row=target, col=col)
                dist = value - agent.y
                self.updateCoordinate(agent, dist, axis=axis)
        elif axis == 1:
            for row in range(self.nRow):
                agent = self.get(row=row, col=target)
                dist = value - agent.x
                self.updateCoordinate(agent, dist, axis=axis)

    def distributed(self, axis, isEven):
        if isEven:
            if axis == 0: # row
                y_North = self.get(row=0, col=0).y
                y_South = self.get(row=self.nRow-1, col=0).y
                dist = y_South-y_North
                pos_new = np.arange(y_North, y_South, dist/(self.nRow-1))
                pos_new = np.append(pos_new, y_South)
                for row in range(self.nRow):
                    for col in range(self.nCol):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        dist = pos_new[row] - agent.y
                        self.updateCoordinate(agent=agent, value=dist, axis=0)
            else:       # col
                x_West = self.get(row=0, col=0).x
                x_East = self.get(row=0, col=self.nCol-1).x
                dist = x_East-x_West
                pos_new = np.arange(x_West, x_East, dist/(self.nCol-1))
                pos_new = np.append(pos_new, x_East)
                for col in range(self.nCol):
                    for row in range(self.nRow):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        dist = pos_new[col] - agent.x
                        self.updateCoordinate(agent=agent, value=dist, axis=1)
        else:
            for row in range(self.nRow):
                for col in range(self.nCol):
                    agent = self.get(row=row, col=col)
                    if not agent or agent.isFake():
                        continue
                    if axis == 0:
                        dist = agent.y_reset - agent.y
                    elif axis == 1:
                        dist = agent.x_reset - agent.x
                    self.updateCoordinate(agent=agent, value=dist, axis=axis)

class Agent():
    def __init__(self, name, row, col):
        '''
        '''
        self.name = name
        self.row, self.col = row, col
        self.y, self.x = 0, 0
        self.y_reset, self.x_reset = 0, 0
        self.pre_rg_W, self.pre_rg_H = range(0), range(0)
        self.border, self.border_reset = dict(), dict()
        for dir in list([Dir.NORTH, Dir.EAST, Dir.SOUTH, Dir.WEST]):
            self.border[dir.name] = 0
            self.border_reset[dir.name] = 0

    def getCoordinate(self):
        '''
        '''
        return self.x, self.y

    def getPreDim(self, isHeight=True):
        '''
        '''
        return self.pre_rg_H if isHeight else self.pre_rg_W

    def getBorder(self, dir):
        return self.border[dir.name]

    def getScoreArea(self, dir, img):
        '''
        Will ragne from 0 to 1
        '''
        isH = dir.value%2 # E->1, S->0
        rg = self.getPreDim(isHeight=isH)
        bd = self.getBorder(dir)
        return img[rg, bd].mean() if isH else img[bd, rg].mean()

    def getScoreGrid(self, dir):
        '''
        Will ragne from 0 to 1
        '''
        isWE = dir.value%2 # is W, E or N, S
        pt_center = self.x if isWE else self.y
        pt_cur = self.getBorder(dir)
        return abs(pt_cur-pt_center)

    def setCoordinate(self, x, y):
        '''
        '''
        self.x, self.y = int(x), int(y)
        self.x_reset, self.y_reset = int(x), int(y)
        self.setBorder(Dir.NORTH, y)
        self.setBorder(Dir.SOUTH, y)
        self.setBorder(Dir.WEST, x)
        self.setBorder(Dir.EAST, x)

    def setPreDim(self, rg):
        '''
        '''
        self.pre_rg_W = range(rg['WEST'], rg['EAST'])
        self.pre_rg_H = range(rg['NORTH'], rg['SOUTH'])
        self.x = int((rg['EAST']+rg['WEST'])/2)
        self.y = int((rg['NORTH']+rg['SOUTH'])/2)
        self.x_reset, self.y_reset = self.x, self.y
        for dir in list([Dir.NORTH, Dir.WEST, Dir.SOUTH, Dir.EAST]):
            self.border_reset[dir.name] = self.border[dir.name]

    def setBorder(self, dir, value):
        '''
        '''
        self.border[dir.name] = int(value)

    def updateBorder(self, dir, value):
        '''
        '''
        self.border[dir.name] += int(value)

    def updateCoordinate(self, value, axis=0):
        '''
        '''
        value = int(value)
        if axis==0:
            self.y += value
            self.border[Dir.NORTH.name] += value
            self.border[Dir.SOUTH.name] += value
        elif axis==1:
            self.x += value
            self.border[Dir.WEST.name] += value
            self.border[Dir.EAST.name] += value
    
    def getQRect(self):
        """
        GUI SPECIFIC
        """
        x = self.getBorder(Dir.WEST)
        y = self.getBorder(Dir.NORTH)
        w = self.getBorder(Dir.EAST) - x
        h = self.getBorder(Dir.SOUTH) - y
        return QRect(x, y, w, h)

    def resetCoordinate(self):
        self.x = self.x_reset
        self.y = self.y_reset
        self.resetBorder()

    def resetBorder(self):
        for dir in list([Dir.NORTH, Dir.WEST, Dir.SOUTH, Dir.EAST]):
            self.border[dir.name] = self.border_reset[dir.name]

    def resetBorderHard(self):
        self.setBorder(Dir.WEST, self.x)
        self.setBorder(Dir.EAST, self.x)
        self.setBorder(Dir.NORTH, self.y)
        self.setBorder(Dir.SOUTH, self.y)

    def isFake(self):
        return self.name=="_FAKE"
