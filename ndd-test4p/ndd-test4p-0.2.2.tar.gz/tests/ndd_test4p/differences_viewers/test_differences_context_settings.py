import os
from pathlib import Path
from unittest.mock import call
from unittest.mock import MagicMock

import pytest
from expects import *

from ndd_test4p.differences_viewers import DifferencesContextMode
from ndd_test4p.differences_viewers import DifferencesContextSettings
from ndd_test4p.differences_viewers import DiffViewerDelegate
from ndd_test4p.differences_viewers import MeldViewerDelegate
from ndd_test4p.test_cases import AbstractTest


class TestDifferencesContextSettings(AbstractTest):

    def setup_method(self):
        self._unset_environment_variables()

    def teardown_method(self):
        self._unset_environment_variables()

    @staticmethod
    def _unset_environment_variables():
        if 'DIFFERENCES_CONTEXT_MODE' in os.environ:
            del os.environ['DIFFERENCES_CONTEXT_MODE']


class TestDifferencesContextSettings_Mode(TestDifferencesContextSettings):  # pylint: disable=invalid-name

    def test_that_mode_is_disabled_by_default(self):
        settings = DifferencesContextSettings()
        expect(settings.mode).to(equal(DifferencesContextMode.DISABLED))

    @pytest.mark.parametrize("mode_name, mode_enum", [
        ('DISABLED', DifferencesContextMode.DISABLED),
        ('ENABLED_ALWAYS', DifferencesContextMode.ENABLED_ALWAYS),
        ('ENABLED_FIRST', DifferencesContextMode.ENABLED_FIRST),
    ])
    def test_that_mode_can_be_set_by_an_environment_variable(self, mode_name, mode_enum):
        os.environ['DIFFERENCES_CONTEXT_MODE'] = mode_name
        settings = DifferencesContextSettings()
        expect(settings.mode).to(equal(mode_enum))

    def test_that_mode_must_exist(self):
        os.environ['DIFFERENCES_CONTEXT_MODE'] = 'invalid-mode'
        with pytest.raises(KeyError):
            DifferencesContextSettings()

    @pytest.mark.parametrize("mode_enum", [
        DifferencesContextMode.DISABLED,
        DifferencesContextMode.ENABLED_ALWAYS,
        DifferencesContextMode.ENABLED_FIRST,
    ])
    def test_that_mode_has_a_getter_and_a_setter(self, mode_enum):
        settings = DifferencesContextSettings()
        settings.mode = mode_enum
        expect(settings.mode).to(equal(mode_enum))


class TestDifferencesContextSettings_Delegate(TestDifferencesContextSettings):  # pylint: disable=invalid-name

    def test_that_delegate_is_diff_by_default(self):
        settings = DifferencesContextSettings()
        expect(settings.delegate).to(be_a(DiffViewerDelegate))

    @pytest.mark.parametrize("delegate_name, delegate_class", [
        ('DIFF', DiffViewerDelegate),
        ('MELD', MeldViewerDelegate),
    ])
    def test_that_delegate_can_be_set_by_an_environment_variable(self, delegate_name, delegate_class):
        os.environ['DIFFERENCES_CONTEXT_DELEGATE'] = delegate_name
        settings = DifferencesContextSettings()
        expect(settings.delegate).to(be_a(delegate_class))


class TestDifferencesContextSettings_Display(TestDifferencesContextSettings):  # pylint: disable=invalid-name

    @pytest.fixture()
    def mock_delegate(self):
        mock_delegate = DiffViewerDelegate()
        mock_delegate.view = MagicMock(name='view')
        return mock_delegate

    def test_that_display_differences_calls_the_delegate(self, mock_delegate):
        settings = DifferencesContextSettings()
        settings.delegate = mock_delegate

        settings.display_differences(Path('actual_file_1'), Path('expected_file_1'))
        mock_delegate.view.assert_called_with(Path('actual_file_1'), Path('expected_file_1'))

    def test_that_display_differences_increases_the_display_count(self, mock_delegate):
        settings = DifferencesContextSettings()
        settings.delegate = mock_delegate

        expect(settings.display_count).to(equal(0))
        settings.display_differences(Path('actual_file_1'), Path('expected_file_1'))
        mock_delegate.view.assert_called_with(Path('actual_file_1'), Path('expected_file_1'))

        expect(settings.display_count).to(equal(1))
        settings.display_differences(Path('actual_file_2'), Path('expected_file_2'))
        mock_delegate.view.assert_has_calls([
            call(Path('actual_file_1'), Path('expected_file_1')),
            call(Path('actual_file_2'), Path('expected_file_2'))
        ])

        expect(settings.display_count).to(equal(2))
        settings.display_differences(Path('actual_file_3'), Path('expected_file_3'))
        mock_delegate.view.assert_has_calls([
            call(Path('actual_file_1'), Path('expected_file_1')),
            call(Path('actual_file_2'), Path('expected_file_2')),
            call(Path('actual_file_3'), Path('expected_file_3'))
        ])

    def test_that_can_display_differences_always_returns_false_when_mode_is_disabled(self, mock_delegate):
        settings = DifferencesContextSettings()
        settings.mode = DifferencesContextMode.DISABLED
        settings.delegate = mock_delegate

        expect(settings.can_display_differences()).to(be_false)

        for _ in range(3):
            settings.display_differences(Path('actual_file_1'), Path('expected_file_1'))
            expect(settings.can_display_differences()).to(be_false)

    def test_that_can_display_differences_always_returns_true_when_mode_is_enabled_always(self, mock_delegate):
        settings = DifferencesContextSettings()
        settings.mode = DifferencesContextMode.ENABLED_ALWAYS
        settings.delegate = mock_delegate

        expect(settings.can_display_differences()).to(be_true)

        for _ in range(3):
            settings.display_differences(Path('actual_file_1'), Path('expected_file_1'))
            expect(settings.can_display_differences()).to(be_true)

    def test_that_can_display_differences_returns_true_only_the_first_time_when_mode_is_enabled_first(
            self, mock_delegate):
        settings = DifferencesContextSettings()
        settings.mode = DifferencesContextMode.ENABLED_FIRST
        settings.delegate = mock_delegate

        expect(settings.can_display_differences()).to(be_true)

        settings.display_differences(Path('actual_file_1'), Path('expected_file_1'))
        expect(settings.can_display_differences()).to(be_false)

        settings.display_differences(Path('actual_file_1'), Path('expected_file_1'))
        expect(settings.can_display_differences()).to(be_false)
