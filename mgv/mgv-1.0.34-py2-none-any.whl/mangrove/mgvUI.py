#! /usr/bin/env python2.7
# -- coding: utf-8 --
from __future__ import print_function
import datetime
import glob
import json
import math
import os
import random
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import webbrowser
import copy
import urllib
import uuid
from six import string_types
import firebase_admin
from firebase_admin import credentials, firestore

from Qt import QtGui, QtCore, QtWidgets, QtSvg, QtXml, QtCompat
from markdown import *
from mgvApi import *
from mgvTextEditor import *

VERSION = '1.0.001'
myFont = 'Heebo'
myFontSize = 10

print('Mangrove v%s' % VERSION)

cred = credentials.Certificate(os.path.join(os.path.dirname(os.path.abspath(__file__)).replace('\\', '/'),
                                            "mangrove-firebase.sdk"))
firebase_admin.initialize_app(cred)
store = firestore.client()


def opposite(color):
    """Return black or white depending on a background color."""
    col = QtGui.QColor(color)
    Y = 0.2126 * col.red() + 0.7152 * col.green() + 0.0722 * col.blue()
    if Y > 90:
        return '#000000'
    return '#CCCCCC'


def set_procname(newname):
    """Change a process name"""
    from ctypes import cdll, byref, create_string_buffer
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(newname) + 1)
    buff.value = newname
    libc.prctl(15, byref(buff), 0, 0, 0)


def longueur(a, b):
    """Returns the length of a 2D vector."""
    return math.sqrt(a * a + b * b)


def clearLayout(layout):
    """Recursively delete all widgets of a qlayout."""
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clearLayout(item.layout())


def clearList(listWidget):
    """Clear a QListWidget, since the clear function is unstable."""
    while listWidget.count() > 0:
        listWidget.takeItem(0)


def respondMgv(address, path, nodename, ok):
    """Send a message to a distant mangrove instance."""
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    text = None
    try:
        address, port = address.split(':')
        port = int(port)
        s.connect((address, port))
        msg = '*MGVSEPARATOR*'.join([ok, path, nodename])
        s.send(msg.encode())
        s.settimeout(5)
        text = s.recv(1024)
    except socket.error as msg:
        print(msg, file=sys.__stderr__)
    finally:
        s.close()
    return text


def splashDialog(obj, root, style, text, duree):
    obj.childWindow = QtWidgets.QDialog(root)
    obj.childWindow.setLayout(QtWidgets.QVBoxLayout())
    obj.childWindow.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint)
    label = QtWidgets.QLabel(text)
    label.setAlignment(QtCore.Qt.AlignCenter)
    obj.childWindow.layout().addWidget(label)
    obj.childWindow.setStyleSheet(style)
    obj.childWindow.setStyleSheet('background: #358c64')

    r = obj.childWindow.geometry()
    r.moveCenter(QtWidgets.QApplication.desktop().availableGeometry().center())
    obj.childWindow.setGeometry(r)
    obj.childWindow.show()
    obj.childWindow.raise_()
    obj.childWindow.activateWindow()

    obj.timer = QtCore.QTimer()
    obj.timer.timeout.connect(obj.childWindow.close)
    obj.timer.start(duree)


class MgvHudThread(QtCore.QThread):
    """Hud thread object used to parallelize hud script execution."""
    signal = QtCore.Signal(list)

    def __init__(self, script):
        QtCore.QThread.__init__(self)
        self.script = script
        self.env = {}

    def run(self):
        s = self.script
        data = []
        s = 'def hudScriptFunction():\n' + '\n'.join(['\t' + x for x in s.split('\n')])
        scope = {}
        exec (s, scope)
        hudScriptFunction = scope['hudScriptFunction']
        old = os.environ
        os.environ = self.env
        try:
            data = hudScriptFunction()
        except:
            pass
        os.environ = old
        if not isinstance(data, list) and not isinstance(data, dict):
            data = [data]
        self.signal.emit(data)


class MgvHudItem(QtWidgets.QGraphicsItem):
    """Hud UI object."""
    obj = 'hud'

    def __init__(self, graphview, hud):
        super(MgvHudItem, self).__init__()
        self.graphview = graphview
        self.setZValue(90)
        self.graphview.scene.addItem(self)
        self.hud = hud
        self.data = []
        self.w = 50
        self.active = False
        self.i = 0
        self.getW()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.blink)
        self.thread = MgvHudThread(self.hud.script)
        self.thread.signal.connect(self.receiveData)

    def getW(self):
        data = self.data if self.active else []
        font = QtGui.QFont(myFont, .75 * myFontSize)
        fm = QtGui.QFontMetrics(font)
        self.w = max([fm.width(x) for x in (data + [self.hud.getName()])]) + 10

    def boundingRect(self):
        data = self.data if self.active else []
        return QtCore.QRectF(0, -(len(data)+1) * 15, self.w + 15, (len(data)+1) * 15)

    def shape(self):
        data = self.data if self.active else []
        path = QtGui.QPainterPath()
        path.addRect(0, -(len(data)+1) * 15, self.w + 15, (len(data)+1) * 15)
        return path

    def paint(self, painter, option, widget):
        pen = QtGui.QPen()
        pen.setWidth(1.5)
        font = QtGui.QFont(myFont, .75 * myFontSize)
        painter.setFont(font)
        t = QtGui.QTextOption()
        data = self.data if self.active else []
        if self.i > 0:
            pen.setStyle(QtCore.Qt.DashLine)
            pen.setDashOffset(self.i)
            pen.setColor(QtGui.QColor('#003300'))
        painter.setPen(pen)
        painter.drawRoundedRect(0, -(len(data)+1) * 15, self.w, (len(data)+1) * 15, 3, 3)
        if len(self.data):
            painter.setBrush(QtGui.QColor("#999999"))
        painter.drawRoundedRect(0, -(len(data) + 1) * 15, self.w, 15, 3, 3)
        pen.setColor(QtGui.QColor('#000000'))
        painter.setPen(pen)
        painter.drawText(QtCore.QRectF(5, -(len(data)+1) * 15, self.w+10, 15), self.hud.getName(), t)
        pen.setColor(QtGui.QColor('#000000'))

        for i, x in enumerate(data):
            painter.drawText(QtCore.QRectF(5, i * 15 - len(data) * 15, self.w+10, 15), x, t)

    def refreshData(self):
        """Execute hud script."""
        dico = self.graphview.graph.getVars()
        for x in os.environ.keys():
            dico[x] = os.environ[x]
        dico = mgvDicoReplace(dico)
        self.thread.env = dico
        self.timer.start(50)
        self.thread.start()

    def receiveData(self, liste):
        """Receive hud script results."""
        self.data = liste
        self.timer.stop()
        self.i = 0
        self.getW()
        self.graphview.refreshHud()

    def blink(self):
        self.i += 1
        self.update()

    def setActive(self, active):
        self.active = active
        if active and self.hud.getEvent() == 'toggle':
            self.refreshData()
        self.getW()
        self.graphview.refreshHud()


class MgvUserHud(QtWidgets.QGraphicsItem):
    """Users UI object."""
    obj = 'userhud'

    def __init__(self, graphview):
        super(MgvUserHud, self).__init__()
        self.graphview = graphview
        self.setZValue(90)
        self.graphview.scene.addItem(self)
        self.over = None
        self.w = 200

    def boundingRect(self):
        return QtCore.QRectF(0, -len(self.graphview.activeUsers) * 15, self.w + 15,
                             len(self.graphview.activeUsers) * 15)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(0, -len(self.graphview.activeUsers) * 15, self.w + 15, len(self.graphview.activeUsers) * 15)
        return path

    def paint(self, painter, option, widget):
        pen = QtGui.QPen()
        pen.setWidth(1.5)
        font = QtGui.QFont(myFont, .75 * myFontSize)
        painter.setFont(font)
        t = QtGui.QTextOption()

        for i, user in enumerate(self.graphview.activeUsers):
            username = user.getName().split('$')[0]
            pen.setColor(QtGui.QColor('#000000'))
            if user == self.over:
                pen.setColor(QtGui.QColor('#FFFF00'))
            painter.setPen(pen)
            painter.setBrush(user.color)
            painter.drawRoundedRect(0, i * 15 + 2.5 - len(self.graphview.activeUsers) * 15, 10, 10, 3, 3)
            painter.drawText(QtCore.QRectF(15, i * 15 - len(self.graphview.activeUsers) * 15, 200, 15), username, t)
            self.w = painter.fontMetrics().width(username) + 15

    def getOver(self, posy):
        self.over = None
        i = int((posy + len(self.graphview.activeUsers) * 15) / 15)
        if 0 <= i < len(self.graphview.activeUsers):
            self.over = self.graphview.activeUsers[i]


class MgvUser(object):
    """User object."""
    def __init__(self, name, me, num=0):
        super(MgvUser, self).__init__()
        self.name = name
        if name == me:
            self.color = QtGui.QColor(0, 125, 255, 200)
        elif name == 'free':
            self.color = QtGui.QColor(0, 0, 0, 0)
        else:
            self.color = QtGui.QColor(0, 125, 255, 200)
            done = [0]
            step = 128
            hue = 0
            for n in range(num):
                while hue in done:
                    hue += step
                    if hue > 255:
                        hue = 0
                        step /= 2
                done.append(hue)
            sat = self.color.hsvSaturation()
            val = self.color.value()
            self.color.setHsv(hue, sat, val)

    def getName(self):
        return self.name


class MgvSelectBox(QtWidgets.QGraphicsItem):
    """Selection yellow box."""
    obj = 'selectBox'

    def __init__(self, x, y, graphview):
        super(MgvSelectBox, self).__init__()
        self.graphview = graphview
        self.startx = x
        self.starty = y
        self.stopx = x
        self.stopy = y
        self.graphview.scene.addItem(self)

    def boundingRect(self):
        minx = min(self.startx, self.stopx) - 2 * self.graphview.globalScale
        miny = min(self.starty, self.stopy) - 2 * self.graphview.globalScale
        maxx = max(self.startx, self.stopx) + 4 * self.graphview.globalScale
        maxy = max(self.starty, self.stopy) + 4 * self.graphview.globalScale
        return QtCore.QRectF(minx, miny, maxx - minx, maxy - miny)

    def shape(self):
        path = QtGui.QPainterPath()
        minx = min(self.startx, self.stopx) - 2 * self.graphview.globalScale
        miny = min(self.starty, self.stopy) - 2 * self.graphview.globalScale
        maxx = max(self.startx, self.stopx) + 4 * self.graphview.globalScale
        maxy = max(self.starty, self.stopy) + 4 * self.graphview.globalScale
        path.addRect(minx, miny, maxx - minx, maxy - miny)
        return path

    def paint(self, painter, option, widget):
        pen = QtGui.QPen()
        pen.setWidth(1.5 * self.graphview.globalScale)
        pen.setStyle(QtCore.Qt.DashLine)
        pen.setColor(QtGui.QColor(220, 220, 0))
        painter.setPen(pen)
        minx, miny, maxx, maxy = min(self.startx, self.stopx), min(self.starty, self.stopy), max(self.startx,
                                                                                                 self.stopx), max(
            self.starty, self.stopy)
        painter.drawRect(minx, miny, maxx - minx, maxy - miny)

    def delete(self):
        self.prepareGeometryChange()
        self.graphview.scene.removeItem(self)

    def setCorner(self, x, y):
        self.prepareGeometryChange()
        self.stopx = x
        self.stopy = y
        self.update()


class MgvArrow(QtWidgets.QGraphicsItem):
    """Dummy link when creating a new link."""
    def __init__(self, linkfrom, linkto, graphview):
        super(MgvArrow, self).__init__()
        self.graphview = graphview
        self.linkfrom = linkfrom
        self.linkto = linkto
        self.height = 15 * self.graphview.globalScale
        self.setZValue(3)
        self.setRotation(-90)
        if linkfrom:
            self.setPos(linkfrom.item.pos().x() + 52 * self.graphview.globalScale, linkfrom.item.pos().y())
        self.graphview.scene.addItem(self)
        self.linkfrom.item.selected += 2
        self.linkfrom.item.update()

    def boundingRect(self):
        return QtCore.QRectF(-6 * self.graphview.globalScale, 0, 12 * self.graphview.globalScale, self.height)

    def shape(self):
        path = QtGui.QPainterPath()
        path.moveTo(-3 * self.graphview.globalScale, 0)
        path.lineTo(-3 * self.graphview.globalScale, self.height - 5 * self.graphview.globalScale)
        path.lineTo(-6 * self.graphview.globalScale, self.height - 5 * self.graphview.globalScale)
        path.lineTo(0, self.height)
        path.lineTo(6 * self.graphview.globalScale, self.height)
        path.lineTo(3 * self.graphview.globalScale, self.height - 5 * self.graphview.globalScale)
        path.lineTo(3 * self.graphview.globalScale, 0)
        return path

    def paint(self, painter, option, widget):
        pen = QtGui.QPen()
        pen.setWidth(1.5 * self.graphview.globalScale)
        pen.setStyle(QtCore.Qt.DashLine)
        pen.setColor(QtGui.QColor(10, 50, 130))
        painter.setPen(pen)
        painter.setBrush(QtGui.QColor(self.linkfrom.type.getColor()))
        painter.drawPolygon([QtCore.QPointF(-3 * self.graphview.globalScale, 0),
                             QtCore.QPointF(-3 * self.graphview.globalScale,
                                            self.height - 5 * self.graphview.globalScale),
                             QtCore.QPointF(-6 * self.graphview.globalScale,
                                            self.height - 5 * self.graphview.globalScale),
                             QtCore.QPointF(0, self.height),
                             QtCore.QPointF(6 * self.graphview.globalScale,
                                            self.height - 5 * self.graphview.globalScale),
                             QtCore.QPointF(3 * self.graphview.globalScale,
                                            self.height - 5 * self.graphview.globalScale),
                             QtCore.QPointF(3 * self.graphview.globalScale, 0),
                             QtCore.QPointF(2 * self.graphview.globalScale, -3 * self.graphview.globalScale),
                             QtCore.QPointF(-2 * self.graphview.globalScale, -3 * self.graphview.globalScale)])

    def setLinkTo(self, node):
        self.prepareGeometryChange()
        if node == self.linkfrom:
            self.linkto = None
        else:
            self.linkto = node
        if self.linkto is None:
            self.height = 15 * self.graphview.globalScale
            self.setRotation(-90)
        else:
            diffx = self.linkfrom.item.pos().x() + 52 * self.graphview.globalScale - self.linkto.item.pos().x()
            diffy = self.linkfrom.item.pos().y() - self.linkto.item.pos().y()
            norm = (diffx * diffx + diffy * diffy) ** .5
            self.height = norm - 10 * self.graphview.globalScale
            angle = -math.acos(diffx / norm) / 3.141592 * 180.0 - 90.0
            if diffy < 0:
                angle = -angle + 180
            self.setRotation(-angle)
        self.update()

    def delete(self):
        self.graphview.dummyLinks.remove(self)
        self.linkfrom.item.selected -= 2
        self.linkfrom.item.update()

        self.linkfrom = None
        self.linkto = None
        if self.scene():
            self.prepareGeometryChange()
            self.graphview.scene.removeItem(self)


