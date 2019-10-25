''' Test `util` module

History:
04-09-2018 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.0'

import unittest

from dds_pylib.util import case


class TestCase(unittest.TestCase):
    def test_camel_to_ashell_case(self):
        self.assertEqual(
            case.camel_to_ashell_case('rec.testCaseTwo'), "rec.test'case'two"
        )

    def test_camel_to_snake_case(self):
        self.assertEqual(
            case.camel_to_snake_case(
                'rec.testCaseTwo'), "rec.test_case_two"
        )

    def test_upcase_first_letter(self):
        self.assertEqual(
            case.upcase_first_letter(
                'rec.testCaseTwo'), "Rec.testCaseTwo"
        )

    def test_upcase_first_letter_lower(self):
        self.assertEqual(
            case.upcase_first_letter(
                'rec.testCaseTwo', lower=True), "Rec.testcasetwo"
        )

    def test_snake_to_ashell_lower(self):
        self.assertEqual(
            case.snake_case_to_ashell(
                'asDF_zXCdv_1Sdf'), "asdf'zxcdv'1sdf"
        )

    def test_snake_to_ashell_upper(self):
        self.assertEqual(
            case.snake_case_to_ashell(
                'asDF_zXCdv_1Sdf', upper=True), "ASDF'ZXCDV'1SDF"
        )

    def test_snake_to_upper_camel(self):
        self.assertEqual(
            case.snake_case_to_camel_case(
                'asdf_zxcdv_1sdf'), "AsdfZxcdv1Sdf"
        )

    def test_snake_to_lower_camel(self):
        self.assertEqual(
            case.snake_case_to_camel_case(
                'asdf_zxcdv_1sdf', upper_camel=False), "asdfZxcdv1Sdf"
        )


if __name__ == '__main__':
    unittest.main()
