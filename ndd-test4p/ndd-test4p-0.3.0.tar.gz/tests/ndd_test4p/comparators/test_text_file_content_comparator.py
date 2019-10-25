from pathlib import PosixPath

import pytest
from expects import *

from ndd_test4p.comparators import TextFileContentComparator
from ndd_test4p.test_cases import AbstractTest


class TestTextFileContentComparator(AbstractTest):

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
        return PosixPath('/non-existent.txt')

    def test_pass_with_equal_content(self, actual_file_path, expected_equal_file_path):
        comparator = TextFileContentComparator(actual_file_path, expected_equal_file_path)

        expect(comparator.are_contents_equal()).to(be_true)

        expect(comparator.unified_diff()).to(equal(''))

    def test_fail_with_a_non_existent_expected_file(self, actual_file_path, non_existent_file_path):
        self._test_fail_with_a_non_existent_file(actual_file_path, non_existent_file_path)

    def test_fail_with_a_non_existent_actual_file(self, non_existent_file_path, expected_equal_file_path):
        self._test_fail_with_a_non_existent_file(non_existent_file_path, expected_equal_file_path)

    def test_fail_with_different_content(self, actual_file_path, expected_different_file_path):
        comparator = TextFileContentComparator(actual_file_path, expected_different_file_path)

        expect(comparator.are_contents_equal()).to(be_false)

        expect(comparator.unified_diff()).to(equal(
            f'--- {actual_file_path.as_posix()}\n'
            + f'+++ {expected_different_file_path.as_posix()}\n'
            + '@@ -1,3 +1,3 @@\n'
            + ' some content\n'
            + '-that must be equal to...\n'
            + '+that may be equal to...\n'
            + ' what?\n'
        ))

    def _test_fail_with_a_non_existent_file(self, actual_file_path, expected_file_path):
        comparator = TextFileContentComparator(actual_file_path, expected_file_path)

        with pytest.raises(FileNotFoundError) as error_info:
            comparator.are_contents_equal()
        expect(str(error_info.value)).to(contain("No such file or directory: '/non-existent.txt'"))

        with pytest.raises(FileNotFoundError) as error_info:
            comparator.unified_diff()
        expect(str(error_info.value)).to(contain("No such file or directory: '/non-existent.txt'"))