class MgvGraphView(QtWidgets.QGraphicsView):
    """Nodal graph UI."""
    def __init__(self, gui, graph):
        super(MgvGraphView, self).__init__()

        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.globalScale = 10
        self.hud = None
        self.pos = (20000 * self.globalScale, 20000 * self.globalScale)
        self.scale = self.globalScale
        self.action = None
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setMouseTracking(1)
        self.setAcceptDrops(True)

        self.scene = QtWidgets.QGraphicsScene()
        self.scene.setSceneRect(0, 0, 40000 * self.globalScale, 40000 * self.globalScale)
        self.scene.setBackgroundBrush(QtGui.QColor(80, 80, 80))
        self.setScene(self.scene)
        self.centerOn(20000 * self.globalScale, 20000 * self.globalScale)
        self.activeUsers = []

        self.gui = gui
        self.selection = []
        self.movingNodes = []
        self.moved = 0
        self.moveOrigin = (0, 0)
        self.moveDelta = (0, 0)
        self.panOrigin = (0, 0)
        self.posOrigin = (0, 0)
        self.scaleOrigin = self.scale
        self.mousePos = (0, 0)
        self.nodesOrigin = []
        self.dragging = 0
        self.tabBox = None
        self.hotbox = None
        self.dummyLinks = []
        self.gridx = 70 * self.globalScale
        self.gridy = 30 * self.globalScale

        self.userHud = MgvUserHud(self)
        self.huds = [MgvHudItem(self, x) for x in graph.pattern.project.huds]
        self.editors = []
        self.groupEditors = []
        self.actionWindow = MgvActionWindow(self)

        self.gui.root.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.actionWindow)
        self.gui.root.setCorner(QtCore.Qt.BottomRightCorner, QtCore.Qt.RightDockWidgetArea)
        self.actionWindow.hide()
        self.actionWindow.visible = False
        self.stopRequest = False
        self.selectBox = None
        self.preselect = []
        self.oldselect = []
        self.graph = graph
        for w in self.huds:
            if w.hud.getEvent() == 'open':
                w.refreshData()

    def objAt(self, x, y):
        items = self.items(x, y)
        for item in items:
            if hasattr(item, 'obj'):
                if item.obj == 'node':
                    if item.node not in self.movingNodes:
                        return item.obj, item.node
                else:
                    return item.obj, item
        return None

    def distToScale(self, diff):
        if diff > 0:
            return (diff / 300.0 + 1) * self.scaleOrigin
        return max(.1, 1.0 - abs(diff) / 300.0) * self.scaleOrigin

    def draw(self):
        self.fitInView(self.pos[0], self.pos[1], self.viewport().size().width() * self.scale,
                       self.viewport().size().height() * self.scale, QtCore.Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        self.draw()
        self.refreshHud()

    def fit(self):
        self.pos = (0, 0)
        if len(self.selection) > 0:
            nodes = [x.node for x in self.selection]
        else:
            nodes = self.graph.nodes
        N = len(nodes)
        if N > 0:
            mini = (nodes[0].item.pos().x(), nodes[0].item.pos().y())
            maxi = (nodes[0].item.pos().x(), nodes[0].item.pos().y())
            for node in nodes:
                mini = (min(mini[0], node.item.pos().x()), min(mini[1], node.item.pos().y()))
                maxi = (max(maxi[0], node.item.pos().x()), max(maxi[1], node.item.pos().y()))
            mini = [mini[0] - self.gridx, mini[1] - self.gridy]
            maxi = [maxi[0] + self.gridx, maxi[1] + self.gridy]

            self.pos = (maxi[0] * .5 + mini[0] * .5, maxi[1] * .5 + mini[1] * .5)
            self.pos = (mini[0], mini[1])
            self.fitInView(mini[0], mini[1], maxi[0] - mini[0], maxi[1] - mini[1], QtCore.Qt.KeepAspectRatio)
            c1 = self.mapToScene(0, 0)
            c2 = self.mapToScene(self.width(), self.height())
            self.scale = (c2.y() - c1.y()) / self.height()
            self.pos = (c1.x(), c1.y())

        else:
            self.pos = (2000 * self.globalScale, 2000 * self.globalScale)
            self.scale = 1 * self.globalScale
        self.draw()
        self.refreshHud()

    def select(self, item, mode):
        if mode == 'replace':
            self.unselectAll()
        items = item
        if not isinstance(items, list):
            items = [items]
        for item in items:
            if mode == 'toggle':
                if not (item in self.selection):
                    mode = 'add'
                else:
                    mode = 'remove'
            if mode == 'add' or mode == 'replace':
                if item not in self.selection:
                    item.setSelected(1)
                    self.selection.append(item)
            if mode == 'remove':
                item.setSelected(0)
                if item in self.selection:
                    self.selection.remove(item)
        if self.action != 'select':
            for w in self.huds:
                if w.hud.getEvent() == 'select':
                    w.refreshData()

    def unselectAll(self):
        for item in self.selection:
            item.setSelected(0)
        self.selection = []

    def panStart(self, x, y):
        self.panOrigin = (x, y)
        self.posOrigin = (self.pos[0], self.pos[1])
        self.action = 'pan'

    def panStop(self):
        self.action = None

    def zoomStart(self, x, y):
        self.panOrigin = (x, y)
        self.scaleOrigin = self.scale
        self.action = 'zoom'

    def zoomStop(self):
        self.action = None

    def pan(self, x, y):
        p1 = self.mapToScene(self.panOrigin[0], self.panOrigin[1])
        p2 = self.mapToScene(x, y)
        self.pos = (self.posOrigin[0] + p1.x() - p2.x(), self.posOrigin[1] + p1.y() - p2.y())
        self.draw()

    def zoom(self, x):
        c = self.mapToScene(self.panOrigin[0], self.panOrigin[1])
        oldscale = self.scale
        self.scale = self.distToScale(self.panOrigin[0] - x)
        self.pos = (c.x() - (c.x() - self.pos[0]) / oldscale * self.scale,
                    c.y() - (c.y() - self.pos[1]) / oldscale * self.scale)
        self.draw()

    def event(self, event):
        if hasattr(event, 'type'):
            if event.type() == QtCore.QEvent.KeyPress:
                if event.key() == QtCore.Qt.Key_Tab:
                    if not event.modifiers() == QtCore.Qt.ControlModifier:
                        self.tabPressed()
                    else:
                        self.toggleIcons()
                    return True
            if event.type() == QtCore.QEvent.Type.MetaCall:
                self.refreshHud()
            return QtWidgets.QGraphicsView.event(self, event)

    def refreshHud(self):
        posy = self.viewport().size().height()
        posx = self.viewport().size().width()
        if self.userHud:
            self.userHud.setPos(self.mapToScene(10, posy - 10))
            self.userHud.setScale(self.scale * 1.25)
            self.userHud.update()
        x = posx
        for w in self.huds:
            w.setPos(self.mapToScene(x-w.w*1.25-10, posy - 10))
            w.setScale(self.scale * 1.25)
            w.update()
            x = x - w.w*1.25-10

    def mouseMoveEvent(self, event):
        self.mousePos = (event.x(), event.y())
        if self.action is None:
            obj = self.objAt(event.x(), event.y())
            if obj:
                if obj[0] == 'link':
                    if obj[1].link.linkto.user == self.graph.user:
                        self.gui.app.setOverrideCursor(
                            QtGui.QCursor(QtGui.QPixmap(os.path.join(self.gui.mgvDirectory, 'icons', 'scissors.png'))))
                        self.action = 'cut'
                else:
                    self.gui.app.restoreOverrideCursor()
                if obj[0] == 'tabCompleter':
                    pos = self.mapToScene(event.x(), event.y())
                    pos = obj[1].mapFromScene(pos.x(), pos.y())
                    obj[1].choice = obj[1].getChoice(pos.y())
                if obj[0] == 'userhud':
                    pos = self.mapToScene(event.x(), event.y())
                    pos = obj[1].mapFromScene(pos.x(), pos.y())
                    obj[1].getOver(pos.y())
                    obj[1].update()
            else:
                self.gui.app.restoreOverrideCursor()
                self.userHud.over = None
                self.userHud.update()
        if self.action == 'cut':
            obj = self.objAt(event.x(), event.y())
            if obj:
                if obj[0] != 'link':
                    self.gui.app.restoreOverrideCursor()
                    self.action = None
            else:
                self.gui.app.restoreOverrideCursor()
                self.action = None
        if self.action == 'pan':
            self.pan(event.x(), event.y())
        if self.action == 'zoom':
            self.zoom(event.x())
        if self.action in ['move', 'moveForced']:
            if self.dragging:
                self.moveStop()
                self.dragging = 0
            else:
                self.move(event.x(), event.y())
        if self.action == 'link':
            self.linkMove(event.x(), event.y())
        if self.action == 'hotbox':
            self.hotboxMove(event.x(), event.y())
        if self.action == 'select':
            self.selectMove(event.x(), event.y())

    def wheelEvent(self, event):
        if not self.hotbox:
            c = self.mapToScene(self.width() * .5, self.height() * .5)
            self.scaleOrigin = self.scale
            self.scale = self.distToScale(-event.delta() * .2)
            self.pos = (c.x() - (c.x() - self.pos[0]) / self.scaleOrigin * self.scale,
                        c.y() - (c.y() - self.pos[1]) / self.scaleOrigin * self.scale)
            self.draw()

    def mouseDoubleClickEvent(self, event):
        obj = self.objAt(event.x(), event.y())
        if event.modifiers() == QtCore.Qt.NoModifier:
            if obj:
                if event.button() == QtCore.Qt.LeftButton:
                    if self.action == 'cut':
                        if obj[0] == 'link':
                            node = obj[1].link.linkto
                            obj[1].link.delete()
                            for editor in self.editors:
                                if node == editor.node:
                                    editor.checkEditable()
                            return

    def mousePressEvent(self, event):
        QtWidgets.QGraphicsView.mousePressEvent(self, event)
        if self.action not in [None, 'cut']:
            return
        obj = self.objAt(event.x(), event.y())
        if event.modifiers() == QtCore.Qt.NoModifier:
            if obj:
                if event.button() == QtCore.Qt.LeftButton:
                    if obj[0] == 'node':
                        if not obj[1].item.selected:
                            self.select(obj[1].item, 'replace')
                            self.gui.editWindow(obj[1])
                        self.moveStart([x.node for x in self.selection], event.x(), event.y())
                        return
                    if obj[0] == 'tabCompleter':
                        obj[1].text = obj[1].possibilities[obj[1].choice - 1]
                        if obj[1].text.lower() in [x.lower() for x in obj[1].types]:
                            for typ in self.graph.pattern.project.getTypes():
                                if typ.getName().lower() == obj[1].text.lower():
                                    if self.tabBox:
                                        self.tabBox.delete()
                                    self.newNodes(typ)
                                    self.action = 'moveForced'
                                    self.moveStart([x.node for x in self.selection], event.x(), event.y())
                                    break
                        return
                    if obj[0] == 'userhud':
                        if obj[1].over:
                            self.select([x.item for x in self.graph.nodes if x.user == obj[1].over.getName()],
                                        'replace')
                            if len(self.selection):
                                self.gui.editWindow(self.selection[0].node)
                            return
                    if obj[0] == 'hud':
                        obj[1].setActive(not obj[1].active)
                        return
                    if obj[0] == 'group':
                        self.select([x.item for x in obj[1].group.getNodes()], 'replace')
                        self.gui.groupEditWindow(obj[1].group)
                        return
                if event.button() == QtCore.Qt.MidButton:
                    if obj[0] == 'node':
                        self.linkStart(obj[1])
                        return
                if event.button() == QtCore.Qt.RightButton:
                    if obj[0] == 'node':
                        if obj[1].user in [self.graph.user, 'free'] and not obj[1].versionActive.isLocked():
                            self.hotboxStart(obj[1])
                        return

            if self.action is None and event.button() == QtCore.Qt.LeftButton:
                self.selectStart(event.x(), event.y(), 'replace')
            if event.button() == QtCore.Qt.MidButton:
                self.panStart(event.x(), event.y())
            if event.button() == QtCore.Qt.RightButton:
                self.zoomStart(event.x(), event.y())

        if event.modifiers() == QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier:
            if event.button() == QtCore.Qt.RightButton:
                if obj[0] == 'node':
                    self.hotboxStart(obj[1], force=True)
        if event.modifiers() == QtCore.Qt.ControlModifier:
            if event.button() == QtCore.Qt.LeftButton:
                if obj:
                    if obj[0] == 'node':
                        self.select(obj[1].item, 'toggle')
                        self.moveStart([x.node for x in self.selection], event.x(), event.y())
                else:
                    self.selectStart(event.x(), event.y(), 'add')

        if event.modifiers() == QtCore.Qt.AltModifier:
            if event.button() == QtCore.Qt.LeftButton:
                self.panStart(event.x(), event.y())
            if event.button() == QtCore.Qt.RightButton:
                self.zoomStart(event.x(), event.y())
        if self.tabBox:
            self.tabBox.delete()

    def mouseReleaseEvent(self, event):
        if self.action == 'pan':
            self.panStop()
        if self.action == 'zoom':
            self.zoomStop()
        if self.action == 'move':
            self.moveStop()
        if self.action == 'link':
            self.linkStop()
        if self.action == 'hotbox':
            self.hotboxStop()
        if self.action == 'select':
            self.selectStop()

    def dragMoveEvent(self, event):
        if self.dragging:
            self.move(event.pos().x(), event.pos().y())
        event.accept()

    def dragLeaveEvent(self, event):
        pass

    def leaveEvent(self, event):
        self.gui.app.restoreOverrideCursor()
        self.action = None

    def dragEnterEvent(self, event):
        if self.tabBox:
            self.tabBox.delete()
        self.setFocus(QtCore.Qt.MouseFocusReason)
        event.accept()
        if event.mimeData().hasText():
            data = str(event.mimeData().text())
            if data in [x.getName() for x in self.graph.pattern.project.types]:
                index = [x.getName() for x in self.graph.pattern.project.types].index(data)
                typ = self.graph.pattern.project.types[index]
                event.mimeData().setText('')
                node = MgvNode(graph=self.graph, type=typ, name=typ.getName())
                node.create()
                MgvNodeItem(node, self)
                pos = self.mapToScene(event.pos().x(), event.pos().y())
                node.item.setItemPos(pos.x(), pos.y())
                self.select(node.item, 'replace')
                self.gui.editWindow(node)
                self.moveStart([node], event.pos().x(), event.pos().y())
                self.dragging = 1

    def dropEvent(self, event):
        self.moveStop()
        self.dragging = 0

    def keyPressEvent(self, event):
        if self.tabBox:
            self.tabBox.keyPressEvent(event)
        else:
            QtWidgets.QGraphicsView.keyPressEvent(self, event)
            if event.modifiers() == QtCore.Qt.ControlModifier:
                if event.key() == ord('C'):
                    self.gui.copy([x.node for x in self.selection])
                if event.key() == ord('V'):
                    self.gui.paste()
                if event.key() == ord('W'):
                    self.gui.tabClose()
                if event.key() == ord('E'):
                    self.gui.setEnv()
                if event.key() == QtCore.Qt.Key_Delete:
                    self.deleteNodes(self.selection, False)
            elif event.modifiers() == QtCore.Qt.ShiftModifier:
                if event.key() == ord('P'):
                    self.freeNodes([x.node for x in self.selection])
            else:
                if event.key() == QtCore.Qt.Key_F5:
                    self.gui.refresh(graphview=self)
                if event.key() == ord('F'):
                    self.fit()
                if event.key() == ord('N'):
                    self.newNodes(self.gui.types[0])
                if event.key() == ord('T') and len(self.gui.shell):
                    self.terminal()
                if event.key() == ord('E') and len(self.gui.explorer):
                    self.explorer()
                if event.key() == ord('B'):
                    self.createGroup([x.node for x in self.selection])
                if event.key() == QtCore.Qt.Key_Delete:
                    self.deleteNodes(self.selection, True)
                if event.key() == QtCore.Qt.Key_Escape:
                    self.stopRequest = True
                    if self.tabBox:
                        self.tabBox.delete()
                    if self.hotbox:
                        self.hotbox.delete()
                        self.hotbox = None
                        self.action = None
                if event.key() == ord('P'):
                    self.protectNodes([x.node for x in self.selection])
                if event.key() == ord('R'):
                    self.reorderInputs([x.node for x in self.selection])
                if event.key() == ord('X'):
                    self.showActions()

    def showActions(self):
        self.actionWindow.show()
        self.actionWindow.visible = True
        self.refreshHud()

    def refresh(self):
        self.gui.refresh(graphview=self)

    def reorderInputs(self, nodes):
        """Reorder inputs by nodes's y coordinates."""
        for node in nodes:
            node.inputLinks = sorted(node.inputLinks, key=lambda k: k.linkfrom.posy)
            mgvWrapper.setNodeAttr(node, inputLinks=';'.join([x.linkfrom.uuid for x in node.inputLinks]))
            mgvWrapper.setNodeAttr(node, updated=time.time())
            for link in node.inputLinks:
                if link.item:
                    link.item.update()

    def protectNodes(self, nodes):
        replyDico = {}
        self.gui.refresh(graphview=self)
        nodes = [x for x in self.graph.nodes if
                 x.name in [y.name for y in nodes] and x.getUser() != '*locked*' and x.type]
        for node in list(nodes):
            nodes.extend(node.getLinkedGroup())
        nodes = list(set(nodes))
        list_ok = []
        for node in nodes:
            add = True
            check = node.catch()
            if not check and len(node.port):
                toaddress, toport = node.port.split(':')
                if not node.port == self.gui.port:
                    code = '%s:%s' % (toaddress, toport)
                    if code not in replyDico:
                        replyDico[code] = [unlock_request(toaddress, toport, self.graph.getFullName(), node.getName(),
                                                          self.graph.getUser(), self.gui.IP + ':' + self.gui.port),
                                           node, toaddress, toport]
                    if replyDico[code][0] not in ['noroute', 'notmine', None]:
                        add = False

            if add:
                list_ok.append(node)
        for response in replyDico:
            response = replyDico[response]
            if response[0]:
                if response[0] not in ['noroute', 'notmine']:
                    response[1].item.graphview.gui.requested(response[1].name, response[2], response[3])

        for node in nodes:
            if node not in list_ok:
                for n in node.getLinkedGroup():
                    if n in list(list_ok):
                        list_ok.remove(n)
        for node in list_ok:
            node.setUser(user=self.graph.user, port=self.gui.port, ip=self.gui.IP)
            for editor in self.editors:
                if editor.node == node:
                    editor.read()
            node.item.userChanged()
            node.item.update()

    def freeNodes(self, nodes):
        for node in list(nodes):
            nodes.extend(node.getLinkedGroup())
        running = [x.node_version.node for x in self.actionWindow.tasks if not x.stopped]
        nonodes = [x for x in nodes if x in running]
        for n in list(nonodes):
            nonodes.extend(n.getLinkedGroup())
        nodes = [x for x in nodes if x not in nonodes]
        nodes = list(set(nodes))
        for node in nodes:
            node.free()
            node.item.userChanged()
            node.item.update()
            for editor in self.editors:
                if editor.node == node:
                    editor.read()

        for user in list(self.activeUsers):
            if user not in [x.item.user for x in self.graph.nodes]:
                self.activeUsers.remove(user)
        self.refreshHud()
        if len(nonodes) > 1:
            self.gui.notify('%s are running !' % ', '.join([x.getName() for x in nonodes]), 1)
        if len(nonodes) == 1:
            self.gui.notify('%s is running !' % nonodes[0].getName(), 1)

    def terminal(self):
        for x in self.selection:
            path = x.node.getPath()
            if not os.path.exists(path):
                path = x.node.graph.getWorkDirectory()
            if not sys.platform.startswith('win'):
                cmd = [y.replace('$PATH', path) for y in self.gui.shell.split(' ')]
                subprocess.Popen(cmd)
            else:
                path = path.replace('/', '\\')
                cmd = [y.replace('$PATH', path) for y in self.gui.shell.split(' ')]
                subprocess.Popen(cmd, shell=True)

    def explorer(self):
        for x in self.selection:
            path = x.node.getPath()
            if not os.path.exists(path):
                path = x.node.graph.getWorkDirectory()
            if not sys.platform.startswith('win'):
                cmd = [y.replace('$PATH', path) for y in self.gui.explorer.split(' ')]
                subprocess.Popen(cmd)
            else:
                path = path.replace('/', '\\')
                cmd = [y.replace('$PATH', path) for y in self.gui.explorer.split(' ')]
                subprocess.Popen(cmd, shell=True)

    def deleteNodes(self, liste, delfiles):
        liste = [x for x in liste if x.node.getUser() == self.graph.getUser() and not x.node.isRunning]
        if len(liste):
            a = QtWidgets.QMessageBox(self.gui.root)
            if delfiles:
                a.setText('Remove all data from those nodes ?')
            else:
                a.setText('Remove those nodes and keep data ?')
            a.setInformativeText('\n'.join([x.node.getName() for x in liste]))

            a1 = QtWidgets.QPushButton('Yes')
            a.addButton(a1, QtWidgets.QMessageBox.YesRole)
            a3 = QtWidgets.QPushButton('No')
            a.addButton(a3, QtWidgets.QMessageBox.NoRole)
            a.setDefaultButton(a3)
            r = a.exec_()
            if not r:
                ok = []
                for y in [x.node for x in liste]:
                    if y.delete(remove_files=delfiles):
                        if y.item in self.selection:
                            self.selection.remove(y.item)
                        ok.append(y)
                    else:
                        QtWidgets.QMessageBox.information(self.gui.root, 'error',
                                                          "Can't delete  %s's folder" % y.getName())
                if len(ok):
                    multi = 's' if len(ok) > 1 else ''
                    names = ', '.join([x.getName() for x in ok])
                    self.gui.notify('Node%s %s deleted' % (multi, names))

    def createGroup(self, nodes):
        if len(nodes):
            group = MgvGroup(graph=self.graph, nodeuuids=[x.uuid for x in nodes])
            group.create()
            MgvGroupItem(group, self)

    def tabPressed(self):
        pos = self.mapToScene(30, 30)
        if self.tabBox:
            self.tabBox.delete()
        self.tabBox = MgvTabCompleter(self, pos.x(), pos.y())

    def newNodes(self, typ):
        self.unselectAll()
        node = MgvNode(graph=self.graph, type=typ, name=typ.getName())
        node.create()
        MgvNodeItem(node, self)
        self.select(node.item, 'replace')
        pos = self.mapToScene(self.mousePos[0], self.mousePos[1])
        node.item.setItemPos(pos.x(), pos.y())
        self.moveStart([node], self.mousePos[0], self.mousePos[1])
        self.gui.editWindow(node)

    def hotboxStart(self, node, force=False):
        self.action = 'hotbox'
        self.hotbox = MgvHotBox(node, self, force=force)
        self.hotbox.start()

    def hotboxStop(self):
        self.action = None
        hudrefresh = False
        if self.hotbox.node.type:
            if self.hotbox.node.graph.path[-1] != '*template*':
                for action in self.hotbox.node.type.getActions(
                        version_id=self.hotbox.node.versionActive.typeForceVersion):
                    if self.hotbox.selected == action:
                        if self.hotbox.node.getUser() == 'free':
                            nodename = self.hotbox.node.getName()
                            self.protectNodes([self.hotbox.node])
                            node = self.graph.getNode(nodename)
                            if not node:
                                self.gui.notify('Oh oh, the node %s vanished !' % nodename)
                                self.hotbox.delete()
                                self.hotbox = None
                                return
                            else:
                                self.hotbox.node = node

                        if self.hotbox.node.getUser() == self.graph.user or self.hotbox.force:
                            if self.hotbox.force:
                                nodename = self.hotbox.node.getName()
                                self.refresh()
                                self.hotbox.node = self.graph.getNode(nodename)
                                if not self.hotbox.node:
                                    self.gui.notify('Oh oh, the node %s vanished !' % nodename)
                                    self.hotbox.delete()
                                    self.hotbox = None
                                    return
                            if len(action.warning):
                                result = QtWidgets.QMessageBox.question(self.gui.root, 'Warning', action.warning,
                                                                        QtWidgets.QMessageBox.Yes |
                                                                        QtWidgets.QMessageBox.No,
                                                                        QtWidgets.QMessageBox.No)
                                if result != QtWidgets.QMessageBox.Yes:
                                    break
                            self.actionWindow.exe(self.hotbox.node.versionActive, action)
                            hudrefresh = True
            else:
                self.gui.notify('Sorry, not permitted on a graph template !', 1)
        self.hotbox.delete()
        self.hotbox = None
        if hudrefresh:
            self.showActions()

    def hotboxMove(self, x, y):
        if self.hotbox:
            self.hotbox.chooseOption(x, y)

    def linkStart(self, node):
        nodes = [x.node for x in self.selection]
        if node not in nodes:
            nodes = [node]
        for node in nodes:
            if hasattr(node.type, 'name'):
                self.action = 'link'
                self.dummyLinks.append(MgvArrow(node, None, self))

    def linkStop(self):
        linkto = None
        for dummyLink in list(self.dummyLinks):
            if dummyLink.linkto:
                linkto = dummyLink.linkto
                link = dummyLink.linkfrom.setLinkTo(dummyLink.linkto)
                MgvLinkItem(link, self)
                if dummyLink.linkto.type.uuid in dummyLink.linkfrom.type.getLinkWith():
                    if dummyLink.linkfrom.versionActive.id != dummyLink.linkto.versionActive.id:
                        dummyLink.linkto.setVersion(dummyLink.linkfrom.versionActive.id)
            dummyLink.delete()
        self.action = None
        if linkto:
            self.reorderInputs([linkto])

    def isLinkPossible(self, nodea, nodeb):
        if nodeb in [x.linkfrom for x in self.dummyLinks]:
            return 0
        if nodea == nodeb:
            return 0
        if nodeb.user != self.graph.user:
            return 0

        # liens cycliques
        nodes = [nodeb]
        while len(nodes):
            for node in nodes:
                if node == nodea:
                    self.gui.notify('Cyclic links detected !', 1)
                    return 0
                nodes.remove(node)
                if len(node.outputLinks):
                    nodes.extend([link.linkto for link in node.outputLinks])
        return 1

    def linkMove(self, x, y):
        obj = self.objAt(x, y)
        for dummyLink in self.dummyLinks:
            dummyLink.setLinkTo(None)
            if obj:
                if obj[0] == 'node':
                    if self.isLinkPossible(dummyLink.linkfrom, obj[1]):
                        if obj[1] != dummyLink.linkfrom:
                            if dummyLink.linkfrom not in [x.linkfrom for x in obj[1].inputLinks if not x == dummyLink]:
                                dummyLink.setLinkTo(obj[1])

    def selectStart(self, x, y, mode):
        self.action = 'select'
        self.preselect = []
        self.oldselect = list(self.selection)
        if mode == 'replace':
            self.unselectAll()
        pos = self.mapToScene(x, y)
        self.selectBox = MgvSelectBox(pos.x(), pos.y(), self)

    def selectMove(self, x, y):
        pos = self.mapToScene(x, y)
        self.selectBox.setCorner(pos.x(), pos.y())
        items = self.scene.items(min(self.selectBox.startx, self.selectBox.stopx),
                                 min(self.selectBox.starty, self.selectBox.stopy),
                                 abs(self.selectBox.stopx - self.selectBox.startx),
                                 abs(self.selectBox.stopy - self.selectBox.starty))
        for x in self.preselect:
            self.select(x, 'remove')
        self.preselect = []
        for x in items:
            if x.obj == 'node':
                if x not in self.selection:
                    self.select(x, 'add')
                    self.preselect.append(x)

    def selectStop(self):
        self.selectBox.delete()
        self.action = None
        if len(self.selection):
            self.gui.editWindow(self.selection[0].node)
        if set(self.selection) != set(self.oldselect):
            for w in self.huds:
                if w.hud.getEvent() == 'select':
                    w.refreshData()

    def moveStart(self, nodes, x, y):
        nodes = [u for u in nodes if u.user == self.graph.user]
        if len(nodes):
            if self.action != 'moveForced':
                self.action = 'move'
            self.moved = 0
            self.moveOrigin = self.mapToScene(x, y)
            self.nodesOrigin = [[x.posx * self.globalScale, x.posy * self.globalScale] for x in nodes]
            self.movingNodes = nodes

    def moveStop(self):
        self.action = None
        self.moved = 0
        self.moveOrigin = [0, 0]
        self.nodesOrigin = []
        self.movingNodes = []

    def move(self, x, y):
        self.action = 'move'
        posS = self.mapToScene(x, y)
        for node, pos in zip(self.movingNodes, self.nodesOrigin):
            posx = pos[0] + posS.x() - self.moveOrigin.x()
            posy = pos[1] + posS.y() - self.moveOrigin.y()
            node.item.setItemPos(posx - posx % self.gridx + self.gridx * .5, posy - posy % self.gridy)
        # si on est dans un groupe, on ajoute le node au groupe
        if longueur(x - self.moveDelta[0], y - self.moveDelta[1]) < 50:
            for node in self.movingNodes:
                for group in self.graph.groups:
                    if node.uuid not in group.nodeuuids:
                        if group.item.maxposx > posS.x() > group.item.minposx and\
                                group.item.maxposy > posS.y() > group.item.minposy:
                            group.addNodes([node])
        # si on est dans un groupe, on ajoute le node au groupe
        else:
            for node in self.movingNodes:
                for group in self.graph.groups:
                    if node.uuid in group.nodeuuids:
                        group.removeNodes([node])
        self.moveDelta = (x, y)

    def toggleIcons(self):
        self.gui.toggleIcons()


class MgvHotBoxAction(QtWidgets.QGraphicsItem):
    """Action UI object."""
    obj = 'action'

    def __init__(self, graphview, father, action, z):
        super(MgvHotBoxAction, self).__init__()
        self.action = action
        self.radius = father.radiusB
        self.radiusA = father.radiusA
        self.radiusB = father.radiusB
        self.graphview = graphview
        self.father = father
        self.selected = False
        self.setZValue(z)
        self.graphview.scene.addItem(self)

        self.hide()

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        if not self.father:
            return QtGui.QPainterPath()
        offset = self.father.pos() - self.pos()

        path = QtGui.QPainterPath()
        ind = self.father.options.index(self)
        if len(self.father.options) > 1:
            start_angle = self.father.startAngle + (
                    self.father.endAngle - self.father.startAngle) / len(self.father.options) * .5 + (
                    self.father.endAngle - self.father.startAngle) / len(self.father.options) * ind
            arc = -(self.father.endAngle - self.father.startAngle) / len(self.father.options)
        else:
            start_angle = self.father.endAngle*.5 - self.father.startAngle*.5 + self.father.startAngle
            arc = 3.141592 * .5

        start_angle = -(start_angle + arc * .5) * 180 / 3.141592
        arc = arc * 180 / 3.141592

        rad = self.radiusA - self.radiusB
        rad *= self.graphview.scale*.12
        path.moveTo(math.cos(start_angle * 3.141592 / 180) * rad * self.graphview.globalScale + offset.x(),
                    -math.sin(start_angle * 3.141592 / 180) * rad * self.graphview.globalScale + offset.y())
        rad = self.radiusA + self.radiusB
        rad *= self.graphview.scale*.12
        path.arcTo(-rad * self.graphview.globalScale + offset.x(), -rad * self.graphview.globalScale + offset.y(),
                   2 * rad * self.graphview.globalScale, 2 * rad * self.graphview.globalScale,
                   start_angle, arc)
        rad = self.radiusA - self.radiusB
        rad *= self.graphview.scale*.12
        path.arcTo(-rad * self.graphview.globalScale + offset.x(), -rad * self.graphview.globalScale + offset.y(),
                   2 * rad * self.graphview.globalScale, 2 * rad * self.graphview.globalScale,
                   start_angle + arc, -arc)
        return path

    def paint(self, painter, option, widget):
        pen = QtGui.QPen()
        pen.setWidth(1.5 * self.graphview.globalScale * self.graphview.scale * .12)
        pen.setColor(QtGui.QColor(200, 200, 200))

        pen.setStyle(QtCore.Qt.DashLine)
        painter.setPen(pen)
        painter.setBrush(QtGui.QColor(60, 60, 60))
        font = QtGui.QFont(myFont, .75 * myFontSize * self.graphview.globalScale * self.graphview.scale * .12)
        painter.setFont(font)
        t = QtGui.QTextOption()
        t.setAlignment(QtCore.Qt.AlignCenter)
        if self.selected:
            painter.setBrush(QtGui.QColor(180, 120, 60))
        else:
            painter.setBrush(QtGui.QColor(60, 60, 60))
            pen.setColor(QtGui.QColor(200, 200, 200))
            painter.setPen(pen)
        # ELLIPSE
        path = self.shape()
        painter.drawPath(path)
        # TEXT
        painter.drawText(QtCore.QRectF(-self.radius * self.graphview.globalScale * self.graphview.scale * .12,
                                       -self.radius * self.graphview.globalScale * self.graphview.scale * .12,
                                       self.radius * 2 * self.graphview.globalScale * self.graphview.scale * .12,
                                       self.radius * 2 * self.graphview.globalScale * self.graphview.scale * .12),
                         self.action.getName(), t)

    def select(self):
        self.selected = True
        self.update()

    def unselect(self):
        self.selected = False
        self.update()

    def reset(self):
        pass

    def delete(self):
        self.prepareGeometryChange()
        self.graphview.scene.removeItem(self)

    def getSelection(self):
        if self.selected:
            return self.action
        return None


class MgvHotBoxMenu(QtWidgets.QGraphicsItem):
    """Action's menu UI object."""
    obj = 'menu'

    def __init__(self, graphview, father, menuname, node, actions, prefix, z):
        super(MgvHotBoxMenu, self).__init__()
        self.graphview = graphview
        self.father = father
        self.node = node
        self.menuname = menuname
        self.selected = False
        self.radiusA = 60
        self.radiusB = 25
        self.radius1 = self.radiusA * self.graphview.globalScale
        self.radius2 = 1
        self.setZValue(z)
        self.options = []
        self.menus = []
        if len(prefix):
            prefix += '|'

        for action in actions:
            if self.graphview.graph.user.split('$')[0] in action.users.split(' ') or len(action.users) == 0:
                ctx = action.menu[len(prefix):].split('|')[0]

                if len(ctx):
                    if ctx.strip() not in self.menus:
                        option = MgvHotBoxMenu(graphview=graphview, father=self, menuname=ctx.strip(), node=node,
                                               actions=[x for x in actions if x.menu.startswith(prefix + ctx)],
                                               prefix=prefix + ctx, z=z + 1)
                        self.menus.append(ctx.strip())
                        self.options.append(option)
                else:
                    self.options.append(MgvHotBoxAction(graphview=graphview, father=self, action=action, z=z + 1))

        if len(self.options):
            self.startAngle = -3.141592 / len(self.options)
            self.endAngle = self.startAngle + 3.141592 * 2
        else:
            self.startAngle = 0.0
            self.endAngle = 0.0

        self.graphview.scene.addItem(self)
        self.hide()

    def boundingRect(self):
        if not len(self.menuname):
            stroker = QtGui.QPainterPathStroker()
            stroker.setWidth(8 * self.graphview.globalScale)
            path = stroker.createStroke(self.node.item.chemin)
            path = path.united(self.node.item.chemin)
            return path.boundingRect()
        return self.shape().boundingRect()

    def shape(self):
        if not self.father:
            return QtGui.QPainterPath()
        if self.selected:
            path = QtGui.QPainterPath()
            path.addEllipse(-self.radiusB * self.graphview.globalScale * self.graphview.scale * .12,
                            -self.radiusB * self.graphview.globalScale * self.graphview.scale * .12,
                            self.radiusB * 2 * self.graphview.globalScale * self.graphview.scale * .12,
                            self.radiusB * 2 * self.graphview.globalScale * self.graphview.scale * .12)
            return path
        if any([x.selected for x in self.options]):
            path = QtGui.QPainterPath()
            path.addEllipse(-self.radiusB * self.graphview.globalScale * self.graphview.scale * .12,
                            -self.radiusB * self.graphview.globalScale * self.graphview.scale * .12,
                            self.radiusB * 2 * self.graphview.globalScale * self.graphview.scale * .12,
                            self.radiusB * 2 * self.graphview.globalScale * self.graphview.scale * .12)
            return path
        offset = self.father.pos() - self.pos()

        path = QtGui.QPainterPath()
        ind = self.father.options.index(self)
        start_angle = self.father.startAngle + (
                self.father.endAngle - self.father.startAngle) / len(self.father.options) * .5 + (
                self.father.endAngle - self.father.startAngle) / len(self.father.options) * ind

        arc = -(self.father.endAngle - self.father.startAngle) / (len(self.father.options))

        start_angle = -(start_angle + arc * .5) * 180 / 3.141592
        arc = arc * 180 / 3.141592

        rad = self.radiusA - self.radiusB
        rad *= self.graphview.scale*.12
        path.moveTo(math.cos(start_angle * 3.141592 / 180) * rad * self.graphview.globalScale + offset.x(),
                    -math.sin(start_angle * 3.141592 / 180) * rad * self.graphview.globalScale + offset.y())
        rad = self.radiusA + self.radiusB
        rad *= self.graphview.scale*.12
        path.arcTo(-rad * self.graphview.globalScale + offset.x(), -rad * self.graphview.globalScale + offset.y(),
                   2 * rad * self.graphview.globalScale, 2 * rad * self.graphview.globalScale,
                   start_angle, arc)
        rad = self.radiusA - self.radiusB
        rad *= self.graphview.scale*.12
        path.arcTo(-rad * self.graphview.globalScale + offset.x(), -rad * self.graphview.globalScale + offset.y(),
                   2 * rad * self.graphview.globalScale, 2 * rad * self.graphview.globalScale,
                   start_angle + arc, -arc)
        return path

    def paint(self, painter, option, widget):
        pen = QtGui.QPen()
        pen.setWidth(1.5 * self.graphview.globalScale * self.graphview.scale * .12)
        pen.setColor(QtGui.QColor(200, 200, 200))

        pen.setStyle(QtCore.Qt.DashLine)
        painter.setPen(pen)
        painter.setBrush(QtGui.QColor(60, 60, 60))
        font = QtGui.QFont(myFont, .75 * myFontSize * self.graphview.globalScale * self.graphview.scale * .12)
        font.setWeight(QtGui.QFont.Bold)
        painter.setFont(font)
        t = QtGui.QTextOption()
        t.setAlignment(QtCore.Qt.AlignCenter)
        if self.selected:
            painter.setBrush(QtGui.QColor(220, 160, 100))
        else:
            painter.setBrush(QtGui.QColor(100, 100, 100))
            pen.setColor(QtGui.QColor(200, 200, 200))
            painter.setPen(pen)
        if len(self.menuname):
            path = self.shape()
            painter.drawPath(path)

            painter.drawText(QtCore.QRectF(-self.radiusB * self.graphview.globalScale * self.graphview.scale * .12,
                                           -self.radiusB * self.graphview.globalScale * self.graphview.scale * .12,
                                           self.radiusB * 2 * self.graphview.globalScale * self.graphview.scale * .12,
                                           self.radiusB * 2 * self.graphview.globalScale * self.graphview.scale * .12),
                             self.menuname, t)

        else:
            pen.setWidth(1.5 * self.graphview.globalScale)
            pen.setColor(QtGui.QColor(200, 200, 200))
            painter.setBrush(QtGui.QBrush())
            painter.setPen(pen)
            stroker = QtGui.QPainterPathStroker()
            stroker.setWidth(8 * self.graphview.globalScale)
            path = stroker.createStroke(self.node.item.chemin)
            path = path.united(self.node.item.chemin)
            painter.drawPath(path)

    def grow(self):
        self.prepareGeometryChange()
        for n, option in enumerate(self.options):
            option.prepareGeometryChange()
            # MINI ELLIPSE
            if len(self.options) > 1:
                angle = self.startAngle + (
                        self.endAngle - self.startAngle) / len(self.options) * .5 + (
                        self.endAngle - self.startAngle) / len(self.options) * n
            else:
                angle = self.startAngle * .5 + self.endAngle * .5
            x = math.cos(angle) * self.radius1 * self.graphview.scale * .12
            y = math.sin(angle) * self.radius1 * self.graphview.scale * .12
            option.setPos(x + self.pos().x(), y + self.pos().y())
            option.setScale(self.radius2)

            option.startAngle = angle - 3.141592*.7
            option.endAngle = angle + 3.141592*.7
            option.update()
        self.update()

    def delete(self):
        for x in self.options:
            x.delete()
        self.prepareGeometryChange()
        self.graphview.scene.removeItem(self)

    def select(self):
        self.setScale(1)
        if self.father:
            self.father.selected = False
            if self.father.father is not None:
                self.father.setScale(.5)
            for option in self.father.options:
                if option is not self:
                    option.unselect()
                    option.hide()
        self.selected = True
        for option in self.options:
            option.unselect()
            option.show()
        self.grow()

    def unselect(self):
        self.selected = False
        for option in self.options:
            option.unselect()
            option.hide()

    def getSelection(self):
        for o in self.options:
            sel = o.getSelection()
            if sel:
                return sel
        return None


class MgvHotBox(object):
    """Actions and their menus main object."""
    obj = 'hotbox'

    def __init__(self, node, graphview, force):
        self.force = force
        self.graphview = graphview
        self.node = node
        self.father = None
        self.selected = None
        self.mainMenu = MgvHotBoxMenu(graphview=graphview, father=None, menuname='', node=node,
                                      actions=node.type.getActions(version_id=node.versionActive.typeForceVersion),
                                      prefix='', z=95)
        for o in self.mainMenu.options:
            o.show()
        self.mainMenu.show()
        if self.node.item:
            node.item.checkExists()
            self.mainMenu.prepareGeometryChange()
            self.mainMenu.setPos(self.node.item.pos().x(), self.node.item.pos().y())

    def start(self):
        self.mainMenu.grow()

    def chooseOption(self, x, y):
        obj = self.graphview.objAt(x, y)
        ok = False
        if obj:
            if obj[0] in ['menu', 'action']:
                ok = True
                if not obj[1] is self.mainMenu:
                    if not obj[1].selected:
                        for o in obj[1].father.options:
                            if o is not obj[1]:
                                o.unselect()
                        obj[1].select()
            if obj[1] is self.mainMenu.node:
                ok = True
                for o in self.mainMenu.options:
                        o.unselect()
                        o.show()
                        o.setScale(1)
        if not ok:
            pos = self.graphview.mapToScene(x, y)
            dist = pow(pow(pos.x() - self.mainMenu.pos().x(), 2) + pow(pos.y() - self.mainMenu.pos().y(), 2), .5)
            if dist > 3000:
                for o in self.mainMenu.options:
                    o.unselect()
                    o.hide()
        self.selected = self.mainMenu.getSelection()

    def delete(self):
        self.mainMenu.delete()


class BinCategory(QtWidgets.QGraphicsItem):
    """Category labels on the left panel."""
    obj = 'category'

    def __init__(self, view, category, y):
        super(BinCategory, self).__init__()
        self.category = category
        self.view = view
        self.view.scene.addItem(self)
        self.x = 3
        self.y = y
        self.width = 100

    def boundingRect(self):
        return QtCore.QRectF(self.x, self.y, self.width, 25)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(QtCore.QRectF(self.x, self.y, self.width, 25))
        return path

    def paint(self, painter, option, widget):
        pen = QtGui.QPen()
        pen.setWidth(1.5)
        pen.setColor(QtGui.QColor('#CCCCCC'))
        painter.setPen(pen)

        font = QtGui.QFont(myFont, .75 * myFontSize)
        painter.setFont(font)
        factor = 1
        if len(self.category):
            factor = 0.9 * self.width / painter.fontMetrics().width(self.category)
        if factor < 1:
            font.setPointSizeF(font.pointSizeF() * factor)
            painter.setFont(font)
        t = QtGui.QTextOption()
        t.setAlignment(QtCore.Qt.AlignHCenter)
        painter.drawText(QtCore.QRectF(self.x, self.y + 4, self.width, 25), self.category, t)


class BinNode(QtWidgets.QGraphicsItem):
    """Types UI objects on the left panel."""
    obj = 'node'

    def __init__(self, view, typ, y):
        super(BinNode, self).__init__()
        self.type = typ
        self.view = view
        self.view.scene.addItem(self)
        self.x = 3
        self.y = y
        self.over = 0
        self.width = 100
        if len(typ.getHelp()):
            self.setToolTip(markdown(typ.getHelp().replace('\n', '<br>')))

    def setOver(self, value):
        self.over = value
        self.update()

    def boundingRect(self):
        return QtCore.QRectF(self.x, self.y, self.width, 25)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(QtCore.QRectF(self.x, self.y, self.width, 25))
        return path

    def paint(self, painter, option, widget):
        pen = QtGui.QPen()
        pen.setWidth(1.5)
        if self.over:
            pen.setColor(QtGui.QColor('#CCCCCC'))
            painter.setBrush(QtGui.QColor('#358c64'))
        else:
            pen.setColor(opposite(self.type.getColor()))
            painter.setBrush(QtGui.QColor(self.type.getColor()))
        painter.setPen(pen)
        painter.drawRoundedRect(self.x, self.y, self.width, 25, 3, 3)

        font = QtGui.QFont(myFont, myFontSize)
        painter.setFont(font)
        factor = 0.9 * self.width / painter.fontMetrics().width(self.type.getName())
        if factor < 1:
            font.setPointSizeF(font.pointSizeF() * factor)
            painter.setFont(font)
        t = QtGui.QTextOption()
        t.setAlignment(QtCore.Qt.AlignHCenter)
        painter.drawText(QtCore.QRectF(self.x, self.y + 4, self.width, 25), self.type.getName(), t)


class IconView(QtWidgets.QGraphicsView):
    """Left UI panel."""
    def __init__(self, gui):
        super(IconView, self).__init__()
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setMouseTracking(1)

        self.scene = QtWidgets.QGraphicsScene()
        self.scene.setSceneRect(0, 0, 2000, 2000)
        self.scene.setBackgroundBrush(QtGui.QColor('#333333'))
        self.setScene(self.scene)
        self.centerOn(0, 0)

        self.drag = None
        self.gui = gui

    def refreshTypes(self, type_filter=''):
        self.scene.clear()
        self.centerOn(0, 0)
        dico = {}
        for t in self.gui.currentProject.types:
            if t.category not in dico:
                dico[t.category] = []
            dico[t.category].append(t)
        y = 0
        for key in sorted(dico):
            if len([x for x in dico[key] if type_filter.lower() in x.getName().lower()]):
                BinCategory(self, key, y + 3)
                y += 25
            for t in sorted(dico[key], key=lambda sort_key: sort_key.getName()):
                if type_filter.lower() in t.getName().lower():
                    BinNode(self, t, y + 3)
                    y += 30

    def mouseMoveEvent(self, event):
        item = self.itemAt(event.x(), event.y())
        if item and item.obj == 'category':
            item = None
        if item:
            if item.over == 0:
                for i in self.items():
                    if i.obj == 'node':
                        i.setOver(0)
                item.setOver(1)
        else:
            for i in self.items():
                if i.obj == 'node':
                    i.setOver(0)

    def mousePressEvent(self, event):
        if event.modifiers() == QtCore.Qt.NoModifier:
            if event.button() == QtCore.Qt.LeftButton:
                item = self.itemAt(event.x(), event.y())
                if item and item.obj == 'category':
                    item = None
                if item:
                    mimeData = QtCore.QMimeData()
                    mimeData.setText(item.type.getName())
                    self.drag = QtGui.QDrag(self)
                    self.drag.setMimeData(mimeData)
                    self.drag.start(QtCore.Qt.MoveAction)

            if event.button() == QtCore.Qt.RightButton:
                item = self.itemAt(event.x(), event.y())
                if item and item.obj == 'category':
                    item = None
                newAction = QtWidgets.QAction('New', self)
                menu = QtWidgets.QMenu(self)
                if item:
                    editAction = QtWidgets.QAction('Edit', self)
                    removeAction = QtWidgets.QAction('Remove', self)
                    exportAction = QtWidgets.QAction('Export', self)
                    menu.addAction(editAction)
                    menu.addAction(newAction)
                    menu.addAction(removeAction)
                    menu.addAction(exportAction)
                    action = menu.exec_(self.mapToGlobal(event.pos()))
                    if action:
                        if action == editAction:
                            item.type._copy(self.gui.currentProject.readType(item.type.uuid))
                            self.gui.editType(item.type)
                        if action == newAction:
                            self.gui.newType()
                        if action == removeAction:
                            self.gui.removeType(item.type)
                        if action == exportAction:
                            self.gui.exportType(item.type)
                else:
                    menu.addAction(newAction)
                    action = menu.exec_(self.mapToGlobal(event.pos()))
                    if action:
                        if action == newAction:
                            self.gui.newType()

    def leaveEvent(self, event):
        for i in self.items():
            if i.obj == 'node':
                i.setOver(0)


class MgvLinkItem(QtWidgets.QGraphicsItem):
    """Link UI object."""
    obj = 'link'

    def __init__(self, link, graphview):
        super(MgvLinkItem, self).__init__()
        self.graphview = graphview
        self.link = link
        self.link.item = self
        self.setZValue(-5)
        if self.link.linkto.type and self.link.linkfrom.type and \
                self.link.linkto.type.getName() in self.link.linkfrom.type.getLinkWith():
            self.thickness = 6
        else:
            self.thickness = 3
        if self.link.linkfrom.type:
            self.colorfrom = QtGui.QColor(self.link.linkfrom.type.getColor())
        else:
            self.colorfrom = QtGui.QColor(255, 0, 0)
        if self.link.linkto.type:
            self.colorto = QtGui.QColor(self.link.linkto.type.getColor())
        else:
            self.colorto = QtGui.QColor(255, 0, 0)

        if hasattr(self.graphview, 'scene'):
            self.graphview.scene.addItem(self)

        for x in self.link.linkto.inputLinks:
            if not isinstance(x, string_types):
                if x.item:
                    x.item.update()

    def getY(self):
        numLink = len(self.link.linkto.inputLinks) - 1
        y = 0
        if numLink > 0:
            if self.link in self.link.linkto.inputLinks:
                iLink = self.link.linkto.inputLinks.index(self.link)
                y = 1.0 * iLink / numLink * 14 * self.graphview.globalScale - 7 * self.graphview.globalScale
        return y

    def boundingRect(self):
        if self.link:
            return self.shape().boundingRect()
        return QtCore.QRectF(0, 0, 0, 0)

    def shape(self):
        y = self.getY()
        path = QtGui.QPainterPath()
        path.moveTo(self.link.linkfrom.item.pos().x() + 50 * self.graphview.globalScale,
                    self.link.linkfrom.item.pos().y() + self.thickness * self.graphview.globalScale)
        path.cubicTo((self.link.linkfrom.item.pos().x() + 50 * self.graphview.globalScale) * .5 + (
                self.link.linkto.item.pos().x() - 50 * self.graphview.globalScale) * .5,
                     self.link.linkfrom.item.pos().y() + self.thickness * self.graphview.globalScale,
                     (self.link.linkfrom.item.pos().x() + 50 * self.graphview.globalScale) * .5 + (
                             self.link.linkto.item.pos().x() - 50 * self.graphview.globalScale) * .5,
                     self.link.linkto.item.pos().y() + self.thickness * self.graphview.globalScale + y,
                     self.link.linkto.item.pos().x() - 50 * self.graphview.globalScale,
                     self.link.linkto.item.pos().y() + self.thickness * self.graphview.globalScale + y)
        path.lineTo(self.link.linkto.item.pos().x() - 50 * self.graphview.globalScale,
                    self.link.linkto.item.pos().y() - self.thickness * self.graphview.globalScale + y)
        path.cubicTo((self.link.linkfrom.item.pos().x() + 50 * self.graphview.globalScale) * .5 + (
                self.link.linkto.item.pos().x() - 50 * self.graphview.globalScale) * .5,
                     self.link.linkto.item.pos().y() - self.thickness * self.graphview.globalScale + y,
                     (self.link.linkfrom.item.pos().x() + 50 * self.graphview.globalScale) * .5 + (
                             self.link.linkto.item.pos().x() - 50 * self.graphview.globalScale) * .5,
                     self.link.linkfrom.item.pos().y() - self.thickness * self.graphview.globalScale,
                     self.link.linkfrom.item.pos().x() + 50 * self.graphview.globalScale,
                     self.link.linkfrom.item.pos().y() - self.thickness * self.graphview.globalScale)
        return path

    def paint(self, painter, option, widget):
        y = self.getY()
        grad = QtGui.QLinearGradient(self.link.linkfrom.item.pos().x() + 50 * self.graphview.globalScale,
                                     self.link.linkfrom.item.pos().y(),
                                     self.link.linkto.item.pos().x() - 50 * self.graphview.globalScale,
                                     self.link.linkto.item.pos().y() + y)
        grad.setColorAt(0, self.colorfrom)
        grad.setColorAt(1, self.colorto)

        pen = QtGui.QPen()
        pen.setWidth(self.thickness * self.graphview.globalScale)
        pen.setBrush(grad)
        painter.setPen(pen)

        path = QtGui.QPainterPath()
        if self.link.linkto != self.link.linkfrom:
            path.moveTo(self.link.linkfrom.item.pos().x() + 50 * self.graphview.globalScale,
                        self.link.linkfrom.item.pos().y())
            path.cubicTo((self.link.linkfrom.item.pos().x() + 50 * self.graphview.globalScale) * .5 + (
                    self.link.linkto.item.pos().x() - 50 * self.graphview.globalScale) * .5,
                         self.link.linkfrom.item.pos().y(),
                         (self.link.linkfrom.item.pos().x() + 50 * self.graphview.globalScale) * .5 + (
                                 self.link.linkto.item.pos().x() - 50 * self.graphview.globalScale) * .5,
                         self.link.linkto.item.pos().y() + y,
                         self.link.linkto.item.pos().x() - 50 * self.graphview.globalScale,
                         self.link.linkto.item.pos().y() + y)
        painter.drawPath(path)
        # DOTS
        pen = QtGui.QPen()
        pen.setWidth(.75 * self.graphview.globalScale)

        painter.setPen(pen)
        painter.drawEllipse(
            self.link.linkfrom.item.pos().x() + 50 * self.graphview.globalScale - 2.5 * self.graphview.globalScale,
            self.link.linkfrom.item.pos().y() - 2.5 * self.graphview.globalScale, 5 * self.graphview.globalScale,
            5 * self.graphview.globalScale)
        painter.drawEllipse(
            self.link.linkto.item.pos().x() - 50 * self.graphview.globalScale - 2.5 * self.graphview.globalScale,
            self.link.linkto.item.pos().y() - 2.5 * self.graphview.globalScale + y, 5 * self.graphview.globalScale,
            5 * self.graphview.globalScale)

    def delete(self):
        for x in self.link.linkto.inputLinks:
            if not isinstance(x, string_types):
                if x.item:
                    x.item.update()
        for x in self.link.linkto.outputLinks:
            if not isinstance(x, string_types):
                if x.item:
                    x.item.update()
        self.link.item = None
        self.link = None
        if self.graphview:
            self.prepareGeometryChange()
            self.graphview.scene.removeItem(self)

    def updatePos(self):
        self.prepareGeometryChange()


class MgvGroupItem(QtWidgets.QGraphicsItem):
    """Group UI object."""
    obj = 'group'

    def __init__(self, group, graphview):
        super(MgvGroupItem, self).__init__()
        self.group = group
        self.group.item = self
        self.graphview = graphview
        self.minposx = None
        self.minposy = None
        self.maxposx = None
        self.maxposy = None
        self.getBox()
        self.setZValue(-1)
        self.graphview.scene.addItem(self)

    def getBox(self):
        nodes = self.group.getNodes()
        if len(nodes):
            self.minposx = min([x.posx * self.graphview.globalScale - x.item.width / 2 for x in
                                nodes]) - 30 * self.graphview.globalScale
            self.minposy = min([x.posy * self.graphview.globalScale - x.item.height / 2 for x in
                                nodes]) - 30 * self.graphview.globalScale
            self.maxposx = max([x.posx * self.graphview.globalScale + x.item.width / 2 for x in
                                nodes]) + 30 * self.graphview.globalScale
            self.maxposy = max([x.posy * self.graphview.globalScale + x.item.height / 2 for x in
                                nodes]) + 30 * self.graphview.globalScale
        else:
            self.group.delete()
            if self.group.item in self.graphview.scene.items():
                self.group.item.prepareGeometryChange()
                self.graphview.scene.removeItem(self.group.item)

    def boundingRect(self):
        return QtCore.QRectF(self.minposx, self.minposy, (self.maxposx - self.minposx), (self.maxposy - self.minposy))

    def shape(self):
        chemin = QtGui.QPainterPath()
        chemin.addRoundedRect(self.minposx, self.minposy, (self.maxposx - self.minposx), (self.maxposy - self.minposy),
                              4 * self.graphview.globalScale, 4 * self.graphview.globalScale)
        return chemin

    def paint(self, painter, option, widget):
        self.getBox()
        pen = QtGui.QPen()
        pen.setWidth(1.5 * self.graphview.globalScale)

        brush = QtGui.QBrush(QtGui.QColor(self.group.color))
        painter.setBrush(brush)

        painter.drawRoundedRect(self.minposx, self.minposy, self.maxposx - self.minposx, self.maxposy - self.minposy,
                                4 * self.graphview.globalScale, 4 * self.graphview.globalScale)

        # NOM
        text = self.group.getName()
        pen.setColor(QtGui.QColor(0, 0, 0))
        pen.setColor(QtGui.QColor(opposite(self.group.color)))
        painter.setPen(pen)
        font = QtGui.QFont(myFont, .75 * myFontSize * self.graphview.globalScale)
        t = QtGui.QTextOption()
        t.setAlignment(QtCore.Qt.AlignCenter)
        painter.setFont(font)
        painter.drawText(
            QtCore.QRectF(self.minposx, self.minposy, self.maxposx - self.minposx, 30 * self.graphview.globalScale),
            text, t)


class MgvNodeItem(QtWidgets.QGraphicsItem):
    """Node UI object."""
    obj = 'node'

    def __init__(self, node, graphview):
        super(MgvNodeItem, self).__init__()
        self.node = node
        self.node.item = self
        self.graphview = graphview
        self.width = 100 * graphview.globalScale
        self.height = 20 * graphview.globalScale
        self.selected = False
        self.scale = 1
        self.image = None
        if node.type:
            self.exists = (len(node.type.typeFiles) == 0)
        else:
            self.exists = True
        self.user = None
        self.userChanged()
        self.chemin = QtGui.QPainterPath()
        self.pshape = None
        self.imageHash = None
        self.chooseShape()
        self.graphview.scene.addItem(self)
        self.setPos(node.posx * self.graphview.globalScale, node.posy * self.graphview.globalScale)
        self.counter = 0
        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.setGraphicsEffect(self.shadow)

    def pump(self):
        self.counter += 1
        self.setScale(math.sin(self.counter * .15) * .03 + 1)
        self.update()

    def pumpStop(self):
        self.counter = 0
        self.scale = 1
        self.update()

    def checkExists(self):
        if self.exists is False:
            if not len(self.node.type.typeFiles):
                self.exists = True
                self.update()
                return
            dico = self.node.getVars()
            for f in self.node.type.typeFiles:
                path = dico[f.name]
                path = path.replace('@', '#').replace('#', '[0-9-]')
                listeall = glob.glob(path)
                liste = []
                for obj in listeall:
                    if os.path.isdir(obj):
                        liste.extend(os.listdir(obj))
                    else:
                        try:
                            if os.stat(obj).st_size > 0:
                                liste.append(obj)
                        except OSError as msg:
                            print(msg, file=sys.__stderr__)
                if len(liste) > 0:
                    self.exists = True
                    self.update()
                    return

    def userChanged(self):
        self.user = None
        for u in self.graphview.activeUsers:
            if u.getName() == self.node.getUser():
                self.user = u
                break
        if self.user is None:
            newUser = MgvUser(self.node.getUser(), self.graphview.graph.user, len(self.graphview.activeUsers))
            self.graphview.activeUsers.append(newUser)
            self.user = newUser

    def chooseShape(self):
        if self.node.type:
            self.pshape = self.node.type.getShape()
        else:
            self.pshape = 'Rectangle'
        self.chemin = QtGui.QPainterPath()
        self.image = None
        self.imageHash = None
        if self.pshape == 'Image':
            if os.path.exists(self.node.type.getImage()) or True:
                self.image = QtGui.QImage()
                ByteArr = QtCore.QByteArray.fromBase64(self.node.type.getImage())
                self.image.loadFromData(ByteArr)

                self.width = self.node.type.width * self.graphview.globalScale
                self.image = self.image.scaledToWidth(self.width)
                self.height = self.image.height()
                if len(self.node.type.getShapeVector()):
                    pos = self.node.type.getShapeVector()[0]
                    pos = [pos[0] * self.node.type.getWidth() / 100, pos[1] * self.node.type.getWidth() / 100]
                    self.chemin.moveTo(pos[0] * self.graphview.globalScale, pos[1] * self.graphview.globalScale)
                    for pos in self.node.type.getShapeVector():
                        pos = [pos[0] * self.node.type.getWidth() / 100, pos[1] * self.node.type.getWidth() / 100]
                        self.chemin.lineTo(pos[0] * self.graphview.globalScale, pos[1] * self.graphview.globalScale)
                else:
                    self.chemin.addRect(-self.width / 2, -self.height / 2, self.width, self.height)
                self.imageHash = QtGui.QImage(self.image)
                p = QtGui.QPainter(self.imageHash)
                path = os.path.join(self.graphview.gui.mgvDirectory, 'icons', 'hash.png')
                b = QtGui.QBrush(QtGui.QColor(self.node.type.getColor()))
                b.setTexture(QtGui.QPixmap(path))
                trf = QtGui.QTransform()
                trf.scale(4.0, 4.0)
                b.setTransform(trf)
                p.setCompositionMode(QtGui.QPainter.CompositionMode_SourceAtop)
                p.fillRect(0, 0, self.imageHash.width(), self.imageHash.height(), b)
                p.end()
            else:
                self.pshape = 'Rectangle'

        if self.pshape == 'Rectangle':
            if self.node.type:
                self.width = self.node.type.getWidth() * self.graphview.globalScale
            else:
                self.width = 100 * self.graphview.globalScale
            self.height = 20 * self.graphview.globalScale
            self.chemin.addRoundedRect(-self.width / 2, -self.height / 2, self.width, self.height,
                                       4 * self.graphview.globalScale, 4 * self.graphview.globalScale)
        elif self.pshape == 'Circle':
            self.width = self.node.type.getWidth() * self.graphview.globalScale
            self.height = self.node.type.getWidth() * self.graphview.globalScale
            self.chemin.addEllipse(-self.width / 2, -self.height / 2, self.width, self.height)

    def boundingRect(self):
        return QtCore.QRectF(-60 * self.graphview.globalScale, -60 * self.graphview.globalScale,
                             120 * self.graphview.globalScale, 120 * self.graphview.globalScale)

    def shape(self):
        return self.chemin

    def paint(self, painter, option, widget):
        # USER
        if not self.node.getUser() == 'free':
            grad = QtGui.QRadialGradient(0, 0, 60 * self.graphview.globalScale)
            grad.setColorAt(0, self.user.color)
            grad.setColorAt(1, QtGui.QColor(0, 0, 0, 0))
            painter.setBrush(grad)
            painter.setPen(QtCore.Qt.NoPen)
            if self.height < 50 * self.graphview.globalScale:
                painter.scale(1, .5)
            painter.drawEllipse(-60 * self.graphview.globalScale, -60 * self.graphview.globalScale,
                                120 * self.graphview.globalScale, 120 * self.graphview.globalScale)
            if self.height < 50 * self.graphview.globalScale:
                painter.scale(1, 2)
        pen = QtGui.QPen()
        pen.setWidth(1.5 * self.graphview.globalScale)
        # SELECTED
        if self.selected:
            stroker = QtGui.QPainterPathStroker()
            stroker.setWidth(4 * self.graphview.globalScale)
            path = stroker.createStroke(self.chemin)
            path = path.united(self.chemin)
            pen.setColor(QtGui.QColor(220, 220, 0))
            pen.setStyle(QtCore.Qt.DashLine)
            painter.setPen(pen)
            painter.drawPath(path)

        pen.setColor(QtGui.QColor(50, 50, 50))
        pen.setStyle(QtCore.Qt.SolidLine)
        painter.setPen(pen)

        if self.node.type:
            type_color = self.node.type.getColor()
        else:
            type_color = '#FF0000'

        brush = QtGui.QBrush(QtGui.QColor(type_color))
        painter.setBrush(brush)

        if self.selected:
            self.setZValue(1)
        else:
            self.setZValue(0)
        pen.setColor(QtGui.QColor(30, 30, 30))
        painter.setPen(pen)

        # FORME DE BASE
        if self.node.item.exists:
            if self.pshape == 'Image':
                painter.drawImage(-self.width / 2, -self.height / 2, self.image, sw=self.width, sh=self.height)
            else:
                painter.drawPath(self.chemin)
        else:
            if self.pshape == 'Image':
                painter.drawImage(-self.width / 2, -self.height / 2, self.imageHash, sw=self.width, sh=self.height)
            else:
                painter.drawPath(self.chemin)
                path = os.path.join(self.graphview.gui.mgvDirectory, 'icons', 'hash.png')
                brush.setTexture(QtGui.QPixmap(path))
                trf = QtGui.QTransform()
                trf.scale(4.0, 4.0)
                brush.setTransform(trf)
                painter.setBrush(brush)
                painter.drawPath(self.chemin)
        # NOM
        text = self.node.getName()
        brush = QtGui.QBrush(QtGui.QColor(opposite(type_color)))
        painter.setBrush(brush)
        pen = QtGui.QPen()
        pen.setColor(opposite(opposite(type_color)))
        pen.setWidth(2 * self.graphview.globalScale)
        pen.setStyle(QtCore.Qt.NoPen)
        painter.setPen(pen)

        p = QtGui.QPainterPath()
        font = QtGui.QFont(myFont, 1 * myFontSize * self.graphview.globalScale)
        font.setWeight(35)
        painter.setFont(font)
        factor = .9 * self.width / painter.fontMetrics().width(text)
        x = -painter.fontMetrics().width(text)*.5
        y = painter.fontMetrics().height() * .25
        if factor < 1:
            font.setPointSizeF(font.pointSizeF() * factor)
            x *= factor
            y *= factor

        p.addText(x, y, font, text)
        painter.strokePath(p, pen)
        painter.fillPath(p, brush)

    def delete(self):
        if self in self.graphview.selection:
            self.graphview.selection.remove(self)
        if self.scene():
            self.prepareGeometryChange()
            self.graphview.scene.removeItem(self)
        for editor in self.graphview.editors:
            if editor.node == self.node:
                if editor.isFloating():
                    editor.close()
                else:
                    editor.close()
                    self.graphview.gui.editWindow(None)

    def setItemPos(self, x, y):
        if x == self.x() and y == self.y():
            return
        for link in self.node.inputLinks:
            if not isinstance(link, string_types):
                if link.item:
                    link.item.prepareGeometryChange()
        for link in self.node.outputLinks:
            if not isinstance(link, string_types):
                if link.item:
                    link.item.prepareGeometryChange()

        self.setPos(x, y)

        for link in self.node.inputLinks:
            if not isinstance(link, string_types):
                if link.item:
                    link.item.update()
        for link in self.node.outputLinks:
            if not isinstance(link, string_types):
                if link.item:
                    link.item.update()
        for group in self.graphview.graph.groups:
            if group.item:
                if self.node in group.getNodes():
                    group.item.update()
        self.node.setNodePos(x / self.graphview.globalScale, y / self.graphview.globalScale)

    def setSelected(self, value):
        self.selected = value
        self.update()


class MgvTabCompleter(QtWidgets.QGraphicsItem):
    """Create node helper (Tab shortcut)."""
    obj = 'tabCompleter'

    def __init__(self, graphview, x, y):
        super(MgvTabCompleter, self).__init__()
        self.graphview = graphview
        self.types = sorted([w.getName() for w in self.graphview.graph.pattern.project.types])
        self.x = x
        self.y = y
        self.text = ''
        self.possibilities = self.types
        self.curseur = 0
        self.choice = 0
        self.on = 1
        self.setZValue(50)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.blink)
        self.timer.start(500)
        self.graphview.scene.addItem(self)
        self.scale = self.graphview.scale * 1.25

    def blink(self):
        self.on = not self.on
        self.update()

    def boundingRect(self):
        return QtCore.QRectF(self.x, self.y, 150 * self.scale,
                             25 * self.scale + 20 * self.scale * len(self.possibilities))

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(QtCore.QRectF(self.x, self.y, 150 * self.scale,
                                   25 * self.scale + 20 * self.scale * len(self.possibilities)))
        return path

    def paint(self, painter, option, widget):
        pen = QtGui.QPen()
        pen.setWidth(1 * self.scale)
        pen.setColor(QtGui.QColor(220, 220, 0))
        painter.setPen(pen)

        # RECTANGLE
        painter.setBrush(QtGui.QColor(30, 30, 30))
        painter.drawRoundedRect(self.x, self.y, 150 * self.scale, 20 * self.scale, 3 * self.scale, 3 * self.scale)

        # TEXT
        pen.setColor(QtGui.QColor(200, 200, 200))
        painter.setPen(pen)
        font = QtGui.QFont(myFont, .75 * myFontSize * self.scale)
        painter.setFont(font)
        t = QtGui.QTextOption()
        t.setAlignment(QtCore.Qt.AlignLeft)
        t.setAlignment(QtCore.Qt.AlignVCenter)
        painter.drawText(QtCore.QRectF(self.x + 5, self.y, 140 * self.scale, 20 * self.scale), self.text, t)

        # CURSEUR
        if self.on:
            pen.setColor(QtGui.QColor(200, 200, 200))
        else:
            pen.setColor(QtGui.QColor(30, 30, 30))
        painter.setPen(pen)
        font = QtGui.QFont(myFont, .75 * myFontSize * self.scale)
        painter.setFont(font)
        t = QtGui.QTextOption()
        t.setAlignment(QtCore.Qt.AlignLeft)
        t.setAlignment(QtCore.Qt.AlignVCenter)
        text = '|'
        fmetrics = QtGui.QFontMetrics(font)
        offset = fmetrics.width(self.text[:self.curseur])
        painter.drawText(QtCore.QRectF(self.x + 3 * self.scale + offset, self.y, 140 * self.scale, 20 * self.scale),
                         text, t)

        if len(self.possibilities):
            # SOLUTIONS
            pen.setColor(QtGui.QColor(0, 0, 0))
            painter.setPen(pen)
            painter.setBrush(QtGui.QColor(60, 60, 60))
            painter.drawRoundedRect(self.x, self.y + 25 * self.scale, 150 * self.scale,
                                    20 * self.scale * len(self.possibilities), 3 * self.scale, 3 * self.scale)

            # TEXT
            for n, x in enumerate(self.possibilities):
                if n == self.choice - 1:
                    pen.setColor(QtGui.QColor(200, 200, 0))
                else:
                    pen.setColor(QtGui.QColor(200, 200, 200))
                painter.setPen(pen)
                font = QtGui.QFont(myFont, .75 * myFontSize * self.scale)
                painter.setFont(font)
                t = QtGui.QTextOption()
                t.setAlignment(QtCore.Qt.AlignLeft)
                t.setAlignment(QtCore.Qt.AlignVCenter)
                painter.drawText(QtCore.QRectF(self.x + 5 * self.scale, self.y + 25 * self.scale + 20 * n * self.scale,
                                               140 * self.scale, 20 * self.scale), x, t)

    def getChoice(self, posy):
        return int((posy - self.y - 25 * self.scale) / 20 / self.scale) + 1

    def delete(self):
        self.timer.stop()
        self.graphview.tabBox = None
        if self.scene():
            self.prepareGeometryChange()
            self.graphview.scene.removeItem(self)

    def keyPressEvent(self, event):
        s = event.text()
        toCheck = 1
        toDelete = 0
        if event.key() == QtCore.Qt.Key_Escape:
            toCheck = 0
            toDelete = 1
        elif event.key() == QtCore.Qt.Key_Return:
            for mgvtype in self.graphview.graph.pattern.project.types:
                if mgvtype.getName().lower() == self.text.lower():
                    self.graphview.newNodes(mgvtype)
                    break
            toCheck = 0
            toDelete = 1

        elif event.key() == QtCore.Qt.Key_Backspace:
            if len(self.text):
                self.text = '%s%s' % (self.text[:self.curseur - 1], self.text[self.curseur:])
                self.curseur -= 1
                self.choice = 0
        elif event.key() == QtCore.Qt.Key_Left:
            if self.curseur > 0:
                self.curseur -= 1
        elif event.key() == QtCore.Qt.Key_Right:
            if self.curseur < len(self.text):
                self.curseur += 1
        elif event.key() == QtCore.Qt.Key_End:
            self.curseur = len(self.text)
        elif event.key() == QtCore.Qt.Key_Home:
            self.curseur = 0
        elif event.key() == QtCore.Qt.Key_Down:
            if self.choice < len(self.possibilities):
                self.choice += 1
                self.text = self.possibilities[self.choice - 1]
                self.curseur = len(self.text)
            toCheck = 0
        elif event.key() == QtCore.Qt.Key_Up:
            if self.choice > 1:
                self.choice -= 1
                self.text = self.possibilities[self.choice - 1]
                self.curseur = len(self.text)
            toCheck = 0

        elif len(s):
            self.text = '%s%s%s' % (self.text[:self.curseur], s, self.text[self.curseur:])
            self.curseur += 1
            self.choice = 0

        if toCheck:
            self.prepareGeometryChange()
            self.possibilities = [x for x in self.types if self.text.lower() in x.lower()]
        self.update()
        if toDelete:
            self.delete()


