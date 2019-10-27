'''
Example 2
Create a simple two mirror cavity with radius of curvature of 1.0 meter,
and distance between the mirrors of 0.5 meters
R1 = 1934 m        R2 = 2245 m
______              ______
|    /______________\    |
|   /    L=3995 m    \   |
|   \ ______________ /   |
|____\              /____|
'''

# LIGO arm cavity
import numpy as np
from beamtrace import BeamTrace
R1 = 1934. # m
R2 = 2245. # m
L = 3994.469 # m
arm_cav = BeamTrace()

arm_cav.add_mirror(R1, name='ITMY')
arm_cav.add_space(L)
arm_cav.add_mirror(R2, name='ETMY')

import matplotlib.pyplot as plt
fig = arm_cav.plot_cavity_scan(round_trip=True)
plt.show()
