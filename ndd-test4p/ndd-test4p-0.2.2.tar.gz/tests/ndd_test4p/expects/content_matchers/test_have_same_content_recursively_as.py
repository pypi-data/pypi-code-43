from pathlib import PosixPath

import pytest
from expects import *

from ndd_test4p.expects.content_matchers import have_same_content_recursively_as
from ndd_test4p.test_cases import AbstractTest


class TestHaveSameContentRecursivelyAs(AbstractTest):

    @pytest.fixture()
    def actual_directory_path(self) -> PosixPath:
        return self._test_data_file_path('actual')

    @pytest.fixture()
    def expected_equal_directory_path(self) -> PosixPath:
        return self._test_data_file_path('expected-equal')

    @pytest.fixture()
    def expected_different_directory_path(self) -> PosixPath:
        return self._test_data_file_path('expected-different')

    @pytest.fixture()
    def non_existent_directory_path(self) -> PosixPath:
        return PosixPath('/non-existent')

    def test_pass_with_equal_content(self, actual_directory_path, expected_equal_directory_path):
        expect(actual_directory_path).to(have_same_content_recursively_as(expected_equal_directory_path))

    def test_fail_with_a_non_existent_expected_file(self, actual_directory_path, non_existent_directory_path):
        with pytest.raises(AssertionError) as error_info:
            expect(actual_directory_path).to(have_same_content_recursively_as(non_existent_directory_path))
        expect(str(error_info.value)).to(contain(f'expected directory "/non-existent" does not exist'))

    def test_fail_with_a_non_existent_actual_file(self, non_existent_directory_path, expected_equal_directory_path):
        with pytest.raises(AssertionError) as error_info:
            expect(non_existent_directory_path).to(have_same_content_recursively_as(expected_equal_directory_path))
        expect(str(error_info.value)).to(contain(f'actual directory "/non-existent" does not exist'))

    def test_fail_with_different_content(self, actual_directory_path, expected_different_directory_path):
        with pytest.raises(AssertionError) as error_info:
            expect(actual_directory_path).to(have_same_content_recursively_as(expected_different_directory_path))
        expect(str(error_info.value)).to(contain('contents are different'))
        expect(str(error_info.value)).to(contain('useful commands:'))
        expect(str(error_info.value)).to(match(r'  diff -ru ".+/actual" ".+/expected-different"'))
        expect(str(error_info.value)).to(match(r'  meld ".+/actual" ".+/expected-different" &'))
        expect(str(error_info.value)).to(contain(
            'differences:\n'
            + f'  actual only files:\n'
            + f'  - {self._test_data_file_path("actual/dir_1/actual-1.txt").as_posix()}\n'
            + f'  - {self._test_data_file_path("actual/dir_2/actual-2.txt").as_posix()}\n'
            + f'  expected only files:\n'
            + f'  - {self._test_data_file_path("expected-different/dir_1/dir_1_1/actual-1-2.txt").as_posix()}\n'
            + f'  - {self._test_data_file_path("expected-different/dir_2/actual-X.txt").as_posix()}\n'
            + f'  different files:\n'
            + f'  - {self._test_data_file_path("actual/dir_1/dir_1_1/actual-1-1.txt").as_posix()}\n'
            + f'  not compared files:\n'
            + f'  - <None>'))
