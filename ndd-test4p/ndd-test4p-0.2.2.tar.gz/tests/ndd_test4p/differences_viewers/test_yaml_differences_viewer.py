import os
import re
from abc import abstractmethod
from pathlib import PosixPath
from typing import Any
from typing import List

import pytest
from expects import *

from ndd_test4p.differences_viewers import DIFFERENCES_CONTEXT_SETTINGS
from ndd_test4p.differences_viewers import DifferencesContextMode
from ndd_test4p.differences_viewers import DifferencesViewerDelegate
from ndd_test4p.differences_viewers import DiffViewerDelegate
from ndd_test4p.differences_viewers import YamlDifferencesViewer
from ndd_test4p.test_cases import AbstractTest


class AbstractTestYamlDifferencesViewer(AbstractTest):
    _actual_data: Any
    _expected_data_or_file_path: Any
    _delegate: '_RecordingView'

    def setup_method(self):
        self._unset_environment_variable()

        self._actual_data = {'key1': 1, 'key2': {'key3': 3}}
        self._expected_data_or_file_path = self._create_expected_data_or_file_path()

        self._delegate = _RecordingView()

    def teardown_method(self):
        self._unset_environment_variable()

    def test_when_mode_is_disabled_and_no_assertion_error_is_raised(self):
        self._configure_settings(DifferencesContextMode.DISABLED)

        self._call_viewer_without_assertion_error()
        self._check_view_has_not_been_called()

        self._call_viewer_without_assertion_error_with_force()
        self._check_view_has_not_been_called()

    def test_when_mode_is_disabled_and_an_assertion_error_is_raised(self):
        self._configure_settings(DifferencesContextMode.DISABLED)

        self._call_viewer_with_assertion_error()
        self._check_view_has_not_been_called()

        self._call_viewer_with_assertion_error_with_force()
        self._check_view_has_been_called_once()

    def test_when_mode_is_enabled_always_and_no_assertion_error_is_raised(self):
        self._configure_settings(DifferencesContextMode.ENABLED_ALWAYS)

        self._call_viewer_without_assertion_error()
        self._check_view_has_not_been_called()

        self._call_viewer_without_assertion_error_with_force()
        self._check_view_has_not_been_called()

    def test_when_mode_is_enabled_always_and_an_assertion_error_is_raised(self):
        self._configure_settings(DifferencesContextMode.ENABLED_ALWAYS)

        self._call_viewer_with_assertion_error()
        self._check_view_has_been_called_once()

        self._call_viewer_with_assertion_error_with_force()
        self._check_view_has_been_called_twice()

    def test_when_mode_is_enabled_first_and_no_assertion_error_is_raised(self):
        self._configure_settings(DifferencesContextMode.ENABLED_FIRST)

        self._call_viewer_without_assertion_error()
        self._check_view_has_not_been_called()

        self._call_viewer_without_assertion_error_with_force()
        self._check_view_has_not_been_called()

    def test_when_mode_is_enabled_first_and_an_assertion_error_is_raised(self):
        self._configure_settings(DifferencesContextMode.ENABLED_FIRST)

        self._call_viewer_with_assertion_error()
        self._check_view_has_been_called_once()

        self._call_viewer_with_assertion_error()
        self._check_view_has_been_called_once()

        self._call_viewer_with_assertion_error_with_force()
        self._check_view_has_been_called_twice()

    def test_default_viewer(self, capsys):
        DIFFERENCES_CONTEXT_SETTINGS.reset()
        DIFFERENCES_CONTEXT_SETTINGS.mode = DifferencesContextMode.ENABLED_ALWAYS
        DIFFERENCES_CONTEXT_SETTINGS.delegate = DiffViewerDelegate()

        with pytest.raises(AssertionError) as error_info:
            with YamlDifferencesViewer(self._actual_data, self._expected_data_or_file_path):
                raise AssertionError()

        captured_output = capsys.readouterr().out

        expect(error_info.value.__cause__).to(be_none)
        self._do_test_default_viewer(captured_output)

    @staticmethod
    def _unset_environment_variable():
        if 'DIFFERENCES_CONTEXT_MODE' in os.environ:
            del os.environ['DIFFERENCES_CONTEXT_MODE']

    def _configure_settings(self, mode):
        DIFFERENCES_CONTEXT_SETTINGS.reset()
        DIFFERENCES_CONTEXT_SETTINGS.mode = mode
        DIFFERENCES_CONTEXT_SETTINGS.delegate = self._delegate

    def _call_viewer_without_assertion_error(self):
        with YamlDifferencesViewer(self._actual_data, self._expected_data_or_file_path):
            pass

    def _call_viewer_without_assertion_error_with_force(self):
        with YamlDifferencesViewer(self._actual_data, self._expected_data_or_file_path, True):
            pass

    def _call_viewer_with_assertion_error(self):
        with pytest.raises(AssertionError):
            with YamlDifferencesViewer(self._actual_data, self._expected_data_or_file_path):
                raise AssertionError()

    def _call_viewer_with_assertion_error_with_force(self):
        with pytest.raises(AssertionError):
            with YamlDifferencesViewer(self._actual_data, self._expected_data_or_file_path, True):
                raise AssertionError()

    def _check_view_has_not_been_called(self):
        expect(self._delegate.records).to(be_empty)

    def _check_view_has_been_called_once(self):
        self._check_view_has_been_called(1)

    def _check_view_has_been_called_twice(self):
        self._check_view_has_been_called(2)

    @abstractmethod
    def _create_expected_data_or_file_path(self) -> Any:
        pass

    @abstractmethod
    def _do_test_default_viewer(self, captured_output: str) -> None:
        pass

    @abstractmethod
    def _check_view_has_been_called(self, times):
        pass