class MgvTypeEditor(QtWidgets.QMainWindow):
    """Type editor UI."""
    def __init__(self, gui, typ):
        super(MgvTypeEditor, self).__init__()
        self.gui = gui
        self.project = self.gui.currentProject
        mainUIPath = os.path.join(self.gui.mgvDirectory, 'UI', 'type.ui')
        self.root = QtCompat.loadUi(mainUIPath)
        self.setWindowTitle('Type ' + typ.getName())
        iconPath = os.path.join(self.gui.mgvDirectory, 'icons', 'mgvIcon.svg')
        self.setWindowIcon(QtGui.QIcon(iconPath))
        self.type = typ._dup()
        self.realtype = typ
        self.currentVersion = self.type.versionActive
        self.setCentralWidget(self.root)
        self.root.actionTextEdit = MultiEditor(os.path.join(self.gui.mgvDirectory, 'editorDefinitions'))
        self.root.actionTextLayout.addWidget(self.root.actionTextEdit)
        self.root.paramDefaultTextEdit = MultiEditor(os.path.join(self.gui.mgvDirectory, 'editorDefinitions'))
        self.root.paramTextLayout.addWidget(self.root.paramDefaultTextEdit)
        self.currentParam = None
        self.currentAction = None
        self.errorBox = None
        self.auto = False

        self.root.addParamButton.setIcon(QtGui.QIcon(os.path.join(gui.mgvDirectory, 'icons', 'plus.svg')))
        self.root.addActionButton.setIcon(QtGui.QIcon(os.path.join(gui.mgvDirectory, 'icons', 'plus.svg')))
        self.root.delParamButton.setIcon(QtGui.QIcon(os.path.join(gui.mgvDirectory, 'icons', 'x.svg')))
        self.root.delActionButton.setIcon(QtGui.QIcon(os.path.join(gui.mgvDirectory, 'icons', 'x.svg')))
        self.root.upParamButton.setIcon(QtGui.QIcon(os.path.join(gui.mgvDirectory, 'icons', 'arrow-up.svg')))
        self.root.upActionButton.setIcon(QtGui.QIcon(os.path.join(gui.mgvDirectory, 'icons', 'arrow-up.svg')))
        self.root.downParamButton.setIcon(QtGui.QIcon(os.path.join(gui.mgvDirectory, 'icons', 'arrow-down.svg')))
        self.root.downActionButton.setIcon(QtGui.QIcon(os.path.join(gui.mgvDirectory, 'icons', 'arrow-down.svg')))

        by = QtCore.QByteArray.fromBase64(self.type.getImage())
        image = QtGui.QImage.fromData(by)
        icon = QtGui.QIcon(QtGui.QPixmap.fromImage(image))
        self.root.shapeButton.setIcon(icon)
        self.root.shapeButton.setIconSize(QtCore.QSize(32, 32))

        # PROPERTIES
        self.root.categoryLineEdit.setText(self.type.getCategory())
        self.root.softwareLineEdit.setText(self.type.getSoftware())
        self.root.nameLineEdit.setText(self.type.getName())
        self.root.shapeComboBox.setCurrentIndex(self.root.shapeComboBox.findText(self.type.getShape()))
        self.root.helpTextEdit.setPlainText(self.type.getHelp())
        self.root.widthSlider.setValue(self.type.getWidth())
        self.root.widthSpinBox.setValue(self.type.getWidth())
        self.scriptEdit = MultiEditor(os.path.join(self.gui.mgvDirectory, 'editorDefinitions'))
        contextnames = [x.name for x in self.project.contexts]
        self.root.contextComboBox.addItems(contextnames)
        if self.type.context in contextnames:
            self.root.contextComboBox.setCurrentIndex(contextnames.index(self.type.context))
        else:
            self.contextChanged()

        self.root.tabScript.layout().addWidget(self.scriptEdit)
        vs = sorted(self.type.versions, key=lambda z: z.id)
        liste = [str(x.id) if x.id != self.type.versionActive.id else '%s - Published' % x.id for x in vs]
        self.root.versionComboBox.addItems(liste)
        self.root.versionComboBox.setCurrentIndex(vs.index(self.type.versionActive))
        self.currentParamChanged()
        self.currentActionChanged()

        self.scriptEdit.textChanged.connect(self.scriptChanged)
        self.root.paramListWidget.itemSelectionChanged.connect(self.currentParamChanged)
        self.root.actionListWidget.itemSelectionChanged.connect(self.currentActionChanged)

        # TYPES
        self.root.categoryLineEdit.editingFinished.connect(self.currentCategoryChanged)
        self.root.softwareLineEdit.editingFinished.connect(self.currentSoftwareChanged)
        self.root.nameLineEdit.editingFinished.connect(self.currentNameChanged)
        self.root.colorButton.clicked.connect(self.colorClickEvent)
        self.root.shapeComboBox.currentIndexChanged.connect(self.currentShapeChanged)
        self.root.shapeButton.clicked.connect(self.currentShapePathDialog)
        self.root.widthSpinBox.valueChanged.connect(self.root.widthSlider.setValue)
        self.root.widthSlider.valueChanged.connect(self.widthChanged)
        self.root.versionComboBox.currentIndexChanged.connect(self.changeVersion)
        self.root.newVersionPushButton.clicked.connect(self.newVersion)
        self.root.deleteVersionPushButton.clicked.connect(self.delVersion)
        self.root.publishVersionPushButton.clicked.connect(self.publishVersion)
        self.root.contextComboBox.currentIndexChanged.connect(self.contextChanged)

        # PARAMS
        self.root.paramNameLineEdit.editingFinished.connect(self.currentParamNameChanged)
        self.root.paramTypeComboBox.currentIndexChanged[str].connect(self.currentParamTypeChanged)
        self.root.enumLineEdit.editingFinished.connect(self.currentParamEnumChanged)
        self.root.paramVisibleCheckBox.stateChanged.connect(self.currentParamVisibilityChanged)
        self.root.paramDefaultTextEdit.textChanged.connect(self.currentParamDefaultChanged)
        self.root.addParamButton.clicked.connect(self.addParam)
        self.root.delParamButton.clicked.connect(self.delParam)
        self.root.upParamButton.clicked.connect(self.upParam)
        self.root.downParamButton.clicked.connect(self.downParam)
        self.root.advancedCheckBox.stateChanged.connect(self.currentParamAdvancedChanged)
        # HELP
        self.root.helpTextEdit.textChanged.connect(self.helpChanged)
        # OUTPUTS
        self.root.addOutputButton.clicked.connect(self.addOutput)
        for out in self.type.typeFiles:
            self.addOutput(out, first=False)

        # ACTIONS
        self.root.actionMenuLineEdit.editingFinished.connect(self.currentActionMenuChanged)
        self.root.actionNameLineEdit.editingFinished.connect(self.currentActionNameChanged)
        self.root.actionWarningLineEdit.editingFinished.connect(self.currentActionWarningChanged)
        self.root.actionUsersLineEdit.editingFinished.connect(self.currentActionUsersChanged)
        self.root.actionStackCheckBox.stateChanged.connect(self.currentActionStackChanged)
        self.root.actionTextEdit.textChanged.connect(self.currentActionValueChanged)
        self.root.addActionButton.clicked.connect(self.addAction)
        self.root.delActionButton.clicked.connect(self.delAction)
        self.root.upActionButton.clicked.connect(self.upAction)
        self.root.downActionButton.clicked.connect(self.downAction)
        self.root.closeButton.clicked.connect(self.closeEditor)
        self.root.saveButton.clicked.connect(self.save)
        self.root.applyButton.clicked.connect(self.apply)

        self.setStyleSheet(self.gui.style)
        self.root.enumLineEdit.hide()
        self.show()
        r = self.root.geometry()
        r.moveCenter(QtWidgets.QApplication.desktop().availableGeometry().center())
        self.setGeometry(r)

        self.currentParam = None
        self.currentAction = None
        self.loadVersion()

        self.currentParamChanged()
        self.currentActionChanged()
        self.currentShapeChanged()
        self.currentColorChanged('')

        self.root.linksComboBox.addItem('')
        self.root.linksComboBox.setItemIcon(0, QtGui.QIcon(os.path.join(gui.mgvDirectory, 'icons', 'plus-white.svg')))
        self.types = sorted([x for x in self.project.types], key=lambda k: k.getName())
        self.root.linksComboBox.addItems([x.getName() for x in self.types])
        self.root.linksComboBox.currentIndexChanged.connect(self.addLink)
        for x in self.type.getLinkWith():
            if x in [y.uuid for y in self.types]:
                self.addLink([y.uuid for y in self.types].index(x) + 1)
        self.root.linksComboBox.setMaximumWidth(50)
        self.root.linksComboBox.setMaximumHeight(29)
        self.root.linksComboBox.setStyleSheet("""QComboBox{ border: 2px solid black; border-radius: 6px; font: 14px; margin 0 0 0 0}
                                                QComboBox::down-arrow {image: none; width: 14px;}
                                                QComboBox::drop-down {border-width: 0px; }
                                                QComboBox QAbstractItemView { min-width: 150 }
                                                """)

    def contextChanged(self):
        self.type.context = str(self.root.contextComboBox.currentText())

    def addOutput(self, outFile=None, first=True):
        if outFile is None:
            outFile = MgvTypeFile(type=self.type)
            self.type.typeFiles.append(outFile)

        varUIPath = os.path.join(self.gui.mgvDirectory, 'UI', 'typeFile.ui')
        w = QtCompat.loadUi(varUIPath)
        w.deleteButton.setStyleSheet('background: transparent; color: #FF0000')
        w.deleteButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'trash-2.svg')))
        w.deleteButton.setStyleSheet('background: transparent; color: #FF0000')
        w.deleteButton.setIconSize(QtCore.QSize(16, 16))
        w.nameEdit.setText(outFile.name)
        w.pathEdit.setText(outFile.path)
        w.copyCheckBox.setChecked(outFile.copy)
        w.deleteButton.clicked.connect(lambda widget=w, out=outFile: self.deleteOutput(widget, out))
        w.nameEdit.textChanged.connect(lambda s, out=outFile, widget=w.nameEdit: self.outNameChanged(widget, out))
        w.pathEdit.textChanged.connect(lambda s, out=outFile, widget=w.pathEdit: self.outPathChanged(widget, out))
        w.copyCheckBox.stateChanged.connect(lambda i, out=outFile,
                                            widget=w.copyCheckBox: self.outCopyChanged(widget, out))
        if first:
            w.nameEdit.setStyleSheet('background-color: #FF9933')
            w.pathEdit.setStyleSheet('background-color: #FF9933')
            w.copyCheckBox.setStyleSheet("""
QCheckBox{color:#FF9933; font: bold}
QCheckBox::indicator:unchecked{image: url(:/icons/square-orange.svg); width: 30px;}
QCheckBox::indicator:checked{image: url(:/icons/check-square-orange.svg); width: 30px;}
""".replace('url(:', 'url(' + self.gui.mgvDirectory))
        self.root.outputLayout.addWidget(w)

    def deleteOutput(self, widget, outFile):
        self.type.typeFiles.remove(outFile)
        self.root.outputLayout.removeWidget(widget)
        clearLayout(widget.layout())
        widget.deleteLater()

    @staticmethod
    def outNameChanged(widget, outFile):
        outFile.name = widget.text()
        widget.setStyleSheet('')

    @staticmethod
    def outPathChanged(widget, outFile):
        outFile.path = widget.text()
        widget.setStyleSheet('')

    @staticmethod
    def outCopyChanged(widget, outFile):
        outFile.copy = widget.isChecked()
        widget.setStyleSheet('')

    def scriptChanged(self):
        self.currentVersion.script = self.scriptEdit.toPlainText()

    def changeVersion(self, num):
        s = self.root.versionComboBox.itemText(num).replace(' - Published', '')
        for v in self.type.versions:
            if v.id == int(s):
                self.currentVersion = v
                self.loadVersion()
                break

    def loadVersion(self):
        self.currentParam = None
        self.currentAction = None
        clearList(self.root.paramListWidget)
        self.root.paramListWidget.addItems([x.getName() for x in self.currentVersion.getParameters()])
        self.showActions()

        self.scriptEdit.setText(self.currentVersion.script)
        self.currentActionChanged()
        if self.currentVersion is self.type.versionActive:
            color = '#505050'
        else:
            color = '#BB6633'
        self.root.tabWidget_2.setStyleSheet('QTabWidget::pane{border: 2px solid %s}' % color)

    def showActions(self):
        self.auto = True
        clearList(self.root.actionListWidget)
        liste = []
        menus = []
        for x in self.currentVersion.getActions():
            length = x.menu.count('|') + (len(x.menu.strip()) > 0)
            menu_name = '|'.join([y.strip() for y in x.menu.split('|')])
            if menu_name not in menus and len(menu_name):
                menus.append(menu_name)
                liste.append([menu_name, '   ' * (length - 1) + menu_name.split('|')[-1]])
            liste.append(['%s|%s|%s' % (menu_name, x.order, x.name), '   ' * length + x.name])
        liste = sorted(liste, key=lambda k: k[0])
        self.root.actionListWidget.addItems([x[1] for x in liste])
        if self.currentAction:
            for i, x in enumerate(liste):
                if x[1].strip() == self.currentAction.getName():

                    self.root.actionListWidget.setCurrentItem(self.root.actionListWidget.item(i))
                    break
        self.auto = False

    def newVersion(self):
        vid = self.type.versionActive.id + 1
        while vid in [x.id for x in self.type.versions]:
            vid += 1
        ver = self.currentVersion._dup()
        ver.uuid = None
        ver.id = vid
        self.type.versions.append(ver)
        self.currentVersion = ver
        self.root.versionComboBox.addItems([str(ver.id)])
        i = self.root.versionComboBox.count() - 1
        self.root.versionComboBox.setCurrentIndex(i)
        self.loadVersion()

    def delVersion(self):
        if len(self.type.versions) and self.currentVersion is not self.type.versionActive:
            self.type.versions.remove(self.currentVersion)
            self.root.versionComboBox.removeItem(self.root.versionComboBox.currentIndex())

    def publishVersion(self):
        i = self.type.versions.index(self.type.versionActive)
        self.root.versionComboBox.setItemText(i, str(self.type.versionActive.getId()))
        self.type.versionActive = self.currentVersion
        i = self.type.versions.index(self.type.versionActive)
        self.root.versionComboBox.setItemText(i, '%s - Published' % self.type.versionActive.getId())
        color = '#505050'
        self.root.tabWidget_2.setStyleSheet('QTabWidget::pane{border: 2px solid %s}' % color)

    def addLink(self, i):
        if i > 0:
            typ = self.types[i - 1]
            if typ.uuid not in self.type.getLinkWith():
                self.type.linkWith.append(typ.uuid)
                toto = QtWidgets.QPushButton(typ.getName())
                toto.setFixedWidth(120)
                toto.setStyleSheet("""
                    QPushButton::!pressed{ background-color: %s; color: #CCCCCC; border-radius: 6; font: 14px;
                        border-width: 2px; border-color: #000000; border-style: outset; padding: 3px}
                    QPushButton::pressed{ background-color: #333333; color: #4B4B4B; border-radius: 6;
                        border-width: 2px; border-color: #000000; border-style: outset}""" % typ.color)
                self.root.linksLayout.insertWidget(self.root.linksLayout.count() - 2, toto)
                toto.clicked.connect(lambda t=typ, w=toto: self.removeLink(t, w))
            self.root.linksComboBox.setCurrentIndex(0)

    def removeLink(self, typ, widget):
        self.type.linkWith.remove(typ.uuid)
        self.root.linksLayout.removeWidget(widget)
        widget.deleteLater()

    def colorClickEvent(self):
        dialog = QtWidgets.QColorDialog(self.root)
        dialog.setModal(1)
        dialog.setCurrentColor(QtGui.QColor(self.type.getColor()))
        if dialog.exec_():
            self.currentColorChanged(0, dialog.selectedColor().name())
            self.root.actionListWidget.setFocus(QtCore.Qt.NoFocusReason)

    def apply(self):
        date = time.strftime("%y%m%d_%H%M", time.gmtime())
        backup = os.path.join(self.gui.home, 'mangrove1.0', 'types_backup', '%s_%s.json' % (self.type.name, date))
        lines = json.dumps(self.realtype.getJson(), sort_keys=True, indent=4)
        try:
            if not os.path.exists(os.path.dirname(backup)):
                os.makedirs(os.path.dirname(backup))
            with open(backup, 'w') as fid:
                fid.writelines(lines)
        except (OSError, IOError):
            self.gui.notify("Can't backup type !", 1)
        mgvWrapper.deleteNode(self.type)
        self.realtype._copy(self.type)
        self.realtype.create(self.type.uuid)

        self.gui.unlockType(self.realtype)
        self.gui.icons.refreshTypes()
        self.gui.notify('Type %s saved' % self.type.getName())

        for graphview in [self.gui.root.graphTab.widget(x) for x in range(self.gui.root.graphTab.count())]:
            for node in graphview.graph.nodes:
                if (node.type and node.type.uuid == self.realtype.uuid) or\
                        (node.type_name and node.type_name == self.realtype.name):
                    node.type = self.realtype
                    node.item.chooseShape()
                    node.item.update()
                    node._checkType()
                    for editor in graphview.editors:
                        if editor.node == node:
                            editor.read()

    def save(self):
        self.apply()
        self.close()

    def closeEvent(self, event):
        if self in self.gui.typeEditors:
            self.gui.typeEditors.remove(self)
        self.gui.unlockType(self.type)

    def closeEditor(self):
        self.close()

    def upAction(self):
        if self.currentAction:
            liste = []
            for x in self.currentVersion.getActions():
                menu_name = '|'.join([y.strip() for y in x.menu.split('|')])
                liste.append(['%s|%s' % (menu_name, x.order), x, x.order, menu_name])
            liste = sorted(liste, key=lambda k: k[0])
            ia = [x[1] for x in liste].index(self.currentAction)
            ib = ia - 1
            if ib >= 0:
                if liste[ia][3] == liste[ib][3]:
                    self.currentAction.order = liste[ib][2]
                    liste[ib][1].order = liste[ia][2]
                    self.showActions()

    def downAction(self):
        if self.currentAction:
            liste = []
            for x in self.currentVersion.getActions():
                menu_name = '|'.join([y.strip() for y in x.menu.split('|')])
                liste.append(['%s|%s' % (menu_name, x.order), x, x.order, menu_name])
            liste = sorted(liste, key=lambda k: k[0])
            ia = [x[1] for x in liste].index(self.currentAction)
            ib = ia + 1
            if ib < len(liste):
                if liste[ia][3] == liste[ib][3]:
                    self.currentAction.order = liste[ib][2]
                    liste[ib][1].order = liste[ia][2]
                    self.showActions()

    def upParam(self):
        if self.currentParam:
            for i, param in enumerate(self.currentVersion.parameters):
                if param == self.currentParam:
                    if i > 0:
                        self.root.paramListWidget.insertItem(i, self.root.paramListWidget.takeItem(i - 1))
                        tmp = self.currentVersion.parameters[i - 1]
                        self.currentVersion.parameters[i - 1] = self.currentVersion.parameters[i]
                        self.currentVersion.parameters[i] = tmp
                        break
            for i, param in enumerate(self.currentVersion.parameters):
                param.order = i

    def downParam(self):
        if self.currentParam:
            for i, param in enumerate(self.currentVersion.parameters):
                if param == self.currentParam:
                    if i < len(self.currentVersion.parameters) - 1:
                        self.root.paramListWidget.insertItem(i, self.root.paramListWidget.takeItem(i + 1))
                        tmp = self.currentVersion.parameters[i + 1]
                        self.currentVersion.parameters[i + 1] = self.currentVersion.parameters[i]
                        self.currentVersion.parameters[i] = tmp
                        break
            for i, param in enumerate(self.currentVersion.parameters):
                param.order = i

    def delParam(self):
        if self.currentParam:
            for i, param in enumerate(self.currentVersion.parameters):
                if param == self.currentParam:
                    self.root.paramListWidget.takeItem(i)
                    self.currentVersion.parameters.remove(param)
                    self.currentParamChanged()
                    break
            for i, param in enumerate(self.currentVersion.parameters):
                param.order = i

    def delAction(self):
        if self.currentAction:
            for i, action in enumerate(self.currentVersion.actions):
                if action == self.currentAction:
                    self.root.actionListWidget.takeItem(i)
                    self.currentVersion.actions.remove(action)
                    self.currentActionChanged()
                    break
            for i, action in enumerate(self.currentVersion.actions):
                action.order = i

    def addParam(self):
        num = 1
        while ('param%s' % num) in [x.getName() for x in self.currentVersion.parameters]:
            num += 1
        self.currentVersion.parameters.append(MgvParam(name='param%s' % num, version=self.currentVersion))
        self.root.paramListWidget.addItem('param%s' % num)
        for i, param in enumerate(self.currentVersion.parameters):
            param.order = i

    def addAction(self):
        num = 1
        while ('action%s' % num) in [x.getName() for x in self.currentVersion.actions]:
            num += 1
        self.currentVersion.actions.append(MgvAction(name='action%s' % num, version=self.currentVersion))
        self.root.actionListWidget.addItem('action%s' % num)
        for i, action in enumerate(self.currentVersion.actions):
            action.order = i

    def currentActionValueChanged(self):
        if self.currentAction:
            val = self.root.actionTextEdit.toPlainText()
            self.currentAction.command = val

    def currentParamDefaultChanged(self):
        if self.currentParam:
            val = self.root.paramDefaultTextEdit.toPlainText()
            try:
                if self.currentParam.type == 'int':
                    self.currentParam.default = int(val)
                elif self.currentParam.type in ['string', 'text', 'python', 'file', 'enum']:
                    self.currentParam.default = str(val)
                elif self.currentParam.type == 'float':
                    self.currentParam.default = float(val)
                elif self.currentParam.type == 'bool':
                    self.currentParam.default = val in ['True', 'true', '1']
                self.root.paramDefaultTextEdit.setStyleSheet(self.root.styleSheet())
            except ValueError:
                self.root.paramDefaultTextEdit.setStyleSheet('QTextEdit {background-color:#BB3333}')

    def currentParamVisibilityChanged(self, v):
        if self.currentParam:
            self.currentParam.visibility = self.root.paramVisibleCheckBox.isChecked()
            if self.currentParam.visibility:
                self.root.paramDefaultLabel.setText('Default Value')
                self.root.advancedCheckBox.show()
                self.root.advancedLabel.show()
            else:
                self.root.paramDefaultLabel.setText('Value')
                self.root.advancedCheckBox.hide()
                self.root.advancedLabel.hide()

    def currentParamAdvancedChanged(self, v):
        if self.currentParam:
            self.currentParam.advanced = self.root.advancedCheckBox.isChecked()

    def currentParamTypeChanged(self, s):
        if self.currentParam:
            self.currentParam.type = str(s).lower()
            if self.currentParam.type == 'int':
                if str(self.currentParam.default).replace('.', '').isdigit():
                    self.currentParam.default = int(float(self.currentParam.default))
                else:
                    self.currentParam.default = 0
            elif self.currentParam.type in ['string', 'text', 'python', 'file', 'enum']:
                self.currentParam.default = str(self.currentParam.default)
            elif self.currentParam.type == 'float':
                if str(self.currentParam.default).replace('.', '').isdigit():
                    self.currentParam.default = float(self.currentParam.default)
                else:
                    self.currentParam.default = 0.0
            elif self.currentParam.type == 'bool':
                self.currentParam.default = str(self.currentParam.default) in ['True', 'true', '1']
            self.root.paramDefaultTextEdit.setText(str(self.currentParam.default))
            if self.currentParam.type == 'enum':
                self.root.enumLineEdit.show()
            else:
                self.root.enumLineEdit.hide()

    def currentParamNameChanged(self):
        newname = self.root.paramNameLineEdit.text()
        if newname != self.currentParam.getName():
            if not (newname in [x.getName() for x in self.currentVersion.parameters]):
                self.currentParam.setName(self.root.paramNameLineEdit.text())
                self.root.paramListWidget.currentItem().setText(self.currentParam.getName())
            else:
                self.errorBox = QtWidgets.QMessageBox(self.root)
                self.errorBox.setIcon(QtWidgets.QMessageBox.Critical)
                self.errorBox.setWindowTitle('Error')
                self.errorBox.setText('This name already exists !')
                self.errorBox.open()
                self.root.paramNameLineEdit.setText(self.currentParam.getName())

    def widthChanged(self, value):
        self.root.widthSpinBox.setValue(value)
        self.type.width = value

    def currentParamEnumChanged(self):
        self.currentParam.enum = self.root.enumLineEdit.text()

    def currentActionMenuChanged(self):
        if self.currentAction:
            self.currentAction.menu = self.root.actionMenuLineEdit.text()
            self.showActions()

    def currentActionNameChanged(self):
        if self.currentAction:
            newname = self.root.actionNameLineEdit.text().strip()
            if newname != self.currentAction.getName():
                if not (newname in [x.getName() for x in self.currentVersion.getActions()]):
                    self.currentAction.name = newname
                    self.showActions()
                else:
                    self.errorBox = QtWidgets.QMessageBox(self.root)
                    self.errorBox.setIcon(QtWidgets.QMessageBox.Critical)
                    self.errorBox.setWindowTitle('Error')
                    self.errorBox.setText('This name already exists !')
                    self.errorBox.open()
                    self.root.actionNameLineEdit.setText(self.currentAction.getName())

    def currentActionWarningChanged(self):
        if self.currentAction:
            self.currentAction.warning = self.root.actionWarningLineEdit.text()

    def currentActionUsersChanged(self):
        if self.currentAction:
            self.currentAction.users = self.root.actionUsersLineEdit.text()

    def currentActionStackChanged(self):
        if self.currentAction:
            self.currentAction.stack = self.root.actionStackCheckBox.isChecked()

    def currentColorChanged(self, r, color=None):
        if not color:
            color = self.type.getColor()
        self.root.colorButton.setStyleSheet('QPushButton{ background: %s;}' % color)
        self.type.color = color

    def currentCategoryChanged(self):
        self.type.category = str(self.root.categoryLineEdit.text())

    def currentSoftwareChanged(self):
        self.type.software = str(self.root.softwareLineEdit.text())

    def currentNameChanged(self):
        newname = str(self.root.nameLineEdit.text())

        if newname != self.type.getName():
            if newname not in [x.getName() for x in self.project.types]:
                self.type.setName(newname)
            else:
                self.errorBox = QtWidgets.QMessageBox(self.gui.root)
                self.errorBox.setIcon(QtWidgets.QMessageBox.Critical)
                self.errorBox.setWindowTitle('Error')
                self.errorBox.setText('This name already exists !')
                self.errorBox.open()
                self.root.nameLineEdit.setText(self.type.getName())

    def helpChanged(self):
        self.type.help = self.root.helpTextEdit.toPlainText()

    def currentShapeChanged(self):
        self.type.shape = str(self.root.shapeComboBox.currentText())
        if self.type.shape == 'Image':
            self.root.imageWidget.show()
        else:
            self.root.imageWidget.hide()

    def currentShapePathDialog(self):
        path = self.gui.mgvDirectory
        if len(self.type.getImage()):
            path = self.type.getImage()
        out = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', path)[0]
        if len(out):
            out = os.path.abspath(out)
            img = QtGui.QImage(out)
            img = img.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
            temp = tempfile.NamedTemporaryFile(suffix='.png')
            temp.close()
            img.save(temp.name)
            self.type.setImage(temp.name)
            os.remove(temp.name)

            self.root.shapeButton.setIcon(QtGui.QIcon(out))
            self.type.shapeVector, color = extractPath(out)
            self.root.colorButton.setStyleSheet('QPushButton{ background: %s;}' % color)
            self.type.color = color

            by = QtCore.QByteArray.fromBase64(self.type.getImage())
            image = QtGui.QImage.fromData(by)
            icon = QtGui.QIcon(QtGui.QPixmap.fromImage(image))
            self.root.shapeButton.setIcon(icon)
            self.root.shapeButton.setIconSize(QtCore.QSize(32, 32))

    def currentParamChanged(self):
        self.currentParam = None
        if self.root.paramListWidget.currentItem():
            for x in self.currentVersion.parameters:
                if x.getName() == self.root.paramListWidget.currentItem().text():
                    self.currentParam = x
                    break
        if self.currentParam is None:
            self.root.paramNameLineEdit.setEnabled(0)
            self.root.enumLineEdit.setEnabled(0)
            self.root.paramTypeComboBox.setEnabled(0)
            self.root.paramVisibleCheckBox.setEnabled(0)
            self.root.paramDefaultTextEdit.setEnabled(0)
            self.root.delParamButton.setEnabled(0)
            self.root.upParamButton.setEnabled(0)
            self.root.downParamButton.setEnabled(0)

            self.root.paramNameLineEdit.setText('')
            self.root.paramTypeComboBox.setCurrentIndex(-1)
            self.root.paramDefaultTextEdit.setText('')
            self.root.advancedCheckBox.setEnabled(0)
        else:
            self.root.paramNameLineEdit.setEnabled(1)
            self.root.enumLineEdit.setEnabled(1)
            self.root.paramTypeComboBox.setEnabled(1)
            self.root.paramVisibleCheckBox.setEnabled(1)
            self.root.paramDefaultTextEdit.setEnabled(1)
            self.root.delParamButton.setEnabled(1)
            self.root.upParamButton.setEnabled(1)
            self.root.downParamButton.setEnabled(1)
            self.root.advancedCheckBox.setEnabled(1)

            self.root.paramNameLineEdit.setText(self.currentParam.getName())
            index = self.root.paramTypeComboBox.findText(self.currentParam.type, flags=QtCore.Qt.MatchFixedString)
            self.root.paramTypeComboBox.setCurrentIndex(index)
            self.root.enumLineEdit.setText(self.currentParam.enum)
            self.root.paramVisibleCheckBox.setChecked(self.currentParam.visibility)
            self.root.paramDefaultTextEdit.setText(str(self.currentParam.default))
            self.root.advancedCheckBox.setChecked(self.currentParam.advanced)
            if self.currentParam.visibility:
                self.root.advancedCheckBox.show()
                self.root.advancedLabel.show()
            else:
                self.root.advancedCheckBox.hide()
                self.root.advancedLabel.hide()

    def currentActionChanged(self):
        if self.auto:
            return
        self.currentAction = None
        if self.root.actionListWidget.currentItem():
            for x in self.currentVersion.actions:
                if x.getName() == self.root.actionListWidget.currentItem().text().strip():
                    self.currentAction = x
                    break
        if self.currentAction is None:
            self.root.actionNameLineEdit.setEnabled(0)
            self.root.actionMenuLineEdit.setEnabled(0)
            self.root.actionWarningLineEdit.setEnabled(0)
            self.root.actionUsersLineEdit.setEnabled(0)
            self.root.actionStackCheckBox.setEnabled(0)
            self.root.actionTextEdit.setEnabled(0)
            self.root.delActionButton.setEnabled(0)
            self.root.upActionButton.setEnabled(0)
            self.root.downActionButton.setEnabled(0)

            self.root.actionMenuLineEdit.setText('')
            self.root.actionNameLineEdit.setText('')
            self.root.actionWarningLineEdit.setText('')
            self.root.actionUsersLineEdit.setText('')
            self.root.actionStackCheckBox.setChecked(False)
            self.root.actionTextEdit.setText('')
        else:
            self.root.actionNameLineEdit.setEnabled(1)
            self.root.actionMenuLineEdit.setEnabled(1)
            self.root.actionWarningLineEdit.setEnabled(1)
            self.root.actionUsersLineEdit.setEnabled(1)
            self.root.actionStackCheckBox.setEnabled(1)
            self.root.actionTextEdit.setEnabled(1)
            self.root.delActionButton.setEnabled(1)
            self.root.upActionButton.setEnabled(1)
            self.root.downActionButton.setEnabled(1)

            self.root.actionNameLineEdit.setText(self.currentAction.getName())
            self.root.actionMenuLineEdit.setText(self.currentAction.menu)
            self.root.actionWarningLineEdit.setText(self.currentAction.warning)
            self.root.actionUsersLineEdit.setText(self.currentAction.users)
            self.root.actionStackCheckBox.setChecked(self.currentAction.stack)
            self.root.actionTextEdit.setText(self.currentAction.command)


