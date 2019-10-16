"""
Utilities helping compare various data formats.
"""

import difflib
import filecmp
from pathlib import Path
from typing import List


class TextFileContentComparator:
    """
    Compare contents of two files.
    """

    def __init__(self, actual_file_path: Path, expected_file_path: Path):
        """
        Args:
            actual_file_path (pathlib.Path): The file path of the actual content to compare.
            expected_file_path (pathlib.Path): The file path of the expected content to compare.
        """
        self._actual_file_path = actual_file_path
        self._expected_file_path = expected_file_path

    def are_contents_equal(self) -> bool:
        """
        Returns:
            bool: True if the contents of the files are equal, False otherwise
        """
        actual_file_content = self._actual_file_path.read_text()
        expected_file_content = self._expected_file_path.read_text()
        return actual_file_content == expected_file_content

    def unified_diff(self) -> str:
        """
        Returns:
            str: The unified diff between the two files
        """
        actual_content_lines = self._actual_file_path.open().readlines()
        expected_content_lines = self._expected_file_path.open().readlines()
        unified_diff_as_array = difflib.unified_diff(
            actual_content_lines,
            expected_content_lines,
            fromfile=self._actual_file_path.as_posix(),
            tofile=self._expected_file_path.as_posix())
        return ''.join(unified_diff_as_array)


class DirectoryContentComparator:
    """
    Compare the contents of two directories, taking into account the content of the files.
    """

    def __init__(self, actual_directory_path: Path, expected_directory_path: Path, fail_fast: bool = True):
        """
        Args:
            actual_directory_path (pathlib.Path): The path of the actual directory to compare.
            expected_directory_path (pathlib.Path): The path of the expected directory to compare.
            fail_fast (bool): Fail as soon as two subdirectories are reported different.
        """
        self._actual_directory_path = actual_directory_path
        self._expected_directory_path = expected_directory_path
        self._fail_fast = fail_fast
        self._actual_only_files = []
        self._expected_only_files = []
        self._different_files = []
        self._funny_files = []

    def are_contents_equal(self) -> bool:
        """
        Recursively compare the contents of the two directories, taking into account the content of the files.

        Returns:
            bool: True if the contents of the directories are equal, False otherwise
        """
        self._actual_only_files = []
        self._expected_only_files = []
        self._different_files = []
        self._funny_files = []

        if not self._actual_directory_path.is_dir():
            raise FileNotFoundError(f"No such directory: '{self._actual_directory_path.as_posix()}'")
        if not self._expected_directory_path.is_dir():
            raise FileNotFoundError(f"No such directory: '{self._expected_directory_path.as_posix()}'")

        if self._fail_fast:
            return self._are_contents_equal_fast(self._actual_directory_path, self._expected_directory_path)

        return self._are_contents_equal_complete(self._actual_directory_path, self._expected_directory_path)

    @property
    def actual_only_files(self) -> List[Path]:
        """
        Returns:
            pathlib.Path[]: The paths of the files which appear in the actual directory only.
        """
        return self._actual_only_files

    @property
    def expected_only_files(self) -> List[Path]:
        """
        Returns:
            pathlib.Path[]: The paths of the files which appear in the expected directory only.
        """
        return self._expected_only_files

    @property
    def different_files(self) -> List[Path]:
        """
        Returns:
            pathlib.Path[]: The paths of the files which are different.
        """
        return self._different_files

    @property
    def funny_files(self) -> List[Path]:
        """
        Returns:
            pathlib.Path[]: The paths of the files which couldn't be compared.
        """
        return self._funny_files

    def _are_contents_equal_complete(self, directory_1: Path, directory_2: Path) -> bool:
        """
        Recursively compare the contents of two directories, taking into account the content of the files.

        Args:
            directory_1 (pathlib.Path): The path of the first directory to compare.
            directory_2 (pathlib.Path): The path of the second directory to compare.

        Returns:
            bool: True if the contents of the directories are equal, False otherwise
        """
        compared = _RecursiveDirectoryComparator(directory_1, directory_2)

        if compared.left_only:
            self._actual_only_files.extend([directory_1.joinpath(f) for f in compared.left_only])
        if compared.right_only:
            self._expected_only_files.extend([directory_2.joinpath(f) for f in compared.right_only])
        if compared.diff_files:
            self._different_files.extend([directory_1.joinpath(f) for f in compared.diff_files])
        if compared.funny_files:
            self._funny_files.extend([directory_1.joinpath(f) for f in compared.funny_files])

        for sub_directory in compared.common_dirs:
            self._are_contents_equal_complete(directory_1.joinpath(sub_directory), directory_2.joinpath(sub_directory))

        actual_length = len(self._actual_only_files)
        expected_length = len(self._expected_only_files)
        different_length = len(self._different_files)
        funny_length = len(self._funny_files)
        return actual_length + expected_length + different_length + funny_length == 0

    def _are_contents_equal_fast(self, directory_1: Path, directory_2: Path) -> bool:
        """
        Recursively compare the contents of two directories, taking into account the content of the files.
        Returns at the first difference found.

        Args:
            directory_1 (pathlib.Path): The path of the first directory to compare.
            directory_2 (pathlib.Path): The path of the second directory to compare.

        Returns:
            bool: True if the contents of the directories are equal, False otherwise
        """
        compared = _RecursiveDirectoryComparator(directory_1, directory_2)

        if compared.left_only or compared.right_only or compared.diff_files or compared.funny_files:
            self._actual_only_files.extend([directory_1.joinpath(f) for f in compared.left_only])
            self._expected_only_files.extend([directory_2.joinpath(f) for f in compared.right_only])
            self._different_files.extend([directory_1.joinpath(f) for f in compared.diff_files])
            self._funny_files.extend([directory_1.joinpath(f) for f in compared.funny_files])
            return False

        for sub_directory in compared.common_dirs:
            sub_directory_1 = directory_1.joinpath(sub_directory)
            subdirectory_2 = directory_2.joinpath(sub_directory)
            if not self._are_contents_equal_fast(sub_directory_1, subdirectory_2):
                return False

        return True


class _RecursiveDirectoryComparator(filecmp.dircmp):
    """
    Compare the content of two directories.
    In contrast with :func:`filecmp.dircmp`, this subclass compares the content of files with the same path.
    """

    def phase3(self):
        """
        Find out differences between common files.
        Ensure we are using content comparison with 'shallow=False'.
        If shallow is True, comparison is done based solely on 'stat()' information.
        """
        comparison = filecmp.cmpfiles(self.left, self.right, self.common_files, shallow=False)
        # pylint: disable=attribute-defined-outside-init
        self.same_files, self.diff_files, self.funny_files = comparison
