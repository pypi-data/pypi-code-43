# -*- coding: utf-8 -*-
#  this file is intended to used in the debugger
# write a script that calls your function to debug it

import numpy as np
import jscatter as js
# some arrays
w = np.r_[-100:100]
q = np.r_[0.001:5:0.01]
x = np.r_[1:10]

sic = js.sas.sasImage(js.examples.datapath+'/Silicon.tiff')
sic.setDetectorPosition([130,-100],0.070,90,90,0)
sic.showPolar()












