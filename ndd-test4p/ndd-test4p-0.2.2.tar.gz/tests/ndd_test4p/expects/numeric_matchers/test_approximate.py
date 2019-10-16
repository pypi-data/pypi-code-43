import pytest
from expects import *

from ndd_test4p.expects.numeric_matchers import approximate


class TestApproximate:

    @pytest.mark.parametrize("error_margin", [0.050, 0.105])
    def test_pass_with_float(self, error_margin):
        expect(2.1).to(approximate(2.0).by(error_margin))

    @pytest.mark.parametrize("error_margin", ["5%", "10.5%"])
    def test_pass_with_string(self, error_margin):
        expect(2.1).to(approximate(2.0).by(error_margin))

    @pytest.mark.parametrize("error_margin, error_margin_str", [
        (0.010, '1.0%'),
        (0.049, '4.9%')
    ])
    def test_fail_with_float(self, error_margin, error_margin_str):
        self._test_fail_with_invalid_value(error_margin, error_margin_str)

    @pytest.mark.parametrize("error_margin, error_margin_str", [
        ('1%', '1.0%'),
        ('4.9%', '4.9%')
    ])
    def test_fail_with_valid_string(self, error_margin, error_margin_str):
        self._test_fail_with_invalid_value(error_margin, error_margin_str)

    @pytest.mark.parametrize("error_margin", ["1.0", "1.2.3%", ".1%"])
    def test_fail_with_invalid_string(self, error_margin):
        expect(
            lambda: expect(2.1).to(approximate(2.0).by(error_margin))
        ).to(
            raise_error(ValueError, "Percentage must be a string matching '(\\d+(?:\\.\\d+)?)%'"))

    @staticmethod
    def _test_fail_with_invalid_value(error_margin, error_margin_str):
        with pytest.raises(AssertionError) as error_info:
            expect(2.1).to(approximate(2.0).by(error_margin))
        expect(str(error_info.value)).to(contain('expected: 2.1 to approximate 2.0'))
        expect(str(error_info.value)).to(contain(f'values ​​differ by more than {error_margin_str}'))