class TestYamlDifferencesViewer_Data(AbstractTestYamlDifferencesViewer):  # pylint: disable=invalid-name

    def _create_expected_data_or_file_path(self) -> Any:
        return {'key1': 1, 'key2': {'key3': 999}}

    def _do_test_default_viewer(self, captured_output):
        expect(captured_output).to(match(
            r'--- /.+/actual.yml\n'
            + r'\+\+\+ /.+/expected.yml\n'
            + re.escape(
                '@@ -5,4 +5,4 @@\n'
                + ' \n'
                + ' key1: 1\n'
                + ' key2:\n'
                + '-  key3: 3\n'
                + '+  key3: 999\n'
            )
        ))

    def _check_view_has_been_called(self, times):
        expect(self._delegate.records).to(have_length(times))

        for record in self._delegate.records:
            expect(record.actual_file_path.as_posix()).to(end_with('/actual.yml'))
            expect(record.expected_file_path.as_posix()).to(end_with('/expected.yml'))
            expect(record.actual_text).to(equal(self._test_data_from('expected-actual.yml')))
            expect(record.expected_text).to(equal(self._test_data_from('expected-expected.yml')))


class TestYamlDifferencesViewer_File(AbstractTestYamlDifferencesViewer):  # pylint: disable=invalid-name

    def _create_expected_data_or_file_path(self) -> Any:
        return self._test_data_file_path('expected-expected.yml')

    def _do_test_default_viewer(self, captured_output):
        expect(captured_output).to(match(
            r'--- /.+/actual.yml\n'
            + re.escape(
                f'+++ {self._expected_data_or_file_path.as_posix()}\n'
                + '@@ -5,4 +5,4 @@\n'
                + ' \n'
                + ' key1: 1\n'
                + ' key2:\n'
                + '-  key3: 3\n'
                + '+  key3: 999\n'
            )
        ))

    def _check_view_has_been_called(self, times):
        expect(self._delegate.records).to(have_length(times))

        for record in self._delegate.records:
            expect(record.actual_file_path.as_posix()).to(end_with('/actual.yml'))
            expect(record.expected_file_path.as_posix()).to(end_with('/expected-expected.yml'))
            expect(record.actual_text).to(equal(self._test_data_from('expected-actual.yml')))
            expect(record.expected_text).to(equal(self._test_data_from('expected-expected.yml')))


class _RecordingView(DifferencesViewerDelegate):
    records: List['_Record']

    def __init__(self):
        self.records = []

    def view(self, actual_file_path: PosixPath, expected_file_path: PosixPath):
        self.records.append(_Record(actual_file_path, expected_file_path))


class _Record:
    actual_file_path: PosixPath
    expected_file_path: PosixPath
    actual_text: str
    expected_text: str

    def __init__(self, actual_file_path: PosixPath, expected_file_path: PosixPath):
        self.actual_file_path = actual_file_path
        self.expected_file_path = expected_file_path
        self.actual_text = actual_file_path.read_text()
        self.expected_text = expected_file_path.read_text()
