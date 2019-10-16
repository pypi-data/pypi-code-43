from pathlib import Path

import pytest
from expects import *

from ndd_test4p.test_cases import AbstractTest


class TestAbstractTest(AbstractTest):

    @pytest.fixture()
    def tests_directory_path(self) -> Path:
        return Path(__file__).parent.parent.parent

    @pytest.fixture()
    def test_case_directory_path(self, tests_directory_path: Path) -> Path:
        test_case_directory_path = tests_directory_path.joinpath('ndd_test4p', 'test_cases')
        expect(test_case_directory_path.as_posix()).to(end_with('/tests/ndd_test4p/test_cases'))
        return test_case_directory_path

    def test_test_file_path(self, test_case_directory_path: Path):
        expected_path = test_case_directory_path.joinpath('test_abstract_test.py')
        expect(self._test_file_path()).to(equal(expected_path))
        expect(self._test_file_path().is_file()).to(be_true)

    def test_test_directory_path(self, test_case_directory_path: Path):
        expected_path = test_case_directory_path
        expect(self._test_directory_path()).to(equal(expected_path))
        expect(self._test_directory_path().is_dir()).to(be_true)

    def test_test_data_directory_path(self, test_case_directory_path: Path):
        expected_path = test_case_directory_path.joinpath('_test_abstract_test')
        expect(self._test_data_directory_path()).to(equal(expected_path))
        expect(self._test_data_directory_path().is_dir()).to(be_true)

    def test_test_data_subdirectory_path(self, test_case_directory_path: Path):
        expected_path = test_case_directory_path.joinpath('_test_abstract_test', 'subdirectory')
        expect(self._test_data_subdirectory_path('subdirectory')).to(equal(expected_path))
        expect(self._test_data_subdirectory_path('subdirectory').is_dir()).to(be_true)

    def test_test_data_file_path(self, test_case_directory_path: Path):
        expected_path = test_case_directory_path.joinpath('_test_abstract_test', 'some-file.txt')
        expect(self._test_data_file_path('some-file.txt')).to(equal(expected_path))
        expect(self._test_data_file_path('some-file.txt').is_file()).to(be_true)

        expected_path = test_case_directory_path.joinpath('_test_abstract_test', 'non-existing-file.txt')
        expect(self._test_data_file_path('non-existing-file.txt')).to(equal(expected_path))
        expect(self._test_data_file_path('non-existing-file.txt').exists()).to(be_false)

    def test_test_data_file_paths(self, test_case_directory_path: Path):
        expected_paths = [
            test_case_directory_path.joinpath('_test_abstract_test', 'another-file.txt'),
            test_case_directory_path.joinpath('_test_abstract_test', 'some-file.txt'),
        ]
        expect(self._test_data_file_paths('*.txt')).to(equal(expected_paths))
        for expected_path in expected_paths:
            expect(expected_path.is_file()).to(be_true)

        expect(self._test_data_file_paths('*.invalid')).to(be_empty)

    def test_test_data_from(self):
        expected_content = 'content of some-file.txt'
        expect(self._test_data_from('some-file.txt')).to(equal(expected_content))

        with pytest.raises(FileNotFoundError):
            self._test_data_from('non-existing-file.txt')

    def test_test_data_from_json(self):
        expected_content = {'file': 'some-file.json'}
        expect(self._test_data_from_json('some-file.json')).to(equal(expected_content))

        with pytest.raises(FileNotFoundError):
            self._test_data_from_json('non-existing-file.json')

    def test_test_data_from_yaml(self):
        expected_content = {'file': 'some-file.yaml'}
        expect(self._test_data_from_yaml('some-file.yaml')).to(equal(expected_content))

        with pytest.raises(FileNotFoundError):
            self._test_data_from_yaml('non-existing-file.yaml')
