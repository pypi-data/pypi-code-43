# -*- coding: utf-8 -*-
# written by Ralf Biehl at the Forschungszentrum Jülich ,
# Jülich Center for Neutron Science 1 and Institute of Complex Systems 1
#    Jscatter is a program to read, analyse and plot data
#    Copyright (C) 2015-2019  Ralf Biehl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""

This file is for testing of basic functions in dataarray and related modules.

Run as ::

 cd jscatter/directory
 python test.py

Test a single case or subcase
::

 ipython3 -m unittest jscatter.test.dataListTest.test_basic_merge

"""

import unittest
import os
import numpy.testing as nptest
import warnings

# noinspection PyPackageRequirements
import jscatter as js
import numpy as np
import scipy
from scipy import special
import pickle
from numpy import linalg as la

asciitext = """# these are really ugly data
 # temp     ;    293 1 2 3 4 5 6
 # pressure ; 1013 14  bar
 # @name     ; temp1bsa
 &doit
 0,854979E-01  0,178301E+03  0,383044E+02
 0,882382E-01  0,156139E+03  0,135279E+02
 0,909785E-01  **            0,110681E+02
 0,937188E-01  0,147430E+03  0,954762E+01
 0,964591E-01  0,141615E+03  0,846613E+01
 nan           nan           0
 1 2 3

# these are more really ugly data
 # temp     ;    1000 1 2 3 4 5 6
 # pressure ; 1013 12  bar
 # @name     ; temp2bsa
 &doit
 link @linktest
 1 2 3 0.
 2 1 2 3.
 3 1 2 .3
 4 1 2 .3
 5 1 2 .3
 6 1 2 .3
 nan  nan  0 0
 7 2 3 0

 @name linktest
 1 2 3 4 
 2 3 4 5 

