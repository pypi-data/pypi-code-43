from typing import List, Dict, Tuple, AnyStr
import threading
import numpy as np
import time

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtWinExtras import *

import vtk

import vmi

tr = QObject()
tr = tr.tr


class SelectEdit(QObject, vmi.Menu, vmi.Mouse):
    def __init__(self, view: vmi.View, name=None):
        QObject.__init__(self)

        self.name = name if name else tr('选区编辑 (Select edit)')
        vmi.Menu.__init__(self, name=self.name)
        self.actions = {'Activate': QAction(tr('激活 (Activate)')),
                        'Cancel': QAction(tr('取消 (Cancel)')),
                        'Apply': QAction(tr('应用 (Apply)')),
                        'CurveType': QAction('')}

        self.actions['Activate'].triggered.connect(self.activate)
        self.actions['Cancel'].triggered.connect(self.cancel)
        self.actions['Apply'].triggered.connect(self.apply)
        self.actions['CurveType'].triggered.connect(self.setCurveType)

        def aboutToShow():
            self.actions['Activate'].setEnabled(not self.isActivated())
            self.actions['Cancel'].setEnabled(self.isActivated())
            self.actions['Apply'].setEnabled(self.canApply())
            self.actions['CurveType'].setText('{} = {}'.format(tr('线型 (Curve type)'),
                                                               self.curveTypeText[self.curveType]))

            self.menu.clear()
            self.menu.addAction(self.actions['Activate'])
            self.menu.addAction(self.actions['Cancel'])
            self.menu.addSeparator()
            self.menu.addAction(self.actions['CurveType'])
            self.menu.addSeparator()
            self.menu.addAction(self.actions['Apply'])

        self.menu.aboutToShow.connect(aboutToShow)

        vmi.Mouse.__init__(self, menu=self)
        self.mouse['LeftButton']['PressMove'] = self.mouseblock
        self.mouse['LeftButton']['PressRelease'] = self.pick

        self.view = view

        self.nodes: List[Tuple] = []
        self.nodeActors: List[vmi.PolyActor] = []
        self.nodeShapes: List[vmi.ShapeData] = []

        self.curveShape = vmi.ShapeData()
        self.curveActor = vmi.PolyActor(self.view)
        self.curveActor.color(rgb=(1, 0.2, 0.2))
        self.curveActor.size(line=4)
        self.curveActor.alwaysOnTop(True)
        self.curveActor.pickable(True)
        self.curveActor.bind(self.curveShape)
        self.curveActor.mouse['LeftButton']['PressMove'] = self.move

        self.curveType = 0
        self.curveTypeText = dict(enumerate([tr('折线 (Polyline)'), tr('样条 (Spline)')]))

        self.assignDefault = -3071
        self._Bind: vmi.ImageSlice = None

    def __setstate__(self, s):
        self.__init__(s['view'], s['name'])
        self.__dict__.update(s)
        s = self.__dict__

    def __getstate__(self):
        s = self.__dict__.copy()
        for kw in ['menu', 'actions', '__METAOBJECT__']:
            if kw in s:
                del s[kw]
        return s

    def move(self, **kwargs):
        if kwargs['picked'] in self.nodeActors:
            over = self.view.mouseOverFPlane()
            j = self.nodeActors.index(kwargs['picked'])
            node = [self.nodes[j][i] + over[i] for i in range(3)]
            if node not in self.nodes:
                self.nodes[j] = node
                self.rebuild()
        elif kwargs['picked'] is self.curveActor:
            over = self.view.mouseOverFPlane()
            for j in range(len(self.nodes)):
                for i in range(3):
                    self.nodes[j][i] += over[i]
            self.rebuild()

    def pick(self, **kwargs):
        if kwargs['double']:
            if kwargs['picked'] in self.nodeActors:
                j = self.nodeActors.index(kwargs['picked'])
                self.removeNode(self.nodeActors[j])
            else:
                pt = self.view.pickFPlane()
                if self._Bind is not None:
                    cnt = vmi.imCenter(self._Bind.data())
                    look = self.view.camera('look')
                    pt = vmi.ptOnPlane(pt, cnt, look)
                self.addNode(pt)

    def nodeMenu(self, **kwargs):
        if kwargs['picked'] in self.nodeActors:
            i = self.nodeActors.index(kwargs['picked'])
            pos = self.view.pickToDisplay(self.nodes[i])
            pos = (pos.x(), pos.y())

            menu = QMenu()
            nodeReset = menu.addAction(tr('坐标 (Coordinates)') + ' = ' + repr(pos))

            action = menu.exec_(QCursor.pos())

            if action is nodeReset:
                size = (self.view.width(), self.view.height())
                pos = vmi.askInts([0, 0], pos, size, '{} {}'.format(
                    tr('坐标 (Coordinates)'), repr(size)))
                if pos is not None:
                    node = self.view.pickFPlane(QPoint(pos[0], pos[1]))
                    if node not in self.nodes:
                        self.nodes[i] = node
                        self.rebuild()

    def bind(self, bind):
        if self._Bind is not bind:
            self._Bind = bind

    def setCurveType(self, *args, lineType=None):
        if lineType is None:
            self.curveType += 1
            self.curveType = self.curveType % len(self.curveTypeText)
            self.rebuild()
        elif lineType.lower() == 'polyline':
            self.curveType = 0
            self.rebuild()
        elif lineType.lower() == 'spline':
            self.curveType = 1
            self.rebuild()

    def activate(self):
        self.view.addMouse(self)

    def isActivated(self):
        return self.view.checkMouse(self)

    def canApply(self):
        return bool(self._Bind) and len(self.nodes) > 2

    def apply(self):
        if self._Bind is not None:
            target = vmi.askInt(vtk.VTK_SHORT_MIN, self.assignDefault, vtk.VTK_SHORT_MAX, tr('赋值 (Assign value)'))

            face = vmi.mkFace(self.curveShape.shape())
            look = self.view.camera('look')
            lthn = vmi.imLength(self._Bind.data(), self.view.camera('look'))
            region = vmi.mkPrism(face, [-look[i] for i in range(3)], lthn)
            region = vmi.mkBoolean_Union(vmi.mkPrism(face, look, lthn), region)
            region = vmi.mkPolyData_Shape(region)

            stencil = vmi.imStencil(self._Bind.data(), region)
            ext = vmi.imExtent(self._Bind.data(), region.GetBounds())
            it = vmi.imIterator(self._Bind.data(), ext, stencil)

            p = [0]

            def func():
                count, sum = 0, (ext[5] - ext[4] + 1) * (ext[3] - ext[2] + 1) * (ext[1] - ext[0] + 1)
                while not it.IsAtEnd():
                    if it.IsInStencil():
                        vmi.imValue(self._Bind.data(), it.GetIndex(), target)
                    it.Next()
                    count += 1
                    p[0] = 100 * count / sum

            t = threading.Thread(target=func)
            t.start()

            vmi.appwait(t, p)
            self.view.updateInTime()

    def cancel(self):
        self.view.removeMouse(self)
        self.clearNode()
        self.rebuild()

    def addNode(self, pt):
        if pt not in self.nodes:
            self.nodes.append(pt)
            self.nodeShapes.append(vmi.ShapeData())
            self.nodeActors.append(vmi.PolyActor(self.view))
            self.nodeActors[-1].color(rgb=(0.2, 0.6, 1))
            self.nodeActors[-1].size(point=8)
            self.nodeActors[-1].pickable(True)
            self.nodeActors[-1].alwaysOnTop(True)
            self.nodeActors[-1].bind(self.nodeShapes[-1])
            self.nodeActors[-1].mouse['LeftButton']['PressMove'] = self.move
            self.nodeActors[-1].mouse['LeftButton']['PressRelease'] = self.pick
            self.nodeActors[-1].mouse['RightButton']['PressRelease'] = self.nodeMenu
            self.rebuild()

    def removeNode(self, actorNode: vmi.PolyActor):
        actorNode.delete()
        i = self.nodeActors.index(actorNode)
        del self.nodes[i], self.nodeShapes[i], self.nodeActors[i]
        self.rebuild()

    def clearNode(self):
        for actorNode in self.nodeActors:
            actorNode.delete()
        self.nodes.clear()
        self.nodeShapes.clear()
        self.nodeActors.clear()
        self.rebuild()

    def rebuild(self):
        for i in range(len(self.nodes)):
            self.nodeShapes[i].clone(vmi.mkVertex(vmi.mkPnt(self.nodes[i])))
        if len(self.nodes) > 2:
            if self.curveType == 0:
                self.curveShape.clone(vmi.mkWire(vmi.mkSegments(pts=self.nodes, closed=True)))
            elif self.curveType == 1:
                self.curveShape.clone(vmi.mkWire(vmi.mkBSplineKochanek(pts=self.nodes, closed=True)))
        elif len(self.nodes) > 1:
            if self.curveType == 0:
                self.curveShape.clone(vmi.mkWire(vmi.mkSegments(pts=self.nodes, closed=False)))
            elif self.curveType == 1:
                self.curveShape.clone(vmi.mkWire(vmi.mkBSplineKochanek(pts=self.nodes, closed=False)))
        else:
            self.curveShape.clone(None)
        self.curveActor.view.updateInTime()


