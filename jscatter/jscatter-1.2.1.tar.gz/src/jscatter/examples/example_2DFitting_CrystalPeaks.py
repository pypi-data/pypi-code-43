import jscatter as js
import numpy as np

# load a image with hexagonal peaks (synthetic data)
image = js.sas.sasImage(js.examples.datapath + '/2Dhex.tiff')
image.setPlaneCenter([51, 51])
image.gaussianFilter()
# transform to dataarray with X,Z as wavevectors
# The fit algorithm works also with masked areas
hexa = image.asdataArray(0)


def latticemodel(qx, qz, R, ds, rmsd, hklmax, bgr, I0):
    # a hexagonal grid with background, domain size and Debye Waller-factor (rmsd)
    # 3D wavevector
    qxyz = np.c_[qx, qz, np.zeros_like(qx)]
    # define lattice
    grid = js.sf.hcpLattice(R, [3, 3, 3])
    # here one may rotate the crystal

    # calc scattering
    lattice = js.sf.orientedLatticeStructureFactor(qxyz, grid, domainsize=ds, rmsd=rmsd, hklmax=hklmax)
    # add I0 and background
    lattice.Y = I0 * lattice.Y + bgr
    return lattice


# Because of the high plateau in the chi2 landscape
# we first need to use a algorithm finding a global minimum
# this needs around 2300 evaluations and some time
if 0:
    # Please do this if you want to wait
    hexa.fit(latticemodel, {'R': 2, 'ds': 10, 'rmsd': 0.1, 'bgr': 1, 'I0': 10},
             {'hklmax': 4, }, {'qx': 'X', 'qz': 'Z'}, method='differential_evolution')
    #
    fig = js.mpl.surface(hexa.X, hexa.Z, hexa.Y, image.shape)
    fig = js.mpl.surface(hexa.lastfit.X, hexa.lastfit.Z, hexa.lastfit.Y, image.shape)

# We use as starting parameters the result of the previous fit
# Now we use LevenbergMarquardt algorithm to polish the result
hexa.fit(latticemodel, {'R': 3.02, 'ds': 12., 'rmsd': 0.24, 'bgr': 3.1, 'I0': 31},
         {'hklmax': 4, }, {'qx': 'X', 'qz': 'Z'})

fig = js.mpl.surface(hexa.X, hexa.Z, hexa.Y, image.shape)
fig.suptitle('original')
fig.show()
fig2 = js.mpl.surface(hexa.lastfit.X, hexa.lastfit.Z, hexa.lastfit.Y, image.shape)
fig2.suptitle('fit result')
fig2.show()
fig3 = js.mpl.surface(hexa.lastfit.X, hexa.lastfit.Z, hexa.lastfit.Y-hexa.Y, image.shape)
fig3.suptitle('difference')
fig3.show()


