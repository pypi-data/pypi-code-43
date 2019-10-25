"""
Utilities helping compare various data formats in a visual way.
"""

import os
import subprocess
import sys
import tempfile
from abc import ABC
from abc import abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from ndd_test4p.comparators import TextFileContentComparator


# -------------------------------------------------------------------------------------- DifferencesViewerDelegate -----

class DifferencesViewerDelegate(ABC):
    """
    Base class for all the viewer delegates.
    The role of a viewer delegate is to display differences between two files.
    """

    @abstractmethod
    def view(self, actual_file_path: Path, expected_file_path: Path):
        """
        Display differences between the given files.

        Args:
            actual_file_path (pathlib.Path): The file path of the actual content to compare.
            expected_file_path (pathlib.Path): The file path of the expected content to compare.
        """


class DiffViewerDelegate(DifferencesViewerDelegate):
    """
    Display differences between two files using `diff <https://en.wikipedia.org/wiki/Diff>`_.
    """

    def view(self, actual_file_path: Path, expected_file_path: Path):
        """
        Display differences between two files using `diff <https://en.wikipedia.org/wiki/Diff>`_.

        Args:
            actual_file_path (pathlib.Path): The file path of the actual content to compare.
            expected_file_path (pathlib.Path): The file path of the expected content to compare.
        """
        comparator = TextFileContentComparator(actual_file_path, expected_file_path)
        sys.stdout.writelines(comparator.unified_diff())


class MeldViewerDelegate(DifferencesViewerDelegate):
    """
    Display differences between two files using `Meld <https://meldmerge.org/>`_.
    """

    def view(self, actual_file_path: Path, expected_file_path: Path):
        """
        Display differences between two files using `Meld <https://meldmerge.org/>`_.

        Args:
            actual_file_path (pathlib.Path): The file path of the actual content to compare.
            expected_file_path (pathlib.Path): The file path of the expected content to compare.
        """
        subprocess.call(['meld', expected_file_path, actual_file_path])


# --------------------------------------------------------------------------------------------- DifferencesContext -----

class DifferencesContextMode(Enum):
    """
    The available display modes.
    They are made available through the environment variable named "DIFFERENCES_CONTEXT_MODE".
    """
    #: Differences will never be displayed
    DISABLED = 'disabled'
    #: Differences will always be displayed upon :class:`AssertionError`
    ENABLED_ALWAYS = 'enabled-always'
    #: Differences will be displayed only the first time upon :class:`AssertionError`
    ENABLED_FIRST = 'enabled-first'


class DifferencesContextDelegate(Enum):
    """
    The viewer delegates.
     They are made available through the environment variable named "DIFFERENCES_CONTEXT_DELEGATE".
    """
    #: diff is a data comparison tool between two files
    DIFF = DiffViewerDelegate
    #: Meld is a visual diff and merge tool
    MELD = MeldViewerDelegate