class MgvTaskOutput(QtCore.QThread):
    """Separated thread that transmit an action's output."""
    signal = QtCore.Signal(str, int)

    def __init__(self, fid, sign, filename=''):
        QtCore.QThread.__init__(self)
        self.fid = fid
        self.filename = filename
        self.sign = sign

    def run(self):
        for line in iter(self.fid.readline, b''):
            self.signal.emit(line, self.sign)
        if len(self.filename):
            os.remove(self.filename)
            self.signal.emit('--- Finished ---', 2)


class MgvTask(object):
    """Separated thread that execute an action."""
    def __init__(self, actionWindow, node_version, action, widget, item):
        self.actionWindow = actionWindow
        self.node_version = node_version
        self.action = action
        self.process = None
        self.widget = widget
        self.item = item
        self.stopped = False
        self.timeStart = 0
        self.timeStop = 0
        self.outThread = None
        self.errThread = None
        self.timer = None

    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.node_version.node.item.pump)
        self.timer.start(10)
        date = time.strftime('%H:%M', time.gmtime())
        self.actionWindow.receive('--- Started at %s ---' % date, 3, self)
        self.node_version.node.item.exists = False
        self.node_version.node.item.checkExists()
        self.node_version.setLastExec(time.strftime("%d/%m/%y %H:%M", time.gmtime()),
                                      self.node_version.node.user.split("$")[0])
        self.node_version.node.graph._saveState(self.node_version)
        dico = self.node_version.getVars()
        for x in os.environ.keys():
            dico[x] = os.environ[x]
        dico = mgvDicoReplace(dico)
        for p in self.node_version.node.type.typeFiles:
            path = os.path.dirname(dico[p.name])
            if len(path):
                if not os.path.exists(path):
                    try:
                        os.makedirs(path)
                    except (OSError, IOError):
                        self.actionWindow.parent.gui.notify('Can\'t create "%s" !' % path, 1)

        cmdpath = dico['MGVNODEPATH']
        if not os.path.exists(cmdpath):
            cmdpath = dico['MGVGRAPHPATH']
        if not os.path.exists(cmdpath):
            cmdpath = os.getenv('USERPROFILE') if os.getenv('USERPROFILE') else os.getenv('HOME')
        script = self.node_version.compileScripts(self.action)
        tmpfile = tempfile.NamedTemporaryFile('w', suffix='.py', delete=False)
        tmpfile.write(script)
        tmpfile.close()
        cmd = ['python', '-u', tmpfile.name]
        if not sys.platform.startswith('win'):
            self.process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            cwd=cmdpath, preexec_fn=os.setpgrp, env=dico)
        else:
            for x in dico:
                v = dico[x]
                del dico[x]
                dico[x.encode('utf-8')] = v.encode('utf-8')
            self.process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            cwd=cmdpath, env=dico)
        self.outThread = MgvTaskOutput(self.process.stdout, 0)
        self.errThread = MgvTaskOutput(self.process.stderr, 1, tmpfile.name)
        self.outThread.signal.connect(lambda text, value: self.actionWindow.receive(text, value, self))
        self.errThread.signal.connect(lambda text, value: self.actionWindow.receive(text, value, self))
        self.outThread.start()
        self.errThread.start()


class MgvActionItem(QtWidgets.QListWidgetItem):
    """Action list widget item."""
    def __init__(self, text):
        super(MgvActionItem, self).__init__(text)


class MgvActionWindow(QtWidgets.QDockWidget):
    """Actions executions UI stack."""
    signal = QtCore.Signal(str, int)

    def __init__(self, parent):
        super(MgvActionWindow, self).__init__()
        self.parent = parent
        self.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        actionWindowPath = os.path.join(self.parent.gui.mgvDirectory, 'UI', 'action.ui')
        self.ui = QtCompat.loadUi(actionWindowPath)
        self.setWidget(self.ui)
        self.setWindowTitle('Actions')
        self.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        self.setFeatures(QtWidgets.QDockWidget.AllDockWidgetFeatures)
        self.ui.listWidget.currentItemChanged.connect(self.rowChanged)
        self.ui.clearButton.clicked.connect(self.clear)
        self.ui.killButton.clicked.connect(self.kill)
        self.ui.nowButton.clicked.connect(self.now)
        self.visible = False
        self.dico = {}
        self.tasks = []

    def clear(self):
        for task in list(self.tasks):
            if task.process:
                if task.stopped:
                    self.tasks.remove(task)
                    task.widget.deleteLater()
                    self.ui.listWidget.takeItem(self.ui.listWidget.row(task.item))

    def kill(self):
        if self.ui.listWidget.currentItem() is None:
            return
        task = self.dico[self.ui.listWidget.currentItem().id]
        c = 0
        if task.process:
            while task.process.poll() is None and c < 500:
                if not sys.platform.startswith('win'):
                    os.killpg(os.getpgid(task.process.pid), signal.SIGKILL)
                else:
                    os.popen('TASKKILL /PID %s /F /T' % task.process.pid)
                c += 1
        else:
            self.tasks.remove(task)
            task.widget.deleteLater()
            self.ui.listWidget.takeItem(self.ui.listWidget.row(task.item))

    def now(self):
        if self.ui.listWidget.currentItem() is None:
            return
        task = self.dico[self.ui.listWidget.currentItem().id]
        task.action.stack = False
        self.nextTask()

    def rowChanged(self, i):
        for task in self.tasks:
            task.widget.hide()
        if len(self.tasks):
            self.dico[i.id].widget.show()

            if self.dico[i.id].process:
                if self.dico[i.id].process.poll() is not None:
                    # fini
                    self.ui.listWidget.setStyleSheet("""
                        QListView{ background-color: #4B4B4B; color: #CCCCCC; font: 18px}
                        QListView::item:selected{ background-color: #358c64; color: #999999; font: 18px}""")
                else:
                    # en cours
                    self.ui.listWidget.setStyleSheet("""
                        QListView{ background-color: #4B4B4B; color: #CCCCCC; font: 18px}
                        QListView::item:selected{ background-color: #358c64; color: #EE9933; font: 18px}""")
            else:
                # pas fait
                self.ui.listWidget.setStyleSheet("""
                    QListView{ background-color: #4B4B4B; color: #CCCCCC; font: 18px}
                    QListView::item:selected{ background-color: #358c64; color: #CCCCCC; font: 18px}""")

    def exe(self, node_version, action):
        node_version.node.type._copy(mgvWrapper.getType(node_version.node.graph.getProject().getName(),
                                                        uuid=node_version.node.getType().uuid))
        action2 = node_version.node.type.getAction(action.getName(),
                                                   version_id=node_version.node.versionActive.typeForceVersion)
        if action2:
            action = action2
        else:
            self.parent.gui.notify('Action may be outdated', 1)
        for task in self.tasks:
            task.widget.hide()
        w = QtWidgets.QTextEdit()
        w.setStyleSheet('QTextEdit{background-color:#111111;border:1px solid #999999}')
        self.ui.layoutH.addWidget(w)
        item = MgvActionItem(node_version.node.getName() + ' - ' + action.getName())
        item.id = random.random()
        item.setToolTip(time.strftime('%H:%M', time.gmtime()))

        task = MgvTask(self, node_version, action, w, item)
        self.tasks.append(task)

        self.dico[item.id] = task
        self.ui.listWidget.insertItem(0, item)
        self.ui.listWidget.setCurrentRow(0)
        self.ui.layoutH.setStretch(self.ui.layoutH.count() - 1, 1)
        item = self.ui.listWidget.currentItem()
        if item:
            self.rowChanged(item)
        self.nextTask()

    def nextTask(self):
        running = False
        for task in self.tasks:
            # est-ce qu'un process existe ?
            if task.process:
                # est-il en cours et en mode stack ?
                if task.process.poll() is None and task.action.stack:
                    running = True
            else:
                if running is False or task.action.stack is False:
                    task.node_version.node.isRunning = True
                    for editor in self.parent.editors:
                        if editor.node == task.node_version.node:
                            editor.checkEditable()
                    task.start()
                    time.sleep(.1)
                    self.ui.listWidget.setCurrentItem(task.item)
                    self.rowChanged(task.item)
                    if task.action.stack is True:
                        running = True

    def receive(self, text, value, task):
        text = text.replace('\t', '&nbsp;&nbsp;&nbsp;').replace('<', '&#60;').replace('>', '&#62;')
        if task.widget:
            if value == 0:
                task.widget.append('<font color="grey">' + text + '</font>')
            if value == 1:
                task.widget.append('<font color="red">' + text + '</font>')
            if value == 2:  # finished
                task.timer.stop()
                node = task.node_version.node
                node.item.pumpStop()
                task.item.setForeground(QtGui.QBrush(QtGui.QColor('#666666')))
                task.timeStop = time.time()
                t = datetime.timedelta(seconds=task.timeStop - task.timeStart)
                task.widget.append('<font color="#11BB11">%s in %s</font>' % (text, t))
                node.item.checkExists()
                task.stopped = True
                node.isRunning = False
                for editor in self.parent.editors:
                    if editor.node == node:
                        editor.checkEditable()
                node.item.update()
                task.node_version._ungotvar()
                if node.user != node.graph.user:
                    respondMgv(node.port, node.graph.getFullName(), node.getName(), "UPDATE")
                self.nextTask()
            if value == 3:  # started
                task.widget.append('<font color="#11BB11">' + text + '</font>')
                task.item.setForeground(QtGui.QBrush(QtGui.QColor('#EE9933')))
                task.timeStart = time.time()

    def refresh(self):
        self.parent.gui.refresh(graphview=self.parent)


class MgvListener(QtCore.QThread):
    """External incoming message listener."""
    receiveNetworkSignal = QtCore.Signal(str, socket.socket)
    sendSignal = QtCore.Signal(str, socket.socket)
    killSignal = QtCore.Signal(int)
    portSignal = QtCore.Signal(int)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.killSignal.connect(self.interrupt)
        self.sendSignal.connect(self.send)
        self.port = 10000
        self.s = None
        self.active = False

    def __del__(self):
        self.wait()

    def interrupt(self, port):
        self.active = False
        try:
            s = socket.socket()
            s.connect(('127.0.0.1', port))
            s.close()
        except socket.error:
            pass

    def run(self):
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        fail = True

        while fail:
            try:
                self.s.bind(('127.0.0.1', self.port))
                fail = False
            except socket.error:
                self.port += 1
                if self.port > 10100:
                    self.port = -1
                    break
        self.portSignal.emit(self.port)
        self.active = True
        self.s.settimeout(15)
        while self.active:
            self.s.listen(5)
            try:
                client, info = self.s.accept()
                client.setblocking(True)
                msg = client.recv(4096).decode()
                self.receiveNetworkSignal.emit(msg, client)
            except socket.error:
                pass
        self.s.close()

    @staticmethod
    def send(text, client):
        client.send(text.encode())


