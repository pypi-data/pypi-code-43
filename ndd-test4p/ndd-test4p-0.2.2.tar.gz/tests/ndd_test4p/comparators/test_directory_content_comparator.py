from pathlib import PosixPath

import pytest
from expects import *

from ndd_test4p.comparators import DirectoryContentComparator
from ndd_test4p.test_cases import AbstractTest


class TestDirectoryContentComparator(AbstractTest):

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

    @staticmethod
    def _test_fail_with_a_non_existent_file(actual_directory_path, expected_directory_path, fail_fast):
        comparator = DirectoryContentComparator(actual_directory_path, expected_directory_path, fail_fast)

        with pytest.raises(FileNotFoundError) as error_info:
            comparator.are_contents_equal()
        expect(str(error_info.value)).to(contain("No such directory: '/non-existent'"))

    @staticmethod
    def _assert_paths(actual_paths, expected_file_paths):
        expect(actual_paths).to(have_length(len(expected_file_paths)))

        for index, expected_path_pattern in enumerate(expected_file_paths):
            expect(actual_paths[index]).to(equal(expected_path_pattern))


class TestDirectoryContentComparator_FailFast(TestDirectoryContentComparator):  # pylint: disable=invalid-name

    def test_pass_with_equal_content(self, actual_directory_path, expected_equal_directory_path):
        comparator = DirectoryContentComparator(actual_directory_path, expected_equal_directory_path, True)

        expect(comparator.are_contents_equal()).to(be_true)

        expect(comparator.actual_only_files).to(be_empty)
        expect(comparator.expected_only_files).to(be_empty)
        expect(comparator.different_files).to(be_empty)
        expect(comparator.funny_files).to(be_empty)

    def test_fail_with_a_non_existent_expected_file(self, actual_directory_path, non_existent_directory_path):
        self._test_fail_with_a_non_existent_file(actual_directory_path, non_existent_directory_path, True)

    def test_fail_with_a_non_existent_actual_file(self, non_existent_directory_path, expected_equal_directory_path):
        self._test_fail_with_a_non_existent_file(non_existent_directory_path, expected_equal_directory_path, True)

    def test_fail_with_different_content(self, actual_directory_path, expected_different_directory_path):
        comparator = DirectoryContentComparator(actual_directory_path, expected_different_directory_path, True)

        expect(comparator.are_contents_equal()).to(be_false)

        expect(comparator.actual_only_files).to(be_empty)
        expect(comparator.expected_only_files).to(be_empty)
        self._assert_paths(comparator.different_files,
                           [self._test_data_file_path('actual/dir_1/dir_1_1/actual-1-1.txt')])
        expect(comparator.funny_files).to(be_empty)


class TestDirectoryContentComparator_DontFailFast(TestDirectoryContentComparator):  # pylint: disable=invalid-name

    def test_pass_with_equal_content(self, actual_directory_path, expected_equal_directory_path):
        comparator = DirectoryContentComparator(actual_directory_path, expected_equal_directory_path, False)

        expect(comparator.are_contents_equal()).to(be_true)

        expect(comparator.actual_only_files).to(be_empty)
        expect(comparator.expected_only_files).to(be_empty)
        expect(comparator.different_files).to(be_empty)
        expect(comparator.funny_files).to(be_empty)

    def test_fail_with_a_non_existent_expected_file(self, actual_directory_path, non_existent_directory_path):
        self._test_fail_with_a_non_existent_file(actual_directory_path, non_existent_directory_path, False)

    def test_fail_with_a_non_existent_actual_file(self, non_existent_directory_path, expected_equal_directory_path):
        self._test_fail_with_a_non_existent_file(non_existent_directory_path, expected_equal_directory_path, False)

    def test_fail_with_different_content(self, actual_directory_path, expected_different_directory_path):
        comparator = DirectoryContentComparator(actual_directory_path, expected_different_directory_path, False)

        expect(comparator.are_contents_equal()).to(be_false)

        self._assert_paths(comparator.actual_only_files,
                           [self._test_data_file_path('actual/dir_2/actual-2.txt')])
        self._assert_paths(comparator.expected_only_files,
                           [self._test_data_file_path('expected-different/dir_2/actual-X.txt')])
        self._assert_paths(comparator.different_files,
                           [self._test_data_file_path('actual/dir_1/dir_1_1/actual-1-1.txt')])
        self._assert_paths(comparator.funny_files, [])
