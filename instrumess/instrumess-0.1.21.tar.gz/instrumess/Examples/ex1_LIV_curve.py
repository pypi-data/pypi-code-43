# -*- coding: utf-8 -*-
"""
Created on Monday 25-March-2019 at 20:40

@author: Rastko Pajković
"""

from Keithley2400 import Keithley2400
from Agilent_PM import AgilentPM
import utilities as ut
import matplotlib.pyplot as plt
from plot_aux import fig_new, fig_2y, colors, save_last_fig  # , fig_label, interactive_legend,\

plt.rcParams.update({'font.size': 14})  # set default font size for all plots
# ----- USER INTERFACE ---------------------------------------------------------
wait = 0.5  # seconds
currents = ut.array(start=0, step=1, stop=160)
laser = 'L2'
boost = True
i_boost = 100
filename = 'LIV, {}, boost={}, ib={}mA.txt'.format(laser, str(boost), i_boost)
save_to = ut.make_fold(name='SP24 LIV and crosstalk',
                       date=True,
                       root='D:/Dropbox/PhD - ITL for SS-OCT/Measurements')
df = ut.df_init(columns=['p', 'i', 'v', 'ts'],
                numel=len(currents),
                units=['mW', 'mA','V','microsecond'])
# ------------------------------------------------------------------------------

with Keithley2400(address='GPIB0::24::INSTR') as k,\
     AgilentPM(address='GPIB::20::INSTR', slot=1) as pm:
    # set current, measure power and voltage
    k.source_current(lim_V=2, sense='voltage', nplc=4)
    pm.set_range(range='auto')
    pm.setup(wl_nm=1530)
    pm.set_unit(unit='dbm')  # remember to convert to mW
    for ind, i in enumerate(currents):
        k.set_current(i_ma=i, slow_start=False)
        ut.wait_s(wait)
        v, *_ = k.measure()
        p = ut.dbm2mw(pm.get_power())  # conversion to mw
        df.loc[i] = p, i, v, ut.get_time(form='str')

# plot results
fig, ax1, ax2 = fig_2y(color_left=colors[0], color_right=colors[1],
                       name='fig_2y')
ax1.plot(df.i[1:], df.p[1:])
ax2.plot(df.i[1:], df.v[1:], color=colors[1])
ax1.set(
    title='LIV curve, boost 100 mA',
    xlabel='Current [mA]',
    ylabel='Power [mW]',
)
ax2.set(
    ylabel='Voltage [V]',
)
save_last_fig(name=filename[:-4], dest=save_to, filetype='png', dpi=150)
# save df
ut.df_write(df, save_to/filename, overwrite=True, header={
                    'Measured_by':'Rastko',
                    'Chip':'SP24-23-j6',
                    'Temperature':'18°C',
                    'Equipment':'Keithley 2450, Agilent 81636B PM',
                    'Wait':'{} s'.format(wait),
                    'Boost': '{}'.format(str(boost)),
                    'Iboost': '{} mA'.format(i_boost)
                     })