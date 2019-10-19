# #basic imports
# import sys
# import os

# # 3rd party imports
# from PyQt5.QtWidgets import QApplication
# from PyQt5.QtCore import QTimer
# import qdarkstyle

# # self imports
# from .gridGUI import *


# app = QApplication(sys.argv)
# if '--light' not in sys.argv:
#     app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

# grid = GRID_GUI()

# timer = QTimer()
# timer.timeout.connect(lambda: None)
# timer.start(100)

# app.exec_()

# # TEST
# import sys
# import pickle
# import grid as gd
# from .gridGUI import *
# from PyQt5.QtWidgets import QApplication
# grid = gd.GRID()
# grid.run(pathImg="/Users/jameschen/Dropbox/James Chen/GRID/Modeling/Rhombus.jpg", k=5, lsSelect=[4], path="/Users/jameschen", prefix="letmesleep")
# grid.loadData("/Users/jameschen/Dropbox/James Chen/GRID/Modeling/Rhombus.jpg")
# grid.binarizeImg(k=5, lsSelect=[4], valShad=0, valSmth=0, outplot=False)
# grid.findPlots(outplot=False)
# # grid.cpuSeg(outplot=True)

# # with open("/Users/jameschen/Dropbox/photo_grid/Outputter_1018.grid", "wb") as file:
# #     pickle.dump(grid, file, pickle.HIGHEST_PROTOCOL)

# # grid.loadData("/Users/jameschen/Dropbox/James_Git/FN/data/demo.png")
# # grid.binarizeImg(k=3, lsSelect=[0, 1], valShad=0, valSmth=0, outplot=False)

# app = QApplication(sys.argv)
# with open("/Users/jameschen/Dropbox/photo_grid/Outputter_1018.grid", "rb") as file:
#     grid = pickle.load(file)

# g = GRID_GUI(grid, 4)
# app.exec_()