class MangroveGUI(object):
    """Main UI."""
    def __init__(self, app):
        self.mgvDirectory = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
        self.types = []
        self.recent = []
        self.currentGraphView = None
        self.explorer = ''
        self.shell = ''
        self.database_id = ''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 0))
        self.IP = s.getsockname()[0]
        s.close()
        self.port = 10000
        os.environ['MGVBIN'] = self.mgvDirectory
        self.home = os.getenv('HOME')
        if not self.home:
            self.home = os.getenv('USERPROFILE')
        self.user = os.getenv('USER')
        if not self.user:
            self.user = os.getenv('USERNAME')
        self.localSettingsFile = os.path.join(self.home, 'mangrove1.0', 'settings.info')
        self.projectFile = os.path.join(self.home, 'mangrove1.0', 'project.info')
        self.recentFile = os.path.join(self.home, 'mangrove1.0', 'recentGraphs.info')
        self.favoritesFile = os.path.join(self.home, 'mangrove1.0', 'favorites.info')
        self.lastFile = os.path.join(self.home, 'mangrove1.0', 'lastOpened.info')
        self.jokeFile = os.path.join(self.mgvDirectory, 'jokes.txt')
        if not os.path.exists(os.path.join(self.home, 'mangrove1.0')):
            os.mkdir(os.path.join(self.home, 'mangrove1.0'))

        self.app = app
        self.dicoPaths = {}
        self.currentProject = None

        self.window = QtWidgets.QMainWindow()
        self.childWindow = None
        self.window.closeEvent = self.closeEvent
        mainUIPath = os.path.join(self.mgvDirectory, 'UI', 'main.ui')
        self.root = QtCompat.loadUi(mainUIPath)
        self.window.setCentralWidget(self.root)
        iconPath = os.path.join(self.mgvDirectory, 'icons', 'mgvIcon.svg')
        self.window.setWindowIcon(QtGui.QIcon(iconPath))

        if sys.platform.startswith('win'):
            import ctypes
            myappid = u'theYardVfx.mangrove.1.0.0'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.icons = IconView(self)
        self.typeEditors = []
        for f in glob.glob(self.mgvDirectory + '/fonts/*.ttf'):
            QtGui.QFontDatabase.addApplicationFont(f)

        self.style = open(self.mgvDirectory + '/style.css').read().replace('url(:', 'url(' + self.mgvDirectory)
        self.root.setStyleSheet(self.style)
        self.notify('Welcome to Mangrove !')

        self.icons.setMaximumWidth(119)
        self.icons.setMinimumWidth(119)
        self.iconFilter = QtWidgets.QLineEdit()
        self.iconFilter.setPlaceholderText('Filter')
        self.iconFilter.setMaximumWidth(100)
        self.iconFilter.setMinimumWidth(100)
        self.iconFilter.setMinimumHeight(25)
        self.iconFilter.setStyleSheet("""
            QLineEdit{ background-color: #333333; color: #CCCCCC; font: %s; border-radius: 5;
            border-width: 2px; border-style: solid; border-color: #777777}""" % myFontSize)
        self.iconHide = QtWidgets.QPushButton('<<')
        self.iconHide.setMaximumWidth(12)
        self.iconHide.setStyleSheet("""
            QPushButton::!pressed{ background-color: #333333; color: #CCCCCC; font: 8px}
            QPushButton::pressed{  background-color: #358c64; color: #CCCCCC; font: 8px}""")
        v = QtWidgets.QVBoxLayout()
        h = QtWidgets.QHBoxLayout()
        h.addWidget(self.iconFilter)
        h.addWidget(self.iconHide)
        h.setContentsMargins(3, 0, 0, 0)
        h.setSpacing(0)
        v.addLayout(h)
        v.addWidget(self.icons)
        v.addStretch()
        self.root.centralWidget().layout().insertLayout(0, v)

        self.iconHide.clicked.connect(self.toggleIcons)
        self.iconFilter.textChanged.connect(self.iconsRefresh)
        self.root.actionVars.triggered.connect(self.helpVars)
        self.root.actionHotkeys.triggered.connect(self.hotkeys)
        self.root.actionAbout.triggered.connect(self.about)
        self.root.actionHelp.triggered.connect(self.help)
        self.root.actionLocalSettings.triggered.connect(self.localSettings)
        self.root.actionProjectSettings.triggered.connect(self.projectSettings)
        self.root.actionImport_Types.triggered.connect(self.transfert)
        self.root.actionDownload.triggered.connect(self.download)
        self.root.actionHuds.triggered.connect(self.hudsSettings)
        self.root.graphTab.currentChanged.connect(self.tabChanged)
        self.root.graphTab.tabCloseRequested.connect(self.tabClose)
        self.root.actionManageGraphs.triggered.connect(self.manageGraphs)
        self.root.actionAutomation.triggered.connect(self.automation)

        self.root.graphTab.hide()
        self.window.resize(1000, 700)

        r = self.window.geometry()
        r.moveCenter(QtWidgets.QApplication.desktop().availableGeometry().center())
        self.window.setGeometry(r)
        self.window.show()

        self.root.splashTab = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout()
        self.root.splashTab.setLayout(h)
        self.root.splashTab.keyPressEvent = self.noGraphTabEvent

        label = QtWidgets.QPushButton()
        policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        label.setSizePolicy(policy)
        h.addWidget(label)
        label.setStyleSheet('background-color:transparent')
        label.setIcon(QtGui.QIcon(os.path.join(self.mgvDirectory, 'icons', 'mgvIconG.svg')))
        label.setIconSize(QtCore.QSize(250, 250))
        self.root.centralWidget().layout().addWidget(self.root.splashTab)

        self.toggleIcons()
        self.window.setWindowTitle('Mangrove 1.0')
        self.listener = MgvListener()
        self.listener.receiveNetworkSignal.connect(self.networkReceive)
        self.listener.portSignal.connect(self.getPort)
        self.listener.start()
        self.menus = []
        self.menusT = []

        self.readProjects()
        self.app.processEvents()
        self.root.splashTab.setFocus(QtCore.Qt.ActiveWindowFocusReason)
        if os.path.exists(self.lastFile):
            with open(self.lastFile) as fid:
                lines = fid.readlines()
            if len(lines):
                result = QtWidgets.QMessageBox.question(self.root, 'Open', 'Open last graphs ?',
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                        QtWidgets.QMessageBox.Yes)
                if result == QtWidgets.QMessageBox.Yes:
                    paths = []
                    for x in lines:
                        if len(x.strip().split(':')) > 1:
                            paths.append(x.strip().split(':'))
                        else:
                            paths.append(x.strip())
                    self.openGraphs(paths)
        self.readLocalSettings()

    def noGraphTabEvent(self, event):
        if event.key() == QtCore.Qt.Key_Tab:
            if event.modifiers() == QtCore.Qt.ControlModifier:
                self.toggleIcons()

    def toggleIcons(self):
        if self.iconFilter.isVisible():
            self.iconFilter.hide()
            self.iconHide.setText('>>')
            self.icons.hide()

        else:
            self.iconFilter.show()
            self.iconHide.setText('<<')
            self.icons.show()

    def iconsRefresh(self):
        self.icons.refreshTypes(type_filter=self.iconFilter.text())

    def getPort(self, port):
        self.port = str(port)
        os.environ['MGVPORT'] = str(port)
        print('%s:%s' % (self.IP, port))

    def requested(self, name, address, port):
        QtWidgets.QMessageBox.information(self.root, 'Free', 'Freeing %s: Request sent to %s:%s' % (name, address, port))

    def networkReceive(self, text, client):
        params = text.strip().split('*MGVSEPARATOR*')[1:]
        if len(params) > 0:
            sent = False
            graphfullpath = params[0]
            nodename = params[1]
            torespond = 'notmine' if text.startswith('MGVUNLOCK') else 'ok'
            for graphview in [self.root.graphTab.widget(x) for x in range(self.root.graphTab.count())]:
                if graphview.graph.getFullName() == graphfullpath:
                    for node in graphview.graph.nodes:
                        if node.getName() == nodename:
                            if not node.type:
                                continue
                            if text.startswith('SETNODEPARAM'):
                                paramname, value = params[2:]
                                if paramname in [x.getName() for x in
                                                 node.type.getParameters(node.versionActive.typeForceVersion)]:
                                    typ = [x for x in node.type.getParameters(node.versionActive.typeForceVersion) if
                                           x.getName() == paramname][0].type
                                    try:
                                        if typ == 'int':
                                            value = int(float(value))
                                        if typ == 'float':
                                            value = float(value)
                                        if typ == 'bool':
                                            value = str(value) in ['True', 'true', '1']
                                        node.setParameter(paramname, value)
                                    except ValueError:
                                        pass
                                    for editor in graphview.editors:
                                        if editor.node == node:
                                            editor.readValues()
                            if text.startswith('NEWVERSION'):
                                new = node.newVersion()
                                self.listener.sendSignal.emit(str(new.id), client)
                                sent = True
                                self.refresh(graphview=graphview)
                                pad = node.graph.pattern.project.versions_padding
                                for editor in graphview.editors:
                                    if editor.node == node:
                                        editor.root.versionComboBox.addItem(
                                            '%s - %s' % (str(new.id).zfill(pad), new.comment))
                                        editor.root.versionComboBox.setCurrentIndex(
                                            editor.root.versionComboBox.count() - 1)
                            if text.startswith('SETVERSION'):
                                value = int(params[2])
                                node.setVersion(value)
                            if text.startswith('SETCOMMENT'):
                                value = params[2]
                                node.versionActive.setComment(value)
                                for editor in graphview.editors:
                                    if editor.node == node:
                                        editor.root.versionComboBox.lineEdit().setText(value)
                            if text.startswith('EXE'):
                                n = graphview.graph.getNode(params[2])
                                if n is not None:
                                    actionsok = [x.strip() for x in params[3].split(',')]
                                    for action in n.type.getActions(version_id=n.versionActive.typeForceVersion):
                                        if action.getName() in actionsok:
                                            graphview.actionWindow.exe(n.versionActive, action)
                            if text.startswith('UPDATE'):
                                self.refresh(graphview=graphview)
                            if text.startswith('ACCEPTED'):
                                nodename = node.getName()
                                self.refresh(graphview=graphview)
                                newnode = graphview.graph.getNode(nodename)
                                if newnode:
                                    for n in [newnode]+newnode.getLinkedGroup():
                                        if n.getUser() == 'free':
                                            n.setUser(graphview.graph.getUser(), port=self.port, ip=self.IP)
                                            n.item.userChanged()
                                            n.item.update()
                                            self.notify('%s is all yours' % n.getName())
                                        else:
                                            self.notify('%s has not been freed as promised ! ' % n.getName())

                            if text.startswith('REFUSED'):
                                self.notify('Freeing of %s has been refused' % node.getName(), 1)
                            if text.startswith('SETNODEDATA'):
                                dataname, value = params[2:]
                                node.setData(dataname, value)
                            if text.startswith('GETNODEDATA'):
                                dataname = params[2]
                                torespond = node.getData(dataname)
                            if text.startswith('DELNODEDATA'):
                                dataname = params[2]
                                node.removeData(dataname)
                            if text.startswith('SETVERSIONDATA'):
                                dataname, value = params[2:]
                                node.versionActive.setData(dataname, value)
                            if text.startswith('DELVERSIONDATA'):
                                dataname = params[2]
                                node.versionActive.removeData(dataname)
                            if text.startswith('GETVERSIONDATA'):
                                dataname = params[2]
                                torespond = node.versionActive.getData(dataname)
                            if text.startswith('LOCKVERSION'):
                                node.versionActive.lock()
                                for editor in graphview.editors:
                                    if editor.node == node:
                                        editor.read()
                            if text.startswith('MGVUNLOCK'):
                                if not node.getUser() == graphview.graph.getUser():
                                    break
                                user = params[2]
                                if user == graphview.graph.getUser():
                                    torespond = 'nochange'
                                    break
                                port = params[3]
                                self.listener.sendSignal.emit('wait', client)
                                ok = QtWidgets.QMessageBox.question(self.root, 'Unlock request',
                                                                    '%s wants you to free node %s/%s.' % (
                                                                        user.split('$')[0], graphview.graph.getName(),
                                                                        nodename),
                                                                    QtWidgets.QMessageBox.Yes |
                                                                    QtWidgets.QMessageBox.No,
                                                                    QtWidgets.QMessageBox.No)
                                if ok == QtWidgets.QMessageBox.Yes:
                                    nodes = [node] + node.getLinkedGroup()
                                    for n in nodes:
                                        n.setUser('free')
                                        n.user = user
                                        n.port = port
                                        n.item.userChanged()
                                        n.item.update()
                                    respondMgv(port, graphfullpath, nodename, 'ACCEPTED')
                                else:
                                    respondMgv(port, graphfullpath, nodename, 'REFUSED')
                                sent = True
                            break
                    break
            if not sent:
                self.listener.sendSignal.emit(torespond, client)
        else:
            print('BAD INCOMING MESSAGE: "%s"' % text, file=sys.__stderr__)

    def tabChanged(self, i):
        if self.currentGraphView:
            self.currentGraphView.actionWindow.hide()
            self.currentGraphView.refreshHud()
            for editor in self.currentGraphView.editors:
                if not editor.isFloating():
                    editor.hide()
                    break
        self.currentGraphView = self.root.graphTab.currentWidget()
        if self.currentGraphView:
            self.window.setWindowTitle('%s - Mangrove 1.0' % self.currentGraphView.graph.getName())
            if self.currentGraphView.actionWindow.visible:
                self.currentGraphView.actionWindow.show()
            for editor in self.currentGraphView.editors:
                if not editor.isFloating():
                    editor.show()
                    break
            self.currentGraphView.refreshHud()
        else:
            self.window.setWindowTitle('Mangrove 1.0')

    def tabClose(self, i=None):
        if i is None:
            i = self.root.graphTab.currentIndex()
        if self.root.graphTab.widget(i) is not None:
            for editor in self.root.graphTab.widget(i).editors:
                editor.close()
            for editor in self.root.graphTab.widget(i).groupEditors:
                editor.close()
            self.root.graphTab.widget(i).graph._close()
        self.root.graphTab.removeTab(i)
        self.tabChanged(self.root.graphTab.currentIndex())
        if self.root.graphTab.count() == 0:
            self.root.graphTab.hide()
            self.root.splashTab.show()

    def copyNodeData(self, patha, pathb, grapha, graphb, namea, nameb, graphview, version):
        liste = os.listdir(patha)
        dirs = [x for x in liste if os.path.isdir(os.path.join(patha, x))]
        files = [x for x in liste if not os.path.isdir(os.path.join(patha, x))]
        for drct in dirs:
            self.app.processEvents()
            if not graphview.stopRequest:
                if not os.path.islink(os.path.join(patha, drct)):
                    link = drct
                    link = os.path.join(os.path.dirname(link), os.path.basename(link).replace(grapha, graphb))
                    link = os.path.join(os.path.dirname(link), os.path.basename(link).replace(namea, nameb))
                    if not os.path.exists(os.path.join(pathb, link)):
                        rep = os.path.join(pathb, link)
                        try:
                            os.makedirs(rep)
                        except (IOError, OSError):
                            self.notify("Can't create %s !" % rep, 1)
                    self.copyNodeData(os.path.join(patha, drct), os.path.join(pathb, link), grapha, graphb,
                                      namea, nameb, graphview, version)
                else:
                    files.append(drct)
        for f in sorted(files):
            self.app.processEvents()
            if not graphview.stopRequest:
                link = f
                if version not in link:
                    continue

                link = os.path.join(os.path.dirname(link), os.path.basename(link).replace(grapha, graphb))
                link = os.path.join(os.path.dirname(link), os.path.basename(link).replace(namea, nameb))
                if version == 'all':
                    link = os.path.join(os.path.dirname(link), os.path.basename(link).replace(version, '_v000'))
                if not os.path.islink(os.path.join(patha, f)):
                    self.notify('Copy %s...' % f)
                    try:
                        shutil.copy(os.path.join(patha, f), os.path.join(pathb, link))
                    except (IOError, OSError):
                        print("Can't copy %s to %s !" % (os.path.join(patha, f), os.path.join(pathb, link)),
                              file=sys.__stderr__)
                else:
                    linkto = os.readlink(os.path.join(patha, f))
                    linkto = linkto.replace(patha, pathb)
                    linkto = os.path.join(os.path.dirname(linkto), os.path.basename(linkto).replace(grapha, graphb))
                    linkto = os.path.join(os.path.dirname(linkto), os.path.basename(linkto).replace(namea, nameb))
                    if version == 'all':
                        linkto = os.path.join(os.path.dirname(linkto), os.path.basename(linkto).replace(version, '_v000'))
                    os.system('ln -sfT %s %s' % (linkto, os.path.join(pathb, link)))
                    if not sys.platform.startswith('win'):
                        os.system('ln -sfT %s %s' % (linkto, os.path.join(pathb, link)))
                    else:
                        if os.path.isdir(linkto):
                            os.system('mklink /D %s %s' % (os.path.join(pathb, link), linkto))
                        else:
                            os.system('mklink %s %s' % (os.path.join(pathb, link), linkto))

    def merge(self, nodes):
        oldnames = [x.getName() for x in self.currentGraphView.graph.nodes]
        newnodes = []
        pos = self.currentGraphView.mapToScene(self.currentGraphView.mousePos[0], self.currentGraphView.mousePos[1])
        moy = [0, 0]
        for node in nodes:
            node['oldname'] = node['name']
            moy = [moy[0] + float(node['posx']) * self.currentGraphView.globalScale,
                   moy[1] + float(node['posy']) * self.currentGraphView.globalScale]

            startname = node['name']
            num = ''
            while startname[-1].isdigit():
                num = startname[-1] + num
                startname = startname[:-1]
            num = int(num) if len(num) else 0
            while node['name'] in oldnames:
                num += 1
                node['name'] = '%s%s' % (startname, num)

        moy = [moy[0] / len(nodes), moy[1] / len(nodes)]

        a = QtWidgets.QMessageBox(self.root)
        a.setText("Copy associated files ?")
        a1 = QtWidgets.QPushButton('Yes')
        a2 = QtWidgets.QPushButton('No')
        a.addButton(a1, QtWidgets.QMessageBox.YesRole)
        a.addButton(a2, QtWidgets.QMessageBox.NoRole)
        a.setDefaultButton(a2)
        c = QtWidgets.QCheckBox('Flatten versions')
        c.setChecked(True)
        c.setLayoutDirection(QtCore.Qt.RightToLeft)
        a.layout().addWidget(c, 1, 1)
        a.layout().setRowMinimumHeight(1, 50)
        r = a.exec_()

        tocopy = False
        if r == 0:
            tocopy = True

        flatten = c.isChecked()
        if flatten:
            for node in nodes:
                for x in list(node['versions']):
                    if x['id'] != node['versionActive']:
                        node['versions'].remove(x)
                    else:
                        x['id'] = 0
                node['oldVersionActive'] = node['versionActive']
                node['versionActive'] = 0

        nodes_left = list(nodes)
        for node in nodes:
            if not self.currentGraphView.stopRequest:
                nodename = node['oldname']
                nodepath = node['path']
                nodegraphname = node['graphname']
                node['posx'] = node['posx'] + (pos.x() - moy[0]) / self.currentGraphView.globalScale
                node['posy'] = node['posy'] + (pos.y() - moy[1]) / self.currentGraphView.globalScale
                graphnode = MgvNode.getFromJson(node, self.currentGraphView.graph)
                graphnode.user = self.currentGraphView.graph.user
                graphnode.create()
                nodes_left.remove(node)
                for n in newnodes:
                    if node['uuid'] in n.inputLinks:
                        n.inputLinks = [x if x != node['uuid'] else graphnode.uuid for x in n.inputLinks]
                for n in nodes_left:
                    if node['uuid'] in n['inputLinks'].split(';'):
                        n['inputLinks'] = ';'.join(
                            [x if x != node['uuid'] else graphnode.uuid for x in n['inputLinks'].split(';')])

                self.currentGraphView.stopRequest = False
                if tocopy and nodepath and os.path.exists(nodepath):
                    if flatten:
                        version = 'all'
                    else:
                        pad = graphnode.graph.pattern.project.versions_padding
                        version = self.currentGraphView, '_v' + str(node['oldVersionActive']).zfill(pad)
                    self.copyNodeData(nodepath, graphnode.getPath(), nodegraphname, graphnode.graph.name,
                                      nodename, graphnode.getName(), self.currentGraphView, version)
                    if self.currentGraphView.stopRequest:
                        self.notify('Copy aborted.', 1)

                if not self.currentGraphView.stopRequest:
                    newnodes.append(graphnode)
        self.currentGraphView.stopRequest = False
        self.currentGraphView.graph._linksFromString(self.currentGraphView)
        for node in newnodes:
            mgvWrapper.setNodeAttr(node, inputLinks=';'.join([x.linkfrom.uuid for x in node.inputLinks]),
                                   updated=time.time())
        self.createNodesItem(self.currentGraphView)
        self.createLinksItem(self.currentGraphView)

        return newnodes

    def newFavorites(self):
        name, ok = QtWidgets.QInputDialog.getText(self.root, 'New Favorite', 'New favorite name :', text='current')
        if ok:
            with open(self.favoritesFile) as fid:
                root = json.load(fid)
            fav = {'project': self.currentProject.getName(), 'name': name, 'paths': []}
            for x in range(self.root.graphTab.count()):
                path = self.root.graphTab.widget(x).graph.getFullName()
                fav['paths'].append(path)
            for element in list(root):
                if element['project'] == self.currentProject.getName() and element['name'] == name:
                    root.remove(element)
            root.append(fav)
            lines = json.dumps(root, sort_keys=True, indent=4)
            try:
                with open(self.favoritesFile, 'w') as fid:
                    fid.writelines(lines)
            except IOError:
                self.notify("Can't create %s !" % self.favoritesFile, 1)
        self.readFavorites()

    def deleteFavorite(self, name):
        with open(self.favoritesFile) as fid:
            root = json.load(fid)
        for element in root:
            if element['project'] == self.currentProject.getName() and element['name'] == name:
                root.remove(element)
        lines = json.dumps(root, sort_keys=True, indent=4)
        try:
            with open(self.favoritesFile, 'w') as fid:
                fid.writelines(lines)
        except IOError:
            self.notify("Can't create %s !" % self.favoritesFile, 1)
        self.readFavorites()

    def readFavorites(self):
        self.root.menuFavorites.clear()
        if not self.currentProject:
            return
        try:
            with open(self.favoritesFile) as fid:
                root = json.load(fid)
        except IOError:
            root = []
            lines = json.dumps(root, sort_keys=True, indent=4)
            try:
                with open(self.favoritesFile, 'w') as fid:
                    fid.writelines(lines)
            except IOError:
                self.notify("Can't create %s !" % self.favoritesFile, 1)
            self.readFavorites()
            return

        for fav in root:
            proj = fav['project']
            name = fav['name']

            if self.currentProject.getName() == proj:
                menu = QtWidgets.QMenu(name, self.root.menuFavorites)
                self.root.menuFavorites.addMenu(menu)
                action = QtWidgets.QAction('Open all', menu)
                menu.addAction(action)
                favspath = [path.split(':') for path in fav['paths']]
                action.triggered.connect(lambda p=favspath: self.openGraphs(p))
                action = QtWidgets.QAction('Delete', menu)
                menu.addAction(action)
                action.triggered.connect(lambda n=name: self.deleteFavorite(n))
                menu.addSeparator()
                for path in fav['paths']:
                    path = path.split(':')
                    if path[-1] == '*template*':
                        name = ':'.join(path[1:-1])
                    else:
                        name = ':'.join(path[1:])
                    action = QtWidgets.QAction(name, menu)
                    menu.addAction(action)
                    action.triggered.connect(lambda p=path: self.openGraph(p))

        action = QtWidgets.QAction('New...', self.root.menuFavorites)
        self.root.menuFavorites.addAction(action)
        action.triggered.connect(self.newFavorites)

    def readRecent(self):
        self.recent = []
        if not self.currentProject:
            return
        if not os.path.exists(self.recentFile):
            try:
                with open(self.recentFile, 'w') as fid:
                    fid.write('')
            except IOError:
                self.notify("Can't create %s !" % self.recentFile, 1)
        with open(self.recentFile) as fid:
            lines = fid.readlines()
        for line in lines:
            line = line.strip()
            if len(line):
                if line.split(':')[0] == self.currentProject.getName():
                    self.recent.append(line.split(':'))

    def addRecent(self, path):
        with open(self.recentFile) as fid:
            lines = fid.readlines()
        lines = [x.strip() for x in lines if len(x.strip()) > 0]
        if path in lines:
            lines.remove(path)
        lines.insert(0, path)
        lines = lines[:10]
        try:
            with open(self.recentFile, 'w') as fid:
                fid.writelines('\n'.join(lines))
        except IOError:
            self.notify("Can't create %s !" % self.recentFile, 1)

    def readLocalSettings(self):
        welcome = True
        if os.path.exists(self.localSettingsFile):
            with open(self.localSettingsFile) as fid:
                root = json.load(fid)
                self.shell = root['shell']
                self.explorer = root['explorer']
                welcome = root['welcome'] if 'welcome' in root.keys() else True
                ok = False
                if 'database_id' not in root.keys():
                    ok = True
                elif root['database_id'].split(':')[0] != self.user:
                    ok = True
                if ok:
                    root['database_id'] = self.user + ':' + str(uuid.uuid1())
                    lines = json.dumps(root, sort_keys=True, indent=4)
                    with open(self.localSettingsFile, 'w') as fid:
                        fid.writelines(lines)
                self.database_id = root['database_id']
        else:
            root = {'wrapper': {'current': 'mgvWrapperNoServer',
                                'mgvWrapperNoServer': {'host': '', 'user': '', 'pwd': ''}},
                    'welcome': True, 'database_id': self.user + ':' + str(uuid.uuid1())}
            if not sys.platform.startswith('win'):
                root['shell'] = "gnome-terminal --working-directory=$PATH"
                root['explorer'] = "nautilus $PATH"
            else:
                root['shell'] = 'start /D $PATH'
                root['explorer'] = '%windir%\\explorer.exe $PATH'

            lines = json.dumps(root, sort_keys=True, indent=4)
            try:
                with open(self.localSettingsFile, 'w') as fid:
                    fid.writelines(lines)
            except IOError:
                self.notify("Can't create %s !" % self.localSettingsFile, 1)
            self.shell = root['shell']
            self.explorer = root['explorer']
            self.database_id = root['database_id']
        if welcome:
            self.childWindow = MgvWelcome(self)

    def readProjects(self):
        self.root.menuProject.clear()
        self.currentProject = None
        project_names = mgvWrapper.getProjectNames()
        if os.path.exists(self.projectFile):
            with open(self.projectFile) as fid:
                lines = fid.readlines()
            if len(lines):
                name = lines[0].strip()
                self.currentProject = MgvProject.Project(name)
                if self.currentProject:
                    self.icons.refreshTypes()
        if self.currentProject is None:
            if len(project_names):
                self.currentProject = MgvProject.Project(project_names[0])
                try:
                    with open(self.projectFile, 'w') as fid:
                        fid.write(project_names[0])
                except IOError:
                    self.notify("Can't create %s !" % self.projectFile, 1)
        projgroup = QtWidgets.QActionGroup(self.root.menuProject)
        projgroup.setExclusive(True)
        for project in project_names:
            projaction = QtWidgets.QAction(project, self.root.menuProject)
            self.root.menuProject.addAction(projaction)
            projaction.setActionGroup(projgroup)
            projaction.setCheckable(True)
            if project == self.currentProject.getName():
                projaction.setChecked(True)
            projaction.triggered.connect(lambda p=project: self.changeProject(p))

        self.root.menuProject.addSeparator()
        projnew = QtWidgets.QWidgetAction(self.root.menuProject)
        label = QtWidgets.QLabel('    New project')
        label.setStyleSheet('QLabel{font: italic} QLabel:hover{background-color: #358c64}')
        projnew.setDefaultWidget(label)
        self.root.menuProject.addAction(projnew)
        projnew.triggered.connect(self.newProject)

        self.readRecent()
        self.createGraphTemplateMenu()
        self.createOpenMenu()
        self.readFavorites()

        for i in range(self.root.graphTab.count()):
            graph = self.root.graphTab.widget(i).graph
            if graph.pattern.project.getName() == self.currentProject.getName():
                graph.pattern.project = self.currentProject

    def newProject(self):
        self.readProjects()
        lbl = '<p><i><font color="#666666">Server : %s</font></i></p>Project name :' % choosen_wrapper[10:]
        text, ok = QtWidgets.QInputDialog().getText(self.root, 'New Project', lbl, text='new')
        text = str(text)
        if ok:
            project_names = mgvWrapper.getProjectNames()
            if text not in project_names:
                p = MgvProject(name=text)
                p.create()
                self.readProjects()
                self.changeProject(text)

    def changeProject(self, project_name):
        self.currentProject = MgvProject.Project(project_name)
        try:
            with open(self.projectFile, 'w') as fid:
                fid.write(self.currentProject.getName())
        except IOError:
            self.notify("Can't create %s !" % self.projectFile, 1)
        self.readRecent()
        self.readFavorites()
        self.createGraphTemplateMenu()
        self.createOpenMenu()
        self.currentProject.readTypes()
        self.icons.refreshTypes()
        for graphview in [self.root.graphTab.widget(x) for x in range(self.root.graphTab.count())]:
            for node in graphview.graph.nodes:
                for typ in self.currentProject.types:
                    if node.type.uuid == typ.uuid:
                        node.type = typ
                        node._checkType()
        for i in range(self.root.graphTab.count()):
            if self.root.graphTab.widget(i).graph.pattern.project == self.currentProject:
                self.root.graphTab.widget(i).show()
            else:
                self.root.graphTab.widget(i).hide()
        self.notify('Project set to %s' % self.currentProject.getName())

    def createGraphTemplateMenu(self):
        for menu in self.menusT:
            menu.deleteLater()
        self.menusT = []
        if self.currentProject:
            for pattern in self.currentProject.patterns:
                menu = QtWidgets.QMenu(pattern.getName(), self.root.menuGraphTemplates)
                self.root.menuGraphTemplates.addMenu(menu)
                self.menusT.append(menu)
                for template in pattern.templates:
                    action = QtWidgets.QAction(template.getName(), menu)
                    menu.addAction(action)
                    actionpath = [self.currentProject.getName(), pattern.getName(), template.getName(), '*template*']
                    action.triggered.connect(lambda p=actionpath: self.openGraph(p))

    def createOpenMenu(self):
        for menu in self.menus:
            menu.deleteLater()
        self.menus = []
        self.dicoPaths = {}
        if self.currentProject:
            for pattern in sorted(self.currentProject.patterns, key=lambda x: x.order):
                menu = QtWidgets.QMenu(pattern.getName(), self.root.menuOpen)
                self.root.menuOpen.addMenu(menu)
                self.menus.append(menu)
                edit = QtWidgets.QLineEdit()
                wac = QtWidgets.QWidgetAction(menu)
                wac.setDefaultWidget(edit)
                menu.addAction(wac)
                self.dicoPaths[pattern] = pattern.getGraphs()
                edit.textChanged.connect(
                    lambda filtertext=edit.text(), m=menu, p=pattern: self.filterMenu(filtertext, m, p))
                self.filterMenu('', menu, pattern)

    def filterDico(self, text, dico):
        for key in list(dico.keys()):
            if isinstance(dico[key], dict):
                dico[key] = self.filterDico(text, dico[key])
                if not len(dico[key].keys()):
                    del dico[key]
            else:
                if text not in ':'.join(dico[key]):
                    del dico[key]
        return dico

    def filterMenuRec(self, filtertext, menu, dico, pattern):
        dico = self.filterDico(filtertext, dico)
        keys = sorted(dico.keys())
        more = False
        if len(keys) > 20:
            keys = keys[:20]
            more = True

        for key in keys:
            if isinstance(dico[key], dict):
                m = QtWidgets.QMenu(key, menu)
                menu.addMenu(m)
                self.filterMenuRec('', m, dico[key], pattern)
            else:
                shotaction = QtWidgets.QAction(pattern.convertGraphName(dico[key]), menu)
                menu.addAction(shotaction)
                shotaction.triggered.connect(
                    lambda path=[self.currentProject.getName(), pattern.name] + dico[key]: self.openGraph(path))
        if more:
            a = menu.addAction('...')
            a.setDisabled(True)

    def getMgvs(self, dico, filtertext):
        liste = []
        for key in dico:
            if isinstance(dico[key], dict):
                liste.extend(self.getMgvs(dico[key], filtertext))
            else:
                if filtertext.lower() in dico[key][-1].lower():
                    liste.append(dico[key])
        liste = sorted(liste, key=lambda x: x[-1])
        return liste

    def filterMenu(self, filtertext, mastermenu, pattern):
        actions = mastermenu.actions()
        for action in actions[1:]:
            mastermenu.removeAction(action)
        if len(filtertext) or len(self.dicoPaths[pattern]) < 20:
            self.filterMenuRec(filtertext, mastermenu, copy.deepcopy(self.dicoPaths[pattern]), pattern)
        else:
            a = mastermenu.addAction('Recently openned')
            a.setDisabled(True)
            for recent in self.recent:
                name = os.path.basename(recent).split('.')[0]
                action = QtWidgets.QAction(name, mastermenu)
                mastermenu.addAction(action)
                action.triggered.connect(lambda path=recent: self.openGraph(path))

    def lockType(self, typ):
        user = mgvWrapper.getLockType(typ)
        if not len(user):
            mgvWrapper.setLockType(typ, self.user)
            user = mgvWrapper.getLockType(typ)
        return user

    def unlockType(self, typ):
        mgvWrapper.setLockType(typ, '')

    def editType(self, typ):
        found = False
        for t in self.typeEditors:
            if t.type.uuid == typ.uuid:
                t.show()
                found = True
                break
        if not found:
            user = self.lockType(typ)
            if user != self.user:
                self.notify('Types are locked by %s' % user, 1)
            else:
                self.typeEditors.append(MgvTypeEditor(self, typ))

    def removeType(self, typ):
        result = QtWidgets.QMessageBox.question(self.root, 'Warning',
                                            'Are you sure to delete the type %s ?' % typ.getName(),
                                            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            self.currentProject.types.remove(typ)
            mgvWrapper.deleteNode(typ)
            self.icons.refreshTypes()

    def exportType(self, typ):
        result = QtWidgets.QFileDialog.getSaveFileName(self.root, 'Export Type', '', selectedFilter='*.json')
        if result[0]:
            try:
                with open(result[0], 'w') as fid:
                    fid.write(json.dumps([typ.getJson()], sort_keys=True, indent=4))
            except IOError:
                self.notify("Can't create %s !" % result[0], 1)

    def newType(self):
        text, ok = QtWidgets.QInputDialog.getText(self.root, 'New Type', 'New type name :', text='Type')
        text = str(text)
        if ok:
            if text not in [x.getName() for x in self.currentProject.getTypes()]:
                new = MgvType(name=text, project=self.currentProject)
                new.create()
                self.currentProject.types.append(new)
                self.editType(new)
            else:
                self.notify('Type named %s already exists !' % text, 1)
                self.newType()

    def localSettings(self):
        self.childWindow = MgvLocalSettings(self)

    def projectSettings(self):
        if self.currentProject:
            user = self.currentProject.lock(self.user)
            if user == self.user:
                self.readProjects()
                MgvProjectSettings(self, self.currentProject)
            else:
                self.notify('Projects are locked by %s !' % user, 1)
        else:
            self.newProject()

    def hudsSettings(self):
        user = self.currentProject.lock(self.user)
        if user == self.user:
            self.readProjects()
            MgvHudsSettings(self, self.currentProject)
        else:
            self.notify('Projects are locked by %s !' % user, 1)

    def transfert(self):
        self.childWindow = MgvTransfert(self)

    def download(self):
        try:
            [x for x in store.collection('TYPE').limit(1).get()]
        except credentials.google.api_core.exceptions.ServiceUnavailable:
            self.notify("Can't connect to cloud database", 1)
            return
        self.childWindow = MgvDownload(self)

    def openGraphs(self, paths=None):
        for path in paths:
            if not path:
                continue
            self.openGraph(path)

    def openGraph(self, path=None):
        for i in range(self.root.graphTab.count()):
            if isinstance(path, string_types):
                if path == self.root.graphTab.widget(i).graph.getPath():
                    self.root.graphTab.setCurrentIndex(i)
                    return
            else:
                if ':'.join(path) == self.root.graphTab.widget(i).graph.getFullName():
                    self.root.graphTab.setCurrentIndex(i)
                    return

        if self.currentGraphView:
            self.currentGraphView.actionWindow.hide()
            for editor in self.currentGraphView.editors:
                if not editor.isFloating():
                    editor.hide()
                    break

        self.root.graphTab.show()
        self.root.splashTab.hide()
        self.app.processEvents()
        if isinstance(path, string_types):
            class DummyPattern(object):
                def __init__(self, proj):
                    self.project = proj

                def getName(self):
                    return ''
            graph = MgvGraph(pattern=DummyPattern(self.currentProject), path=path, name=os.path.basename(path))
            graphview = MgvGraphView(self, graph)
        else:
            if path[0] == self.currentProject.getName():

                graph_name = ''
                graph_path = path[2:]
                if len(graph_path):
                    if graph_path[-1] == '*template*':
                        graph_name = path[-2]
                    else:
                        graph_name = self.currentProject.getPattern(path[1]).convertGraphName(graph_path)
                graph = MgvGraph(pattern=self.currentProject.getPattern(path[1]), path=graph_path, name=graph_name)
                graphview = MgvGraphView(self, graph)
            else:
                self.notify('%s: its project is not the current one' % path, 1)
                return

        if not len(graphview.graph.nodes) and path[-1] != '*template*':
            _templates = list(graphview.graph.pattern.templates)
            if len(_templates):
                if not len(graphview.graph.template_name):
                    d = QtWidgets.QDialog(self.root)
                    d.setWindowTitle('Select template')
                    g = QtWidgets.QGridLayout()
                    g.setSpacing(30)
                    g.setContentsMargins(30, 30, 30, 30)
                    d.setLayout(g)

                    _templates.append(MgvGraphTemplate(uuid=-1))
                    show_icons = any([len(x.icon) for x in _templates])
                    for i, t in enumerate(_templates):
                        v = QtWidgets.QVBoxLayout()
                        b = QtWidgets.QPushButton('' if show_icons else t.getName())
                        b.setMinimumWidth(80)
                        v.addWidget(b)
                        v.setSpacing(3)
                        if show_icons:
                            label = QtWidgets.QLabel(t.getName())
                            label.setAlignment(QtCore.Qt.AlignCenter)
                            v.addWidget(label)
                        g.addLayout(v, int(i / 5), i % 5)

                        if show_icons:
                            try:
                                b.setMinimumHeight(80)
                                if len(t.icon):
                                    b.setIcon(QtGui.QIcon(t.icon))
                                else:
                                    b.setIcon(QtGui.QIcon(os.path.join(self.mgvDirectory, 'icons', 'slash.svg')))
                                b.setIconSize(QtCore.QSize(70, 70))
                            except:
                                pass
                        b.clicked.connect(lambda ind=i: d.done(ind + 1))
                    out = d.exec_()
                    if out:
                        template = _templates[out - 1]
                        if template.uuid != -1:
                            graphview.graph._fillWithGraphTemplate(template)
                else:
                    for t in _templates:
                        if t.name == graphview.graph.template_name:
                            graphview.graph._fillWithGraphTemplate(t)
                            break

        self.currentGraphView = graphview
        i = self.root.graphTab.addTab(graphview, graph_name)
        self.root.graphTab.setCurrentIndex(i)

        self.createNodesItem(graphview)
        self.createLinksItem(graphview)
        self.createGroupsItem(graphview)
        for x in graphview.graph.getNodes():
            x.item.checkExists()
        graphview.setFocus(QtCore.Qt.NoFocusReason)
        self.addRecent(graphview.graph.getFullName())
        graphview.fit()
        graphview.refreshHud()
        self.notify('%s opened' % path)

    @staticmethod
    def createNodesItem(graphview):
        for node in graphview.graph.getNodes():
            if not node.item:
                MgvNodeItem(node, graphview).checkExists()

    @staticmethod
    def createLinksItem(graphview):
        for node in graphview.graph.getNodes():
            for link in node.outputLinks:
                if not link.item:
                    MgvLinkItem(link, graphview)
            for link in node.inputLinks:
                if not link.item:
                    MgvLinkItem(link, graphview)

    @staticmethod
    def createGroupsItem(graphview):
        for group in graphview.graph.getGroups():
            if not group.item:
                MgvGroupItem(group, graphview).getBox()

    def saveLast(self):
        opens = []
        for x in range(self.root.graphTab.count()):
            opens.append(self.root.graphTab.widget(x).graph.getFullName())
        try:
            with open(self.lastFile, 'w') as fid:
                fid.write('\n'.join(opens))
        except IOError:
            self.notify("Can't create %s !" % self.lastFile, 1)

    def refresh(self, graphview):
        graphview.activeUsers = []
        sel = [x.node.getName() for x in graphview.selection]
        graphview.graph.refresh(graphview=graphview)

        for editor in graphview.editors:
            editor.read()

        self.createNodesItem(graphview)
        self.createLinksItem(graphview)
        self.createGroupsItem(graphview)
        for x in graphview.graph.getNodes():
            x.item.checkExists()
        for node in graphview.graph.getNodes():
            node.item.userChanged()
            if node.getName() in sel:
                graphview.select(node.item, 'add')

        graphview.draw()
        for w in graphview.huds:
            if w.hud.getEvent() == 'refresh':
                w.refreshData()

    def copy(self, nodes):
        strnodes = json.dumps([x.getJson() for x in nodes], sort_keys=True, indent=4)

        data = QtCore.QMimeData()
        data.setData('MGVNODES', strnodes)
        QtWidgets.QApplication.clipboard().setMimeData(data)
        self.notify('%s nodes copied' % len(nodes))

    def paste(self):
        data = QtWidgets.QApplication.clipboard().mimeData()
        if data.hasFormat('MGVNODES'):
            strnodes = data.data('MGVNODES').__str__()
            root = json.loads(strnodes)

            newnodes = self.merge(root)
            self.currentGraphView.select([x.item for x in newnodes], 'replace')
            if len(newnodes):
                self.editWindow(newnodes[0])
            self.currentGraphView.action = 'moveForced'
            pos = self.currentGraphView.mousePos
            self.currentGraphView.moveStart(newnodes, pos[0], pos[1])
            self.notify('%s nodes pasted' % len(newnodes))
        else:
            self.notify('No data', 1)

    def setEnv(self):
        if not (None in [x.node for x in self.currentGraphView.editors]):
            new = MgvEnvEditor(self, self.currentGraphView)
            for editor in self.currentGraphView.editors:
                if not editor.isFloating():
                    editor.close()
                    break
            for editor in self.currentGraphView.groupEditors:
                if not editor.isFloating():
                    editor.close()
                    break
            self.currentGraphView.editors.append(new)
            self.root.addDockWidget(QtCore.Qt.RightDockWidgetArea, new)

    def manageGraphs(self):
        if len(self.currentProject.patterns):
            self.childWindow = MgvBatch(self, mode='manage')
        else:
            self.notify('No pattern !', 1)

    def automation(self):
        if len(self.currentProject.patterns):
            self.childWindow = MgvBatch(self, mode='automation')
        else:
            self.notify('No pattern !', 1)

    def helpVars(self):
        text = """You can use those environement variables in nodes and types scripts and variables :
        
---------------------------------------------------------------------------------------------------------------

MGVBIN :\t\tMangrove directory
MGVPROJECTNAME :\tProject Name
MGVPATTERNNAME :\tPattern Name
MGVGRAPHPATH :\tGraph directory
MGVGRAPHKEYS :\tGraph keys
MGVGRAPHNAME :\tGraph name
MGVNODEPATH :\tNode directory
MGVNODENAME :\tNode name
MGVNODETYPE :\t\tNode type
MGVNODEVERSION :\tNode version
MGVINPUTS : \t\tList of inputs's output var names separated by ";"
MGVINPUTS_x:\t\tValues of inputs's output var named x separated by ";"
KEYx :\t\t\tGraph key number x"""
        self.childWindow = QtWidgets.QMessageBox.about(self.root, 'Mangrove variables', text)

    def about(self):
        text = """<p><body>Mangrove v1.0 By Djelloul Bekri</body></p>
<br>Developped at <a href='http://theyard-vfx.com'><font color=#5bf2ad>The Yard VFX</font></a></br><br>
Issues: <a href='https://gitlab.com/TheYardVFX/mangrove/issues'><font color=#5bf2ad>gitlab</font></a></br><br>
Contact: <a href='mailto:mangrove@theyard-vfx.com'><font color=#5bf2ad>mangrove@theyard-vfx.com</font></a></br>
"""
        self.childWindow = QtWidgets.QMessageBox.about(self.root, 'About', text)

    @staticmethod
    def help():
        url = 'https://sites.google.com/theyard-vfx.com/mangrove/accueil?authuser=1'
        webbrowser.open(url)

    def hotkeys(self):
        text = """--------------------------------------------------------------------------------------
E: Open an explorer on the output directory for each selected nodes
F: Fit on all nodes or selected ones
N: Create a node of the first type
R: Sorting input links of the selected nodes by the y coordinates
T: Open a terminal on the output directory for each selected nodes
X: Show the action window
Tab: Open the node completer
P: Protect selected nodes
Shift-P: Free selected nodes
Ctrl + W: Close tab
Ctrl + C: Copy selected nodes
Ctrl + V: Paste selected nodes
Ctrl + Tab: Change the icon view
Ctrl + E: Open the Graph variables editor
Delete: removes selected nodes and associated files
Ctrl + Del: remove selected nodes but keep files
Movements :
   Alt + Left Mouse: pan view
   Alt + Right Mouse: zoom view
Selection :
   Left Mouse on node: Select the node (replace)
   Ctrl + Left Mouse on node: Select the node (add)
   Left Mouse on nothing: Start a selection box (replace)
   Ctrl + Left Mouse: Start a selection box (add)
Links :
   Double Click on link: Cut a link
   Middle Mouse: Start a link
   Right Mouse: Popup actions
Node Editor :
    Ctrl + Left Mouse on a parameter label to revert to default
--------------------------------------------------------------------------------------"""
        self.childWindow = QtWidgets.QMessageBox.about(self.root, 'Mangrove hotkeys', text)

    def editWindow(self, node):
        if not (node in [x.node for x in self.currentGraphView.editors]):
            new = MgvNodeEditor(self, self.currentGraphView, node)
            for editor in self.currentGraphView.editors:
                if not editor.isFloating():
                    editor.close()
                    break
            for editor in self.currentGraphView.groupEditors:
                if not editor.isFloating():
                    editor.close()
                    break
            self.currentGraphView.editors.append(new)
            self.root.addDockWidget(QtCore.Qt.RightDockWidgetArea, new)

    def groupEditWindow(self, group):
        if not (group in [x.group for x in self.currentGraphView.groupEditors]):
            new = MgvGroupEditor(self, self.currentGraphView, group)
            for editor in self.currentGraphView.editors:
                if not editor.isFloating():
                    editor.close()
                    break
            for editor in self.currentGraphView.groupEditors:
                if not editor.isFloating():
                    editor.close()
                    break
            self.currentGraphView.groupEditors.append(new)
            self.root.addDockWidget(QtCore.Qt.RightDockWidgetArea, new)

    def closeEvent(self, event):
        liste = ['Bye.']
        if os.path.exists(self.jokeFile):
            with open(self.jokeFile) as fid:
                liste = fid.readlines()
            liste = [x.strip().replace('\\n', '\n') for x in liste]
        haz = int(random.random() * len(liste))
        msg = liste[haz].decode('utf8')
        result = QtWidgets.QMessageBox.question(self.root, 'Do you want to quit ?', msg,
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.No:
            event.ignore()
        else:
            self.saveLast()
            port = int(os.getenv('MGVPORT'))
            self.listener.killSignal.emit(port)
            for t in self.typeEditors:
                t.close()
            while self.root.graphTab.count():
                self.tabClose(0)
                self.window.hide()
            self.listener.wait()
            self.listener = None
            os._exit(0)

    def notify(self, text, mode=0):
        if mode:
            col1 = '#BB0000'
        else:
            col1 = '#006600'
        col2 = '#BBBBBB'
        QtCore.QTimer.singleShot(4000, self.notifyOff)
        self.root.status.setStyleSheet('background-color:%s;color:%s' % (col1, col2))
        self.root.status.showMessage(text)

    def notifyOff(self):
        col1 = '#333333'
        col2 = '#BBBBBB'
        self.root.status.setStyleSheet('background-color:%s;color:%s' % (col1, col2))


class MgvWelcome(object):
    """Welcome UI."""
    def __init__(self, gui):
        self.gui = gui
        mainUIPath = os.path.join(self.gui.mgvDirectory, 'UI', 'welcome.ui')
        self.root = QtCompat.loadUi(mainUIPath)
        self.root.setWindowTitle('Welcome')
        iconPath = os.path.join(self.gui.mgvDirectory, 'icons', 'mgvIcon.svg')
        self.root.setWindowIcon(QtGui.QIcon(iconPath))
        self.root.setStyleSheet(self.gui.style)
        self.root.normalPushButton.clicked.connect(self.normal)
        self.root.discoverPushButton.clicked.connect(self.discover)
        self.root.progressBar.hide()

        self.root.show()
        self.root.setModal(True)
        r = self.root.geometry()
        r.moveCenter(QtWidgets.QApplication.desktop().availableGeometry().center())
        self.root.setGeometry(r)

    def checkShowUp(self):
        if self.root.showUpCheckBox.isChecked():
            with open(self.gui.localSettingsFile) as fid:
                root = json.load(fid)
                root['welcome'] = False

            lines = json.dumps(root, sort_keys=True, indent=4)
            try:
                with open(self.gui.localSettingsFile, 'w') as fid:
                    fid.writelines(lines)
            except IOError:
                self.gui.notify("Can't create %s !" % self.gui.localSettingsFile, 1)

    def normal(self):
        self.checkShowUp()
        self.root.close()

    def discover(self):
        self.checkShowUp()
        self.root.progressBar.setValue(0)
        self.root.progressBar.show()

        temp_dir = tempfile.mkdtemp()
        # set local settings
        with open(self.gui.localSettingsFile) as fid:
            root = json.load(fid)
            root['wrapper']['current'] = 'mgvWrapperNoServer'
            root['wrapper']['mgvWrapperNoServer'] = {'host': temp_dir, 'user': '', 'pwd': ''}
        lines = json.dumps(root, sort_keys=True, indent=4)
        with open(self.gui.localSettingsFile, 'w') as fid:
            fid.writelines(lines)
        with open(os.path.join(temp_dir, 'projects.json'), 'w') as fid:
            fid.write('{}')
        self.root.progressBar.setValue(5)
        global mgvWrapper
        mgvWrapper = changeWrapper()
        self.root.progressBar.setValue(10)

        # new pattern
        pattern = os.path.join(temp_dir, '${0}', '${0}_${1}')
        pattern = MgvPattern(name='Shots', pattern=pattern)
        self.root.progressBar.setValue(20)

        # new project
        self.gui.currentProject = MgvProject(name='Example_Project', patterns=[pattern])
        self.gui.currentProject.create()
        self.root.progressBar.setValue(30)

        # import basic types
        json_types = os.path.join(temp_dir, 'example_types.json')
        json_graph = os.path.join(temp_dir, 'example_graph.json')
        url_types = 'https://drive.google.com/uc?export=download&id=1yN8EhxdhnMK8LgNVbgq4v1ANGnOayszU'
        url_graph = 'https://drive.google.com/uc?export=download&id=1_uGXVoUqIurPJLy4-cY2oT6BmNj88ykD'
        try:
            urllib.urlretrieve(url_types, json_types)
            self.root.progressBar.setValue(50)
            urllib.urlretrieve(url_graph, json_graph)
        except:
            import urllib.request
            urllib.request.urlretrieve(url_types, json_types)
            self.root.progressBar.setValue(50)
            urllib.request.urlretrieve(url_graph, json_graph)

        self.root.progressBar.setValue(80)
        root = None
        with open(json_types) as fid:
            root = json.load(fid)
        for obj in root:
            if obj['code'] == 'Type':
                t = MgvType.getFromJson(obj)
                t.project = self.gui.currentProject
                self.gui.currentProject.types.append(t)
                t.create()
            elif obj['code'] == 'Hud':
                w = MgvHud.getFromJson(obj)
                w.project = self.gui.currentProject
                self.gui.currentProject.huds.append(w)
                w.create()
            elif obj['code'] == 'BatchScript':
                self.gui.currentProject.setBatchScript(obj.keys()[0], obj.values()[0])

        self.root.progressBar.setValue(85)
        # new graph
        with open(json_graph) as fid:
            element = json.load(fid)
        g = MgvGraph.getFromJson(element, pattern)
        g._linksFromString()
        self.root.progressBar.setValue(90)
        g.create()
        self.root.progressBar.setValue(95)

        while self.gui.root.graphTab.count():
            self.gui.root.graphTab.removeTab(0)
        self.gui.readProjects()
        self.root.progressBar.setValue(100)
        self.gui.changeProject('Example_Project')
        self.root.close()
        self.gui.openGraph([self.gui.currentProject.name, pattern.name] + g.path)


class MgvEnvEditor(QtWidgets.QDockWidget):
    """Graph variables UI editor."""
    def __init__(self, gui, graphview):
        super(MgvEnvEditor, self).__init__()
        self.gui = gui
        self.graphview = graphview
        mainUIPath = os.path.join(self.gui.mgvDirectory, 'UI', 'envEditor.ui')
        self.root = QtCompat.loadUi(mainUIPath)
        self.setWidget(self.root)
        self.node = None
        self.variables = graphview.graph.variables
        addButton = QtWidgets.QPushButton()
        addButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'chevron-down.svg')))
        addButton.setMaximumHeight(14)
        self.root.varsLayout.addWidget(addButton)
        addButton.clicked.connect(self.newVar)
        self.readVars()

    def readVars(self):
        while self.root.varsLayout.count() > 1:
            toto = self.root.varsLayout.takeAt(0)
            toto.widget().deleteLater()
        for var in self.variables:
            MgvVariableWidget(self.gui, self, self.root.varsLayout, var)

    def newVar(self):
        newVar = MgvVariable(parent=self.graphview.graph)
        self.variables.append(newVar)
        MgvVariableWidget(self.gui, self, self.root.varsLayout, newVar)
        newVar.create()

    def checkEditable(self):
        pass

    def closeEvent(self, event):
        self.graphview.editors.remove(self)
        self.graphview.refreshHud()
        self.deleteLater()


