''' Test pyext.collection module

History:
04-05-2018 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.0'
import unittest

from dds_pylib.pyext.collection import flatten, multidim_list


class TestFlatten(unittest.TestCase):
    ''' test methods for flatten '''

    def flatten_consume(self, dim=None, coll=None):
        if dim:
            coll = multidim_list(dim)
        return list(flatten(i=coll))

    def setUp(self):
        '''
        initialize instance
        '''

    def test_one_dim(self):
        '''
        test that  can be accessed as dictionary
        '''
        self.assertEqual(
            self.flatten_consume((1,)), [None]
        )

    def test_two_dim_3x4(self):
        '''
        test that  can be accessed as dictionary
        '''
        self.assertEqual(
            self.flatten_consume((3, 4)), [
                None, None, None, None,
                None, None, None, None,
                None, None, None, None
            ]
        )

    def test_three_dim_4x4x2(self):
        '''
        test that  can be accessed as dictionary
        '''
        self.assertEqual(
            self.flatten_consume((4, 4, 2)), [
                None, None, None, None, None,
                None, None, None, None, None,
                None, None, None, None, None,
                None, None, None, None, None,
                None, None, None, None, None,
                None, None, None, None, None,
                None, None
            ]
        )

    def test_tuples_numbers(self):
        '''
        test that  can be accessed as dictionary

        coll = [('a', 'A'),
            ('b', 'B'),
            ('c', 'C'),
            ('d', 'D'),
            ('e', 'E'),
            ('f', 'F'),
            ('g', 'G'),
            ('h', 'H'),
            ('i', 'I'),
            ('j', 'J'),
            ('k', 'K'),
            ('l', 'L'),
            ('m', 'M'),
            ('n', 'N'),
            ('o', 'O'),
            ('p', 'P'),
            ('q', 'Q'),
            ('r', 'R'),
            ('s', 'S'),
            ('t', 'T'),
            ('u', 'U'),
            ('v', 'V'),
            ('w', 'W'),
            ('x', 'X'),
            ('y', 'Y'),
            ('z', 'Z'),
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8]
        '''
        coll = (
            [
                (chr(i), chr(i - 32))
                for i in xrange(ord('a'), ord('z') + 1)
            ] + range(0, 9)
        )
        self.assertEqual(
            self.flatten_consume(coll=coll), [
                'a', 'A', 'b', 'B', 'c', 'C', 'd', 'D', 'e', 'E', 'f', 'F',
                'g', 'G', 'h', 'H', 'i', 'I', 'j', 'J', 'k', 'K', 'l', 'L',
                'm', 'M', 'n', 'N', 'o', 'O', 'p', 'P', 'q', 'Q', 'r', 'R',
                's', 'S', 't', 'T', 'u', 'U', 'v', 'V', 'w', 'W', 'x', 'X',
                'y', 'Y', 'z', 'Z', 0, 1, 2, 3, 4, 5, 6, 7, 8
            ]
        )


class TestMultidimList(unittest.TestCase):
    ''' test methods for multidim_list '''

    def setUp(self):
        '''
        initialize instance
        '''

    def test_one_dim(self):
        '''
        test that  can be accessed as dictionary
        '''
        self.assertEqual(
            multidim_list((1,)), [None]
        )

    def test_two_dim_3x4(self):
        '''
        test that  can be accessed as dictionary
        '''
        self.assertEqual(
            multidim_list((3, 4)), [
                [None, None, None, None],
                [None, None, None, None],
                [None, None, None, None]
            ]
        )

    def test_three_dim_4x4x2(self):
        '''
        test that  can be accessed as dictionary
        '''
        self.assertEqual(
            multidim_list((4, 4, 2)), [
                [[None, None], [None, None], [None, None], [None, None]],
                [[None, None], [None, None], [None, None], [None, None]],
                [[None, None], [None, None], [None, None], [None, None]],
                [[None, None], [None, None], [None, None], [None, None]]
            ]
        )


if __name__ == '__main__':
    unittest.main()
