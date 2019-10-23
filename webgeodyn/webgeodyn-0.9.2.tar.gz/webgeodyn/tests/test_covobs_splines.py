import unittest
import os.path
import numpy as np
import scipy.signal

import webgeodyn.inout.covobs_splines as covspl

ABS_TOL = 1e-4


class TestBuildingFromSplines(unittest.TestCase):
    def setUp(self):
        file_folder = os.path.join(os.path.dirname(__file__), 'Spline_benchmark')
        self.spl_dates, self.spl_coeffs, self.spl_order, self.knot_sp = covspl.read_spline_coeffs_file(os.path.join(file_folder,'real_001'))

        raw_benchmark = np.genfromtxt(os.path.join(file_folder, 'real001_mf_int_coefs.dat'))
        self.dates_benchmark = raw_benchmark[:, 0]
        self.gnm_benchmark = raw_benchmark[:, 1:]

    def test_get_full_knots(self):
        n = len(self.spl_coeffs)
        full_knots = covspl.get_full_knots(self.spl_dates, self.spl_order, n)
        self.assertEqual(len(full_knots), n+self.spl_order+1)

    def test_eval_derivate_spline(self):
        dt = 0.1
        t = np.arange(1980, 1990, dt)
        center_date = np.random.choice(t)
        spl_order = 4
        knot_spacing = 1

        spline_array = covspl.eval_spline(t, center_date, spl_order, knot_spacing)
        numeric_derivative = scipy.signal.savgol_filter(spline_array, window_length=11, polyorder=3, deriv=1, delta=dt)
        spline_derivative = covspl.eval_derivative_spline(t, center_date, spl_order, knot_spacing)

        np.testing.assert_allclose(numeric_derivative, spline_derivative, atol=1e-2)

    def test_get_required_splines(self):
        """ Test that the date indexes required for the evaluation include ALL the non-zero splines """
        eval_date = np.random.choice(self.dates_benchmark)
        required_date_indexes = covspl.get_date_indexes_for_spl_eval(eval_date, self.spl_dates, self.spl_order)
        for j, center_date in enumerate(self.spl_dates):
            with self.subTest(date=center_date):
                if j not in required_date_indexes:
                    self.assertEqual(covspl.eval_spline(eval_date, center_date, self.spl_order, self.knot_sp), 0.)

    def test_building_gnm_few_splines(self):
        """ Test the method building from the splines  """
        dates_gnm, gnm = covspl.build_gnm_from_spline_coeffs(self.dates_benchmark, self.spl_dates, self.spl_coeffs, self.spl_order, with_derivatives=False)
        self.assertTrue(np.alltrue(np.abs(gnm - self.gnm_benchmark) < ABS_TOL))

    def test_building_gnm_all_splines(self):
        """ Test the old method building from all the splines """
        dates_gnm, gnm = covspl.build_gnm_from_spline_coeffs_old(self.dates_benchmark, self.spl_dates, self.spl_coeffs, self.spl_order, with_derivative=False, all_splines=True)
        self.assertTrue(np.alltrue(np.abs(gnm - self.gnm_benchmark) < ABS_TOL))

    def test_building_methods(self):
        """ Test that all methods give the same result """
        dates_gnm, gnm = covspl.build_gnm_from_spline_coeffs_old(self.dates_benchmark, self.spl_dates, self.spl_coeffs, self.spl_order, with_derivative=False, all_splines=False)
        dates_gnm_2, gnm_2 = covspl.build_gnm_from_spline_coeffs_old(self.dates_benchmark, self.spl_dates, self.spl_coeffs, self.spl_order, with_derivative=False, all_splines=True)
        dates_gnm_3, gnm_3 = covspl.build_gnm_from_spline_coeffs(self.dates_benchmark, self.spl_dates, self.spl_coeffs, self.spl_order, with_derivatives=False)
        np.testing.assert_equal(gnm, gnm_2)
        # Almost_equal as it uses different implementation of the bsplines (sp.signal.bspline vs. sp.interpolate.Bspline)
        np.testing.assert_almost_equal(gnm, gnm_3)


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TestBuildingFromSplines)
    RES = unittest.TextTestRunner(verbosity=2).run(SUITE)
    import sys
    sys.exit(max(len(RES.failures), len(RES.errors)))
