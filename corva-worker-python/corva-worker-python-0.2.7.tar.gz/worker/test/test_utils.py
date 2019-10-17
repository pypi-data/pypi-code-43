import unittest
import numpy as np
from worker.data import math
from worker.data.operations import is_number, to_number, none_to_nan, is_finite


class TestGeneral(unittest.TestCase):
    def test_data_utils(self):
        self.assertFalse(is_number("nan"))
        self.assertFalse(is_number(None))
        self.assertFalse(is_number(""))
        self.assertFalse(is_number(''))
        self.assertFalse(is_number("null"))
        self.assertFalse(is_number(np.nanpercentile([np.nan], 50)))
        self.assertTrue(is_number(-999.25))
        self.assertTrue(is_number("-999.25"))
        self.assertTrue(is_number("0.0"))

        self.assertTrue(is_number(float('inf')))
        self.assertFalse(is_finite(float('inf')))

        self.assertIsNone(to_number("nan"))
        self.assertIsNone(to_number(""))
        self.assertIsNone(to_number(''))
        self.assertIsNone(to_number("null"))
        self.assertEqual(to_number(-999.25), -999.25)
        self.assertEqual(to_number("-999.25"), -999.25)
        self.assertEqual(to_number("0.0"), 0.0)

        np.testing.assert_equal(none_to_nan(None), np.nan)
        np.testing.assert_equal(none_to_nan(np.nan), np.nan)
        np.testing.assert_equal(none_to_nan(1), 1)
        np.testing.assert_equal(none_to_nan([1, 2, None]), [1, 2, np.nan])
        np.testing.assert_equal(none_to_nan([1, 2, 3, np.nan, None]), [1, 2, 3, np.nan, np.nan])

    def test_math_utils(self):
        self.assertEqual(math.percentile([1, 2, None, np.nan], 50), 1.5)
        self.assertEqual(math.percentile([None, 1, np.nan], 50), 1.0)
        self.assertIsNone(math.percentile([np.nan, np.nan], 50))
        self.assertIsNone(math.percentile([None], 50))

        mean_angle = math.mean_angles([248, 315, 174, 112, 236, 276, 276, 39, 270, 231, 259, 186, 298])
        self.assertTrue(253 < mean_angle < 254)
        self.assertTrue(2.999 <= math.mean_angles([1, 2, 3, 4, 5]) <= 3.001)
        self.assertTrue(356.999 <= math.mean_angles([-1, -2, -3, -4, -5]) <= 357.001)

        self.assertEqual(math.angle_difference(10, 350), -20.0)
        self.assertEqual(math.angle_difference(350, 10), 20.0)

        self.assertEqual(math.abs_angle_difference(10, 350), 20.0)
        self.assertEqual(math.abs_angle_difference(350, 10), 20.0)

        self.assertEqual(
            math.split_zip_edges(np.array([0, 1, 2, 4, 6, 8, 9, 10, 12, 14, 15, 16])),
            [(0, 2), (4, 4), (6, 6), (8, 10), (12, 12), (14, 16)]
        )
        self.assertEqual(
            math.split_zip_edges(np.array([0, 1, 2, 4, 6, 8, 9, 10, 12, 14, 15, 16]), min_segment_length=2),
            [(0, 2), (8, 10), (14, 16)]
        )

        self.assertEqual(
            math.start_stop([1, 1, 1, 2, 4, 1, 1, 1, 2, 1, 1, 1], 1),
            [(0, 2), (5, 7), (9, 11)]
        )
        self.assertEqual(
            math.start_stop([True, True, True, False, False, True, True, True, False, True, True, True], True),
            [(0, 2), (5, 7), (9, 11)]
        )