class MgvRename(object):
    """Node rename UI."""
    def __init__(self, editor):
        self.editor = editor
        self.tree = []
        mainUIPath = os.path.join(self.editor.gui.mgvDirectory, 'UI', 'rename.ui')
        self.root = QtCompat.loadUi(mainUIPath)
        self.root.nameLabel.setText(self.editor.node.getName())
        self.root.nameEdit.setText(self.editor.node.getName())
        self.root.treeViewNew.header().hide()
        self.root.treeViewOld.header().hide()
        self.root.setWindowTitle('Renaming ' + editor.node.getName())
        iconPath = os.path.join(self.editor.gui.mgvDirectory, 'icons', 'mgvIcon.svg')
        self.root.setWindowIcon(QtGui.QIcon(iconPath))
        self.root.nameEdit.textChanged.connect(lambda a, x=self.root.treeViewNew: self.refresh(x))
        self.root.cancelButton.clicked.connect(self.cancel)
        self.root.applyButton.clicked.connect(self.apply)
        self.root.setStyleSheet(self.editor.gui.style)
        self.root.show()
        r = self.root.geometry()
        r.moveCenter(QtWidgets.QApplication.desktop().availableGeometry().center())
        self.root.setGeometry(r)
        self.root.setModal(True)
        self.readDisk()
        self.refresh(self.root.treeViewOld)
        self.refresh(self.root.treeViewNew)

    def match(self, text):
        return str(self.root.nameLabel.text()) in os.path.basename(text)

    def readPos(self, pos):
        if not os.path.exists(pos):
            return ''
        out = [pos]
        liste = os.listdir(pos)
        for elem in liste:
            if not elem.startswith('.'):
                elem = os.path.join(pos, elem)
                if os.path.isdir(elem):
                    a = self.readPos(elem)
                    if len(a):
                        out.append(a)
                else:
                    if self.match(elem):
                        out.append(elem)
        if self.match(pos) or len(out) > 1 or os.path.islink(pos):
            return out
        return ''

    def readDisk(self):
        out = self.editor.node.getVars()['MGVNODEPATH']
        self.tree = self.readPos(out)

    def refreshElement(self, element, mode):
        if isinstance(element, string_types):
            name = os.path.basename(element)
            if mode:
                newname = name.replace(str(self.root.nameLabel.text()), str(self.root.nameEdit.text()))
                if newname != name:
                    item = QtGui.QStandardItem(newname)
                    item.setForeground(QtCore.Qt.red)
                    return item
            return QtGui.QStandardItem(name)
        if len(element):
            name = os.path.basename(element[0])
            parent = QtGui.QStandardItem(name)
            if mode:
                newname = name.replace(str(self.root.nameLabel.text()), str(self.root.nameEdit.text()))
                if newname != name:
                    parent = QtGui.QStandardItem(newname)
                    parent.setForeground(QtCore.Qt.red)
            if len(element) > 1:
                for sub in element[1:]:
                    parent.appendRow(self.refreshElement(sub, mode))
            return parent
        return QtGui.QStandardItem()

    def refresh(self, view):
        model = QtGui.QStandardItemModel()
        view.setModel(model)
        mode = (view == self.root.treeViewNew)
        model.appendRow(self.refreshElement(self.tree, mode))
        view.expandAll()

    def rename(self, element, old, new, torename):
        if isinstance(element, list):
            if len(element) == 0:
                return True
            for sub in element[1:]:
                if not self.rename(sub, old, new, torename):
                    return False
            element = element[0]

        name = os.path.basename(element)
        newname = name.replace(old, new)
        oldpath = os.path.join(os.path.dirname(element), name)
        newpath = os.path.join(os.path.dirname(element), newname)
        if newname != name:
            try:
                os.rename(oldpath, newpath)
            except OSError:
                self.editor.gui.notify('Error renaming files', 1)
                return False
        if os.path.islink(newpath):
            link = os.readlink(newpath)
            link = link.replace(old, new)
            if not sys.platform.startswith('win'):
                os.system('ln -sfT %s %s' % (link, newpath))
            else:
                if os.path.isdir(link):
                    os.system('mklink /D %s %s' % (newpath, link))
                else:
                    os.system('mklink %s %s' % (newpath, link))
        return True

    def treeToList(self, a):
        b = []
        for x in a:
            if isinstance(x, list):
                b.extend(self.treeToList(x))
            else:
                b.append(x)
        return b

    def apply(self):
        old = str(self.root.nameLabel.text())
        new = str(self.root.nameEdit.text())

        if new != old:
            torename = self.treeToList(self.tree)
            self.editor.gui.refresh(graphview=self.editor.graphview)
            for node in self.editor.graphview.graph.getNodes():
                if node.getName() == new:
                    self.editor.gui.notify('Dammit, another node has this name !', 1)
                    return
            self.rename(self.tree, old, new, torename)
            self.editor.node.setName(new)
            self.editor.node.item.update()
            self.editor.root.nameLabel.setText(self.editor.node.getName())
            self.editor.node._ungotvar()

            self.root.close()

    def cancel(self):
        self.root.close()


class MgvGroupEditor(QtWidgets.QDockWidget):
    """Group UI editor."""
    def __init__(self, gui, graphview, group):
        super(MgvGroupEditor, self).__init__()
        self.gui = gui
        self.graphview = graphview
        self.group = group
        mainUIPath = os.path.join(self.gui.mgvDirectory, 'UI', 'groupEditor.ui')
        if group:
            self.root = QtCompat.loadUi(mainUIPath)
            self.setWidget(self.root)
            self.root.nameLineEdit.setText(group.getName())
            self.root.colorButton.setStyleSheet('background-color: %s' % group.color)
            self.root.nameLineEdit.textChanged.connect(self.nameChanged)
            self.root.deleteButton.clicked.connect(self.delete)
            self.root.colorButton.clicked.connect(self.colorClick)
        self.graphview.refreshHud()

    def colorClick(self):
        dialog = QtGui.QColorDialog(self.root)
        dialog.setModal(1)
        dialog.setCurrentColor(QtGui.QColor(self.group.color))
        if dialog.exec_():
            self.group.setColor(dialog.selectedColor().name())
            self.root.colorButton.setStyleSheet('background-color: %s' % dialog.selectedColor().name())
            self.group.item.update()

    def nameChanged(self):
        self.group.setName(self.root.nameLineEdit.text())
        self.group.item.update()

    def delete(self):
        self.group.delete()
        self.group.item.prepareGeometryChange()
        self.graphview.scene.removeItem(self.group.item)
        self.close()

    def closeEvent(self, event):
        self.graphview.groupEditors.remove(self)
        self.graphview.refreshHud()
        self.deleteLater()


class MyQPlainTextEdit(QtWidgets.QPlainTextEdit):
    """A QPlainTextEdit with editingFinished signal."""
    editingFinished = QtCore.Signal()

    def __init__(self, parent=None):
        super(MyQPlainTextEdit, self).__init__(parent)
        self.setMinimumWidth(400)
        self.setTabStopWidth(30)
        self.moveCursor(QtGui.QTextCursor.End)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.setTabChangesFocus(False)
        self.setStyleSheet("background-color: #272822; color: #f8f8f2")

    def focusOutEvent(self, event):
        QtWidgets.QPlainTextEdit.focusOutEvent(self, event)
        self.editingFinished.emit()


class MgvNodeEditor(QtWidgets.QDockWidget):
    """Node UI editor."""
    def __init__(self, gui, graphview, node):
        super(MgvNodeEditor, self).__init__()
        self.gui = gui
        self.graphview = graphview
        self.node = node
        self.advanced = False
        self.widgets = []
        self.typeCombo = None
        self.spacerItem = None
        mainUIPath = os.path.join(self.gui.mgvDirectory, 'UI', 'editor.ui')
        if node and node.type:
            self.root = QtCompat.loadUi(mainUIPath)
            self.setWidget(self.root)
            self.root.advancedWidget.hide()
            self.root.versionButton.setStyleSheet('QPushButton{background-color: #999999; color: #333333}')
            self.root.versionLabel.setStyleSheet('QPushButton{background-color: #999999; color: #333333}')
            self.root.renameButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'edit-3.svg')))
            self.root.renameButton.setIconSize(QtCore.QSize(24, 24))
            self.root.renameButton.setStyleSheet("""
                QPushButton::!pressed{  background-color: transparent; color: #CC0000}
                QPushButton::pressed{   background-color: #4B4B4B; color: #333333}
            """)
            self.root.dataButton.setStyleSheet("""
                            QPushButton::!pressed{  background-color: transparent; color: #CC0000}
                            QPushButton::pressed{   background-color: #4B4B4B; color: #333333}
                        """)
            self.root.newVersionButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'plus.svg')))
            self.root.newVersionButton.setIconSize(QtCore.QSize(24, 24))
            self.root.delVersionButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'trash-2.svg')))
            self.root.delVersionButton.setIconSize(QtCore.QSize(24, 24))
            self.root.metaButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'info.svg')))
            self.root.metaButton.setIconSize(QtCore.QSize(24, 24))
            self.root.dataButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'info.svg')))
            self.root.dataButton.setIconSize(QtCore.QSize(24, 24))
            self.root.openButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'eye.svg')))
            self.root.openButton.setIconSize(QtCore.QSize(24, 24))
            ico = 'lock.svg'
            if self.node.versionActive.isLocked():
                ico = 'unlock.svg'
            self.root.lockButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', ico)))
            self.root.lockButton.setIconSize(QtCore.QSize(24, 24))
            self.root.versionLabel.setPixmap(
                QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'chevron-down.svg')).pixmap(20, 20))
            self.root.versionLabel.setMaximumHeight(20)
            if hasattr(node.type, 'name'):
                self.setStyleSheet('QDockWidget::title{ background-color: %s} QDockWidget{ color: %s}' % (
                    node.type.getColor(), opposite(node.type.getColor())))
                self.setWindowTitle(node.type.getName().upper())
            else:
                self.setWindowTitle(node.type.upper())

            self.root.versionButton.setStyleSheet('padding: 3px 0px; background-color: #555555; color: #000000')
            self.root.versionLabel.setStyleSheet(
                'background-color: #555555; color: #CCCCCC; border-bottom-right-radius: 6; border-top-right-radius: 6;')

            self.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
            self.setFeatures(QtWidgets.QDockWidget.AllDockWidgetFeatures)

            self.root.renameButton.clicked.connect(self.renameCallback)
            self.auto = False
            self.root.commentTextEdit.textChanged.connect(self.commentChanged)
            self.root.versionButton.clicked.connect(self.versionPopup)
            self.root.lockButton.clicked.connect(self.toggleLock)

            self.root.newVersionButton.clicked.connect(self.newVersion)
            self.root.delVersionButton.clicked.connect(self.delVersion)
            self.root.metaButton.clicked.connect(self.viewMeta)
            self.root.dataButton.clicked.connect(self.viewNodeMeta)
            self.root.openButton.clicked.connect(self.openVersion)
            self.root.advancedButton.clicked.connect(self.advancedChanged)
            self.read()
            self.root.commentTextEdit.setMinimumHeight(30)
            self.root.splitter.setSizes([1, 10000])
        self.graphview.refreshHud()

    def checkLock(self):
        if self.node.versionActive.isLocked():
            self.root.lockButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'unlock.svg')))
        else:
            self.root.lockButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'lock.svg')))

    def toggleLock(self):
        if self.node.versionActive.isLocked():
            self.node.versionActive.unlock()
            self.root.lockButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'lock.svg')))
        else:
            self.node.versionActive.lock()
            self.root.lockButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'unlock.svg')))
        self.checkEditable()

    def advancedChanged(self):
        self.advanced = not self.advanced
        if self.advanced:
            self.root.advancedButton.setText('- Advanced')
            self.root.advancedWidget.show()
        else:
            self.root.advancedButton.setText('+ Advanced')
            self.root.advancedWidget.hide()
        self.checkEditable()

    def read(self):
        self.root.nameLabel.setText(self.node.getName())
        self.readVersions()
        pad = self.node.graph.pattern.project.versions_padding
        self.root.versionButton.setText('v' + str(self.node.versionActive.id).zfill(pad))
        self.widgets = []
        self.spacerItem = None
        self.readValues()
        self.readVars()
        self.checkLock()
        self.checkEditable()

    def viewMeta(self):
        s = ''
        dico = self.node.versionActive.getAllData()
        if len(dico):
            for key in dico:
                s += '%s: %s\n' % (key, dico[key])
        else:
            s = 'No metadata in this version.'
        QtWidgets.QMessageBox.information(self.root, 'Metadatas of %s' % self.node.getName(), s)

    def viewNodeMeta(self):
        s = ''
        dico = self.node.getAllData()
        if len(dico):
            for key in dico:
                s += '%s: %s\n' % (key, dico[key])
        else:
            s = 'No metadata in this node.'
        QtWidgets.QMessageBox.information(self.root,
                                          'Metadatas of %s, version %s' % (self.node.getName(),
                                                                           self.node.versionActive.getId()), s)

    def readVersions(self):
        items = []
        pad = self.node.graph.pattern.project.versions_padding
        for ver in self.node.getVersions():
            items.append('%s - %s' % (str(ver.id).zfill(pad), ver.comment))
        self.auto = True
        self.root.commentTextEdit.setPlainText(self.node.versionActive.comment)
        self.root.versionButton.setText('v' + str(self.node.versionActive.id).zfill(pad))
        self.auto = False

    def checkEditable(self):
        if self.node and self.node.type:
            active = (self.node.getUser() == self.node.graph.getUser() and not self.node.isRunning)
            self.root.renameButton.setEnabled(active)
            self.root.versionButton.setEnabled(active)
            self.root.newVersionButton.setEnabled(active)
            self.root.lockButton.setEnabled(active)

            if active:
                color = '#000000'
            else:
                color = '#777777'
            self.root.versionButton.setStyleSheet("""padding: 3px 0px; border-top-left-radius: 6;
            border-bottom-left-radius: 6; background-color: #555555; color: %s""" % color)

            if self.node.versionActive.isLocked():
                active = False
            self.root.commentTextEdit.setEnabled(active)
            self.root.delVersionButton.setEnabled(active)
            for i in range(self.root.varsLayout.count()):
                w = self.root.varsLayout.itemAt(i)
                w.widget().setEnabled(active)
            for w in self.widgets:
                try:
                    w.setReadOnly(not active)
                except AttributeError:
                    w.setEnabled(active)

    def renameCallback(self):
        MgvRename(self)

    def rename(self, name):
        if name != self.node.getName():
            self.gui.refresh(graphview=self.graphview)
            for node in self.graphview.graph.getNodes():
                if node.getName() == name:
                    self.gui.notify('Dammit, another node has this name !', 1)
                    return
            self.node.setName(name)
            self.node.item.update()
            self.root.nameLabel.setText(self.node.getName())
            self.node._ungotvar()

    def typeVersionChanged(self, v):
        if v == 0:
            self.node.setTypeForceVersion(-1)
        else:
            self.node.setTypeForceVersion(int(self.typeCombo.itemText(v)))
        self.readValues()

    def readValues(self):
        self.root.versionButton.setToolTip('Last execution: %s by %s' % (
            self.node.versionActive.getLastExec(), self.node.versionActive.getLastUser()))
        self.widgets = []
        clearLayout(self.root.paramsLayout)
        clearLayout(self.root.advancedLayout)

        h = QtWidgets.QHBoxLayout()
        self.typeCombo = QtWidgets.QComboBox()
        label = QtWidgets.QLabel('Type Version')
        label.setMinimumWidth(100)
        h.addWidget(label)
        h.addWidget(self.typeCombo)
        self.root.advancedLayout.addLayout(h)
        self.widgets.append(label)
        self.widgets.append(self.typeCombo)
        self.widgets.append(h)
        self.typeCombo.addItems(['Published'])
        self.typeCombo.addItems([str(x.id).zfill(3) for x in self.node.type.versions])
        self.root.setStyleSheet('#Form{background-color: #333333}')
        if self.node.versionActive.typeForceVersion > -1:
            for i, ver in enumerate(self.node.type.versions):
                if ver.id == self.node.versionActive.typeForceVersion:
                    self.typeCombo.setCurrentIndex(i + 1)
                    self.root.setStyleSheet('#Form{background-color: #3A3333}')
                    break
        self.typeCombo.currentIndexChanged.connect(self.typeVersionChanged)
        last = None
        if hasattr(self.node.type, 'name'):
            for param in self.node.type.getParameters(self.node.versionActive.typeForceVersion):
                if param.visibility:
                    last = None
                    val = self.node.versionActive.getParameter(param.getName())
                    value_changed = param.getName() in self.node.versionActive.parameters

                    class MyLabel(QtWidgets.QLabel):
                        def __init__(self, gui, text, parameter, parent=None):
                            super(MyLabel, self).__init__(parent)
                            self.gui = gui
                            self.parameter = parameter
                            self.setText(text)

                        def mousePressEvent(self, event):
                            if event.modifiers() == QtCore.Qt.ControlModifier:
                                self.gui.revertToDefault(self.parameter)
                            event.accept()

                    label = MyLabel(self, param.getName(), param)
                    if param.type == 'int':
                        layout = QtWidgets.QHBoxLayout()
                        layout.setContentsMargins(1, 1, 1, 1)
                        label.setMinimumWidth(100)
                        edit = QtWidgets.QSpinBox()
                        edit.setMaximum(999999999)
                        edit.setMinimum(-999999999)
                        edit.setValue(val)
                        layout.addWidget(label)
                        layout.addWidget(edit)
                        layout.setStretch(1, 1)
                        if param.advanced:
                            self.root.advancedLayout.addLayout(layout)
                        else:
                            self.root.paramsLayout.addLayout(layout)
                        self.widgets.append(label)
                        self.widgets.append(edit)
                        self.widgets.append(layout)

                        edit.valueChanged.connect(lambda v, p=param.getName(), lab=label: self.intChanged(v, p, lab))

                    if param.type == 'bool':
                        layout = QtWidgets.QHBoxLayout()
                        layout.setContentsMargins(1, 1, 1, 1)
                        label.setMinimumWidth(100)
                        edit = QtWidgets.QCheckBox()
                        edit.setChecked(val)
                        layout.addWidget(edit)
                        layout.addWidget(label)
                        layout.setStretch(1, 1)
                        if param.advanced:
                            self.root.advancedLayout.addLayout(layout)
                        else:
                            self.root.paramsLayout.addLayout(layout)
                        self.widgets.append(label)
                        self.widgets.append(edit)
                        self.widgets.append(layout)

                        edit.stateChanged.connect(lambda v, p=param.getName(), lab=label: self.boolChanged(v, p, lab))

                    if param.type == 'float':
                        layout = QtWidgets.QHBoxLayout()
                        layout.setContentsMargins(1, 1, 1, 1)
                        label.setMinimumWidth(100)
                        edit = QtWidgets.QDoubleSpinBox()
                        edit.setDecimals(4)
                        edit.setMaximum(999999999)
                        edit.setMinimum(-999999999)
                        edit.setValue(val)
                        layout.addWidget(label)
                        layout.addWidget(edit)
                        layout.setStretch(1, 1)
                        if param.advanced:
                            self.root.advancedLayout.addLayout(layout)
                        else:
                            self.root.paramsLayout.addLayout(layout)
                        self.widgets.append(label)
                        self.widgets.append(edit)
                        self.widgets.append(layout)

                        edit.valueChanged.connect(lambda v, p=param.getName(), lab=label: self.floatChanged(v, p, lab))

                    if param.type == 'string':
                        layout = QtWidgets.QHBoxLayout()
                        layout.setContentsMargins(1, 1, 1, 1)
                        label.setMinimumWidth(100)
                        edit = QtWidgets.QLineEdit()
                        edit.setText(val)
                        layout.addWidget(label)
                        layout.addWidget(edit)
                        layout.setStretch(1, 1)
                        if param.advanced:
                            self.root.advancedLayout.addLayout(layout)
                        else:
                            self.root.paramsLayout.addLayout(layout)
                        self.widgets.append(label)
                        self.widgets.append(edit)
                        self.widgets.append(layout)

                        edit.editingFinished.connect(lambda w=edit, p=param.getName(),
                                                     lab=label: self.stringChanged(w, p, lab))

                    if param.type == 'file':
                        layout = QtWidgets.QHBoxLayout()
                        layout.setContentsMargins(1, 1, 1, 1)
                        layout.setSpacing(1)
                        label.setMinimumWidth(100)
                        edit = QtWidgets.QLineEdit()
                        edit.setText(val)
                        button = QtWidgets.QPushButton()
                        button.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'folder.svg')))
                        button.setIconSize(QtCore.QSize(16, 16))
                        button.setMaximumSize(20, 20)
                        button.setStyleSheet('background: transparent')
                        layout.addWidget(label)
                        layout.addWidget(edit)
                        layout.addWidget(button)
                        layout.setStretch(1, 1)
                        if param.advanced:
                            self.root.advancedLayout.addLayout(layout)
                        else:
                            self.root.paramsLayout.addLayout(layout)
                        self.widgets.append(label)
                        self.widgets.append(edit)
                        self.widgets.append(layout)

                        edit.editingFinished.connect(lambda w=edit, p=param.getName(),
                                                     lab=label: self.stringChanged(w, p, lab))
                        button.clicked.connect(lambda p=edit.text(), w=edit: self.fileRequest(p, w))
                    if param.type == 'enum':
                        layout = QtWidgets.QHBoxLayout()
                        layout.setContentsMargins(1, 1, 1, 1)
                        label.setMinimumWidth(100)
                        combo = QtWidgets.QComboBox()
                        liste = param.enum.split(';')
                        combo.addItems(liste)
                        if val in liste:
                            combo.setCurrentIndex(liste.index(val))
                        layout.addWidget(label)
                        layout.addWidget(combo)
                        layout.setStretch(1, 1)
                        if param.advanced:
                            self.root.advancedLayout.addLayout(layout)
                        else:
                            self.root.paramsLayout.addLayout(layout)
                        self.widgets.append(label)
                        self.widgets.append(combo)
                        self.widgets.append(layout)
                        combo.currentIndexChanged.connect(lambda v, p=param.getName(), lab=label:
                                                          self.enumChanged(v, p, liste, lab))
                    if param.type in ['text', 'python']:
                        last = 'text'
                        layout = QtWidgets.QVBoxLayout()
                        layout.setContentsMargins(1, 1, 1, 1)

                        if param.type == 'python':
                            edit = MultiEditor(os.path.join(self.gui.mgvDirectory, 'editorDefinitions'))
                            textedit = edit.text
                        else:
                            edit = MyQPlainTextEdit()
                            textedit = edit

                        edit.setPlainText(val)
                        layout.addWidget(label)
                        layout.addWidget(edit)
                        layout.setStretch(1, 1)
                        if param.advanced:
                            self.root.advancedLayout.addLayout(layout)
                        else:
                            self.root.paramsLayout.addLayout(layout)
                        self.widgets.append(label)
                        self.widgets.append(edit)
                        self.widgets.append(layout)

                        textedit.editingFinished.connect(lambda w=textedit, p=param.getName(),
                                                         lab=label: self.textChanged(w, p, lab))

                    if value_changed:
                        label.setStyleSheet('color: #358c64')

        if last is None:
            self.spacerItem = QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding,
                                                    QtWidgets.QSizePolicy.Expanding)
            self.root.paramsLayout.addSpacerItem(self.spacerItem)

    def revertToDefault(self, param):
        self.node.versionActive.delParameter(param.name)
        self.readValues()

    def fileRequest(self, path, edit):
        dico = self.node.getVars()
        dico['dummy_path_456'] = path
        dico = mgvDicoReplace(dico)
        path = dico['dummy_path_456']
        if not os.path.exists(path):
            path = os.path.dirname(path)
            if not os.path.exists(path):
                path = self.graphview.graph.getWorkDirectory()

        class MyFileDialog(QtWidgets.QFileDialog):
            def __init__(self, parent):
                super(MyFileDialog, self).__init__(parent)

            def accept(self):
                files = self.selectedFiles()
                if not len(files):
                    return
                self.filesSelected.emit(files)
                QtWidgets.QDialog.accept(self)
        w = MyFileDialog(self.gui.root)
        w.setDirectory(path)
        w.setFileMode(QtWidgets.QFileDialog.AnyFile)
        out = w.exec_()
        if out:
            out = w.selectedFiles()[0]
            dico = self.node.getVars()
            out = out.replace(dico['MGVNODEPATH'], '${MGVNODEPATH}')
            out = out.replace(dico['MGVGRAPHPATH'], '${MGVGRAPHPATH}')
            edit.setText(out)
            edit.setFocus()

    def nameChanged(self):
        value = self.root.nameEdit.text()
        self.node.setName(value)
        self.node.item.update()
        self.node._ungotvar()

    def commentChanged(self):
        if not self.auto:
            self.node.versionActive.setComment(self.root.commentTextEdit.toPlainText())

    def versionPopup(self):
        if self.node in [x.node_version.node for x in self.graphview.actionWindow.tasks if not x.stopped]:
            self.gui.notify('Node %s is running !' % self.node.getName(), 1)
        menu = QtWidgets.QMenu(self.root)
        actions = []
        pad = self.node.graph.pattern.project.versions_padding
        for v in self.node.versions:
            addAction = QtWidgets.QWidgetAction(menu)
            lab = QtWidgets.QLabel(str(v.id).zfill(pad) + ' - ' + v.comment.split('\n')[0])
            lab.setStyleSheet('QLabel{font: %s;} QLabel:hover{background-color: #358c64; font: %s;}' % (
                myFontSize + 2, myFontSize + 2))
            addAction.setDefaultWidget(lab)
            menu.addAction(addAction)
            actions.append(addAction)
        menu.setMinimumWidth(self.root.versionButton.geometry().width()+self.root.versionLabel.geometry().width())
        action = menu.exec_(self.root.versionButton.mapToGlobal(QtCore.QPoint(0, 0)))
        for ac, v in zip(actions, self.node.versions):
            if ac == action:
                self.auto = True
                self.node.setVersion(v)
                self.root.commentTextEdit.setPlainText(v.comment)
                self.root.versionButton.setText('v' + str(v.id).zfill(pad))
                self.readValues()
                self.readVars()
                self.checkLock()
                self.node._ungotvar()
                self.auto = False
                break

    def readVars(self):
        clearLayout(self.root.varsLayout)
        addButton = QtWidgets.QPushButton()
        addButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'chevron-down.svg')))
        addButton.setMaximumHeight(14)
        addButton.clicked.connect(self.newVar)
        self.root.varsLayout.addWidget(addButton)
        for var in self.node.versionActive.variables:
            MgvVariableWidget(self.gui, self.node.versionActive, self.root.varsLayout, var)

    def newVersion(self):
        self.node.newVersion()

    def delVersion(self):
        nodes = self.node.getLinkedGroup()
        txt = ''
        if len(nodes) > 1:
            txt = 'Warning: ' + ', '.join([x.getName() for x in nodes]) + ' will be affected !'
        result = QtWidgets.QMessageBox.question(self.root, 'Warning',
                                                'Are you sure to delete the version %s ?\n%s' % (
                                                    self.node.versionActive.id, txt),
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            for node, v in zip(nodes, [x.versionActive for x in nodes]):
                node.delVersion(v)

    def openVersion(self):
        pad = self.node.graph.pattern.project.versions_padding
        path = os.path.join(self.graphview.graph.getWorkDirectory(), self.node.getName(),
                            '.exec_state_v' + str(self.node.versionActive.id).zfill(pad))
        if not os.path.exists(path):
            self.gui.notify('No state saved for this version', 1)
            return
        self.gui.openGraph(path)

    def newVar(self):
        newVar = MgvVariable(parent=self.node.versionActive)
        newVar.create()
        self.node.versionActive.variables.append(newVar)
        MgvVariableWidget(self.gui, self.node.versionActive, self.root.varsLayout, newVar)
        self.node._ungotvar()

    def intChanged(self, value, param, label):
        self.node.setParameter(str(param), int(value))
        if param in self.node.versionActive.parameters:
            label.setStyleSheet('color: #358c64')
        else:
            label.setStyleSheet('color: #CCCCCC')
        self.node._ungotvar()

    def boolChanged(self, value, param, label):
        self.node.setParameter(str(param), value == 2)
        if param in self.node.versionActive.parameters:
            label.setStyleSheet('color: #358c64')
        else:
            label.setStyleSheet('color: #CCCCCC')
        self.node._ungotvar()

    def floatChanged(self, value, param, label):
        self.node.setParameter(str(param), float(value))
        if param in self.node.versionActive.parameters:
            label.setStyleSheet('color: #358c64')
        else:
            label.setStyleSheet('color: #CCCCCC')
        self.node._ungotvar()

    def stringChanged(self, widget, param, label):
        self.node.setParameter(str(param), widget.text())
        if param in self.node.versionActive.parameters:
            label.setStyleSheet('color: #358c64')
        else:
            label.setStyleSheet('color: #CCCCCC')
        self.node._ungotvar()

    def textChanged(self, widget, param, label):
        self.node.setParameter(str(param), widget.toPlainText())
        if param in self.node.versionActive.parameters:
            label.setStyleSheet('color: #358c64')
        else:
            label.setStyleSheet('color: #CCCCCC')
        self.node._ungotvar()

    def enumChanged(self, value, param, liste, label):
        self.node.setParameter(str(param), liste[value])
        if param in self.node.versionActive.parameters:
            label.setStyleSheet('color: #358c64')
        else:
            label.setStyleSheet('color: #CCCCCC')
        self.node._ungotvar()

    def closeEvent(self, event):
        self.graphview.editors.remove(self)
        self.graphview.refreshHud()
        self.deleteLater()


class MgvVariableWidget(object):
    """Node or graph variable UI object."""
    def __init__(self, gui, ver, layout, variable):
        self.gui = gui
        self.layout = layout
        self.version = ver
        self.variable = variable
        varUIPath = os.path.join(gui.mgvDirectory, 'UI', 'var.ui')
        self.widget = QtCompat.loadUi(varUIPath)
        self.widget.delButton.setIcon(QtGui.QIcon(os.path.join(gui.mgvDirectory, 'icons', 'x.svg')))

        self.layout.insertWidget(self.layout.count() - 1, self.widget)

        self.widget.checkBox.setCheckState(QtCore.Qt.Checked if self.variable.active else QtCore.Qt.Unchecked)
        self.widget.nameEdit.setText(self.variable.getName())
        self.widget.valueEdit.setText(self.variable.value)

        self.widget.delButton.clicked.connect(self.delete)
        self.toggle(save=False)
        self.widget.checkBox.stateChanged.connect(lambda a: self.toggle())
        self.widget.nameEdit.textChanged.connect(lambda a: self.nameChanged(a))
        self.widget.valueEdit.textChanged.connect(lambda a: self.valueChanged(a))

        self.widget.setStyleSheet("""
            QWidget{background-color: #555555;}
            QLineEdit:enabled{  background-color: #666666; color: #CCCCCC; }
            QLineEdit:!enabled{ background-color: #666666; color: #999999; }
            """)
        self.widget.setAcceptDrops(True)

    def nameChanged(self, value):
        self.variable.setName(value)
        if self.version.node:
            self.version.node._ungotvar()

    def valueChanged(self, value):
        self.variable.setValue(value)
        if self.version.node:
            self.version.node._ungotvar()

    def delete(self):
        self.version.variables.remove(self.variable)
        mgvWrapper.deleteNode(self.variable)
        self.widget.deleteLater()
        if self.version.node:
            self.version.node._ungotvar()

    def toggle(self, save=True):
        state = self.widget.checkBox.checkState()
        self.widget.nameEdit.setEnabled(state)
        self.widget.valueEdit.setEnabled(state)
        if state:
            self.variable.active = 1
        else:
            self.variable.active = 0
        if self.version.node:
            self.version.node._ungotvar()
        else:
            if save:
                self.version.graphview.graph.saveEnvs()


class MgvSearchThread(QtCore.QThread):
    """Separated thread that returns graph names from filters."""
    signal = QtCore.Signal(str, int)

    def __init__(self, pattern, graphkey, nodename, nodetype, graphedit, nameedit, typeedit):
        QtCore.QThread.__init__(self)
        self.pattern = pattern
        self.graphkey = graphkey
        self.nodename = nodename
        self.nodetype = nodetype
        self.graphedit = graphedit
        self.nameEdit = nameedit
        self.typeedit = typeedit
        self.stop = False

    def run(self):
        if not self.nodename and not self.nodetype:
            liste = mgvWrapper.getPatternGraphs(self.pattern)
        elif self.nodename and not self.nodetype:
            liste = mgvWrapper.getPatternGraphs(self.pattern, with_node_named=self.nameEdit)
        elif not self.nodename and self.nodetype:
            liste = mgvWrapper.getPatternGraphs(self.pattern, with_type_named=self.typeedit)
        else:
            liste = mgvWrapper.getPatternGraphs(self.pattern,  with_node_named=self.nameEdit,
                                                with_type_named=self.typeedit)
        if self.stop:
            return
        for i, path in enumerate(liste):
            if self.stop:
                return
            self.signal.emit(None, (i * 100) / len(liste))
            if self.graphkey:
                if self.graphedit not in ':'.join(path):
                    continue
            self.signal.emit(':'.join(path), 0)
        self.signal.emit(None, 100)


class MgvBatch(object):
    """Batch UI."""
    def __init__(self, gui, mode):
        self.gui = gui
        mainUIPath = os.path.join(self.gui.mgvDirectory, 'UI', 'macro.ui')
        self.root = QtCompat.loadUi(mainUIPath)
        iconPath = os.path.join(self.gui.mgvDirectory, 'icons', 'mgvIcon.svg')
        self.root.scriptAddButton.setIcon(QtGui.QIcon(os.path.join(gui.mgvDirectory, 'icons', 'plus.svg')))
        self.root.scriptDelButton.setIcon(QtGui.QIcon(os.path.join(gui.mgvDirectory, 'icons', 'trash-2.svg')))
        self.root.scriptRenameButton.setIcon(QtGui.QIcon(os.path.join(gui.mgvDirectory, 'icons', 'edit-3.svg')))
        self.root.setWindowIcon(QtGui.QIcon(iconPath))
        self.root.setStyleSheet(self.gui.style)
        self.root.outputTextEdit.setStyleSheet('QTextEdit{background-color:#111111;border:1px solid #999999}')
        self.root.progressBar.hide()
        self.root.goProgressBar.hide()
        self.root.killButton.hide()
        self.auto = True
        self.ok = False
        self.root.nodeTypeComboBox.addItems(sorted([x.getName() for x in self.gui.currentProject.types]))
        self.root.patternComboBox.addItems([x.getName() for x in self.gui.currentProject.patterns])
        self.root.scriptComboBox.addItems(sorted([x.name for x in self.gui.currentProject.batchScripts]))
        self.pattern = None
        self.batch_thread = None
        self.search_thread = None
        self.childWindow = None

        self.root.patternComboBox.currentIndexChanged.connect(self.patternChanged)
        self.root.graphKeyLineEdit.returnPressed.connect(self.search)
        self.root.nodeNameLineEdit.returnPressed.connect(self.search)
        self.root.nodeTypeComboBox.currentIndexChanged.connect(self.search)
        self.root.goPushButton.clicked.connect(self.go)
        self.root.graphKeyCheckBox.toggled.connect(self.toggleGraphKey)
        self.root.nodeNameCheckBox.toggled.connect(self.toggleNodeName)
        self.root.nodeTypeCheckBox.toggled.connect(self.toggleNodeType)
        self.root.scriptComboBox.currentIndexChanged.connect(self.scriptChanged)
        self.root.scriptAddButton.clicked.connect(self.scriptAdd)
        self.root.scriptDelButton.clicked.connect(self.scriptDel)
        self.root.scriptRenameButton.clicked.connect(self.scriptRename)
        self.root.killButton.clicked.connect(self.kill)
        self.root.resultListWidget.itemSelectionChanged.connect(self.selectGraphs)
        self.root.createPushButton.clicked.connect(self.createGraph)
        self.root.deletePushButton.clicked.connect(self.goDelete)
        self.root.openPushButton.clicked.connect(self.goOpen)
        self.root.allVarCheckBox.toggled.connect(self.selectGraphs)
        self.root.templateComboBox.currentIndexChanged.connect(self.templateChanged)

        self.root.scriptTextEdit = MultiEditor(os.path.join(self.gui.mgvDirectory, 'editorDefinitions'))
        self.root.scriptTextEdit.text.editingFinished.connect(self.scriptTextChanged)
        self.root.optionsLayout.addWidget(self.root.scriptTextEdit)
        self.root.graphKeyLineEdit.hide()
        self.root.nodeNameLineEdit.hide()
        self.root.nodeTypeComboBox.hide()

        if mode == 'automation':
            self.root.varWidget.hide()
            self.root.templateWidget.hide()
            self.root.outputWidget.show()
            self.root.allVarCheckBox.hide()
            self.root.openPushButton.hide()
            self.root.deletePushButton.hide()
            self.root.createPushButton.hide()
            self.ok = True
            self.root.scriptTextEdit.show()
            self.root.scriptWidget.show()

        if mode == 'manage':
            self.root.scriptTextEdit.hide()
            self.root.scriptWidget.hide()
            self.root.goPushButton.hide()
            self.root.outputWidget.hide()
            self.root.allVarCheckBox.show()
            self.root.varWidget.show()
            self.root.optionsLayout.addStretch()

        self.root.show()
        r = self.root.geometry()
        r.moveCenter(QtWidgets.QApplication.desktop().availableGeometry().center())
        self.root.setGeometry(r)

        self.patternChanged()
        self.auto = False
        if mode == 'automation':
            self.scriptChanged()
        if mode == 'manage':
            self.selectGraphs()

    def templateChanged(self):
        if self.auto:
            return
        new_template = self.root.templateComboBox.currentText()
        result = [x.text().split(':') for x in self.root.resultListWidget.selectedItems()]
        for x in result:
            graph_infos = mgvWrapper.getGraphInfo(self.pattern, x)
            graph_infos['project_name'] = self.pattern.project.name
            graph_infos['path'] = os.path.join(self.pattern.convertPath(x), self.pattern.convertGraphName(x)) + '.mgv'
            mgvWrapper.setNodeAttr(graph_infos, template_name=new_template)

    def createGraph(self):
        if len(self.gui.currentProject.patterns):
            self.childWindow = MgvCreateGraph(self.gui, self)
        else:
            self.gui.notify('No pattern !', 1)

    def selectGraphs(self):
        if self.auto:
            return
        self.auto = True
        clearLayout(self.root.varWidget.layout())
        result = [x.text().split(':') for x in self.root.resultListWidget.selectedItems()]
        variables = {}
        template_names = []
        if len(result):
            self.root.openPushButton.setEnabled(True)
            self.root.deletePushButton.setEnabled(True)
            self.root.allVarCheckBox.setEnabled(True)
            self.root.templateComboBox.setEnabled(True)
            self.root.openPushButton.setStyleSheet('')
            self.root.deletePushButton.setStyleSheet('')
            self.root.allVarCheckBox.setStyleSheet('')
        else:
            self.root.openPushButton.setEnabled(False)
            self.root.deletePushButton.setEnabled(False)
            self.root.allVarCheckBox.setEnabled(False)
            self.root.templateComboBox.setEnabled(False)
            self.root.templateComboBox.setStyleSheet('background-color: #555555')
            self.root.templateLabel.setStyleSheet('')
            self.root.templateComboBox.setCurrentIndex(0)
            self.root.openPushButton.setStyleSheet('color: #999999')
            self.root.deletePushButton.setStyleSheet('color: #999999')
            self.root.allVarCheckBox.setStyleSheet('color: #999999')
            
        if len(result):
            for i, x in enumerate(result):
                template_names.append(mgvWrapper.getGraphInfo(self.pattern, x)['template_name'])
            if all([x == template_names[0] for x in template_names]):
                self.root.templateComboBox.setCurrentIndex(self.root.templateComboBox.findText(template_names[0]))
                self.root.templateLabel.setStyleSheet('')
            else:
                self.root.templateComboBox.setCurrentIndex(0)
                self.root.templateLabel.setStyleSheet('color: #999999')

        for i, x in enumerate(result):
            graphvars = mgvWrapper.getGraphVars(self.pattern, x)
            for var in graphvars:
                if var['name'] not in variables:
                    variables[var['name']] = {'value': [], 'active': []}

                variables[var['name']]['value'].append(var['value'])
                variables[var['name']]['active'].append(var['active'])
        for var in variables:
            if len(variables[var]['value']) == len(result) or not self.root.allVarCheckBox.isChecked():
                h = QtWidgets.QHBoxLayout()
                c = QtWidgets.QCheckBox()
                e1 = QtWidgets.QLineEdit()
                e2 = QtWidgets.QLineEdit()
                d = QtWidgets.QPushButton()
                d.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, "icons", "trash-white.svg")))
                d.setIconSize(QtCore.QSize(16, 16))
                d.setFlat(True)
                d.setMaximumWidth(24)
                d.setStyleSheet("""QPushButton{background: transparent}QPushButton::hover{background: #663333}""")
                d.clicked.connect(lambda x=var: self.delVar(x))
                h.addWidget(c)
                h.addWidget(e1)
                h.addWidget(e2)
                h.addWidget(d)
                e1.setText(str(var))
                if len(variables[var]['value']) != len(result):
                    e1.setStyleSheet("background-color: #999999")
                if all([x == variables[var]['value'][0] for x in variables[var]['value']]):
                    e2.setText(variables[var]['value'][0])
                else:
                    e2.setStyleSheet("background-color: #999999")
                if all([x == variables[var]['active'][0] for x in variables[var]['active']]):
                    c.setChecked(variables[var]['active'][0])
                else:
                    c.setStyleSheet("""
QCheckBox::indicator:unchecked{image: url(:/icons/square-grey.svg)}
QCheckBox::indicator:checked{ image: url(:/icons/check-square-grey.svg)}
""".replace('url(:', 'url(' + self.gui.mgvDirectory))
                e1.editingFinished.connect(lambda x=var, w=e1: self.varChanged(x, w, 'name'))
                e2.editingFinished.connect(lambda x=var, w=e2: self.varChanged(x, w, 'value'))
                c.stateChanged.connect(lambda state, x=var, w=c: self.varChanged(x, w, 'active'))
                self.root.varWidget.layout().addLayout(h)
        self.root.varWidget.layout().addStretch()
        if len(result):
            b = QtWidgets.QPushButton('Add Variable')
            b.clicked.connect(self.addVar)
            self.root.varWidget.layout().insertWidget(0, b)
        self.auto = False

    def varChanged(self, name, widget, mode):
        result = [x.text().split(':') for x in self.root.resultListWidget.selectedItems()]
        for x in result:
            if mode == 'value':
                mgvWrapper.setGraphVar(self.pattern, x, name, value=widget.text())
            elif mode == 'active':
                mgvWrapper.setGraphVar(self.pattern, x, name, active=widget.isChecked())
            elif mode == 'name':
                mgvWrapper.setGraphVar(self.pattern, x, name, newname=widget.text())
        self.selectGraphs()

    def addVar(self):
        name, ok = QtWidgets.QInputDialog.getText(self.root, 'New name', 'Script name :')
        if ok:
            result = [x.text().split(':') for x in self.root.resultListWidget.selectedItems()]
            for x in result:
                mgvWrapper.setGraphVar(self.pattern, x, name, None, '', True)
            self.selectGraphs()

    def delVar(self, name):
        result = [x.text().split(':') for x in self.root.resultListWidget.selectedItems()]
        for x in result:
            vars = mgvWrapper.getGraphVars(self.pattern, x)
            for var in vars:
                if var['name'] == name:
                    mgvWrapper.deleteNode(self.pattern.project, var)

        self.selectGraphs()

    def scriptTextChanged(self):
        if not self.auto and self.ok:
            script_name = self.root.scriptComboBox.currentText()
            for x in self.gui.currentProject.batchScripts:
                if x.name == script_name:
                    x.setScript(self.root.scriptTextEdit.text.toPlainText())
                    break

    def scriptChanged(self):
        if not self.auto:
            self.auto = True
            script_name = self.root.scriptComboBox.currentText()
            self.root.scriptDelButton.setEnabled(True)
            self.root.scriptRenameButton.setEnabled(True)
            for x in self.gui.currentProject.batchScripts:
                if x.name == script_name:
                    self.root.scriptTextEdit.setPlainText(x.script)
                    break
            else:
                self.root.scriptTextEdit.setPlainText('')
                self.root.scriptDelButton.setEnabled(False)
                self.root.scriptRenameButton.setEnabled(False)
            self.auto = False

    def scriptAdd(self):
        self.auto = True
        i = 1
        basename = 'new'
        newname = basename
        while newname in [x.name for x in self.gui.currentProject.batchScripts]:
            i += 1
            newname = '%s%s' % (basename, i)
        new_batch = MgvBatchScript(project=self.gui.currentProject, name=newname)
        new_batch.create()
        self.gui.currentProject.batchScripts.append(new_batch)
        self.root.scriptComboBox.clear()
        blist = sorted([x.name for x in self.gui.currentProject.batchScripts])
        self.root.scriptComboBox.addItems(blist)
        i = blist.index(newname)
        self.auto = False
        self.root.scriptComboBox.setCurrentIndex(i)
        self.scriptChanged()

    def scriptDel(self):
        script_name = self.root.scriptComboBox.currentText()
        for x in self.gui.currentProject.batchScripts:
            if x.name == script_name:
                self.gui.currentProject.batchScripts.remove(x)
                mgvWrapper.deleteNode(x)
                break
        self.root.scriptComboBox.removeItem(self.root.scriptComboBox.currentIndex())
        self.scriptChanged()

    def scriptRename(self):
        script_name = self.root.scriptComboBox.currentText()
        text, ok = QtWidgets.QInputDialog.getText(self.root, 'New name', 'Script name :', text=script_name)
        text = str(text)
        if ok:
            if text != script_name:
                if text not in [x.name for x in self.gui.currentProject.batchScripts]:
                    for x in self.gui.currentProject.batchScripts:
                        if x.name == script_name:
                            self.auto = True
                            x.setName(text)
                            self.root.scriptComboBox.clear()
                            blist = sorted([x.name for x in self.gui.currentProject.batchScripts])
                            self.root.scriptComboBox.addItems(blist)
                            i = blist.index(text)
                            self.root.scriptComboBox.setCurrentIndex(i)
                            self.auto = False
                            break
                else:
                    QtWidgets.QMessageBox.information(self.root, 'Error', '%s already exists' % text)

    def toggleGraphKey(self):
        self.root.graphKeyLineEdit.setVisible(self.root.graphKeyCheckBox.isChecked())
        self.search()

    def toggleNodeName(self):
        self.root.nodeNameLineEdit.setVisible(self.root.nodeNameCheckBox.isChecked())
        self.search()

    def toggleNodeType(self):
        self.root.nodeTypeComboBox.setVisible(self.root.nodeTypeCheckBox.isChecked())
        self.search()

    def patternChanged(self):
        self.pattern = [x for x in self.gui.currentProject.patterns
                        if x.getName() == self.root.patternComboBox.currentText()][0]
        self.root.templateComboBox.clear()
        self.root.templateComboBox.addItems([''] + [x.name for x in self.pattern.templates])
        self.search()

    def search(self):
        if self.search_thread:
            self.search_thread.stop = True
            self.search_thread.wait()
        self.root.progressBar.show()
        self.root.progressBar.setValue(0)
        clearList(self.root.resultListWidget)
        self.search_thread = MgvSearchThread(self.pattern, self.root.graphKeyCheckBox.isChecked(),
                                             self.root.nodeNameCheckBox.isChecked(),
                                             self.root.nodeTypeCheckBox.isChecked(),
                                             self.root.graphKeyLineEdit.text().strip(),
                                             self.root.nodeNameLineEdit.text().strip(),
                                             self.root.nodeTypeComboBox.currentText().strip())
        self.search_thread.signal.connect(self.receive)
        self.search_thread.start()

    def receive(self, name, percent):
        self.gui.app.processEvents()
        if name:
            self.auto = True
            self.root.resultListWidget.addItem(name)
            self.root.resultListWidget.findItems(name, QtCore.Qt.MatchExactly)[0].setSelected(True)
            self.auto = False
        else:
            self.root.progressBar.setValue(percent)
            if percent == 100:
                self.root.progressBar.hide()
                self.search_thread = None
                self.selectGraphs()

    def goDelete(self):
        result = [x.text().split(':') for x in self.root.resultListWidget.selectedItems()]
        self.root.goPushButton.hide()
        self.root.goProgressBar.show()
        self.root.goProgressBar.setValue(0)
        out = QtWidgets.QMessageBox.question(self.root, 'Warning', 'Delete graphs folders as well ?',
                                             QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                             QtWidgets.QMessageBox.No)
        deleteFolder = (out == QtWidgets.QMessageBox.Yes)
        for i, x in enumerate(result):
            mgvWrapper.deleteGraph(self.pattern, x)
            if deleteFolder:
                file_path = self.pattern.convertPath(x)
                if len(file_path) > 3 and os.path.exists(file_path):
                    try:
                        shutil.rmtree(file_path)
                    except (IOError, OSError):
                        pass
            self.root.goProgressBar.setValue(((i + 1) * 100) / len(result))
            self.gui.app.processEvents()
        self.root.goProgressBar.hide()
        self.search()
        self.gui.createOpenMenu()

    def goOpen(self):
        result = [x.text().split(':') for x in self.root.resultListWidget.selectedItems()]
        self.root.goPushButton.hide()
        self.root.goProgressBar.show()
        self.root.goProgressBar.setValue(0)
        for i, x in enumerate(result):
            self.gui.openGraph([self.gui.currentProject.name, self.pattern.name]+x)
            self.root.goProgressBar.setValue(((i + 1) * 100) / len(result))
            self.gui.app.processEvents()
            self.root.goProgressBar.hide()

    def go(self):
        if self.batch_thread:
            return
        self.root.outputTextEdit.setPlainText('')
        result = [x.text().split(':') for x in self.root.resultListWidget.selectedItems()]
        self.root.goPushButton.hide()
        self.root.goProgressBar.show()
        self.root.goProgressBar.setValue(0)

        script = self.root.scriptTextEdit.text.toPlainText()
        self.root.outputTextEdit.clear()
        self.root.killButton.show()
        self.batch_thread = MgvBatchThread(script, result, self.pattern.project.name, self.pattern.getName(),
                                           self.gui.mgvDirectory)
        self.batch_thread.sendSignal.connect(self.receiveFromBatch)
        self.batch_thread.start()

    def kill(self):
        self.batch_thread.killSignal.emit()

    def receiveFromBatch(self, i, value):
        if i == 0:
            if value != "end":
                self.root.goProgressBar.setValue(int(value))
            else:
                self.root.goPushButton.show()
                self.root.goProgressBar.hide()
                self.root.killButton.hide()
                self.batch_thread = None
        else:
            self.root.outputTextEdit.append(value)