class RegionResample(QObject, vmi.Menu, vmi.Mouse):
    def __init__(self, view: vmi.View, name=None):
        QObject.__init__(self)

        self.name = name if name else tr('区域重采样 (Region resample)')
        vmi.Menu.__init__(self, name=self.name)
        self.actions = {'Activate': QAction(tr('激活 (Activate)')),
                        'Cancel': QAction(tr('取消 (Cancel)')),
                        'Apply': QAction(tr('应用 (Apply)')),
                        'SetBnd': QAction(tr('输入边界 (Input bounds)')),
                        'ResetBnd': QAction(tr('重置边界 (Reset bounds)'))}

        self.actions['Activate'].triggered.connect(self.activate)
        self.actions['Cancel'].triggered.connect(self.cancel)
        self.actions['Apply'].triggered.connect(self.apply)
        self.actions['SetBnd'].triggered.connect(self.setBnd)
        self.actions['ResetBnd'].triggered.connect(self.resetBnd)

        def aboutToShow():
            self.actions['Activate'].setEnabled(not self.isActivated())
            self.actions['Cancel'].setEnabled(self.isActivated())
            self.actions['Apply'].setEnabled(self.canApply())
            self.actions['ResetBnd'].setEnabled(bool(self._Bind))

            self.menu.clear()
            self.menu.addAction(self.actions['Activate'])
            self.menu.addAction(self.actions['Cancel'])
            self.menu.addSeparator()
            self.menu.addAction(self.actions['SetBnd'])
            self.menu.addAction(self.actions['ResetBnd'])
            self.menu.addSeparator()
            self.menu.addMenu(self.view.menu)
            self.menu.addSeparator()
            self.menu.addAction(self.actions['Apply'])

        self.menu.aboutToShow.connect(aboutToShow)

        vmi.Mouse.__init__(self, menu=self)

        self.view = view

        self.regionShapes = []
        self.regionActors = []

        for k in range(3):
            jlist = [], []
            for j in range(2):
                ilist = [], []
                for i in range(2):
                    shape = vmi.ShapeData()
                    actor = vmi.PolyActor(self.view)
                    actor.color(rgb=[1, 0.2, 0.2])
                    actor.size(line=4)
                    actor.alwaysOnTop(True)
                    actor.pickable(True)
                    actor.bind(shape)
                    actor.mouse['LeftButton']['PressMove'] = self.move

                    ilist[0].append(shape)
                    ilist[1].append(actor)
                jlist[0].append(ilist[0])
                jlist[1].append(ilist[1])
            self.regionShapes.append(jlist[0])
            self.regionActors.append(jlist[1])

        self._Bind: vmi.ImageSlice = None
        self._Bnd = [0, 1, 0, 1.5, 0, 2]

    def __setstate__(self, s):
        self.__init__(s['view'], s['name'])
        self.__dict__.update(s)
        s = self.__dict__

    def __getstate__(self):
        s = self.__dict__.copy()
        for kw in ['menu', 'actions', '__METAOBJECT__']:
            if kw in s:
                del s[kw]
        return s

    def activate(self):
        self.view.addMouse(self)
        self.rebuild()

    def isActivated(self):
        return self.view.checkMouse(self)

    def canApply(self):
        return bool(self._Bind)

    def apply(self):
        if self._Bind is not None:
            spc = vmi.askFloats([0.1, 0.1, 0.1], vmi.imSpacing(self._Bind.data()), [5, 5, 5], 3,
                                tr('采样间距 (Sample spacing) (x, y, z) (mm)'))
            if spc is not None:
                ori, dim = [self._Bnd[0], self._Bnd[2], self._Bnd[4]], [1, 1, 1]
                for i in range(3):
                    dim[i] = int((self._Bnd[2 * i + 1] - self._Bnd[2 * i]) / spc[i])
                ext = [0, dim[0] - 1, 0, dim[1], 0, dim[2]]
                self._Bind.clone(vmi.imResample(self._Bind.data(), ori, ext, spc))
                self.view.updateInTime()

    def cancel(self):
        self.view.removeMouse(self)
        self.rebuild()

    def move(self, **kwargs):
        picked, k, j, i = False, 0, 0, 0
        for k in range(3):
            for j in range(2):
                for i in range(2):
                    if kwargs['picked'] is self.regionActors[k][j][i]:
                        picked = True
                        break
                if picked is True:
                    break
            if picked is True:
                break
        if picked:
            bnd = [[self._Bnd[0], self._Bnd[2], self._Bnd[4]],
                   [self._Bnd[1], self._Bnd[3], self._Bnd[5]]]
            for delta in range(1, 3):
                a, b = (k + delta) % 3, [k, j, i][delta]
                vt = [0, 0, 0]
                vt[a] = 1
                over = self.view.mouseOverFPlane(vt)
                over = vmi.signNorm3(over, vt)
                bnd[b][a] += over
            self._Bnd = [bnd[0][0], bnd[1][0], bnd[0][1], bnd[1][1], bnd[0][2], bnd[1][2]]
            self.rebuild()
        else:
            return 'pass'

    def bind(self, bind):
        if self._Bind is not bind:
            self._Bind = bind
            self.resetBnd()

    def setBnd(self, *args, bnd=None):
        if bnd is None:
            imbnd = vmi.imBounds(self._Bind.data()) if self._Bind else [vtk.VTK_SHORT_MIN, vtk.VTK_SHORT_MAX] * 3
            bnd = vmi.askFloats([imbnd[0], imbnd[0], imbnd[2], imbnd[2], imbnd[4], imbnd[4]],
                                [self._Bnd[0], self._Bnd[1], self._Bnd[2], self._Bnd[3], self._Bnd[4], self._Bnd[5]],
                                [imbnd[1], imbnd[1], imbnd[3], imbnd[3], imbnd[5], imbnd[5]], 3,
                                tr('边界 (Bounds) = (xmin, xmax, ymin, ymax, zmin, zmax) (mm)'))
        if bnd is not None:
            if bnd[0] > bnd[1] or bnd[2] > bnd[3] or bnd[4] > bnd[5]:
                vmi.askInfo(tr('输入无效 (Invalid input)'))
                return
            self._Bnd = bnd
            self.rebuild()

    def resetBnd(self, *args):
        if self._Bind is not None:
            self._Bnd = vmi.imBounds(self._Bind.data())
            self.rebuild()

    def rebuild(self):
        if self.isActivated():
            for k in range(3):
                for j in range(2):
                    for i in range(2):
                        bnd = [[self._Bnd[0], self._Bnd[2], self._Bnd[4]],
                               [self._Bnd[1], self._Bnd[3], self._Bnd[5]]]
                        pt = [[0, 0, 0], [0, 0, 0]]
                        a, b = (k + 1) % 3, (k + 2) % 3

                        pt[0][k], pt[1][k] = bnd[0][k], bnd[1][k]
                        pt[0][a] = pt[1][a] = bnd[j][a]
                        pt[0][b] = pt[1][b] = bnd[i][b]
                        self.regionShapes[k][j][i].clone(vmi.mkEdge(vmi.mkSegment(pt[0], pt[1])))
        else:
            for k in range(3):
                for j in range(2):
                    for i in range(2):
                        self.regionShapes[k][j][i].clone(None)
        self.view.updateInTime()

