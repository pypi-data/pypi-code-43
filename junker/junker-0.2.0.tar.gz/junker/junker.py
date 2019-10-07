#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Thu Dec 15 15:28:14 2016

@author: Robert A. McLeod
'''

import os, os.path, glob, sys
from PySide2 import QtGui as qg, QtCore as qc, QtWidgets as qw

import multiprocessing as mp
import mrcz
import skimage.io
import scipy.ndimage as ni
import numpy as np
import time

from . import util

def partition(sequence, n):
    for I in range(0, len(sequence), n):
        yield sequence[I:I + n]

def batchProcPNG(mrcNames):
    for mrcName in mrcNames:
        print('Converting %s to PNG format' % mrcName)
        pngName = os.path.splitext(mrcName)[0] + '.png'
        image, header = mrcz.readMRC(mrcName)
        image = np.array(image)
        if image.ndim == 4:
            # Pass on multispectral data
            continue
        elif image.ndim == 3:
            image = image.mean(axis=0)

        print(f'Image {pngName} has shape {image.shape}')

        image = util.squarekernel(image)
        image = ni.gaussian_filter(image, 1.0)
        
        clim = util.histClim(image, cutoff=1E-4)
        
        image = util.normalize(np.clip(image, clim[0], clim[1]))
        
        skimage.io.imsave(pngName, image, plugin='pil')

                
class Junker(qw.QMainWindow):
    
    def __init__(self, Q_APP):
        
        qw.QMainWindow.__init__(self)
        self.setupUi()
        
        self.mrcNames = glob.glob('*.mrc') + glob.glob('*.mrcz')
        self.pngNames = [None] * len(self.mrcNames)
        self.baseNames = [None] * len(self.mrcNames)
        self.totalImages = len(self.mrcNames)
        pngNotPresent = np.zeros(len(self.mrcNames), dtype='bool')
        
        for I, mrcName in enumerate(self.mrcNames):
            self.baseNames[I] = os.path.splitext(mrcName)[0]
            self.pngNames[I] = self.baseNames[I] + '.png'
            pngNotPresent[I] = not os.path.isfile(self.pngNames[I])
            
        if np.any(pngNotPresent):
            mrcToDo = np.asarray(self.mrcNames)[pngNotPresent].tolist()
            print( '====Processing %d MRC to diagnostic PNG files====' % len(mrcToDo))
            N_proc = np.minimum(int(mp.cpu_count()/2), len(mrcToDo))
            
            print("Processing: " + str(mrcToDo))
            
            # Multi-processing approach
            # -------------------------
            mrcChunks = partition(mrcToDo, N_proc)
            daPool = mp.Pool(N_proc)
            daPool.map_async(batchProcPNG, mrcChunks)

            # Single-process approach
            # -----------------------
            # batchProcPNG(mrcToDo)

            time.sleep(2.0)
        
        
        try: os.mkdir('salvage')
        except: pass
        try: os.mkdir('junk')
        except: pass
    
        self.currIndex = 0
        self.buttonJunk.clicked.connect(self.junkCurrent)
        self.buttonSalvage.clicked.connect(self.salvageCurrent)
        self.buttonUndo.clicked.connect(self.undoCurrent)
        
        try:
            self.labelPNG.setPixmap(qg.QPixmap(self.pngNames[self.currIndex]))
        except: pass
        
        self.showMaximized()
        Q_APP.exec_()

    def setupUi(self):
        sizePolicy = qw.QSizePolicy(qw.QSizePolicy.Minimum, qw.QSizePolicy.Fixed)


        self.resize(1009, 856)
        self.centralwidget = qw.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.verticalLayout = qw.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.labelPNG = qw.QLabel(self.centralwidget)

        self.labelPNG.setSizePolicy(qw.QSizePolicy.Expanding, qw.QSizePolicy.Expanding)
        self.labelPNG.setAlignment(qc.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.labelPNG)

        self.horizontalLayout = qw.QHBoxLayout()
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.buttonUndo = qw.QPushButton("Undo", self.centralwidget)
        self.buttonUndo.setSizePolicy(qw.QSizePolicy.Minimum, qw.QSizePolicy.Fixed)
        self.buttonUndo.setToolTip('Undo delete (shortcut: "Z")')
        self.buttonUndo.clicked.connect(self.undoCurrent)
        self.buttonUndo.setFocusPolicy(qc.Qt.NoFocus)
        self.horizontalLayout.addWidget(self.buttonUndo)

        self.buttonSalvage = qw.QPushButton("Salvage", self.centralwidget)
        self.buttonSalvage.setSizePolicy(qw.QSizePolicy.Minimum, qw.QSizePolicy.Fixed)
        self.buttonSalvage.setToolTip('Move to Salvage directory (shortcut: "Enter")')
        self.buttonSalvage.clicked.connect(self.salvageCurrent)
        self.buttonSalvage.setFocusPolicy(qc.Qt.NoFocus)
        self.horizontalLayout.addWidget(self.buttonSalvage)

        self.buttonJunk = qw.QPushButton("Junk", self.centralwidget)
        self.buttonJunk.setSizePolicy(qw.QSizePolicy.Minimum, qw.QSizePolicy.Fixed)
        self.buttonJunk.setLayoutDirection(qc.Qt.LeftToRight)
        self.buttonJunk.clicked.connect(self.junkCurrent)
        self.buttonJunk.setToolTip('Move to Junk directory (shortcut: "Space")')
        self.buttonJunk.setFocusPolicy(qc.Qt.NoFocus)
        self.horizontalLayout.addWidget(self.buttonJunk)

        self.menubar = qw.QMenuBar(self)
        self.menubar.setGeometry(qc.QRect(0, 0, 1009, 19))
        self.setMenuBar(self.menubar)
        self.statusbar = qw.QStatusBar(self)
        self.setStatusBar(self.statusbar)
        
    def incrementIndex(self):
        self.currIndex += 1
        if self.currIndex >= len(self.pngNames):
            self.currIndex = 0
        self.updateView()
        
    def decrementIndex(self):
        self.currIndex -= 1
        if self.currIndex < 0:
            self.currIndex = len(self.pngNames) - 1
        self.updateView()
        
    def updateView(self):
        self.statusbar.showMessage('Image (%d / %d)' %(self.currIndex, self.totalImages))
        if not os.path.isfile(self.pngNames[self.currIndex]):
            self.labelPNG.setPixmap(qg.QPixmap(''))
            return
        
        self.labelPNG.setPixmap(qg.QPixmap(self.pngNames[self.currIndex]))

    
    def junkCurrent(self):
        junkNames = glob.glob(self.baseNames[self.currIndex] + '*')
        for junk in junkNames:
            os.rename(junk, os.path.join('junk', junk))
            
        self.updateView()

    
    def salvageCurrent(self):
        salvageNames = glob.glob(self.baseNames[self.currIndex] + '*')
        for salvage in salvageNames:
            os.rename(salvage, os.path.join( 'salvage', salvage))
            
        self.updateView()


    def undoCurrent(self):
        undoNames = glob.glob(os.path.join('junk', self.baseNames[self.currIndex] + '*' ))
        undoNames += glob.glob(os.path.join('salvage', self.baseNames[self.currIndex] + '*' ))
        for undo in undoNames:
            os.rename(undo, os.path.basename(undo))
            
        self.updateView()

    def keyPressEvent(self, event):
        key = event.key()
        # print('Received key %s ' % key)

        if key == qc.Qt.Key_Right:
            self.incrementIndex()
        elif key == qc.Qt.Key_Left:
            self.decrementIndex()
        elif key == qc.Qt.Key_Delete or key == qc.Qt.Key_Space:
            self.junkCurrent()
        elif key == qc.Qt.Key_Z:
            self.undoCurrent()
        elif key == qc.Qt.Key_Enter or key == qc.Qt.Key_Return or key == qc.Qt.Key_S:
            self.salvageCurrent()
    