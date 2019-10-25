"""
Content matchers for the `expects <https://expects.readthedocs.io/en/stable/>`_ library.
"""

from pathlib import Path
from typing import List

from expects.matchers import Matcher

from ndd_test4p.comparators import DirectoryContentComparator
from ndd_test4p.comparators import TextFileContentComparator


class have_same_content_as(Matcher):  # pylint: disable=invalid-name
    """
    Check that a file has the same content as another one.

    :Examples:

    .. code-block:: python

        expect(actual_text_file_path).to(have_same_content_as(expected_text_file_path))
    """

    def __init__(self, expected_file_path: Path):
        """
        Args:
            expected_file_path (pathlib.Path): The file path of the expected content to compare.
        """
        self._expected = expected_file_path
        self._expected_file_path = expected_file_path

    def _match(self, subject):
        """
        Args:
            subject (pathlib.Path): The file path of the actual content to compare.

        Returns:
            (bool, [str]): The result of the comparison and its associated message.
        """
        actual_file_path = subject

        if not self._expected_file_path.is_file():
            return False, [f'expected file "{self._expected_file_path.as_posix()}" does not exist']

        if not actual_file_path.is_file():
            return False, [f'actual file "{actual_file_path.as_posix()}" does not exist']

        comparator = TextFileContentComparator(actual_file_path, self._expected_file_path)

        if comparator.are_contents_equal():
            return True, ['contents are equals']

        return False, [
            'contents are different\n'
            + f'useful commands:\n'
            + f'  diff -ru "{actual_file_path}" "{self._expected_file_path}"\n'
            + f'  meld "{actual_file_path}" "{self._expected_file_path}" &\n'
            + f'diff output:\n'
            + comparator.unified_diff()
        ]


class have_same_content_recursively_as(Matcher):  # pylint: disable=invalid-name
    """
    Check that a directory has the same files with the same content as another one.

    :Examples:

    .. code-block:: python

        expect(actual_directory_path).to(have_same_content_recursively_as(expected_directory))
    """

    def __init__(self, expected_directory_path: Path):
        """
        Args:
            expected_directory_path (pathlib.Path): The path of the directory with the expected content to compare.
        """
        self._expected = expected_directory_path
        self._expected_directory_path = expected_directory_path

    def _match(self, subject):
        """
        Args:
            subject (pathlib.Path): The path of the directory with the actual content to compare.

        Returns:
            (bool, [str]): The result of the comparison and its associated message.
        """
        actual_directory_path = subject

        if not self._expected_directory_path.is_dir():
            return False, [f'expected directory "{self._expected_directory_path.as_posix()}" does not exist']

        if not actual_directory_path.is_dir():
            return False, [f'actual directory "{actual_directory_path.as_posix()}" does not exist']

        comparator = DirectoryContentComparator(actual_directory_path, self._expected_directory_path, fail_fast=False)

        if comparator.are_contents_equal():
            return True, ['contents are equals']

        return False, [
            'contents are different\n'
            + 'useful commands:\n'
            + f'  diff -ru "{actual_directory_path}" "{self._expected_directory_path}"\n'
            + f'  meld "{actual_directory_path}" "{self._expected_directory_path}" &\n'
            + f'differences:\n'
            + f'  actual only files:\n'
            + f'{self._to_bullet_list(comparator.actual_only_files)}\n'
            + f'  expected only files:\n'
            + f'{self._to_bullet_list(comparator.expected_only_files)}\n'
            + f'  different files:\n'
            + f'{self._to_bullet_list(comparator.different_files)}\n'
            + f'  not compared files:\n'
            + f'{self._to_bullet_list(comparator.funny_files)}'
        ]

    @staticmethod
    def _to_bullet_list(file_paths: List[Path]) -> str:
        if file_paths:
            return '\n'.join(['  - ' + f.as_posix() for f in file_paths])
        return '  - <None>'
