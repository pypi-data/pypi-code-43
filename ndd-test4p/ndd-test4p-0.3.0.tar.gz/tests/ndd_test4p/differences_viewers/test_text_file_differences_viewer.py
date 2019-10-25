import os
from pathlib import PosixPath
from unittest.mock import call
from unittest.mock import MagicMock

import pytest
from expects import *

from ndd_test4p.differences_viewers import DIFFERENCES_CONTEXT_SETTINGS
from ndd_test4p.differences_viewers import DifferencesContextMode
from ndd_test4p.differences_viewers import DiffViewerDelegate
from ndd_test4p.differences_viewers import TextFileDifferencesViewer
from ndd_test4p.test_cases import AbstractTest


class TestTextFileDifferencesViewer(AbstractTest):
    _actual_file_path: PosixPath
    _expected_file_path: PosixPath
    _delegate: DiffViewerDelegate

    def setup_method(self):
        self._unset_environment_variable()

        self._actual_file_path = PosixPath('actual.txt')
        self._expected_file_path = PosixPath('expected.txt')

        self._delegate = DiffViewerDelegate()
        self._delegate.view = MagicMock(name='view')

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

        actual_file_path = self._test_data_file_path('actual.txt')
        expected_file_path = self._test_data_file_path('expected-different.txt')

        with pytest.raises(AssertionError) as error_info:
            with TextFileDifferencesViewer(actual_file_path, expected_file_path):
                raise AssertionError()

        expect(error_info.value.__cause__).to(be_none)
        expect(capsys.readouterr().out).to(equal(
            f'--- {actual_file_path.as_posix()}\n'
            + f'+++ {expected_file_path.as_posix()}\n'
            + '@@ -1,3 +1,3 @@\n'
            + ' some content\n'
            + '-that must be equal to...\n'
            + '+that may be equal to...\n'
            + ' what?\n'
        ))

    @staticmethod
    def _unset_environment_variable():
        if 'DIFFERENCES_CONTEXT_MODE' in os.environ:
            del os.environ['DIFFERENCES_CONTEXT_MODE']

    def _configure_settings(self, mode):
        DIFFERENCES_CONTEXT_SETTINGS.reset()
        DIFFERENCES_CONTEXT_SETTINGS.mode = mode
        DIFFERENCES_CONTEXT_SETTINGS.delegate = self._delegate

    def _call_viewer_without_assertion_error(self):
        with TextFileDifferencesViewer(self._actual_file_path, self._expected_file_path):
            pass

    def _call_viewer_without_assertion_error_with_force(self):
        with TextFileDifferencesViewer(self._actual_file_path, self._expected_file_path, True):
            pass

    def _call_viewer_with_assertion_error(self):
        with pytest.raises(AssertionError):
            with TextFileDifferencesViewer(self._actual_file_path, self._expected_file_path):
                raise AssertionError()

    def _call_viewer_with_assertion_error_with_force(self):
        with pytest.raises(AssertionError):
            with TextFileDifferencesViewer(self._actual_file_path, self._expected_file_path, True):
                raise AssertionError()

    def _check_view_has_been_called(self, times):
        expect(self._delegate.view.call_count).to(equal(times))
        self._delegate.view.assert_has_calls([call(self._actual_file_path, self._expected_file_path)] * times)

    def _check_view_has_not_been_called(self):
        self._delegate.view.assert_not_called()

    def _check_view_has_been_called_once(self):
        self._check_view_has_been_called(1)

    def _check_view_has_been_called_twice(self):
        self._check_view_has_been_called(2)
