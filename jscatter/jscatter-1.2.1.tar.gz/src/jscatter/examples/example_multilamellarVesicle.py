# coding=utf-8
import jscatter as js

Q = js.loglist(0.001, 5, 500)  # np.r_[0.01:5:0.01]

ffmV = js.ff.multilamellarVesicles
save = 0

# correlation peak sharpness depends on disorder
dR = 20
nG = 200
p = js.grace(1, 1)
for dd in [0.1, 6, 10]:
    p.plot(ffmV(Q=Q, R=100, displace=dd, dR=dR, N=10, dN=0, phi=0.2, layers=0, SLD=1e-4, nGauss=nG),
           le='displace= %g ' % dd)

p.legend(x=0.3, y=10)
p.title('Scattering of multilamellar vesicle')
p.subtitle('lamella N=10, layers 0 nm, dR=20, R=100')
p.yaxis(label='S(Q)', scale='l', min=1e-7, max=1e2, ticklabel=['power', 0])
p.xaxis(label='Q / nm\S-1', scale='l', min=1e-3, max=5, ticklabel=['power', 0])
p.text('Guinier range', x=0.005, y=10)
p.text(r'Correlation peaks\nsharpness decreases with disorder', x=0.02, y=0.00001)
if save: p.save('multilamellar1.png')

# Correlation peak position depends on average layer distance
dd = 0
dR = 20
nG = 200
p = js.grace(1, 1)
for N in [1, 3, 10, 30, 100]:
    p.plot(ffmV(Q=Q, R=100, displace=dd, dR=dR, N=N, dN=0, phi=0.2, layers=0, SLD=1e-4, nGauss=nG), le='N= %g ' % N)

p.legend(x=0.3, y=10)
p.title('Scattering of multilamellar vesicle')
p.subtitle('shellnumber N, layers 0 nm, dR=20, R=100')
p.yaxis(label='S(Q)', scale='l', min=1e-7, max=1e2, ticklabel=['power', 0])
p.xaxis(label='Q / nm\S-1', scale='l', min=1e-3, max=5, ticklabel=['power', 0])

p.text('Guinier range', x=0.005, y=40)
p.text(r'Correlation peaks\n at 2\xp\f{}N/R', x=0.2, y=0.01)
if save: p.save('multilamellar2.png')

# including the shell formfactor with fluctuations of layer thickness
dd = 2
dR = 20
nG = 200
p = js.grace(1, 1)
# multi lamellar structure factor
mV = ffmV(Q=Q, R=100, displace=dd, dR=dR, N=10, dN=0, phi=0.2, layers=6, SLD=1e-4, nGauss=nG)
for i, ds in enumerate([0.001, 0.1, 0.6, 1.2], 1):
    # calc layer fomfactor
    lf = js.formel.pDA(js.ff.multilayer, ds, 'layerd', q=Q, layerd=6, SLD=1e-4)
    p.plot(mV.X, mV._Sq * lf.Y / lf.Y[0], sy=[i, 0.3, i], le='ds= %g ' % ds)
    p.plot(mV.X, lf.Y, sy=0, li=[3, 3, i])
    p.plot(mV.X, mV._Sq, sy=0, li=[2, 3, i])

p.legend(x=0.003, y=1)
p.title('Scattering of multilamellar vesicle')
p.subtitle('shellnumber N=10, layers 6 nm, dR=20, R=100')
p.yaxis(label='S(Q)', scale='l', min=1e-12, max=1e2, ticklabel=['power', 0])
p.xaxis(label='Q / nm\S-1', scale='l', min=2e-3, max=5, ticklabel=['power', 0])

p.text('Guinier range', x=0.005, y=10)
p.text(r'Correlation peak\n at 2\xp\f{}N/R', x=0.4, y=5e-3)
p.text('Shell form factor', x=0.03, y=1e-6)
p.text(r'Shell structure factor', x=0.02, y=2e-5)
p[0].line(0.08, 1e-5, 2, 1e-5, 2, arrow=2)
if save: p.save('multilamellar3.png')

# Comparing multilamellar and unilamellar vesicle
dd = 2
dR = 5
nG = 100
ds = 0.2
p = js.grace(1, 1)
for i, R in enumerate([40, 50, 60], 1):
    mV = ffmV(Q=Q, R=R, displace=dd, dR=dR, N=4, dN=0, phi=0.2, layers=6, ds=ds, SLD=1e-4, nGauss=nG)
    p.plot(mV, sy=[i, 0.3, i], le='R= %g ' % R)
    p.plot(mV.X, mV[-1], sy=0, li=[3, 3, i])
    p.plot(mV.X, mV[-2] * 0.01, sy=0, li=[2, 3, i])

# comparison double sphere
mV = ffmV(Q=Q, R=50., displace=0, dR=5, N=1, dN=0, phi=1, layers=6, ds=ds, SLD=1e-4, nGauss=100)
p.plot(mV, sy=0, li=[1, 2, 4], le='unilamellar R=50 nm')
mV = ffmV(Q=Q, R=60., displace=0, dR=5, N=1, dN=0, phi=1, layers=6, ds=ds, SLD=1e-4, nGauss=100)
p.plot(mV, sy=0, li=[3, 2, 4], le='unilamellar R=60 nm')