"""


class dataArrayTest(unittest.TestCase):
    """
    Test for dataArray and access of all inside
    """

    setupdone = False

    @classmethod
    def setUp(self):
        if self.setupdone: return

        # create some data to test
        self.x = np.r_[0:10:0.1]
        x = self.x
        # simulate data with error
        self.data = js.dA(np.c_[x, 1.234 * np.sin(x) + 0.001 * np.random.randn(len(x)), x * 0 + 0.001].T)
        self.data.amp = 1.234
        self.data.fit(lambda x, A, a, B: A * np.sin(a * x) + B, {'a': 1.2, 'B': 0}, {}, {'x': 'X', 'A': 'amp'},
                      output=False)
        x = np.r_[0:100:]
        self.data2 = js.dA(np.c_[x, x * 0 + 1., x * 0, x * 0].T)
        self.data2.test = 'dumdum'
        self.data2.Y[1::4] = 2
        self.data2.Y[2::4] = 4
        self.data2.Y[3::4] = 5

        with open('asciitestfile.dat', 'w') as f:    (f.write(asciitext))
        self.data4 = js.dA('asciitestfile.dat', replace={'#': '', ';': '', ',': '.'}, skiplines=['*', '**', 'nan'],
                           ignore='')
        self.data5 = js.dA('asciitestfile.dat', replace={'#': '', ';': '', ',': '.'},
                           skiplines=lambda w: any(a in ['**', 'nan'] for a in w), ignore='', index=1)
        self.data5.save('asciitestfile2.dat')
        self.data6 = js.dA('asciitestfile2.dat')

        self.setupdone = True

    @classmethod
    def tearDown(self):
        try:
            os.remove('asciitestfile.dat')
            os.remove('asciitestfile2.dat')
        except:
            pass

    def test_interpolate(self):
        self.data2[2]=0.1
        self.data2[3]=self.data2.Y
        # interp
        interp=self.data2.interp(np.r_[-1,1.5:4.5:1])
        nptest.assert_array_almost_equal(interp, [1, 3., 4.5, 3.])
        # interpolate
        interpolate=self.data2.interpolate(np.r_[-1, 1.5:4.5:1])

        nptest.assert_array_almost_equal(interpolate.Y, [1, 3., 4.5, 3.])
        nptest.assert_array_almost_equal(interpolate.shape, (2, 4))

        interpolatedeg2 = self.data2.interpolate(np.r_[0, 1.5:4.5:1], deg=2)
        nptest.assert_array_almost_equal(interpolatedeg2.Y, [1, 2.93933983, 5.01040764, 2.99821433], 6)
        interpolateALL = self.data2.interpAll(np.r_[0, 1.5:4.5:1])
        nptest.assert_array_almost_equal(interpolateALL.Y, [1, 3., 4.5, 3.])
        nptest.assert_array_almost_equal(interpolateALL[-1], [1, 3., 4.5, 3.])

    def test_stuff(self):
        # test if this results in single float/array
        self.assertEqual(self.data.max(), 9.9)

    def test_polyfit(self):
        t = np.r_[0:100:]
        q=0.5
        D=0.2
        data = js.dA(np.c_[t, np.exp(-q**2*D*t)].T)
        data2=data.polyfit([10, 20, 40], deg=1, function=np.log)
        nptest.assert_array_almost_equal(np.exp(data2.Y), np.exp(-q**2*D*np.r_[10, 20, 40]))


    def test_fitchi2(self):
        # self.assertEqual( self.data.X,self.x )
        self.assertTrue(np.alltrue(self.data.X == self.x))
        self.assertLess(abs(self.data.lastfit.A - self.data.amp), 0.01)
        self.assertLess(abs(self.data.B), 0.1)
        self.assertLess(abs(self.data.lastfit.chi2 - 1), 0.5)

    def test_prune(self):
        data3 = self.data2[:2].prune(lower=7, number=25, type='mean+')
        self.assertEqual(data3.Y[-1], 3)
        self.assertAlmostEqual(data3.eY[-1], 1.58113883)
        self.assertEqual(data3.shape[1], 25)
        self.assertEqual(data3.X[0], 8.5)
        self.assertTrue(data3.test == 'dumdum')
        # test types
        sums = js.dA(np.c_[1:101, 0:100].T).prune(number=9, type='sum')
        mean = js.dA(np.c_[1:101, 0:100].T).prune(number=9, type='mean')
        self.assertEqual(sums.X[5], 61.0)
        self.assertEqual(sums.Y[5], 660.)
        self.assertListEqual((sums.Y / sums[-1]).tolist(), mean.Y.tolist())

    def test_readwrite(self):
        self.assertEqual(self.data4.pressure[0], self.data5.pressure[0])
        self.assertEqual(self.data4.X[4], 1)
        self.assertEqual(self.data4[2, 4], 3)
        self.assertEqual(self.data4.pressure[-1], 'bar')
        self.assertEqual(self.data5.link.X[1], 2.0)
        self.assertEqual(self.data6.link.X[1], self.data5.link.X[1])
        self.assertEqual(self.data6.comment[1], self.data5.comment[1])

    def test_regrid(self):
        func = lambda x, y: x * (1 - x) * np.cos(np.pi * x) * np.sin(np.pi * y ** 2) ** 2 * 10
        xz = js.parallel.randomPointsInCube(400, 0, 2) * 0.2 + 0.4
        v = func(xz[:, 0], xz[:, 1])
        data = js.dA(np.stack([xz[:, 0], xz[:, 1], v], axis=0), XYeYeX=[0, 2, None, None, 1, None])
        xx = np.r_[0.42:0.58:0.04]
        #newdata = data.regrid(xx, xx, method='nearest')
        newdata = data.regrid(xx, xx, method='linear')
        np.testing.assert_array_almost_equal(func(newdata.X, newdata.Z), newdata.Y, 1)


class dataListTest(unittest.TestCase):
    """
    Test for dataList and access of all inside

    Fit includes access of attributes and lot more
    if it is working it should be ok

    """

    setupdone = False

    @classmethod
    def setUp(self):
        if self.setupdone: return

        # data
        self.diff = js.dL(os.path.join(js.examples.datapath, 'iqt_1hho.dat'))
        self.diffm = self.diff.copy()

        def model(A, D, t, wave=0):
            return A * np.exp(-wave ** 2 * D * t)

        self.diff.fit(model, {'D': [0.1], 'A': 1}, {}, {'t': 'X', 'wave': 'q'}, condition=lambda a: a.X > 0.01,
                      output=False)
        # save should not save lastfit but list attributes
        self.diff.save('testdiffreread.dat')
        self.diffread = js.dL('testdiffreread.dat')
        self.pfdat = js.dL([js.dynamic.simpleDiffusion(q, np.r_[1:100:5], 1, 0.05) for q in np.r_[0.2:2:0.4]])
        self.pfdat[:3].save('pfdattestwrite.dat')
        self.pfreread = js.dL('pfdattestwrite.dat')
        self.pfreread.append('pfdattestwrite.dat', index=-1, XYeYeX=(0, 2, 1))  # take last and change Y,eY columns

        self.serializedm = pickle.dumps(self.diffm.copy())
        self.serialized = pickle.dumps(self.diff.copy())

        self.setupdone = True

    @classmethod
    def tearDown(self):
        try:
            os.remove('pfdattestwrite.dat')
            os.remove('testdiffreread.dat')
        except:
            pass

    def test_basic_merge(self):
        # test mergeAttribut
        diffm = self.diff.copy()
        diffm.mergeAttribut('q')
        self.assertAlmostEqual(diffm.qmean[4], 0.65, places=4)

    def test_basic_append(self):
        # test pop insert append
        diffm1 = self.diff.copy()
        diffm1.pop(10)
        diffm1.insert(10, os.path.join(js.examples.datapath, 'iqt_1hho.dat'), index=2)
        diffm1.append(os.path.join(js.examples.datapath, 'iqt_1hho.dat'), index=2)
        self.assertEqual(diffm1[10].q, 0.4)
        self.assertEqual(diffm1[-1].q, 0.4)

    def test_fit(self):

        self.assertEqual(self.diff[0]._time[-1], 100.)
        self.assertAlmostEqual(self.diff.D[0], 0.086595, 5)
        self.assertAlmostEqual(self.diff.D_err.mean(), 0.00188324, 5)
        self.assertAlmostEqual(self.diff.A[0], 0.99, 2)
        self.assertAlmostEqual(self.diff.lastfit.chi2, 0.99, 2)
        # test polyfit
        pfcalc = js.dynamic.simpleDiffusion(0.4, np.r_[1:100:5], 1, 0.05).Y
        pffit = self.pfdat.polyfit(wavevector=0.4, func=np.log, invfunc=np.exp, degy=2).Y
        self.assertAlmostEqual((pffit - pfcalc).sum(), 0)

    def test_readwritetest(self):
        # Test if file was read correctly
        self.assertAlmostEqual(self.pfdat[2].Y[-1], self.pfreread[-2].Y[-1])
        # test if append worked and Y and ey are changed
        self.assertAlmostEqual(self.pfdat[2].Y[-1], self.pfreread[-1].eY[-1])
        # test if dataList reread is working
        # test for length
        self.assertEqual(len(self.diff), len(self.diffread))
        # test common attributes
        self.assertAlmostEqual(self.diff.D_err[-1], self.diffread.D_err[-1], delta=1e-12)
        self.assertAlmostEqual(self.diff.D[-1], self.diffread.D[-1], delta=1e-12)

    def test_pickle(self):
        # normal pickle of dataList
        restoredm = pickle.loads(self.serializedm)
        nptest.assert_array_equal(restoredm[3].Y, self.diffm[3].Y)
        # model was lambda an cannot be pickled so it is removed
        restored = pickle.loads(self.serialized)
        nptest.assert_array_equal(restored[3].Y, self.diff[3].Y)
        self.assertEqual(restored.model, 'removed during serialization')


def f(x, a, b, c, d):
    return [x, x + a + b + c + d]


class parallelTest(unittest.TestCase):
    """
    Test for parallel
    """

    def test_parallel(self):
        # loop over first argument, here x
        abcd = [1, 2, 3, 4]
        res = js.parallel.doForList(f, looplist=np.arange(100), a=abcd[0], b=abcd[1], c=abcd[2], d=abcd[3])
        self.assertEqual(res[0][0] + np.sum(abcd), res[0][1])
        self.assertEqual(res[-1][0] + np.sum(abcd), res[-1][1])

    def test_random(self):
        # points on sphere
        r = js.formel.fibonacciLatticePointsOnSphere(1000)
        fibzero = la.norm(js.formel.rphitheta2xyz(r).mean(axis=0))
        # pseudorandom gives always same numbers
        pr = js.formel.randomPointsOnSphere(1000)
        pseudorandomcenter = la.norm(js.formel.rphitheta2xyz(pr).mean(axis=0))
        self.assertAlmostEqual(fibzero, 6.148627865656653e-06, 7)
        self.assertAlmostEqual(pseudorandomcenter, 0.0031693025, 7)
        #
        # halton sequence test
        # without fortran we test several times python
        useFortran = js.parallel.useFortran
        if useFortran:
            haltonfortran = js.parallel.haltonSequence(10, 2, 5)
            self.assertAlmostEqual(haltonfortran[1, 4], 0.370370370, 7)
            self.assertAlmostEqual(haltonfortran[0, 9], 0.9375, 7)
        # test python version
        js.parallel.useFortran = False
        haltonpython = js.parallel.haltonSequence(10, 2, 5)
        js.parallel.useFortran = useFortran # reset

        if useFortran:
            np.testing.assert_allclose(haltonfortran, haltonpython)


class formelTest(unittest.TestCase):
    """
    Test for som things in formel
    """

    def test_otherStuff(self):
        # Ea
        z = np.linspace(-2., 2., 50)
        self.assertTrue(np.allclose(js.formel.Ea(z ** 2, 2.), np.cosh(z)))
        z = np.linspace(0., 2., 50)
        self.assertTrue(np.allclose(js.formel.Ea(np.sqrt(z), 0.5), np.exp(z) * special.erfc(-np.sqrt(z))))
        x = np.r_[-10:10:0.1]
        self.assertTrue(np.all(js.formel.Ea(x, 1, 1) - np.exp(x) < 1e-10))

    def test_materialData(self):
        naclwater = ['55.55h2o1', '0d2o1', '0.1Na1Cl1']
        waterelectrondensity = js.formel.scatteringLengthDensityCalc(naclwater, T=237.15 + 20)
        self.assertAlmostEqual(waterelectrondensity[1], 334.329, delta=1e-2)
        self.assertAlmostEqual(js.formel.waterdensity(['55.55h2o1']), 0.9982071296, 7)
        self.assertAlmostEqual(js.formel.waterdensity(['55.55h2o1', '2.5Na1Cl1']), 1.096136675, 7)
        self.assertAlmostEqual(js.formel.bufferviscosity(['55.55h2o1', '1sodiumchloride']), 0.0010965190497, 7)
        self.assertAlmostEqual(js.formel.watercompressibility(units=1), 5.15392074e-05, 7)
        self.assertAlmostEqual(js.formel.viscosity(), 0.0010020268897, 7)

    def test_quadrature(self):
        # integration
        t = np.r_[0:150:0.5]
        D = 0.3
        ds = 0.01
        diff = js.dynamic.simpleDiffusion(t=t, q=0.5, D=D)
        distrib = scipy.stats.norm(loc=D, scale=ds)
        x = np.r_[D - 5 * ds:D + 5 * ds:30j]
        pdf = np.c_[x, distrib.pdf(x)].T
        diff_g = js.formel.parQuadratureSimpson(js.dynamic.simpleDiffusion, -3 * ds + D, 3 * ds + D, parname='D',
                                                          weights=pdf, tol=0.01, q=0.5, t=t)
        gaussint = js.formel.parQuadratureAdaptiveGauss(js.formel.gauss, -20, 120, 'x', mean=50, sigma=10)

        self.assertTrue(all(np.abs((diff.Y - diff_g.Y)) < 0.005))
        self.assertAlmostEqual(gaussint.Y[0], 1, 7)

        # convolution
        s1 = 3
        s2 = 4
        m1 = 50
        m2 = 10
        G1 = js.formel.gauss(np.r_[0:100.1:0.1], mean=m1, sigma=s1)
        G2 = js.formel.gauss(np.r_[-30:30.1:0.2], mean=m2, sigma=s2)
        ggf = js.formel.convolve(G1, G2, 'full')
        gg = js.formel.convolve(G1, G2, 'valid')

        self.assertAlmostEqual(gg.Y.max(), ggf.Y.max(), 7)
        self.assertAlmostEqual(gg.X[gg.Y.argmax()], 60, 7)
        self.assertAlmostEqual(gg.X[gg.Y.argmax()], ggf.X[ggf.Y.argmax()], 7)
        self.assertAlmostEqual(ggf.X.max(), 130, 7)
        self.assertAlmostEqual(gg.X.max(), 70, 7)

        # smooth
        t = np.r_[-3:3:0.01]
        data = np.sin(t) + (js.formel.randomPointsInCube(len(t), 1000, 1).T[0] - 0.5) * 0.1
        smooth = js.dA(np.vstack([t, data]))
        smooth.Y = js.formel.smooth(smooth, windowlen=40, window='gaussian')

        self.assertAlmostEqual(smooth.X[smooth.Y.argmax()] / np.pi, 0.5061127, 6)


class structurefactorTest(unittest.TestCase):
    """
    Test for structurefactor
    """

    def test_PYRMSA(self):
        q = np.r_[0:5:0.5]
        q1 = js.loglist(0.01, 100, 2 ** 13)
        R = 2.5
        eta = 0.3
        scl = 5
        PY = js.sf.PercusYevick(q, 3, eta=0.2)
        RMSA = js.sf.RMSA(q, 3, 1, 0.001, eta=0.2)
        RMSA2 = js.sf.RMSA(q, 3, 1, 4.00, eta=0.3)

        sfh = js.sf.RMSA(q=q1, R=R, scl=scl, gamma=0.01, eta=eta)
        grh = js.sf.sq2gr(sfh, R, interpolatefactor=1)

        # both like hard Sphere if small surface potential
        self.assertAlmostEqual(PY.Y[0], RMSA.Y[0], delta=1e-3)
        self.assertAlmostEqual(RMSA2.Y[0], 0.09347659, delta=1e-3)
        # Test of RMSA and sq2gr for correct q and Y value.
        self.assertAlmostEqual(grh.prune(lower=5).Y[0], 2.24010143, delta=1e-6)

    def test_latticePeaks(self):
        fcc = js.sf.fccLattice(2, 1)
        fccSq = js.sf.latticeStructureFactor(np.r_[0.1:4:0.1], fcc)

        # peak positions in fcc crystal, test for lattices
        self.assertAlmostEqual(fccSq.q_hkl[0], 5.441398, delta=1e-6)
        self.assertAlmostEqual(fccSq.q_hkl[10], 17.77153170, delta=1e-6)


class formfactorTest(unittest.TestCase):
    """
    Test for formfactor
    """

    setupdone = False

    @classmethod
    def setUp(self):
        if self.setupdone: return

        self.csSphereI = js.ff.sphereCoreShell(0, 1., 2., -7., 1.).Y[0]
        R = 2
        NN = 10
        grid = np.mgrid[-R:R:1j * NN, -R:R:1j * NN, -R:R:1j * NN].reshape(3, -1).T
        p2 = 1 * 2  # p defines a superball with 1->sphere p=inf cuboid ....
        inside = lambda xyz, R: (np.abs(xyz[:, 0]) / R) ** p2 + (np.abs(xyz[:, 1]) / R) ** p2 + (
                np.abs(xyz[:, 2]) / R) ** p2 <= 1
        insidegrid = grid[inside(grid, R)]
        # takes about 1.9 s on single core
        self.cloudsphere = js.ff.cloudScattering(np.r_[0, 2.3], insidegrid, relError=50)
        self.gauss = js.ff.gaussianChain(np.r_[3:5:0.05], 5)

        self.setupdone = True

    def test_formfactor(self):
        # designed to have forward scattering equal zero
        self.assertEqual(self.csSphereI, 0)
        # This should get the minimum of the sphere formfactor at 2.3
        self.assertAlmostEqual(self.cloudsphere.Y[1], 1.27815704e-04)
        # normalization to one
        self.assertAlmostEqual(self.cloudsphere.Y[0], 1.)
        # mean of plateau in kratky plot
        self.assertAlmostEqual(np.diff(self.gauss.Y * self.gauss.X ** 2).mean(), 5.7681188e-6, delta=1e-4)


class sasTest(unittest.TestCase):
    """
    Test for sas
    """

    setupdone = False

    @classmethod
    def setUp(self):
        if self.setupdone: return

        self.q = np.r_[0.5:2:0.005]

        # test sasImage calibration
        self.calibration = js.sas.sasImage(os.path.join(js.examples.datapath, 'calibration.tiff'))
        self.calibration.recalibrateDetDistance()
        self.small = self.calibration.reduceSize(2, self.calibration.center, 200)
        small=self.small.copy()
        self.small.data[:, :] = 100
        self.small.maskCircle([50, 50], 20)
        smalla = self.small.asdataArray('linear')
        #smalla = self.small.asdataArray('nearest')
        self.smallamax = smalla[:, (np.abs(smalla.X) < 1) & (np.abs(smalla.Z) < 1)].max()
        small.maskSectors([30, 30 + 180], 20, radialmax=100, invert=True)
        ismall = small.radialAverage()
        self.ismallYmax = ismall.Y[ismall.Y.argmax()]
        self.ismallXmax = ismall.X[ismall.Y.argmax()]
        # some lattices
        self.silicon = js.sf.diamondLattice(0.543, 1).getScatteringAngle(size=5)
        vv=js.sf.latticeVectorsFromLatticeConstants(0.4131, 0.4131, 0.4131, 54.15, 54.15, 54.15)
        self.arsenic = js.sf.rhombicLattice(vv, [3, 3, 3]).getScatteringAngle(size=3, wavelength=0.1541838)
        self.silver = js.sf.fccLattice(0.40875, 1).getScatteringAngle(size=5)

        try:
            with warnings.catch_warnings():
                # temporarily switch of pymatgen generated user warning
                warnings.simplefilter("ignore")
                # try if pymatgen is present
                # noinspection PyPackageRequirements
                import pymatgen
                siliconcarbide = pymatgen.Structure.from_file(js.examples.datapath+'/1011053.cif')
                self.sic=js.sf.latticeFromCIF(siliconcarbide)
        except ImportError:
            self.sic=None

        self.setupdone = True

    @classmethod
    def tearDown(self):
        try:
            # os.remove('sasImage_test.tiff')
            # os.remove('sasImage_test.jpg')
            os.remove('floattif.tif')
            os.remove('i32tif.tif')
        except OSError:
            pass

    def test_sas(self):
        # peak position of AgBe reference
        AgBeref = js.sas.AgBeReference(self.q, 0.58378)
        self.assertAlmostEqual(AgBeref.X[AgBeref.Y.argmax()], 1.076, delta=1e-3)

        self.assertAlmostEqual(self.calibration.detector_distance[0], 0.18078, delta=1e-4)
        self.assertAlmostEqual(self.smallamax, 100)
        self.assertAlmostEqual(self.ismallXmax, 1.076, delta=5e-3)
        self.assertAlmostEqual(self.ismallYmax, 824.147, delta=1e-2)

    def test_smear(self):
        empty = js.dA(js.examples.datapath + '/buffer_averaged_corrected_despiked.pdh',
                      usecols=[0, 1], lines2parameter=[2, 3, 4])
        bwidth = js.sas.getBeamWidth(empty, 'auto')
        self.assertAlmostEqual(bwidth.sigma, 0.01132, 4)
        self.assertAlmostEqual(bwidth.A, 0.893158, 4)
        self.assertAlmostEqual(bwidth.mean, 0.000355, 4)

        # test smear for SANS data
        sphere = js.ff.sphere(js.loglist(0.1, 3, 100), 3)
        Sbeam = js.sas.prepareBeamProfile('SANS', detDist=2000, wavelength=0.4,
                                          wavespread=0.15, extrapolfunc=['guinier', None])
        sphereS = js.sas.smear(unsmeared=sphere, beamProfile=Sbeam)
        self.assertAlmostEqual(sphereS.Y[0], 12209.79, 1)
        nptest.assert_array_almost_equal(sphereS.prune(1.4, 1.8).Y,
                                         [88.932, 56.746, 39.892, 35.097, 38.907, 47.885, 58.821, 68.946], 3)

        # test smear as decorator including change of detDist
        Sbeam2 = js.sas.prepareBeamProfile('SANS', detDist=8000, wavelength=0.4,
                                           wavespread=0.15, extrapolfunc=['guinier', None])
        spherewithdistance = lambda q, R, detDist: js.ff.sphere(q=q, radius=R)
        sphere2 = js.sas.smear(unsmeared=spherewithdistance, beamProfile=Sbeam2)
        sphereS2 = sphere2(q=js.loglist(0.1, 3, 100), R=3, detDist=2000)
        self.assertAlmostEqual(sphereS2.Y[0], 12210.62, 1)
        nptest.assert_array_almost_equal(sphereS2.prune(1.4, 1.8).Y,
                                         [88.932, 56.746, 39.892, 35.097, 38.907, 47.885, 58.821, 68.946], 3)
        # test desmearing
        desmeared = js.sas.desmear(sphereS, Sbeam, NIterations=-15, windowsize=5, output=False)
        self.assertAlmostEqual(np.sum(desmeared.prune(1.4, 1.8).Y -
                                      np.r_[41.640, 23.321, 15.827, 15.705, 21.880, 34.009, 50.489, 67.958]), 0, 2)

    def test_savetif(self):
        cal = self.small.copy()
        cal2 = cal * 0.1
        cal2.saveAsTIF('floattif')
        cal.saveAsTIF('i32tif')
        mycal2 = js.sas.sasImage('floattif.tif')  # as float
        mycal = js.sas.sasImage('i32tif.tif')  # as integer
        nptest.assert_array_almost_equal(cal2, mycal2)
        nptest.assert_array_almost_equal(cal, mycal)

    def test_averageAroundZero(self):
        # create image with random 0,1 entries which in average give 0.5 after Ewald correction
        lotofzeros=self.small.copy()
        # pseudorandom for reproducibility instead of random numbers
        rand= js.formel.randomPointsInCube(lotofzeros.shape[0] * lotofzeros.shape[1], 137, dim=1)
        lotofzeros[:, :]=np.trunc(rand.flatten().reshape(lotofzeros.shape[0], -1)*2)
        ilotofzeros=lotofzeros.radialAverage(number=100)
        # angle = 2*np.arcsin(q*wavelength/10./4./np.pi)    # wavelength in nm
        # Ewald sphere correction lpl0**3  with lpl0 = 1. / np.cos(angle)
        lpl0=1/np.cos(2*np.arcsin(ilotofzeros.X*lotofzeros.wavelength[0]/10./4./np.pi))
        ilotofzeros.Y/=lpl0**3
        mean=ilotofzeros.prune(lower=4, weight=None).Y.mean()
        self.assertAlmostEqual(mean, 0.50, delta=0.001)

    def test_lattices(self):
        # compare lattice scattering angles to known structures
        # silicon diamond lattice http://rruff.info/Silicon
        np.testing.assert_array_almost_equal(self.silicon[:6],
                                             [28.447, 47.311, 56.133, 69.143, 76.392, 88.049], decimal=3)
        # Arsenic rhombic
        # http://rruff.info/repository/sample_child_record_powder/by_minerals/
        # Arsenic__R050653-1__Powder__DIF_File__4696.txt
        np.testing.assert_array_almost_equal(self.arsenic[:7],
                                             [25.36, 28.70, 32.32, 44.20, 48.40, 51.62, 52.03], decimal=1)
        # silver http://rruff.info/repository/sample_child_record_powder/by_minerals/
        # Silver__R070416-1__Powder__DIF_File__8489.txt
        np.testing.assert_array_almost_equal(self.silver[:5],
                                             [38.17, 44.35, 64.48, 77.43, 81.57], decimal=1)
        if self.sic is not None:
            np.testing.assert_array_almost_equal(self.sic.getScatteringAngle(size=13)[:10],
                            [33.93, 35.47, 35.49, 37.96, 41.20, 45.09, 54.39, 59.68, 59.70, 65.34], decimal=2)

    def _test_imagewriting(self):
        # the test fails as on the gitlab served other hash result as on ifflinux or private

        small = self.calibration.copy()
        small.saveAsImage('sasImage_test.tiff', compression=None)
        readsmall = js.sas.sasImage('sasImage_test.tiff')
        # with open('sasImage_test.tiff', 'rb') as tiffile:
        #     buftif = tiffile.read()
        # tiff_hash = hashlib.md5(buftif).hexdigest()

        # test image file md5 hashes
        # self.assertEqual(tiff_hash, '4512a97fee722dce36487eab85be3639')
        # self.assertEqual(jpg_hash, '1dd387f8a153478a90f28d426fd48f4b')
        nptest.assert_array_almost_equal_nulp(small.data, readsmall.data)


class dynamicTest(unittest.TestCase):
    """
    Test for dynamic
    """

    setupdone = False

    @classmethod
    def setUp(self):
        if self.setupdone: return

        w = np.r_[-100:100:0.5]
        start = {'s0': 6, 'm0': 0, 'a0': 1, 's1': None, 'm1': 0, 'a1': 1, 'bgr': 0.00}
        resolution = js.dynamic.resolution_w(w, **start)
        D = 0.035
        qq = 5  # diffusion coefficient of protein alcohol dehydrogenase (140 kDa) is 0.035 nm**2/ns

        self.diff_ffw = js.dynamic.time2frequencyFF(js.dynamic.simpleDiffusion, resolution, q=qq, D=D)
        diff_w = js.dynamic.transDiff_w(w, q=qq, D=D)
        self.diff_cw = js.dynamic.convolve(diff_w, resolution, normB=1)

        self.setupdone = True

    def test_time2frequencyFF(self):
        X = self.diff_cw.X
        # compare diffusion with convolution and transform from time domain
        self.assertTrue(np.all(np.abs(
            (self.diff_ffw.interp(self.diff_cw.X[abs(X) < 70]) - self.diff_cw.Y[abs(X) < 70]) / self.diff_cw.Y[
                abs(X) < 70]) < 0.025))


def suite():
    loader = unittest.TestLoader()
    s = unittest.TestSuite()
    s.addTest(loader.loadTestsFromTestCase(dataListTest))
    s.addTest(loader.loadTestsFromTestCase(dataArrayTest))
    s.addTest(loader.loadTestsFromTestCase(parallelTest))
    s.addTest(loader.loadTestsFromTestCase(formelTest))
    s.addTest(loader.loadTestsFromTestCase(formfactorTest))
    s.addTest(loader.loadTestsFromTestCase(structurefactorTest))
    s.addTest(loader.loadTestsFromTestCase(sasTest))
    s.addTest(loader.loadTestsFromTestCase(dynamicTest))
    return s


def doTest2(verbosity=1):
    """Do only one test."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(parallelTest))
    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(suite)

    return


def doTest(verbosity=1):
    """
    Do some test on Jscatter.

    Parameters
    ----------
    verbosity : int, default 1
        Verbosity level


    """
    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(suite())


if __name__ == '__main__':
    unittest.main()