class MgvBatchThread(QtCore.QThread):
    """Separated thread that execute a batchscript."""
    sendSignal = QtCore.Signal(int, str)
    killSignal = QtCore.Signal()

    def __init__(self, script, result, project_name, pattern_name, mgvpath):
        QtCore.QThread.__init__(self)
        self.script = script
        self.result = sorted(result, key=lambda k: ':'.join(k))
        self.project_name = project_name
        self.pattern_name = pattern_name
        self.mgvpath = mgvpath
        self.stop = False
        self.killSignal.connect(self.interrupt)

        class TextEdit(object):
            def __init__(self, thread):
                self.thread = thread
                self.process = None

            def append(self, text):
                self.thread.sendSignal.emit(1, text)

        self.textedit = TextEdit(self)

    def run(self):
        for i, x in enumerate(self.result):
            if self.stop:
                break
            self.sendSignal.emit(0, str(((i + 1) * 100) / len(self.result)))
            self.textedit.append('<font color=green>########### %s ###########</font>' % ':'.join(x))
            graph_script = """import os, sys
sys.path.insert(0,"%s")
import mgvApi
os.environ["MGVPROJECTNAME"] = "%s"
os.environ["MGVPATTERNNAME"] = "%s"
os.environ["MGVGRAPHKEYS"] = "%s"
current_graph = mgvApi.getCurrentGraph()
""" % (self.mgvpath, self.project_name, self.pattern_name, ':'.join(x)) + self.script + "\nExecute(current_graph)"
            ExeScript(graph_script, self.textedit, env=dict(os.environ), line_offset=5)
        self.sendSignal.emit(0, "end")

    def interrupt(self):
        self.stop = True
        if not sys.platform.startswith('win'):
            os.killpg(os.getpgid(self.textedit.process.pid), signal.SIGKILL)
        else:
            os.popen('TASKKILL /PID %s /F /T' % self.textedit.process.pid)
        self.textedit.append('<font color=red><i>killed</i></font>')


class MgvCreateGraph(object):
    """Create graph UI."""
    def __init__(self, gui, manageGui):
        self.gui = gui
        self.manageGui = manageGui
        mainUIPath = os.path.join(self.gui.mgvDirectory, 'UI', 'createGraph.ui')
        self.root = QtCompat.loadUi(mainUIPath)
        iconPath = os.path.join(self.gui.mgvDirectory, 'icons', 'mgvIcon.svg')
        self.sheet = None
        self.book = None
        self.keys = []

        self.root.setWindowIcon(QtGui.QIcon(iconPath))
        self.root.fileButton.setIcon(
            QtGui.QIcon(os.path.join(self.gui.mgvDirectory, "icons", "folder.svg")))
        self.root.fileButton.setIconSize(QtCore.QSize(16, 16))
        self.root.addKeyButton.setIcon(
            QtGui.QIcon(os.path.join(self.gui.mgvDirectory, "icons", "plus.svg")))
        self.root.addKeyButton.setIconSize(QtCore.QSize(16, 16))
        self.root.originalButton.setIcon(
            QtGui.QIcon(os.path.join(self.gui.mgvDirectory, "icons", "eye.svg")))
        self.root.originalButton.setIconSize(QtCore.QSize(16, 16))

        self.root.patternComboBox.addItems([x.getName() for x in self.gui.currentProject.patterns])
        self.root.patternComboBox.currentIndexChanged.connect(self.fillKeysWidget)
        self.root.startSpinBox.valueChanged.connect(self.preview)
        self.root.stopSpinBox.valueChanged.connect(self.preview)
        self.root.addKeyButton.clicked.connect(self.addKey)

        self.root.createPushButton.clicked.connect(self.create)
        self.root.originalButton.pressed.connect(self.viewOriginal)
        self.root.originalButton.released.connect(self.viewPreview)
        self.root.fileButton.clicked.connect(self.chooseFile)
        self.root.sheetComboBox.currentIndexChanged.connect(self.sheetChanged)
        self.fields = []
        self.mode = 'preview'
        self.keys = []
        self.dico = {}
        self.pattern = None
        self.fillKeysWidget()
        self.root.setStyleSheet(self.gui.style)
        self.root.patternLabel.setStyleSheet('color: #999999; font: italic')
        self.root.originalButton.setStyleSheet('QPushButton::pressed{background-color: transparent}')
        self.root.progressBar.hide()
        self.root.show()
        r = self.root.geometry()
        r.moveCenter(QtWidgets.QApplication.desktop().availableGeometry().center())
        self.root.setGeometry(r)
        self.root.setModal(True)

    def viewOriginal(self):
        self.mode = 'original'
        self.preview()

    def viewPreview(self):
        self.mode = 'preview'
        self.preview()

    def fillKeysWidget(self):
        clearLayout(self.root.keysLayout)
        self.pattern = [x for x in self.gui.currentProject.patterns
                        if x.getName() == self.root.patternComboBox.currentText()][0]
        self.root.patternLabel.setText(self.pattern.pattern)
        self.keys = sorted(list(set(re.findall('\${[0-9]*}', self.pattern.pattern))))
        self.dico = {}
        for key in self.keys:
            self.dico[key] = QtWidgets.QLineEdit()
            self.root.keysLayout.addRow('key %s:   ' % key, self.dico[key])

        self.root.templateComboBox.clear()
        self.root.templateComboBox.addItems([''] + [x.getName() for x in self.pattern.templates])

    def getGraphTemplateName(self):
        template = None
        template_name = self.root.templateComboBox.currentText()
        if len(template_name):
            for x in self.pattern.templates:
                if x.getName() == template_name:
                    template = x
                    break
        templateName = ''
        if template:
            templateName = template.name
        return templateName

    def createFromFile(self):
        if self.sheet:
            self.root.progressBar.setValue(0)
            self.root.progressBar.show()
            self.root.createPushButton.hide()
            templateName = self.getGraphTemplateName()
            start = self.root.startSpinBox.value()
            stop = self.root.stopSpinBox.value()

            for y in range(start, stop+1):
                self.root.progressBar.setValue((y+1-start)*100 / (stop-start+1))
                self.gui.app.processEvents()
                keys = [None] * len(self.keys)
                properties = {}
                for field in self.fields:
                    value = '%s' % self.sheet.cell(y-1, field['column']-1).value
                    oldvalue = value

                    if field['field'].startswith('Key_'):
                        try:
                            if len(field['sep']):
                                value = value.split(field['sep'])
                                if len(value) > field['index']:
                                    value = value[field['index']]
                                else:
                                    value = value[-1]
                            if ':' in field['range']:
                                a = field['range'].split(':')[0]
                                b = field['range'].split(':')[1]
                                a = 0 if not len(a) else int(a)
                                b = len(value) if not len(b) else int(b)
                                value = value[a:b]
                        except Exception as e:
                            print('error', e)
                            value = oldvalue
                    else:
                        properties[field['prop']] = value
                    if field['field'].startswith('Key_'):
                        index = int(field['field'][4:])
                        keys[index] = value
                path = []
                for key in keys:
                    if key:
                        path.append(key)
                    else:
                        break
                exists = mgvWrapper.graphExists(self.pattern, path)
                if not exists:
                    g = MgvGraph(pattern=self.pattern, name=self.pattern.convertGraphName(path),
                                 path=path, template_name=templateName, load=False)
                    g.create()
                    for p in properties:
                        g.setEnv(name=p, value=properties[p])

            self.root.progressBar.setValue(100)
            self.gui.app.processEvents()
            self.root.progressBar.hide()
            self.root.createPushButton.show()
            self.gui.createOpenMenu()
            self.manageGui.search()
            self.root.close()

    def create(self):
        if self.root.tabWidget.currentIndex() == 2:
            self.createFromFile()
            return
        template_name = self.root.templateComboBox.currentText()
        if self.root.tabWidget.currentIndex() == 0:
            graphpath = [self.dico[x].text() for x in self.keys if len(self.dico[x].text())]
            graphname = self.pattern.convertGraphName(graphpath)
            if not mgvWrapper.graphExists(self.pattern, graphpath):
                MgvGraph(pattern=self.pattern, path=graphpath, name=graphname, template_name=template_name).create()
                self.gui.createOpenMenu()
                self.manageGui.search()
                self.root.close()
            else:
                QtWidgets.QMessageBox.information(self.root, 'Error', 'Graph already exists')
        else:
            names = self.root.multiLineEdit.text().replace(', ', ' ').replace(';', ' ').split()
            namesok = []
            error = ''
            for name in names:
                if len(name):
                    if not len(name.split(':')) == len(self.keys):
                        error += 'Bad name %s: keys not matching\n' % name
                        continue
                    graphpath = name.split(':')
                    if mgvWrapper.graphExists(self.pattern, graphpath):
                        error += 'Graph already exists: %s\n' % name
                        continue
                    namesok.append(name)

            go = True
            if len(error):
                go = False
                result = QtWidgets.QMessageBox.question(self.root, 'Errors',
                                                        'There is some errors :\n\n%s\n\nContinue ?' % error,
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                        QtWidgets.QMessageBox.No)
                if result == QtWidgets.QMessageBox.Yes:
                    go = True
            if go:
                self.root.progressBar.setValue(0)
                self.root.progressBar.setMaximum(len(namesok)-1)
                self.root.progressBar.show()
                self.root.createPushButton.hide()
                for i, name in enumerate(namesok):
                    self.root.progressBar.setValue(i)
                    MgvGraph(pattern=self.pattern, path=name.split(':'), template_name=template_name,
                             name=self.pattern.convertGraphName(name.split(':')), load=False).create()
                self.gui.createOpenMenu()
                self.root.progressBar.hide()
                self.root.createPushButton.show()
                self.manageGui.search()
                self.root.close()

    def chooseFile(self):
        path = self.pattern.pattern
        c = 0
        while not os.path.exists(path) and c < 30:
            path = path.split(os.sep)[:-1]
            path = os.sep.join(path)
            c += 1
        out = QtWidgets.QFileDialog.getOpenFileName(self.root, "Select a file", path, filter="Excel File (*.xls *.xlsx)")[0]
        if len(out):
            self.root.fileLineEdit.setText(out)
            import xlrd
            self.book = xlrd.open_workbook(self.root.fileLineEdit.text().strip())
            self.sheet = None
            self.root.sheetComboBox.clear()
            self.root.sheetComboBox.addItems(self.book.sheet_names())

            self.preview()

    def sheetChanged(self):
        name = self.root.sheetComboBox.currentText()
        if name in self.book.sheet_names():
            self.sheet = self.book.sheet_by_name(name)
            Y = self.sheet.nrows
            self.root.previewTableWidget.clear()
            self.root.previewTableWidget.setRowCount(Y)
            self.root.stopSpinBox.setValue(Y)
            self.preview()

    def preview(self):
        if not self.sheet:
            return
        # liste : [[col, field], ...]
        previewColumns = []
        for x in range(self.sheet.ncols):
            found = False
            for field in self.fields:
                if x + 1 == field['column']:
                    previewColumns.append([x, field])
                    found = True
            if not found:
                previewColumns.append([x, None])
        self.root.previewTableWidget.setColumnCount(len(previewColumns))

        for i, previewColumn in enumerate(previewColumns):
            hitem = QtWidgets.QTableWidgetItem(str(previewColumn[0]+1))
            self.root.previewTableWidget.setHorizontalHeaderItem(i, hitem)
            field = previewColumn[1]
            for y in range(self.sheet.nrows):
                col = "#CCCCCC"
                value = '%s' % self.sheet.cell(y, previewColumn[0]).value
                oldvalue = value
                if field:
                    col = field['color']
                    if field['field'] == 'Variable':
                        pass
                    else:
                        try:
                            if len(field['sep']):
                                value = value.split(field['sep'])
                                if len(value) > field['index']:
                                    value = value[field['index']]
                                else:
                                    value = value[-1]

                            a = field['range'].split(':')[0]
                            b = field['range'].split(':')[1]
                            a = 0 if not len(a) else int(a)
                            b = len(value) if not len(b) else int(b)
                            value = value[a:b]
                        except Exception as e:
                            print('error', e)
                            value = oldvalue
                            col = "#FF0000"

                item = QtWidgets.QTableWidgetItem(value)
                if self.root.startSpinBox.value() <= y + 1 <= self.root.stopSpinBox.value() and self.mode == 'preview':
                    item.setForeground(QtGui.QBrush(QtGui.QColor(opposite(col))))
                    item.setBackground(QtGui.QBrush(QtGui.QColor(col)))
                else:
                    item.setForeground(QtGui.QBrush(QtGui.QColor('#CCCCCC')))
                    item.setBackground(QtGui.QBrush(QtGui.QColor('#333333')))
                    item.setText(oldvalue)

                self.root.previewTableWidget.setItem(y, i, item)

    def addKey(self):
        layout = QtWidgets.QHBoxLayout()
        button = QtWidgets.QPushButton()
        button.setFlat(True)
        button.setMaximumHeight(24)
        button.setMaximumWidth(24)
        combo = QtWidgets.QComboBox()
        liste = ['Key_%s' % x for x in range(len(self.keys))]
        liste.append('Variable')
        combo.addItems(liste)
        label = 'Key_0'
        for i in range(len(self.keys)):
            if ('Key_%s' % i) in [x['field'] for x in self.fields]:
                if i < len(self.keys) - 1:
                    label = 'Key_%s' % (i + 1)
                else:
                    label = 'Variable'

        combo.setCurrentIndex(liste.index(label))
        col = QtWidgets.QSpinBox()
        col.setMinimum(1)
        randColor = QtGui.QColor(random.uniform(0, 255), random.uniform(0, 255), random.uniform(0, 255)).name()
        prop = QtWidgets.QLineEdit()
        sep = QtWidgets.QLineEdit()
        ind = QtWidgets.QSpinBox()
        ind.setMinimum(-20)
        ind.setMaximum(20)
        ran = QtWidgets.QLineEdit()
        ran.setText(':')
        closeButton = QtWidgets.QPushButton()
        closeButton.setMaximumHeight(24)
        closeButton.setMaximumWidth(24)
        closeButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, "icons", "trash-2.svg")))
        closeButton.setIconSize(QtCore.QSize(16, 16))

        button.setToolTip("Column color")
        combo.setToolTip("Type of data to extract")
        col.setToolTip("Column number")
        sep.setToolTip("Word separator")
        ind.setToolTip("Index of word")
        ran.setToolTip("Range of characters in the choosen word")
        prop.setToolTip("Graph variable name")

        layout.addWidget(button)
        layout.addWidget(combo)
        layout.addWidget(col)
        layout.addWidget(prop)
        layout.addWidget(sep)
        layout.addWidget(ind)
        layout.addWidget(ran)
        layout.addWidget(closeButton)
        if label == 'Variable':
            sep.hide()
            ind.hide()
            ran.hide()
            prop.show()
        else:
            sep.show()
            ind.show()
            ran.show()
            prop.hide()
        widgets = {'button': button, 'combo': combo, 'prop': prop, 'col': col, 'sep': sep, 'ind': ind, 'ran': ran}
        self.root.keysWidget.layout().addLayout(layout)
        field = {'field': label, 'column': 1, 'prop': '', 'sep': '', 'index': 0, 'range': ':', 'color': randColor}
        button.setStyleSheet("QPushButton{background-color: %s} QPushButton::hover{border-radius:6px}" % field['color'])

        combo.currentIndexChanged[str].connect(lambda t, f=field, w=widgets: self.setField(field=f, name='field',
                                                                                           value=t, widgets=w))
        col.valueChanged.connect(lambda t, f=field: self.setField(field=f, name='column', value=t))
        prop.textChanged.connect(lambda t, f=field: self.setField(field=f, name='prop', value=t))
        sep.textChanged.connect(lambda t, f=field: self.setField(field=f, name='sep', value=t))
        ind.valueChanged.connect(lambda t, f=field: self.setField(field=f, name='index', value=t))
        ran.textChanged.connect(lambda t, f=field: self.setField(field=f, name='range', value=t))
        button.clicked.connect(lambda b=button, f=field: self.colorClick(b, f))
        closeButton.clicked.connect(lambda l=layout, f=field: self.delField(l, f))

        self.fields.append(field)
        self.preview()

    def delField(self, layout, field):
        self.fields.remove(field)
        clearLayout(layout)

    def colorClick(self, button, field):
        dialog = QtGui.QColorDialog(self.root)
        dialog.setModal(1)
        dialog.setCurrentColor(QtGui.QColor(field['color']))
        if dialog.exec_():
            button.setStyleSheet("background-color: %s" % dialog.selectedColor().name())
            self.setField(field=field, name='color', value=dialog.selectedColor().name())

    def setField(self, field=None, name='', value='', widgets=None):
        field[name] = value
        if widgets:
            if name == 'field':
                if value == 'Variable':
                    widgets['sep'].hide()
                    widgets['ind'].hide()
                    widgets['ran'].hide()
                    widgets['prop'].show()
                else:
                    widgets['sep'].show()
                    widgets['ind'].show()
                    widgets['ran'].show()
                    widgets['prop'].hide()

        self.preview()


