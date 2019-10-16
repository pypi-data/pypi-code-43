from pathlib import PosixPath

import pytest
from expects import *

from ndd_test4p.expects.content_matchers import have_same_content_as
from ndd_test4p.test_cases import AbstractTest


class TestHaveSameContentAs(AbstractTest):

    @pytest.fixture()
    def actual_file_path(self) -> PosixPath:
        return self._test_data_file_path('actual.txt')

    @pytest.fixture()
    def expected_equal_file_path(self) -> PosixPath:
        return self._test_data_file_path('expected-equal.txt')

    @pytest.fixture()
    def expected_different_file_path(self) -> PosixPath:
        return self._test_data_file_path('expected-different.txt')

    @pytest.fixture()
    def non_existent_file_path(self) -> PosixPath:
        return self._test_data_file_path('/non-existent.txt')

    def test_pass_with_equal_content(self, actual_file_path, expected_equal_file_path):
        expect(actual_file_path).to(have_same_content_as(expected_equal_file_path))

    def test_fail_with_a_non_existent_expected_file(self, actual_file_path, non_existent_file_path):
        with pytest.raises(AssertionError) as error_info:
            expect(actual_file_path).to(have_same_content_as(non_existent_file_path))
        expect(str(error_info.value)).to(contain(f'expected file "/non-existent.txt" does not exist'))

    def test_fail_with_a_non_existent_actual_file(self, non_existent_file_path, expected_equal_file_path):
        with pytest.raises(AssertionError) as error_info:
            expect(non_existent_file_path).to(have_same_content_as(expected_equal_file_path))
        expect(str(error_info.value)).to(contain(f'actual file "/non-existent.txt" does not exist'))

    def test_fail_with_different_content(self, actual_file_path, expected_different_file_path):
        with pytest.raises(AssertionError) as error_info:
            expect(actual_file_path).to(have_same_content_as(expected_different_file_path))
        expect(str(error_info.value)).to(contain('contents are different'))
        expect(str(error_info.value)).to(contain('useful commands:'))
        expect(str(error_info.value)).to(match(r'  diff -ru ".+/actual\.txt" ".+/expected-different\.txt"'))
        expect(str(error_info.value)).to(match(r'  meld ".+/actual\.txt" ".+/expected-different\.txt" &'))
        expect(str(error_info.value)).to(contain(
            'diff output:\n'
            + f'--- {actual_file_path.as_posix()}\n'
            + f'+++ {expected_different_file_path.as_posix()}\n'
            + '@@ -1,3 +1,3 @@\n'
            + ' some content\n'
            + '-that must be equal to...\n'
            + '+that may be equal to...\n'
            + ' what?\n'))
