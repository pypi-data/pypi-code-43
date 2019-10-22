# basic imports
import sys
import os

# 3rd party imports
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import qdarkstyle

# self imports
from .gridGUI import *

if "--test" not in sys.argv:
    app = QApplication(sys.argv)
    if '--light' not in sys.argv:
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    grid = GRID_GUI()

    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)

    app.exec_()
    exit()


#=== === === === === === DEBUG === === === === === ===
import sys
import pyqtgraph as pg
import numpy as np
import statistics
import grid as gd
# import matplotlib.pyplot as plt
from .gridGUI import *
from .gui.customQt import *
from PyQt5.QtWidgets import QApplication
grid = gd.GRID()
grid.loadData("/Users/jameschen/Dropbox/James Chen/GRID/Modeling/Rhombus.jpg")
grid.binarizeImg(k=5, lsSelect=[0], valShad=0, valSmth=0, outplot=False)
grid.findPlots(outplot=False)
# grid.cpuSeg()
# grid.save(prefix="Pumptree2")

app = QApplication(sys.argv)
g = GRID_GUI(grid, 4) # 0:input, 1:crop, 2:kmean, 3:anchor, 4:output
app.exec_()

# ========== plotting ==========
img = pg.image(grid.map.imgs[0])


# FIXME: Wrong order for the second axis
  
# ========== peak searching ==========
# pks, sig = gd.findPeaks(grid.map.imgs[1])
# plt.plot(sig)
# plt.plot(pks, sig[pks], "x")
# plt.show()



# grid.save(prefix="Pumptree2")

# grid = gd.GRID()
# grid.loadData("/Users/jameschen/Dropbox/James Chen/GRID/Modeling/Rhombus.jpg")
# grid.binarizeImg(k=5, lsSelect=[0], valShad=0, valSmth=0, outplot=False)
# grid.findPlots(nRow=7, nCol=6, outplot=False)
# grid.cpuSeg(outplot=True)
# grid.save(prefix="Rhombus")
# # grid.run(pathImg="/Users/jameschen/Dropbox/James Chen/GRID/Modeling/Rhombus.jpg", k=5, lsSelect=[4], path="/Users/jameschen", prefix="letmesleep")

# # with open("/Users/jameschen/Dropbox/photo_grid/Outputter_1018.grid", "wb") as file:
# #     pickle.dump(grid, file, pickle.HIGHEST_PROTOCOL)

# # grid.loadData("/Users/jameschen/Dropbox/James_Git/FN/data/demo.png")
# # grid.binarizeImg(k=3, lsSelect=[0, 1], valShad=0, valSmth=0, outplot=False)

# app = QApplication(sys.argv)
# with open("/Users/jameschen/Dropbox/photo_grid/Outputter_1018.grid", "rb") as file:
#     grid = pickle.load(file)

# g = GRID_GUI(grid, 4)
# app.exec_()
