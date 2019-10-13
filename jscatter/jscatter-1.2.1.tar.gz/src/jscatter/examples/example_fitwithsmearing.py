import jscatter as js
import numpy as np
q=js.loglist(0.01, 2, 300)

# prepare smeared data
# in practical case these are from a measurement
# and need only additional the .beamProfile attribute


def sphere(q, R, bgr, contrast=1):
    sp = js.ff.sphere(q, R, contrast)
    sp.Y=sp.Y+bgr
    return sp


# prepare different beamprofiles
beam=js.sas.readpdh(js.examples.datapath+'/BeamProfile.pdh')
mbeam = js.sas.prepareBeamProfile(beam, bxw=0.01, dIW=1.)
Sbeam1 = js.sas.prepareBeamProfile('SANS', detDist=1000,wavelength=0.4,wavespread=0.1)
Sbeam2 = js.sas.prepareBeamProfile('SANS', detDist=10000,wavelength=0.4,wavespread=0.1)
fbeam = js.sas.prepareBeamProfile(0.02)  # explicit given width

# smear data and add individual beamprofiles
sig=1
data=sphere(q, R=13, bgr=2, contrast=1e-2).addColumn(1, sig)
data.Y=data.Y+np.random.randn(data.shape[1])*sig
smeared=js.dL()
smeared.append(js.sas.smear(unsmeared=data, beamProfile=mbeam))
smeared[-1].beamProfile=mbeam
smeared.append(js.sas.smear(unsmeared=data, beamProfile=Sbeam1))
smeared[-1].beamProfile=Sbeam1
smeared.append(js.sas.smear(unsmeared=data, beamProfile=Sbeam2))
smeared[-1].beamProfile=Sbeam2
smeared.append(js.sas.smear(unsmeared=data, beamProfile=fbeam))
smeared[-1].beamProfile=fbeam


# define smeared model with beamProfile as parameter
@js.sas.smear(beamProfile=fbeam)
def smearedsphere(q ,R, bgr, contrast=1, beamProfile=None):
    sp = js.ff.sphere(q=q, radius=R, contrast=contrast)
    sp.Y=sp.Y+bgr
    return sp


# fit it
smeared.setlimit(bgr=[1])
smeared.makeErrPlot(yscale='l', fitlinecolor=[1, 2, 5])
smeared.fit(smearedsphere, {'R': 13, 'bgr': 1, 'contrast': 1e-2}, {}, {'q': 'X'})