class DifferencesContextSettings:
    """
    A global context used by the the :class:`DifferencesViewer` to store configuration and maintain state across tests.

    - The display mode is set using the environment variable named "DIFFERENCES_CONTEXT_MODE" if specified,
      or to the default value :attr:`DifferencesContextMode.DISABLED` otherwise.
    - The viewer delegate is set using the environment variable named "DIFFERENCES_CONTEXT_DELEGATE" if specified,
      or to the default value :class:`DiffViewerDelegate` otherwise.
    """

    #: The key of the environment variable to set the mode.
    DIFFERENCES_CONTEXT_MODE_KEY = 'DIFFERENCES_CONTEXT_MODE'
    #: The key of the environment variable to set the delegate.
    DIFFERENCES_CONTEXT_DELEGATE_KEY = 'DIFFERENCES_CONTEXT_DELEGATE'

    #: The default mode.
    DEFAULT_DIFFERENCES_CONTEXT_MODE = DifferencesContextMode.DISABLED
    #: The default delegate.
    DEFAULT_VIEWER_DELEGATE = DiffViewerDelegate()

    def __init__(self):
        """
        - The display mode is set using the environment variable named "DIFFERENCES_CONTEXT_MODE" if specified,
          or to the default value :attr:`DifferencesContextMode.DISABLED` otherwise.
        - The viewer delegate is set using the environment variable named "DIFFERENCES_CONTEXT_DELEGATE" if specified,
          or to the default value :class:`DiffViewerDelegate` otherwise.
        """
        self._display_count: int = 0
        self._mode: DifferencesContextMode = DifferencesContextSettings.DEFAULT_DIFFERENCES_CONTEXT_MODE
        self._delegate: DifferencesViewerDelegate = DifferencesContextSettings.DEFAULT_VIEWER_DELEGATE

        environment_mode = os.environ.get(self.DIFFERENCES_CONTEXT_MODE_KEY)
        if environment_mode:
            self._mode = DifferencesContextMode[environment_mode]

        environment_delegate = os.environ.get(self.DIFFERENCES_CONTEXT_DELEGATE_KEY)
        if environment_delegate:
            self._delegate = DifferencesContextDelegate[environment_delegate].value()

    @property
    def display_count(self) -> int:
        """int: The number of times differences have been actually displayed."""
        return self._display_count

    @property
    def mode(self) -> DifferencesContextMode:
        """DifferencesContextMode: The display mode to be used by all the :class:`DifferencesViewer`."""
        return self._mode

    @mode.setter
    def mode(self, mode: DifferencesContextMode):
        self._mode = mode

    @property
    def delegate(self) -> DifferencesViewerDelegate:
        """DifferencesViewerDelegate: The viewer delegate to be used by all the :class:`DifferencesViewer`."""
        return self._delegate

    @delegate.setter
    def delegate(self, delegate: DifferencesViewerDelegate):
        self._delegate = delegate

    def can_display_differences(self) -> bool:
        """
        Returns:
            bool:

            - False if mode is :attr:`DifferencesContextMode.DISABLED`
            - True if mode is :attr:`DifferencesContextMode.ENABLED_ALWAYS`
            - True if mode is :attr:`DifferencesContextMode.ENABLED_FIRST` and `display_count < 1`
            - False otherwise
        """
        if self.mode == DifferencesContextMode.DISABLED:
            return False
        if self.mode == DifferencesContextMode.ENABLED_ALWAYS:
            return True
        if self.mode == DifferencesContextMode.ENABLED_FIRST:
            return self.display_count < 1
        raise ValueError(f'Invalid mode "{self.mode}"')

    def display_differences(self, actual_file_path: Path, expected_file_path: Path):
        """
        Increase the display count by 1 then display the differences using the current context delegate.

        Args:
            actual_file_path (pathlib.Path): The file path of the actual content to compare.
            expected_file_path (pathlib.Path): The file path of the expected content to compare.
        """
        self._display_count += 1
        self._delegate.view(actual_file_path, expected_file_path)

    def reset(self):
        """
        Restore the display count, the display mode and the :class:`ViewerDelegate`.
        """
        self.__init__()


#: The global instance used by all the :class:`DifferencesViewer`.
DIFFERENCES_CONTEXT_SETTINGS = DifferencesContextSettings()


# ---------------------------------------------------------------------------------------------- DifferencesViewer -----

class DifferencesViewer(ABC):
    """
    Base class to display differences between to sets of data.
    """


class TextFileDifferencesViewer(DifferencesViewer):
    """
    Display differences between two files, according to the current context.
    The display mode and the viewer delegate are set on the current :class:`DifferencesContextSettings`.
    The rules are:

    - if no :class:`AssertionError` is raised, do not display differences
    - if an :class:`AssertionError` is raised:

      - if mode is set to :attr:`DifferencesContextMode.DISABLED`, do not display differences
      - if mode is set to :attr:`DifferencesContextMode.ENABLED_ALWAYS`, display differences
      - if mode is set to :attr:`DifferencesContextMode.ENABLED_FIRST`, display differences the first time only

    :Example:

        Using Meld and the :attr:`DifferencesContextMode.ENABLED_FIRST` mode::

            DIFFERENCES_CONTEXT_SETTINGS.mode = DifferencesContextMode.ENABLED_FIRST
            # or set the environment variable 'DIFFERENCES_CONTEXT_MODE' to 'ENABLED_FIRST'

            DIFFERENCES_CONTEXT_SETTINGS.delegate = DifferencesContextDelegate.MeldViewerDelegate
            # or set the environment variable 'DIFFERENCES_CONTEXT_DELEGATE' to 'MELD'

            with TextFileDifferencesViewer(actual_file_path, expected_file_path):
                expect(actual_file_path).to(have_same_content_as(expected_file_path))

    """

    def __init__(self, actual_file_path: Path, expected_file_path: Path, force_display: bool = False):
        """
        Args:
            actual_file_path (pathlib.Path): The file path of the actual content to compare.
            expected_file_path (pathlib.Path): The file path of the expected content to compare.
            force_display (bool): True to display differences upon AssertionError disregarding the current context.
        """
        self._actual_file_path = actual_file_path
        self._expected_file_path = expected_file_path
        self._force_display = force_display

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type == AssertionError:
            self._compare_file_path(self._actual_file_path, self._expected_file_path)

    def _compare_file_path(self, actual_file_path: Path, expected_file_path: Path) -> None:
        """
        Called when an :class:`AssertionError` is raised.

        Args:
            actual_file_path (pathlib.Path): The file path of the actual content to compare.
            expected_file_path (pathlib.Path): The file path of the expected content to compare.
        """
        if self._force_display or DIFFERENCES_CONTEXT_SETTINGS.can_display_differences():
            DIFFERENCES_CONTEXT_SETTINGS.display_differences(actual_file_path, expected_file_path)


