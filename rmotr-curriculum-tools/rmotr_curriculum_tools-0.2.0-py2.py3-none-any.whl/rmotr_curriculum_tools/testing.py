import hashlib
import os
import sys

import logging
import logging.config
import pytest
import pytoml as toml

from pathlib import Path
from shutil import copyfile
try:
    from tempfile import TemporaryDirectory
except ImportError:
    import tempfile
    import shutil

    class TemporaryDirectory(object):
        def __enter__(self):
            self.dir_name = tempfile.mkdtemp()
            return self.dir_name

        def __exit__(self, exc_type, exc_value, traceback):
            shutil.rmtree(self.dir_name)

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'detailed': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
        },
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': "%(log_color)s%(levelname)-6s%(reset)s %(message)s %(blue)s\"%(lesson_name)s\""
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'colored',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO'
        }
    }
})
logger = logging.getLogger(__name__)

CODE_TYPE = 'code'
SOLUTIONS_RELATIVE_PATH = 'solutions'
TESTS_FILE_NAME = 'tests.py'
TESTS_DIRECTORY_NAME = 'tests'
EXTRA_PYTHON_CODE_FOR_ASSIGNMENTS = """
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import sys
class CaptureOutput(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio
        sys.stdout = self._stdout
"""


class InvalidLessonException(Exception):
    pass


class Lesson(object):
    def __init__(self, name, uuid, path, _lesson_data):
        self.name = name
        self.uuid = uuid
        self.path = path
        self._lesson_data = _lesson_data
        self.__test_data = None

    @property
    def test_data(self):
        if not self.__test_data:
            self.__test_data = read_lesson_tests(self.path)

        return self.__test_data


class Solution(object):
    def __init__(self, lesson, path):
        self.lesson = lesson
        self.path = path


def read_lesson_tests(lesson_path):

    def _read_file(path):
        with path.open('r', encoding='utf-8') as fp:
            return fp.read()

    def _read_tests_directory(path):
        if not path.exists():
            return None

        return '\n'.join([_read_file(p) for p in path.glob('test_*.py')])

    def _read_tests_py(path):
        if not path.exists():
            return None
        return _read_file(path)

    tests_dir_path = lesson_path / TESTS_DIRECTORY_NAME
    test_py_file_path = lesson_path / TESTS_FILE_NAME

    return "{}\n\n{}".format(
        _read_tests_directory(tests_dir_path) or '',
        _read_tests_py(test_py_file_path) or ''
    )


def _get_unit_number(unit_name):
    start = unit_name.index('-') + 1
    end = unit_name.index('-', start)
    return int(unit_name[start:end])


def iter_code_lessons(path='.', unit_glob='unit-*', grep=None, units=None,
                      lesson_glob='lesson-*', rmotr_toml_name='.rmotr'):
    grep = grep or []

    p = Path(path)
    for unit in p.glob(unit_glob):
        unit_number = _get_unit_number(unit.name)
        if units and unit_number not in units:
            continue
        for lesson_path in unit.glob(lesson_glob):
            rmotr_toml = lesson_path / rmotr_toml_name
            if not rmotr_toml.exists():
                raise InvalidLessonException(
                    ("Lessons must contain a .rmotr file. "
                     "Lesson {} doesn't contain any").format(lesson_path.name))

            with rmotr_toml.open() as rmotr_f:
                lesson_data = toml.load(rmotr_f)
                lesson_name = lesson_data['name']
                if lesson_data['type'] == 'assignment':
                    add_lesson = True
                    for keyword in grep:
                        if keyword not in lesson_name.lower():
                            add_lesson = False
                            break
                    if not add_lesson:
                        continue
                    logger.info("Added lesson", extra={'lesson_name': lesson_name})
                    yield Lesson(name=lesson_name,
                                 uuid=lesson_data['uuid'],
                                 path=lesson_path,
                                 _lesson_data=lesson_data)


def iter_lesson_solutions(lesson):
    solutions_path = (lesson.path / SOLUTIONS_RELATIVE_PATH)
    if solutions_path.exists():
        for solution_path in solutions_path.glob('*.py'):
            yield Solution(lesson=lesson, path=solution_path)


def write_solution_test_file(_dir, solution):
    base_path = Path(os.path.abspath(_dir))

    lesson_hash = hashlib.md5(
        str(solution.lesson.path).encode('utf-8')).hexdigest()

    test_file_name = "test_{hash}_{solution}".format(
        solution=solution.path.name, hash=lesson_hash)
    test_lesson_path = base_path / lesson_hash
    test_lesson_path.mkdir(exist_ok=True)
    files_lesson_path = solution.lesson.path / 'files'

    if files_lesson_path.exists():
        for data_file in files_lesson_path.iterdir():
            data_file_test_path = (test_lesson_path / data_file.name)
            if data_file_test_path.exists():
                continue
            copyfile(str(data_file), str(data_file_test_path))

    test_file_path = test_lesson_path / test_file_name

    with test_file_path.open('w') as test_f, solution.path.open('r') as solution_f:
        test_f.write(solution_f.read())
        test_f.write('\n\n')
        test_f.write(EXTRA_PYTHON_CODE_FOR_ASSIGNMENTS)
        test_f.write('\n\n')
        test_f.write(solution.lesson.test_data)


def test_lessons_solutions(path='.', grep=None, units=None, exit=True):
    with TemporaryDirectory() as temp_dir:
        abs_path = os.path.abspath(temp_dir)
        for lesson in iter_code_lessons(path, grep=grep, units=units):
            for solution in iter_lesson_solutions(lesson):
                write_solution_test_file(temp_dir, solution)

        abs_path = Path(abs_path)
        for lesson_test_file in abs_path.iterdir():
            os.chdir(str(lesson_test_file))
            exit = pytest.main(['.', '-s', '-v', '--tb=short'])
            if exit != 0:
                sys.exit(exit)
