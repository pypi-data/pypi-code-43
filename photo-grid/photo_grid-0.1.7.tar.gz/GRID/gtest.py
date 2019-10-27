from PyQt5.QtWidgets import QApplication
# from .lib import *
from .gridGUI import *
import matplotlib.pyplot as plt
import grid as gd
# import statistics
# import numpy as np

#=== === === === === === DEBUG === === === === === ===

grid = gd.GRID()
grid.loadData()
# grid.loadData("/Users/jameschen/Dropbox/James Chen/GRID/Modeling/Rhombus.jpg")
# grid.loadData("/Users/jameschen/Dropbox/James_Git/FN/data/demo.png")
# grid.binarizeImg(k=3, lsSelect=[0], valShad=0, valSmth=0, outplot=False)
# grid.findPlots(outplot=False)


app = QApplication(sys.argv)
g = GRID_GUI(grid, 2) # 0:input, 1:crop, 2:kmean, 3:anchor, 4:output
app.exec_()


# === === === detect default rank of K === === === ===
# import grid as gd
# import numpy as np
# import matplotlib.pyplot as plt

# grid = gd.GRID()
# grid.loadData("/Users/jameschen/Dropbox/James_Git/FN/data/demo.png")
# # grid.loadData("/Users/jameschen/Dropbox/James Chen/GRID/Modeling/Rhombus.jpg")

# k = 5
# row = k
# col = 4
# i = 0

# grid.binarizeImg(k=k, lsSelect=[0], valShad=0, valSmth=0, outplot=False)

# for i in range(row):
#     imgB = (np.isin(grid.imgs.get('kmean'), i)*1).astype(np.int)
#     sigs = imgB.mean(axis=0)
#     plt.subplot(row, col, 1+i*col+0)
#     plt.imshow(imgB)
#     plt.subplot(row, col, 1+i*col+1)
#     plt.ylim(0, 1)
#     plt.plot(sigs)
#     plt.subplot(row, col, 1+i*col+2)
#     sigf = gd.getFourierTransform(sigs)
#     plt.plot(sigf)
#     plt.subplot(row, col, 1+i*col+3)
#     # scMaxF = round(max(sigf)*5, 4)  # [0, 1]
#     scMaxF = round((max(sigf)/sigf.mean())/100, 4)  # [0, 1]
#     scMean = round(1-(sigs.mean()), 4) # [0, 1]
#     scPeaks = round(len(gd.find_peaks(sigs, height=(sigs.mean()))
#                   [0])/len(gd.find_peaks(sigs)[0]), 4)
#     # scPeaks = len(gd.find_peaks(sigs)[0])
#     score = scMaxF*.25 + scMean*.25 + scPeaks*.5
#     plt.text(.3, .8, str(score), fontsize=10)
#     plt.text(.3, .6, str(scMaxF), fontsize=10)
#     plt.text(.3, .4, str(scMean), fontsize=10)
#     plt.text(.3, .2, str(scPeaks), fontsize=10)

# plt.show()

# === === === detect default rank of K === === === ===


# max(getFourierTransform(sigs))


# plt.imshow()
# plt.show()

# grid = gd.GRID()
# grid.loadData("/Users/jameschen/Dropbox/James Chen/GRID/Modeling/Rhombus.jpg")
# grid.binarizeImg(k=5, lsSelect=[0], valShad=0, valSmth=0, outplot=False)
# grid.findPlots(outplot=False)
# grid.map.dt
# # grid.cpuSeg()
# # grid.save(prefix="Pumptree2")

# app = QApplication(sys.argv)
# g = GRID_GUI(grid, 4) # 0:input, 1:crop, 2:kmean, 3:anchor, 4:output
# app.exec_()


# # ========== kmean ==========
# array = numpy.array([4, 2, 7, 1])
# temp = array.argsort()
# ranks = numpy.empty_like(temp)
# ranks[temp] = numpy.arange(len(array))

# def getRank(array):
#     sort = array.argsort()
#     rank = np.zeros(len(sort), dtype=np.int)
#     rank[sort] = np.flip(np.arange(len(array)), axis=0)
#     return rank

# test = np.array([2, 6, 87,1, 3, 6])
# getRank(test)
# temp = test.argsort()
# np.zeros(len(temp))
# rank = np.empty_like(temp)
# rank[temp] = np.flip(np.arange(len(test)), axis=0)
# np.arange(1, 7, 1)
# np.arange(6, 2, 1)

# ========== plotting ==========

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


# g = GRID_GUI(grid, 4)
# app.exec_()

