'''
Example 1
Create a simple two mirror cavity with radius of curvature of 1.0 meter,
and distance between the mirrors of 0.5 meters
R1 = 1.0 m        R2 = 1.0 m
______              ______
|    /______________\    |
|   /    L=0.5 m     \   |
|   \ ______________ /   |
|____\              /____|
'''
import numpy as np
from beamtrace import BeamTrace

my_cav = BeamTrace()   # initializes BeamTrace class
my_cav.add_mirror(1.0) # adds mirror with 1.0 meter radius of curvature at z=0.0 meters
my_cav.add_space(0.5)  # adds 0.5 meters of space to cavity
my_cav.add_mirror(1.0) # adds mirror with 1.0 meter radius of curvature at z=0.5 meters
my_cav.calculate_cavity_ABCD() # Finds the cavity round-trip ABCD matrix, tells you if it's stable.  If it is stable, populates the my_cav.q_input parameter
zz, ww, gouy, qq = my_cav.scan_cavity(round_trip=True) # Returns propagation distance, beam radius, accumulated gouy phase, and beam q-parameter for the entire cavity, plus the round-trip

import matplotlib.pyplot as plt
fig = my_cav.plot_cavity_scan(round_trip=True, label='Simple Cavity')
plt.show()
