"""
Utilities helping writing test cases.
"""

import json
import sys
from abc import ABC
from pathlib import Path

import yaml


class AbstractTest(ABC):
    """
    Base class for tests providing convenient methods to:

    - find test directories and test files
    - read data from test files containing text, JSON or YAML

    :Examples:

        Assuming your project layout looks like::

            /my_project
            ├── src
            │   ├── __init__.py
            │   └── my_package
            │       ├── __init__.py
            │       └── my_module.py
            └── tests
                ├── conftest.py
                └── my_package
                    └── my_module
                        ├── _test_something_in_my_module
                        │   ├── expected.json
                        │   ├── expected.txt
                        │   └── expected.yaml
                        └── test_something_in_my_module.py

        And that `test_something_in_my_module.py` looks like::

            from ndd_test4p.test_cases import AbstractTest
            class TestSomethingInMyModule(AbstractTest):

        Then inside this test class::

            self._test_file_path()
            # Path('/my_project/tests/my_package/my_module/test_something_in_my_module.py')

            self._test_directory_path()
            # Path('/my_project/tests/my_package/my_module/')

            self._test_data_directory_path()
            # Path('/my_project/tests/my_package/my_module/_test_something_in_my_module/')

            self._test_data_file_path('expected.txt')
            # Path('/my_project/tests/my_package/my_module/_test_something_in_my_module/expected.txt')

            self._test_data_file_paths('expected.*')
            # [
            #     Path('/my_project/tests/my_package/my_module/_test_something_in_my_module/expected.json'),
            #     Path('/my_project/tests/my_package/my_module/_test_something_in_my_module/expected.txt'),
            #     Path('/my_project/tests/my_package/my_module/_test_something_in_my_module/expected.yam')l
            # ]

            self._test_data_from('expected.txt')
            # content as text of
            # Path('/my_project/tests/my_package/my_module/_test_something_in_my_module/expected.txt')

            self._test_data_from_json('expected.json')
            # content as given by `json.loads`
            # of Path('/my_project/tests/my_package/my_module/_test_something_in_my_module/expected.json')

            self._test_data_from_yaml('expected.yaml')
            # content as given by `yaml.safe_load`
            # of Path('/my_project/tests/my_package/my_module/_test_something_in_my_module/expected.yaml')

    .. automethod:: _test_file_path
    .. automethod:: _test_directory_path
    .. automethod:: _test_data_directory_path
    .. automethod:: _test_data_file_path
    .. automethod:: _test_data_file_paths
    .. automethod:: _test_data_from
    .. automethod:: _test_data_from_json
    .. automethod:: _test_data_from_yaml
    """

    def _test_file_path(self) -> Path:
        """
        Returns:
            pathlib.Path: The file of the class under test.

        :Example:

        >>> from tests.ndd_test4p.test_cases.test_abstract_test import TestAbstractTest
        >>> file_path = TestAbstractTest()._test_file_path()
        >>> file_path.as_posix().endswith('/tests/ndd_test4p/test_cases/test_abstract_test.py')
        True
        """
        return Path(sys.modules[self.__module__].__file__)

    def _test_directory_path(self) -> Path:
        """
        Returns:
           pathlib.Path: The directory containing the file of the class under test.

        :Example:

        >>> from tests.ndd_test4p.test_cases.test_abstract_test import TestAbstractTest
        >>> directory_path = TestAbstractTest()._test_directory_path()
        >>> directory_path.as_posix().endswith('/tests/ndd_test4p/test_cases')
        True
        """
        return self._test_file_path().parent

    def _test_data_directory_path(self) -> Path:
        """
        Returns:
           pathlib.Path: The directory beside the file of the class under test and named after the test file
           prefixed with an underscore.

        :Example:

        >>> from tests.ndd_test4p.test_cases.test_abstract_test import TestAbstractTest
        >>> data_directory_path = TestAbstractTest()._test_data_directory_path()
        >>> data_directory_path.as_posix().endswith('/tests/ndd_test4p/test_cases/_test_abstract_test')
        True
        """
        return self._test_directory_path().joinpath('_' + self._test_file_path().stem)

    def _test_data_subdirectory_path(self, directory_name: str) -> Path:
        """
        Args:
            directory_name (str): The name of the child directory.

        Returns:
           pathlib.Path: The subdirectory (existing or not) under the "data directory"
           (see :func:`_test_data_directory_path`) with the given name.

        :Example:

        >>> from tests.ndd_test4p.test_cases.test_abstract_test import TestAbstractTest
        >>> data_directory_path = TestAbstractTest()._test_data_subdirectory_path('subdirectory')
        >>> data_directory_path.as_posix().endswith('/tests/ndd_test4p/test_cases/_test_abstract_test/subdirectory')
        True
        """
        return self._test_data_directory_path().joinpath(directory_name)

    def _test_data_file_path(self, file_name: str) -> Path:
        """
        Args:
            file_name (str): The name of the file.

        Returns:
           pathlib.Path: The file (existing or not) under the "data directory"
           (see :func:`_test_data_directory_path`) with the given name.

        :Example:

        >>> from tests.ndd_test4p.test_cases.test_abstract_test import TestAbstractTest
        >>> data_file_path = TestAbstractTest()._test_data_file_path('some-file.txt')
        >>> data_file_path.as_posix().endswith('/tests/ndd_test4p/test_cases/_test_abstract_test/some-file.txt')
        True
        """
        return self._test_data_directory_path().joinpath(file_name)

    def _test_data_file_paths(self, pattern: str) -> [Path]:
        """
        Args:
            pattern (str): The glob pattern of the files to find.

        Returns:
            [pathlib.Path]: The files under the "data directory" (see :func:`_test_data_directory_path`)
            with their name matching the given glob pattern.

        :Example:

        >>> from tests.ndd_test4p.test_cases.test_abstract_test import TestAbstractTest
        >>> data_file_paths = TestAbstractTest()._test_data_file_paths('*.txt')
        >>> len(data_file_paths)
        2
        >>> data_file_paths[0].as_posix().endswith('/tests/ndd_test4p/test_cases/_test_abstract_test/another-file.txt')
        True
        >>> data_file_paths[1].as_posix().endswith('/tests/ndd_test4p/test_cases/_test_abstract_test/some-file.txt')
        True
        """
        return sorted(self._test_data_directory_path().glob(pattern))

    def _test_data_from(self, file_name: str) -> str:
        """
        Args:
            file_name (str): The name of the file.

        Returns:
            str: The content of the given "data file" (see :func:`_test_data_file_path`).

        :Example:

        >>> from tests.ndd_test4p.test_cases.test_abstract_test import TestAbstractTest
        >>> TestAbstractTest()._test_data_from('some-file.txt')
        'content of some-file.txt'
        """
        return self._test_data_file_path(file_name).read_text()

    def _test_data_from_json(self, file_name: str) -> dict:
        """
        Args:
            file_name (str): The name of the file.

        Returns:
            dict: The content of the given JSON "data file" (see :func:`_test_data_file_path`).

        :Example:

        >>> from tests.ndd_test4p.test_cases.test_abstract_test import TestAbstractTest
        >>> TestAbstractTest()._test_data_from_json('some-file.json')
        {'file': 'some-file.json'}
        """
        return json.loads(self._test_data_from(file_name))

    def _test_data_from_yaml(self, file_name: str) -> dict:
        """
        Args:
            file_name (str): The name of the file.

        Returns:
            dict: The content of the given YAML "data file" (see :func:`_test_data_file_path`).

        :Example:

        >>> from tests.ndd_test4p.test_cases.test_abstract_test import TestAbstractTest
        >>> TestAbstractTest()._test_data_from_yaml('some-file.yaml')
        {'file': 'some-file.yaml'}
        """
        return yaml.safe_load(self._test_data_from(file_name))
