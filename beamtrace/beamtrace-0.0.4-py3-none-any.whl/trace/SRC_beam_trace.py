'''
Example 4
SRC cavity at LHO
Create a simple two mirror cavity with radius of curvature of 1.0 meter,
and distance between the mirrors of 0.5 meters
SRM R = -5.69 m                   SR2 R = -6.4 m
 ___                             ___
|   \         L1 = 15.75        /   |
|    | ----------------------- |    |
|___/                   -----   \___|
        L2 = 0.5 m -----
 ____         -----                                ____              ____
|   /    -----         L3 = 19.36 m               /   /  L4 ~ 5.0 m |   /
|  |---------------------------------------------/---/--------------|--|
|___\                                           /___/               |___\
R3 = 35.972                                   BS R = inf          ITMY R = -1934
'''
import numpy as np
from beamtrace import BeamTrace
import matplotlib.pyplot as plt

''' SRC Parameters'''
nn = 1.44963 # index of refraction of silica

RoC_SRM  = -5.6938 #m vs -5.7150 m = 0.0212 m Finesse - Fulda
RoC_SR2  = -6.4060 #m vs -6.4240 m = 0.0180 m Finesse - Fulda
RoC_SR3  = 35.9728 #m vs 36.0130 m = -0.0402 m Finesse - Fulda
RoC_ITMY = -1934.0000 #m vs -1939.3900 m = 5.3900 m Finesse - Fulda

ll_SRM_SR2   = 15.7586 #m vs 15.7400 m = 0.0186 m Finesse - Fulda
ll_SR2_SR3   = 15.4435 #m vs 15.4601 m = -0.0166 m Finesse - Fulda
ll_SR3_BSAR  = 19.3661 #m vs 19.3661 m = 0.0000 m Finesse - Fulda
ll_BSsub     = 0.0687 #m vs 0.0685 m = 0.0002 m Finesse - Fulda
ll_BS_ITMYAR = 5.0126 #m vs 4.9670 m = 0.0456 m Finesse - Fulda
ll_ITMYsub   = 0.2000 #m vs 0.2000 m = 0.0000 m Finesse - Fulda

total_length_SRC = 55.8495 #m vs 55.8017 m = 0.0478 m Finesse - Fulda

f_ITMY = 34500.0000 #m vs 34500.0000 m = 0.0000 m Finesse - Fulda

'''Set up BeamTrace'''
SRC_ABCD = BeamTrace()

SRC_ABCD.add_mirror(RoC_ITMY, index_of_refraction=nn, name='ITMY HR') # reflection from inside ITMY changes effective RoC
SRC_ABCD.add_space(ll_ITMYsub, index_of_refraction=nn, name='ITMY substrate')
SRC_ABCD.add_lens(f_ITMY, name='ITMY AR')
SRC_ABCD.add_space(ll_BS_ITMYAR, name='L BS to ITMYAR')
SRC_ABCD.add_lens(np.inf, name='BS HR')
SRC_ABCD.add_space(ll_BSsub, index_of_refraction=nn, name='BS substrate')
SRC_ABCD.add_lens(np.inf, name='BS AR')
SRC_ABCD.add_space(ll_SR3_BSAR, name='L SR3 to BSAR')
SRC_ABCD.add_mirror(RoC_SR3, name='SR3')
SRC_ABCD.add_space(ll_SR2_SR3, name='L SR2 to SR3')
SRC_ABCD.add_mirror(RoC_SR2, name='SR2')
SRC_ABCD.add_space(ll_SRM_SR2, name='L SRM to SR2')
SRC_ABCD.add_mirror(RoC_SRM, name='SRM')

SRC_ABCD.calculate_cavity_ABCD()
print()
print('SRC ABCD = \n{}\n'.format(SRC_ABCD.ABCD))
print()
print('Input Parameters')
print('q = {}'.format(SRC_ABCD.q_input))
print('w = {}'.format(SRC_ABCD.w_input))
print('RoC = {}'.format(SRC_ABCD.RoC_input))
print()
print('Accum Gouy Phase = {:.2f} deg'.format(SRC_ABCD.get_total_cavity_gouy_phase()))

SRC_ABCD.print()

fig = SRC_ABCD.plot_cavity_scan(round_trip=False, label='Fundamental SRC Mode')

''' Change input beam so it doesn't match the fundamental mode'''
SRC_ABCD.q_input = (1834.203+427.841j) # estimated q_input from arm cavity (Example 2)
fig = SRC_ABCD.plot_cavity_scan(round_trip=False, color='C7', ls='--', label='Mode from Arm Cavity', fig=fig)

s1, s2 = fig.get_axes()

s1.set_title('SRC Cavity Scan')

plt.tight_layout()
plt.savefig('./SRC_beam_trace.pdf')
plt.show()