class MgvDownload(object):
    """Transfert types, batchscripts and widgets between projects UI."""
    def __init__(self, gui):
        self.gui = gui
        self.project = self.gui.currentProject
        mainUIPath = os.path.join(self.gui.mgvDirectory, 'UI', 'share.ui')
        self.root = QtCompat.loadUi(mainUIPath)
        iconPath = os.path.join(self.gui.mgvDirectory, 'icons', 'mgvIcon.svg')
        self.root.setWindowIcon(QtGui.QIcon(iconPath))
        self.filtered_types = []
        self.currentType = None
        self.childWindow = None
        self.timer = None

        self.root.actionWidget.hide()
        self.actionEdit = MultiEditor(os.path.join(self.gui.mgvDirectory, 'editorDefinitions'))
        self.actionEdit.setReadOnly(True)
        self.root.actionWidget.layout().insertWidget(1, self.actionEdit)

        softwares = [x.to_dict()['software'].capitalize() for x in store.collection('TYPE').get()]
        softwares = [x for x in softwares if len(x.strip())]
        softwares = sorted(list(set(softwares)))
        self.root.softwareComboBox.addItems(softwares)
        self.root.importPushButton.setEnabled(False)

        self.root.listWidget.currentRowChanged.connect(self.selectType)
        self.root.deletePushButton.clicked.connect(self.deleteType)
        self.root.softwareComboBox.currentIndexChanged.connect(self.filterTypes)
        self.root.nameLineEdit.returnPressed.connect(self.filterTypes)
        self.root.descriptionLineEdit.returnPressed.connect(self.filterTypes)
        self.root.showActionsPushButton.clicked.connect(self.showActions)
        self.root.hideActionsPushButton.clicked.connect(self.hideActions)
        self.root.actionComboBox.currentIndexChanged.connect(self.showAction)
        self.root.importPushButton.clicked.connect(self.go)
        self.root.refreshPushButton.clicked.connect(self.filterTypes)

        self.root.setStyleSheet(self.gui.style)
        self.root.dateLabel.setStyleSheet('color: #666666')
        self.root.userLabel.setStyleSheet('color: #666666')
        self.root.refreshPushButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'refresh-cw.svg')))
        self.root.refreshPushButton.setIconSize(QtCore.QSize(16, 16))

        self.root.show()
        r = self.root.geometry()
        r.moveCenter(QtWidgets.QApplication.desktop().availableGeometry().center())
        self.root.setGeometry(r)
        self.root.setModal(True)
        self.root.softwareComboBox.setFocus(QtCore.Qt.MouseFocusReason)

        self.filterTypes()
        self.selectType(-1)

    def filterTypes(self):
        clearList(self.root.listWidget)
        self.filtered_types = []
        software = self.root.softwareComboBox.currentText().lower()
        name = self.root.nameLineEdit.text().lower()
        description = self.root.descriptionLineEdit.text().lower()

        doc_ref = store.collection('TYPE')
        docs = doc_ref.get()
        for doc in docs:
            dico = doc.to_dict()
            if software != 'all softwares':
                if software != dico['software'].lower():
                    continue
            if len(name):
                if name not in dico['name'].lower():
                    continue
            if len(description):
                if description not in dico['help'].lower():
                    continue
            self.filtered_types.append(doc)

        self.filtered_types = sorted(self.filtered_types, key=lambda k: k.to_dict()['name'].lower())
        for x in self.filtered_types:
            x = x.to_dict()
            if x['shape'] == 'Image' and len(x['image']):
                by = QtCore.QByteArray.fromBase64(str(x['image']))
                image = QtGui.QImage.fromData(by)
                pixmap = QtGui.QPixmap.fromImage(image)
                pixmap.scaledToWidth(64)
                icon = QtGui.QIcon(pixmap)
                item = QtWidgets.QListWidgetItem(icon, x['name'])
            else:
                item = QtWidgets.QListWidgetItem(x['name'])
            self.root.listWidget.addItem(item)

    def selectType(self, i):
        if i > -1:
            self.currentType = self.filtered_types[i]
            x = self.currentType.to_dict()
            self.root.nameLabel.setText(x['name'])
            self.root.dateLabel.setText('Uploaded at ' + x['date'])
            self.root.userLabel.setText('By ' + x['author'])
            self.root.descriptionTextEdit.setText(markdown(x['help'].replace('\n', '<br>')))
            if x['database_id'] == self.gui.database_id.split(':')[-1]:
                self.root.deletePushButton.show()
            else:
                self.root.deletePushButton.hide()
            if self.root.actionWidget.isVisible():
                self.readActions()
            self.root.importPushButton.setEnabled(True)
        else:
            self.currentType = None
            self.hideActions()
            self.root.deletePushButton.hide()
            self.root.nameLabel.setText('')
            self.root.dateLabel.setText('')
            self.root.userLabel.setText('')
            self.root.descriptionTextEdit.setText('')
            self.root.importPushButton.setEnabled(False)

    def deleteType(self):
        result = QtWidgets.QMessageBox.question(self.root, 'Warning',
                                                'Are you sure to delete this type ?',
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            self.currentType.reference.delete()
            self.filterTypes()

    def showActions(self):
        self.root.actionWidget.show()
        self.root.showActionsPushButton.hide()
        self.readActions()

    def hideActions(self):
        self.root.actionWidget.hide()
        self.root.showActionsPushButton.show()

    def readActions(self):
        if self.currentType:
            x = self.currentType.to_dict()
            last_version = sorted(x['versions'], key=lambda k: k['id'])[-1]
            self.root.actionComboBox.clear()
            self.root.actionComboBox.addItems(['--- ACTIONS ---'] +
                                              [y['name'] for y in last_version['actions']] +
                                              ['--- PARAMETERS ---'] +
                                              [y['name'] for y in last_version['parameters']])

    def showAction(self):
        x = self.currentType.to_dict()
        last_version = sorted(x['versions'], key=lambda k: k['id'])[-1]
        index = self.root.actionComboBox.currentIndex()
        if 0 < index <= len(last_version['actions']):
            action_name = self.root.actionComboBox.currentText()
            action = [y for y in last_version['actions'] if y['name'] == action_name][0]
            self.actionEdit.setPlainText(action['command'])
        elif index > len(last_version['actions']) + 1:
            param_name = self.root.actionComboBox.currentText()
            param = [y for y in last_version['parameters'] if y['name'] == param_name][0]
            self.actionEdit.setPlainText(param['default'])
        else:
            self.actionEdit.setPlainText('')

    def go(self):
        x = self.currentType.to_dict()
        new = MgvType.getFromJson(x)
        new.project = self.project
        self.project.types.append(new)
        new.create()
        self.gui.icons.refreshTypes()

        splashDialog(self, self.gui.root, self.gui.style, 'Type %s imported' % x['name'], 600)


class MgvTransfert(object):
    """Transfert types, batchscripts and widgets between projects UI."""
    def __init__(self, gui):
        self.gui = gui
        self.project = self.gui.currentProject
        mainUIPath = os.path.join(self.gui.mgvDirectory, 'UI', 'transfert.ui')
        self.root = QtCompat.loadUi(mainUIPath)
        iconPath = os.path.join(self.gui.mgvDirectory, 'icons', 'mgvIcon.svg')
        project_names = mgvWrapper.getProjectNames()
        self.root.setWindowIcon(QtGui.QIcon(iconPath))
        self.root.addButton.setIcon(QtGui.QIcon(os.path.join(gui.mgvDirectory, 'icons', 'arrow-right-circle.svg')))
        self.root.removeButton.setIcon(QtGui.QIcon(os.path.join(gui.mgvDirectory, 'icons', 'arrow-left-circle.svg')))
        self.root.addButton.setIconSize(QtCore.QSize(32, 32))
        self.root.removeButton.setIconSize(QtCore.QSize(32, 32))
        self.root.setStyleSheet(self.gui.style)
        self.root.projectComboBox.addItems(project_names)
        self.root.projectComboBox.currentIndexChanged.connect(self.changeProject)
        self.root.addButton.clicked.connect(self.add)
        self.root.removeButton.clicked.connect(self.remove)
        self.root.importButton.clicked.connect(self.importElements)
        self.root.exportButton.clicked.connect(self.exportElements)
        self.root.shareButton.clicked.connect(self.shareElements)
        self.root.pathButton.clicked.connect(self.getPath)
        self.changeProject()
        self.childWindow = None
        self.timer = None
        self.root.show()
        r = self.root.geometry()
        r.moveCenter(QtWidgets.QApplication.desktop().availableGeometry().center())
        self.root.setGeometry(r)
        self.root.setModal(True)

    def getPath(self):
        result = QtWidgets.QFileDialog.getOpenFileName(self.root, 'Get Type File', '', '*.json')
        if result[0]:
            self.root.importListWidget.addItem('<FILE>'+result[0])

    def add(self):
        liste = [self.root.importListWidget.item(x).text() for x in range(self.root.importListWidget.count())]
        if self.root.typeTabWidget.currentIndex() == 0:
            for x in self.root.typesListWidget.selectedItems():
                path = '<TYPE>' + self.root.projectComboBox.currentText() + ' / ' + x.text()
                if path not in liste:
                    self.root.importListWidget.addItem(path)
            self.root.typesListWidget.clearSelection()
        if self.root.typeTabWidget.currentIndex() == 1:
            for x in self.root.hudListWidget.selectedItems():
                path = '<HUD>' + self.root.projectComboBox.currentText() + ' / ' + x.text()
                if path not in liste:
                    self.root.importListWidget.addItem(path)
            self.root.hudListWidget.clearSelection()
        if self.root.typeTabWidget.currentIndex() == 2:
            for x in self.root.batchListWidget.selectedItems():
                path = '<BATCHSCRIPT>' + self.root.projectComboBox.currentText() + ' / ' + x.text()
                if path not in liste:
                    self.root.importListWidget.addItem(path)
            self.root.batchListWidget.clearSelection()

    def remove(self):
        for item in reversed(self.root.importListWidget.selectedItems()):
            self.root.importListWidget.takeItem(self.root.importListWidget.row(item))

    def changeProject(self, i=None):
        clearList(self.root.typesListWidget)
        clearList(self.root.hudListWidget)
        clearList(self.root.batchListWidget)
        project = MgvProject.Project(self.root.projectComboBox.currentText())
        if project:
            self.root.typesListWidget.addItems(sorted([x.getName() for x in project.getTypes()]))
            self.root.hudListWidget.addItems(sorted([x.getName() for x in project.getHuds()]))
            self.root.batchListWidget.addItems(sorted([x.name for x in project.batchScripts]))

    def importElements(self):
        errors = ''
        liste = [self.root.importListWidget.item(x).text() for x in range(self.root.importListWidget.count())]
        for x in liste:
            t = x.split('<')[1].split('>')[0]
            x = x.split('>')[-1]
            if ' / ' in x:
                projName, typeName = x.split(' / ')
                if t == 'TYPE':
                    if typeName not in [x.getName() for x in self.project.getTypes()]:
                        t = mgvWrapper.getType(projName, typeName)
                        t.project = self.project
                        t.create()
                    else:
                        errors += '%s already exists !\n' % typeName
                if t == 'HUD':
                    if typeName not in [x.getName() for x in self.project.getHud()]:
                        t = mgvWrapper.getHud(projName, typeName)
                        t.create()
                    else:
                        errors += '%s already exists !\n' % typeName
                if t == 'BATCHSCRIPT':
                    if typeName not in [x.name for x in self.project.batchScripts]:
                        proj = MgvProject.Project(projName)
                        if proj:
                            for projb in proj.batchScripts:
                                if projb.name == typeName:
                                    new_batch = MgvBatchScript(project=self.gui.currentProject, name=typeName,
                                                               script=projb.script, users=projb.users,
                                                               pattern=projb.pattern, template=projb.template)
                                    new_batch.create()
                                    self.gui.currentProject.batchScripts.append(new_batch)
                    else:
                        errors += '%s already exists !\n' % typeName
            else:
                root = None
                try:
                    with open(x) as fid:
                        root = json.load(fid)
                except IOError:
                    errors += '%s : json error !\n' % x
                for obj in root:
                    if obj['code'] == 'Type':
                        t = MgvType.getFromJson(obj)
                        t.project = self.project
                        t.create()
                    elif obj['code'] == 'Hud':
                        w = MgvHud.getFromJson(obj)
                        w.project = self.project
                        w.create()
                    elif obj['code'] == 'BatchScript':
                        new_batch = MgvBatchScript(project=self.project, name=obj['name'],
                                                   script=obj['script'], users=obj['users'],
                                                   pattern=obj['pattern'], template=obj['template'])
                        new_batch.create()
                        self.project.batchScripts.append(new_batch)

        self.project.readTypes()
        self.gui.icons.refreshTypes()
        for graphview in [self.gui.root.graphTab.widget(x) for x in range(self.gui.root.graphTab.count())]:
            for node in graphview.graph.nodes:
                for typ in self.project.types:
                    if node.type.uuid == typ.uuid:
                        node.type = typ
                        node._checkType()
        if len(errors):
            self.childWindow = QtWidgets.QMessageBox(self.root)
            self.childWindow.setIcon(QtWidgets.QMessageBox.Critical)
            self.childWindow.setWindowTitle('Error')
            self.childWindow.setText(errors)
            self.childWindow.open()
        else:
            self.root.close()

    def exportElements(self):
        liste = [self.root.importListWidget.item(x).text() for x in range(self.root.importListWidget.count())]
        json_list = []
        for x in liste:
            if ' / ' in x:
                t = x.split('<')[1].split('>')[0]
                x = x.split('>')[-1]
                project_name, type_name = x.split(' / ')
                if t == 'TYPE':
                    new_type = mgvWrapper.getType(project_name, type_name)
                    json_list.append(new_type.getJson())
                if t == 'HUD':
                    new_hud = mgvWrapper.getHud(project_name, type_name)
                    json_list.append(new_hud.getJson())
                if t == 'BATCHSCRIPT':
                    new_batch = mgvWrapper.getBatchScript(project_name, type_name)
                    json_list.append(new_batch.getJson())

        result = QtWidgets.QFileDialog.getSaveFileName(self.root, 'Export', '', selectedFilter='*.json')
        if result[0]:
            try:
                with open(result[0], 'w') as fid:
                    fid.write(json.dumps(json_list, sort_keys=True, indent=4))
            except IOError:
                self.gui.notify("Can't create %s !" % result[0], 1)

    def shareElements(self):
        liste = [self.root.importListWidget.item(x).text() for x in range(self.root.importListWidget.count())]
        text = "Types " if len(liste) > 1 else "Type "
        for x in liste:
            if ' / ' in x:
                t = x.split('<')[1].split('>')[0]
                x = x.split('>')[-1]
                project_name, type_name = x.split(' / ')
                element = None
                if t == 'TYPE':
                    new_type = mgvWrapper.getType(project_name, type_name)
                    element = new_type.getJson()
                    element['linkWith'] = ''
                if t == 'HUD':
                    new_hud = mgvWrapper.getHud(project_name, type_name)
                    element = new_hud.getJson()
                if t == 'BATCHSCRIPT':
                    new_batch = mgvWrapper.getBatchScript(project_name, type_name)
                    element = new_batch.getJson()
                if element:
                    element['author'] = self.gui.user
                    element['date'] = time.strftime("%d/%m/%y %H:%M", time.gmtime())
                    self.upload(t, element)
                text = '%s %s,' % (text, element['name'])
        text = '%s shared.' % text[:-1]

        splashDialog(self, self.gui.root, self.gui.style, text, 600)

    def upload(self, mode, element):
        element['database_id'] = self.gui.database_id.split(':')[-1]
        doc_ref = store.collection(mode)
        try:
            # search existing
            docs = doc_ref.where(u'database_id', u'==', element['database_id']).get()
            for doc in docs:
                if doc.to_dict()['name'] == element['name']:
                    result = QtWidgets.QMessageBox.question(self.root, 'Warning',
                                                            'You have already uploaded a %s of the name %s,\n\nReplace it ?' % (mode, element['name']),
                                                            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                            QtWidgets.QMessageBox.No)
                    if result == QtWidgets.QMessageBox.Yes:
                        doc_ref.document(doc.id).update(element)
                        break
            else:
                doc_ref.add(element)
        except credentials.google.api_core.exceptions.ServiceUnavailable:
            splashDialog(self, self.gui.root, self.gui.style, "Can't connect to cloud database", 600)


class MgvHudsSettings(object):
    """Hud UI editor."""
    def __init__(self, gui, project):
        self.gui = gui
        self.project = project
        self.huds = [x._dup() for x in self.project.huds]
        mainUIPath = os.path.join(self.gui.mgvDirectory, 'UI', 'huds.ui')
        self.root = QtCompat.loadUi(mainUIPath)
        iconPath = os.path.join(self.gui.mgvDirectory, 'icons', 'mgvIcon.svg')
        self.root.setWindowIcon(QtGui.QIcon(iconPath))
        self.scriptEdit = MultiEditor(os.path.join(self.gui.mgvDirectory, 'editorDefinitions'))
        self.root.Vlayout.addWidget(self.scriptEdit)
        self.currentHud = None
        self.auto = False

        self.root.cancelButton.clicked.connect(self.close)
        self.root.hudAddButton.clicked.connect(self.addHud)
        self.root.hudDelButton.clicked.connect(self.delHud)
        self.root.hudListWidget.currentRowChanged.connect(self.hudChanged)
        self.root.comboBox.currentIndexChanged.connect(self.eventChanged)
        self.root.nameLineEdit.textChanged.connect(self.nameChanged)
        self.scriptEdit.textChanged.connect(self.scriptChanged)
        self.root.saveButton.clicked.connect(self.save)

        self.showHuds()

        self.root.setStyleSheet(self.gui.style)
        r = self.root.geometry()
        r.moveCenter(QtWidgets.QApplication.desktop().availableGeometry().center())
        self.root.setGeometry(r)
        self.root.setModal(True)
        self.root.exec_()
        self.closeEvent()

    def hudChanged(self, i):
        self.auto = True
        if i > -1:
            self.currentHud = self.huds[i]
            self.root.nameLineEdit.setText(self.currentHud.getName())
            self.scriptEdit.setPlainText(self.currentHud.getScript())
            event = self.currentHud.getEvent()
            if event == 'open':
                self.root.comboBox.setCurrentIndex(0)
            elif event == 'select':
                self.root.comboBox.setCurrentIndex(1)
            elif event == 'refresh':
                self.root.comboBox.setCurrentIndex(2)
            elif event == 'toggle':
                self.root.comboBox.setCurrentIndex(3)
        else:
            self.currentHud = None
            self.root.nameLineEdit.setText('')
            self.scriptEdit.setPlainText('')
            self.root.comboBox.setCurrentIndex(0)
        self.auto = False

    def eventChanged(self):
        if not self.auto:
            event = self.root.comboBox.currentIndex()
            if event == 0:
                self.currentHud.event = 'open'
            elif event == 1:
                self.currentHud.event = 'select'
            elif event == 2:
                self.currentHud.event = 'refresh'
            elif event == 3:
                self.currentHud.event = 'toggle'

    def scriptChanged(self):
        if not self.auto:
            if self.currentHud:
                self.currentHud.script = self.scriptEdit.toPlainText()

    def nameChanged(self):
        if not self.auto:
            self.root.hudListWidget.currentItem().setText(self.root.nameLineEdit.text())
            self.currentHud.name = self.root.nameLineEdit.text()

    def addHud(self):
        self.huds.append(MgvHud(name='new', project=self.project))
        self.showHuds()

    def delHud(self):
        if self.currentHud:
            self.huds.remove(self.currentHud)
            self.showHuds()

    def showHuds(self):
        clearList(self.root.hudListWidget)
        self.root.hudListWidget.addItems([x.getName() for x in self.huds])
        if self.root.hudListWidget.count():
            self.root.hudListWidget.setCurrentRow(self.root.hudListWidget.count()-1)

    def save(self):
        self.project.setHuds(self.huds)
        self.close()

    def close(self):
        self.gui.readProjects()
        self.root.close()

    def closeEvent(self):
        self.project.unlock()


class MgvProjectSettings(object):
    """Current project settings UI."""
    def __init__(self, gui, project):
        self.gui = gui
        self.project = project._dup()
        mainUIPath = os.path.join(self.gui.mgvDirectory, 'UI', 'projectSettings.ui')
        self.root = QtCompat.loadUi(mainUIPath)
        iconPath = os.path.join(self.gui.mgvDirectory, 'icons', 'mgvIcon.svg')
        self.root.setWindowIcon(QtGui.QIcon(iconPath))

        self.root.addPatternButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'plus-white.svg')))
        self.root.addPatternButton.setIconSize(QtCore.QSize(16, 16))
        self.root.projectDelButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'trash-white.svg')))
        self.root.projectDelButton.setIconSize(QtCore.QSize(16, 16))
        self.root.projectDelButton.setStyleSheet("""
            QPushButton{background: transparent}QPushButton::hover{background: #663333}""")
        self.root.addPatternButton.setStyleSheet("""
            QPushButton::!pressed{ outline: 0; background-color: #555555; color: #CCCCCC; border-radius: 6;
                font: MGVSIZE; border-width: 0px; border-color: #333333; border-style: solid; padding: 8px 12px}
            QPushButton::pressed{ outline: 0; background-color: #358c64; color: #CCCCCC; border-radius: 6;
            border-width: 0px; border-color: #333333; border-style: solid; padding: 8px 12px}
                """.replace('MGVSIZE', str(int(myFontSize)) + 'pt'))

        self.auto = False
        self.project = self.gui.currentProject._dup()
        self.currentGraphTemplate = None
        self.currentContext = None
        self.scriptEdit = MultiEditor(os.path.join(self.gui.mgvDirectory, 'editorDefinitions'))
        self.root.scriptLayout.addWidget(self.scriptEdit)
        self.scriptEdit.textChanged.connect(self.scriptChanged)

        self.root.nameLineEdit.textChanged.connect(self.nameChanged)
        self.root.versionPaddingSpinBox.valueChanged.connect(self.paddingChanged)
        self.root.versionStartSpinBox.valueChanged.connect(self.startChanged)
        self.root.cancelButton.clicked.connect(self.close)
        self.root.saveButton.clicked.connect(self.save)
        self.root.addPatternButton.clicked.connect(self.addPattern)
        self.root.patternsTabWidget.tabCloseRequested.connect(self.tabClose)
        self.root.patternsTabWidget.tabBar().tabMoved.connect(self.tabMoved)
        self.root.projectDelButton.clicked.connect(self.delProject)
        self.root.addContextButton.clicked.connect(self.addContext)
        self.root.delContextButton.clicked.connect(self.delContext)
        self.root.contextLineEdit.textChanged.connect(self.contextNameChanged)
        self.root.contextTextEdit.textChanged.connect(self.contextValueChanged)
        self.root.contextListWidget.currentItemChanged.connect(self.contextChanged)

        self.readProject()
        self.root.setStyleSheet(self.gui.style)
        self.root.addPatternButton.setStyleSheet(self.gui.style)

        r = self.root.geometry()
        r.moveCenter(QtWidgets.QApplication.desktop().availableGeometry().center())
        self.root.setGeometry(r)
        self.root.setModal(True)
        self.root.exec_()
        self.closeEvent()

    def contextChanged(self):
        self.currentContext = None
        self.currentContext = [x for x in self.project.contexts
                               if x.name == self.root.contextListWidget.currentItem().text()][0]
        self.root.contextLineEdit.setText(self.currentContext.name)
        self.root.contextTextEdit.setPlainText(self.currentContext.value)

    def contextNameChanged(self):
        if self.currentContext:
            self.root.contextListWidget.currentItem().setText(self.root.contextLineEdit.text())
            self.currentContext.name = self.root.contextLineEdit.text()

    def contextValueChanged(self):
        if self.currentContext:
            self.currentContext.value = self.root.contextTextEdit.toPlainText()

    def addContext(self):
        self.project.contexts.append(MgvContext(name='new', value='VAR=STR_VALUE', project=self.project))
        self.readProject()

    def delContext(self):
        if self.currentContext:
            self.project.contexts.remove(self.currentContext)
            self.readProject()

    def scriptChanged(self):
        self.project.script = self.scriptEdit.toPlainText()

    def delProject(self):
        result = QtWidgets.QMessageBox.question(self.root, 'Warning',
                                                'Delete project %s ?' % self.project.getName(),
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            self.project.delete()
            self.close()

    def addPattern(self):
        if len(self.project.patterns):
            maxorder = max([x.order+1 for x in self.project.patterns])
        else:
            maxorder = 0
        self.project.patterns.append(MgvPattern(project=self.project, order=maxorder))
        self.readProject()

    def readProject(self):
        self.currentContext = None
        self.root.patternsTabWidget.setVisible(False)
        self.root.contextLineEdit.setText('')
        self.root.contextTextEdit.setPlainText('')
        clearList(self.root.contextListWidget)

        self.currentGraphTemplate = None
        self.root.nameLineEdit.setText(self.project.getName())
        self.root.versionPaddingSpinBox.setValue(self.project.getVersionsPadding())
        self.root.versionStartSpinBox.setValue(self.project.getVersionsStart())
        self.scriptEdit.setText(self.project.getScript())
        self.root.contextListWidget.addItems([x.name for x in self.project.contexts])
        self.root.patternsTabWidget.clear()
        self.root.patternsTabWidget.setVisible(len(self.project.patterns))
        if len(self.project.patterns):
            self.root.addPatternButton.setText('')
            self.root.addPatternButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons',
                                                                        'plus-white.svg')))
            self.root.patternsTabWidget.setCornerWidget(self.root.addPatternButton)
            self.root.addPatternButton.show()
        else:
            self.root.tab.layout().addWidget(self.root.addPatternButton)
            self.root.addPatternButton.setText('Add Pattern')
            self.root.addPatternButton.setIcon(QtGui.QIcon())

        for pattern in sorted(self.project.patterns, key=lambda x: x.order):
            ui = os.path.join(self.gui.mgvDirectory, 'UI', 'pattern.ui')
            widget = QtCompat.loadUi(ui)
            widget.patternButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'folder.svg')))
            widget.patternButton.setIconSize(QtCore.QSize(16, 16))
            widget.patternButton.setStyleSheet('background-color: transparent')
            widget.templateIconButton.setIcon(
                QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'folder.svg')))
            widget.templateIconButton.setIconSize(QtCore.QSize(16, 16))
            widget.templateIconButton.setStyleSheet('background-color: transparent')
            widget.nameLineEdit.setText(pattern.getName())
            widget.patternLineEdit.setText(pattern.pattern)
            widget.graphNameLineEdit.setText(pattern.graph_name)
            idx = self.root.patternsTabWidget.addTab(widget, pattern.getName())
            widget.nameLineEdit.textChanged.connect(
                lambda v, p=pattern, w=widget, ind=idx: self.patternNameChanged(p, w, ind))
            widget.patternLineEdit.textChanged.connect(
                lambda v, p=pattern, w=widget: self.patternPatternChanged(p, w))
            widget.graphNameLineEdit.textChanged.connect(
                lambda v, p=pattern, w=widget: self.patternGraphNameChanged(p, w))
            widget.patternButton.clicked.connect(lambda p=pattern, w=widget: self.patternSelect(p, w))
            widget.templateNameLineEdit.textChanged.connect(
                lambda v, p=pattern, w=widget: self.templateNameChanged(p, w))
            widget.templateIconButton.clicked.connect(lambda w=widget: self.templateIconSelect(w))
            widget.templateIconLineEdit.textChanged.connect(lambda v, w=widget: self.templateIconChanged(w))
            widget.templateListWidget.addItems([x.getName() for x in pattern.templates])
            widget.templateListWidget.itemSelectionChanged.connect(
                lambda p=pattern, w=widget: self.templateChanged(p, w))
            widget.templateAddButton.clicked.connect(lambda p=pattern, w=widget: self.templateAdd(p, w))
            widget.templateDelButton.clicked.connect(lambda p=pattern, w=widget: self.templateDel(p, w))

            if self.currentGraphTemplate is None:
                if widget.templateListWidget.count():
                    widget.templateListWidget.setCurrentRow(0)

    def templateAdd(self, pattern, widget):
        text, ok = QtWidgets.QInputDialog.getText(self.root, 'New template', 'GraphTemplate name :', text='new')
        text = str(text)
        if ok:
            if text not in [x.getName() for x in pattern.templates]:
                p = MgvGraphTemplate(name=text, pattern=pattern)
                pattern.templates.append(p)
                widget.templateListWidget.addItem(text)
                widget.templateListWidget.setCurrentRow(widget.templateListWidget.count() - 1)

    def templateDel(self, pattern, widget):
        if self.currentGraphTemplate:
            result = QtWidgets.QMessageBox.question(self.root, 'Warning',
                                                    'Delele template %s ?' % self.currentGraphTemplate.getName(),
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                    QtWidgets.QMessageBox.No)
            if result == QtWidgets.QMessageBox.Yes:
                tid = pattern.templates.index(self.currentGraphTemplate)
                pattern.templates.remove(self.currentGraphTemplate)
                self.currentGraphTemplate = None
                widget.templateListWidget.takeItem(tid)

    def templateChanged(self, pattern, widget):
        self.currentGraphTemplate = None
        widget.templateNameLineEdit.setText('')
        widget.templateIconLineEdit.setText('')
        sel = widget.templateListWidget.selectedItems()
        if len(sel):
            self.currentGraphTemplate = [x for x in pattern.templates if x.getName() == sel[0].text()][0]
            widget.templateNameLineEdit.setText(self.currentGraphTemplate.getName())
            widget.templateIconLineEdit.setText(self.currentGraphTemplate.icon)

    def templateNameChanged(self, pattern, widget):
        if self.currentGraphTemplate:
            self.currentGraphTemplate.name = widget.templateNameLineEdit.text()
            tid = pattern.templates.index(self.currentGraphTemplate)
            widget.templateListWidget.item(tid).setText(self.currentGraphTemplate.getName())

    def templateIconChanged(self, widget):
        if self.currentGraphTemplate:
            self.currentGraphTemplate.icon = widget.templateIconLineEdit.text()

    def templateIconSelect(self, widget):
        out = QtWidgets.QFileDialog.getOpenFileName(self.root, 'Select an icon')[0]
        if len(out):
            widget.templateIconLineEdit.setText(out)
            self.templateIconChanged(widget)

    def patternSelect(self, pattern, widget):
        out = QtWidgets.QFileDialog.getOpenFileName(self.root, 'Select a pattern graph')[0]
        if len(out):
            widget.patternLineEdit.setText(out)
            self.patternPatternChanged(pattern, widget)

    def patternNameChanged(self, pattern, widget, index):
        value = widget.nameLineEdit.text()
        pattern.name = value
        self.root.patternsTabWidget.setTabText(index, value)

    @staticmethod
    def patternPatternChanged(pattern, widget):
        pattern.pattern = widget.patternLineEdit.text()

    @staticmethod
    def patternGraphNameChanged(pattern, widget):
        pattern.graph_name = widget.graphNameLineEdit.text()

    def tabClose(self, i):
        self.root.patternsTabWidget.removeTab(i)
        del self.project.patterns[i]
        self.readProject()

    def tabMoved(self, a, b):
        for i in range(self.root.patternsTabWidget.count()):
            name = self.root.patternsTabWidget.tabText(i)
            for pattern in self.project.patterns:
                if pattern.name == name:
                    pattern.order = i
        self.project.patterns.sort(key=lambda x: x.order)

    def nameChanged(self):
        self.project.name = self.root.nameLineEdit.text()

    def paddingChanged(self):
        self.project.versions_padding = self.root.versionPaddingSpinBox.value()

    def startChanged(self):
        self.project.versions_start = self.root.versionStartSpinBox.value()

    def save(self):
        mgvWrapper.syncProject(self.project)
        self.close()

    def close(self):
        self.gui.readProjects()
        self.root.close()

    def closeEvent(self):
        self.project.unlock()


class MgvLocalSettings(object):
    """Local settings UI."""
    def __init__(self, gui):
        self.gui = gui
        mainUIPath = os.path.join(self.gui.mgvDirectory, 'UI', 'localSettings.ui')
        self.root = QtCompat.loadUi(mainUIPath)
        iconPath = os.path.join(self.gui.mgvDirectory, 'icons', 'mgvIcon.svg')
        self.root.setWindowIcon(QtGui.QIcon(iconPath))
        self.root.shellLineEdit.setText(self.gui.shell)
        self.root.explorerLineEdit.setText(self.gui.explorer)
        self.root.pathButton.setIcon(QtGui.QIcon(os.path.join(self.gui.mgvDirectory, 'icons', 'folder.svg')))
        self.root.pathButton.setIconSize(QtCore.QSize(16, 16))
        self.wrapperModule = ''
        if os.path.exists(self.gui.localSettingsFile):
            with open(self.gui.localSettingsFile) as fid:
                root = json.load(fid)
                self.wrapperModule = root['wrapper']['current']
        items = [os.path.basename(os.path.splitext(x)[0])[10:] for x in glob.glob(self.gui.mgvDirectory +
                                                                                  '/mgvWrapper*.py')]
        self.root.wrapperComboBox.addItems(items)
        self.root.wrapperComboBox.currentIndexChanged[str].connect(self.moduleChanged)
        self.root.wrapperComboBox.setCurrentIndex(self.root.wrapperComboBox.findText(self.wrapperModule[10:]))
        if 'welcome' in root.keys():
            self.root.discoverCheckBox.setChecked(root['welcome'])
        else:
            self.root.discoverCheckBox.setChecked(True)
        self.moduleChanged(self.wrapperModule[10:])
        self.root.cancelButton.clicked.connect(self.root.close)
        self.root.saveButton.clicked.connect(self.save)
        self.root.pathButton.clicked.connect(self.folderPath)
        self.root.setStyleSheet(self.gui.style)
        r = self.root.geometry()
        r.moveCenter(QtWidgets.QApplication.desktop().availableGeometry().center())
        self.root.show()
        self.root.setGeometry(r)
        self.root.setModal(True)

    def folderPath(self):
        out = QtWidgets.QFileDialog.getExistingDirectory(self.root, 'Projects data folder', '')
        if out:
            self.root.pathLineEdit.setText(out)

    def moduleChanged(self, s):
        s = 'mgvWrapper' + s
        with open(self.gui.localSettingsFile) as fid:
            root = json.load(fid)
            host, user, pwd = '', '', ''

        if s in root['wrapper']:
            host = root['wrapper'][s]['host']
            user = root['wrapper'][s]['user']
            pwd = root['wrapper'][s]['pwd']

        if s == 'mgvWrapperNoServer':
            self.root.pathLineEdit.setText(host)
            self.root.hostLineEdit.hide()
            self.root.userLineEdit.hide()
            self.root.pwdLineEdit.hide()
            self.root.hostLabel.hide()
            self.root.nameLabel.hide()
            self.root.pwdLabel.hide()
            self.root.pathLabel.show()
            self.root.pathWidget.show()
        else:
            self.root.hostLineEdit.setText(host)
            self.root.userLineEdit.setText(user)
            self.root.pwdLineEdit.setText(pwd)
            self.root.hostLineEdit.show()
            self.root.userLineEdit.show()
            self.root.pwdLineEdit.show()
            self.root.hostLabel.show()
            self.root.nameLabel.show()
            self.root.pwdLabel.show()
            self.root.pathLabel.hide()
            self.root.pathWidget.hide()

    def save(self):
        self.gui.shell = self.root.shellLineEdit.text()
        self.gui.explorer = self.root.explorerLineEdit.text()
        self.wrapperModule = 'mgvWrapper' + self.root.wrapperComboBox.currentText()
        with open(self.gui.localSettingsFile) as fid:
            root = json.load(fid)
        root['shell'] = self.gui.shell
        root['explorer'] = self.gui.explorer
        root['welcome'] = self.root.discoverCheckBox.isChecked()
        root['wrapper']['current'] = self.wrapperModule
        if self.wrapperModule == 'mgvWrapperNoServer':
            root['wrapper'][self.wrapperModule] = {'host': self.root.pathLineEdit.text(), 'user': '', 'pwd': ''}
        else:
            root['wrapper'][self.wrapperModule] = {'host': self.root.hostLineEdit.text(),
                                                   'user': self.root.userLineEdit.text(),
                                                   'pwd': self.root.pwdLineEdit.text()}

        lines = json.dumps(root, sort_keys=True, indent=4)
        try:
            with open(self.gui.localSettingsFile, 'w') as fid:
                fid.writelines(lines)
        except IOError:
            self.gui.notify("Can't create %s !" % self.gui.localSettingsFile, 1)
        global mgvWrapper
        mgvWrapper = changeWrapper()
        self.gui.readProjects()
        self.root.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    a = MangroveGUI(app)
    sys.exit(app.exec_())

try:
    set_procname('mangrove')
except:
    pass
main()

# batchscripts dans le graph, par user, par pattern et/ou template
# doc enrichie
# doc droits de license
# doc outputs
# doc on mgvCom
# doc protect, unprotect, steal
# super users ?