class YamlDifferencesViewer(DifferencesViewer):
    """
    Display differences as YAML between two pieces of data, according to the current context.
    The expected data can be any data or a :class:`pathlib.Path`.
    The later must be a file with the expected content exactly as dumped by :func:`yaml.dump`.
    The display mode and the viewer delegate are set on the current :class:`DifferencesContextSettings`.
    The rules are:

    - if no :class:`AssertionError` is raised, do not display differences
    - if an :class:`AssertionError` is raised:

      - if mode is set to :attr:`DifferencesContextMode.DISABLED`, do not display differences
      - if mode is set to :attr:`DifferencesContextMode.ENABLED_ALWAYS`, display differences
      - if mode is set to :attr:`DifferencesContextMode.ENABLED_FIRST`, display differences the first time only

    :Example:

        Using Meld and the :attr:`DifferencesContextMode.ENABLED_FIRST` mode::

            DIFFERENCES_CONTEXT_SETTINGS.mode = DifferencesContextMode.ENABLED_FIRST
            # or set the environment variable 'DIFFERENCES_CONTEXT_MODE' to 'ENABLED_FIRST'

            DIFFERENCES_CONTEXT_SETTINGS.delegate = DifferencesContextDelegate.MeldViewerDelegate
            # or set the environment variable 'DIFFERENCES_CONTEXT_DELEGATE' to 'MELD'

            # compare 2 pieces of data
            with YamlDifferencesViewer(actual_data, expected_data):
                expect(actual_data).to(equal(expected_data))

            # compare a piece of data with the content of a YAML file
            with YamlDifferencesViewer(actual_data, expected_file_path):
                expect(actual_data).to(equal(self._test_data_from_yaml(expected_file_path)))

    """

    def __init__(self, actual_data: Any, expected_data_or_file_path: Any, force_display: bool = False):
        """
        Args:
            actual_data (Any): The actual data to compare.
            expected_data_or_file_path (Any): The expected data to compare.
            force_display (bool): True to display differences upon AssertionError disregarding the current context.
        """
        self._actual_data = actual_data
        self._expected_data_or_file_path = expected_data_or_file_path
        self._force_display = force_display

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type == AssertionError:
            if isinstance(self._expected_data_or_file_path, Path):
                self._compare_data_with_file_content(self._actual_data, self._expected_data_or_file_path)
            else:
                self._compare_data_with_data(self._actual_data, self._expected_data_or_file_path)

    def _compare_data_with_data(self, actual_data: Any, expected_data: Any) -> None:
        """
        Called when an :class:`AssertionError` is raised when comparing data with data.

        Args:
            actual_data (Any): The actual data to compare.
            expected_data (Any): The expected data to compare.
        """
        if self._force_display or DIFFERENCES_CONTEXT_SETTINGS.can_display_differences():
            with tempfile.TemporaryDirectory() as directory_path:
                directory_path = Path(directory_path)
                expected_file_path = self._write_yaml(directory_path, 'expected.yml', expected_data)
                actual_file_path = self._write_yaml(directory_path, 'actual.yml', actual_data)
                DIFFERENCES_CONTEXT_SETTINGS.display_differences(actual_file_path, expected_file_path)

    def _compare_data_with_file_content(self, actual_data: Any, expected_file_path: Path) -> None:
        """
        Called when an :class:`AssertionError` is raised when comparing data with a file content.

        Args:
            actual_data (Any): The actual data to compare.
            expected_file_path (pathlib.Path): The file path of the expected content to compare.
        """
        if self._force_display or DIFFERENCES_CONTEXT_SETTINGS.can_display_differences():
            with tempfile.TemporaryDirectory() as directory_path:
                directory_path = Path(directory_path)
                actual_file_path = self._write_yaml(directory_path, 'actual.yml', actual_data)
                DIFFERENCES_CONTEXT_SETTINGS.display_differences(actual_file_path, expected_file_path)

    @staticmethod
    def _write_yaml(directory_path: Path, file_name: str, data: Any) -> Path:
        yaml.Dumper.ignore_aliases = lambda *args: True
        file_path = directory_path.joinpath(file_name).absolute()
        with file_path.open('w') as yaml_file:
            yaml_file.write('\n')
            yaml_file.write('#####################################################\n')
            yaml_file.write('# This file is temporary, all changes will be lost! #\n')
            yaml_file.write('#####################################################\n')
            yaml_file.write('\n')
            yaml_file.write(yaml.dump(data, default_flow_style=False))
            yaml_file.close()
        return file_path