p.legend(x=0.3, y=2e3)
p.title('Comparing multilamellar and unilamellar vesicle')
p.subtitle('R=%.2g nm, N=%.1g, layers=%s nm, dR=%.1g, ds=%.2g' % (R, N, 6, dR, ds))
p.yaxis(label='S(Q)', scale='l', min=1e-10, max=1e4, ticklabel=['power', 0])
p.xaxis(label='Q / nm\S-1', scale='l', min=1e-2, max=5, ticklabel=['power', 0])

p.text('Guinier range', x=0.02, y=1000)
p.text(r'Correlation peaks\n at 2\xp\f{}N/R', x=0.8, y=0.1)
p[0].line(0.8, 4e-2, 0.6, 4e-2, 2, arrow=2)
p.text('Shell form factor', x=1, y=1e-2, rot=335)
# p[0].line(0.2,4e-5,0.8,4e-5,2,arrow=2)
p.text(r'Shell structure factor\n x0.01', x=0.011, y=0.1, rot=0)
p.text('Shell form factor ', x=0.02, y=2e-6, rot=0)
if save: p.save('multilamellar4.png')

# Lipid bilayer in SAXS/SANS
# Values for layer thickness can be found in
# Structure of lipid bilayers
# John F. Nagle et al Biochim Biophys Acta. 1469, 159–195. (2000)
Q = js.loglist(0.01, 5, 500)
dd = 1.5
dR = 5
nG = 100
ds = 0.15  # variation of hydrocarbon layer thickness
R = 50
sd = [1.5, 3.5, 1.5]
N = 2

p = js.grace()
p.title('Multilamellar/unilamellar vesicle for SAXS/SANS')
# SAXS
sld = [0.07e-3, 0.6e-3, 0.07e-3]
saxm = ffmV(Q=Q, R=R, displace=dd, dR=dR, N=N, dN=0, phi=0.2, layers=sd, ds=ds, SLD=sld, solventSLD=0.94e-3, nGauss=nG)
p.plot(saxm, sy=0, li=[1, 1, 1], le='SAXS multilamellar')
saxu = ffmV(Q=Q, R=R, displace=0, dR=dR, N=1, dN=0, phi=0.2, layers=sd, ds=ds, SLD=sld, solventSLD=0.94e-3, nGauss=100)
p.plot(saxu, sy=0, li=[3, 2, 1], le='SAXS unilamellar')
saxu = ffmV(Q=Q, R=R, displace=0, dR=dR, N=1, dN=0, phi=0.2, layers=sd, ds=0, SLD=sld, solventSLD=0.94e-3, nGauss=100)
p.plot(saxu, sy=0, li=[2, 0.3, 1], le='SAXS unilamellar ds=0')

# SANS
sld = [0.3e-4, 1.5e-4, 0.3e-4]
sanm = ffmV(Q=Q, R=R, displace=dd, dR=dR, N=N, dN=0, phi=0.2, layers=sd, ds=ds, SLD=sld, solventSLD=6.335e-4, nGauss=nG)
p.plot(sanm, sy=0, li=[1, 1, 2], le='SANS multilamellar')
sanu = ffmV(Q=Q, R=R, displace=0, dR=dR, N=1, dN=0, phi=0.2, layers=sd, ds=ds, SLD=sld, solventSLD=6.335e-4, nGauss=100)
p.plot(sanu, sy=0, li=[3, 2, 2], le='SANS unilamellar')
sanu = ffmV(Q=Q, R=R, displace=0, dR=dR, N=1, dN=0, phi=0.2, layers=sd, ds=0, SLD=sld, solventSLD=6.335e-4, nGauss=100)
p.plot(sanu, sy=0, li=[2, 0.3, 2], le='SANS unilamellar ds=0')
sanu2 = ffmV(Q=Q, R=R, displace=0, dR=dR, N=1, dN=0, phi=0.2, layers=sd, ds=0, SLD=[0.09e-3, 0.6e-3, 0.07e-3],
             solventSLD=6.335e-4, nGauss=100)
p.plot(sanu2, sy=0, li=[1, 0.5, 4], le='SANS unilamellar asymmetric layer ds=0')

p.legend(x=0.013, y=3e-1, boxcolor=0, boxfillpattern=0)
p.title('Comparing multilamellar and unilamellar vesicle')
p.subtitle('R=%.2g nm, N=%.1g, layers=%s nm, dR=%.1g, ds=%.2g' % (R, N, sd, dR, ds))
p.yaxis(label='S(Q)', scale='l', min=1e-5, max=5e3, ticklabel=['power', 0])
p.xaxis(label='Q / nm\S-1', scale='l', min=1e-2, max=5, ticklabel=['power', 0])

p.text('Guinier range', x=0.03, y=2000)
p.text(r'Correlation peaks\n at 2\xp\f{}N/R', x=0.3, y=20)
p.text(r'For multilayers \n shoulder and peaky', x=0.8, y=0.8)
p[0].line(1.5, 0.1, 3.2, 0.25, 2, arrow=1)
p[0].line(0.7, 0.2, 1, 0.25, 2, arrow=1)
p.text('Shell form factor ds=0', x=0.1, y=0.5e-4)
p[0].line(0.2, 4e-5, 0.6, 4e-5, 2, arrow=2)
if save: p.save('multilamellar5.png')
