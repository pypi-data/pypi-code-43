'''
Example 3
Create a simple two mirror cavity with radius of curvature of 1.0 meter,
and distance between the mirrors of 0.5 meters
R1 = -2 m                   R2 = -4 m
 ___                             ___
|   \         L1 = 1.0          /   |
|    | ----------------------- |    |
|___/                   -----   \___|
                   -----
 ____         -----
|   /    -----    L2 = 0.5 m
|  |-----
|___\
R3 = 1.5
'''
import numpy as np
from beamtrace import BeamTrace
import matplotlib.pyplot as plt

# three mirror cavity
test2 = BeamTrace()
test2.add_mirror(-2.0, name='Input Mirror RoC = -2 meter')
test2.add_space(1.0)
test2.add_mirror(-4.0, name='Middle Mirror RoC = -4 meter')
test2.add_space(0.5)
test2.add_mirror(1.5, name='End Mirror RoC = 1.5 meter')
test2.calculate_cavity_ABCD()

print()
print('Total Round-trip ABCD = \n{}\n'.format(test2.ABCD))
print()
print('Input Parameters')
print('Eigenmode q-parameter = {}'.format(test2.q_input))
print('Beam Waist at Input = {} mm'.format(test2.w_input*1e3))
print('Beam Radius of Curvature at Input = {} m'.format(test2.RoC_input))
print()
print('Total Round-trip Accumulated Gouy Phase = {:.2f} deg'.format(test2.get_total_cavity_gouy_phase()))

fig = test2.plot_cavity_scan(round_trip=True)
plt.show()
