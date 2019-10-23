import pyconrad.autoinit
import ij
from edu.stanford.rsl.conrad.data.numeric import NumericGrid
import numpy as np

pyconrad.start_gui()

a = np.random.rand(20, 30)
grid = NumericGrid.from_numpy(a)
grid.show()

ij.IJ.run('FFT')
