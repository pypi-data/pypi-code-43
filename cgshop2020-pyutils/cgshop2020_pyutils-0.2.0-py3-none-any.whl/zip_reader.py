import json
from io import TextIOWrapper, BytesIO
from typing import BinaryIO, Union, Dict, Iterator
from os import PathLike, path
from zipfile import ZipFile, BadZipFile
from json import JSONDecodeError

import chardet

from cgshop2020_pyutils.solution_set import BestSolutionSet
from cgshop2020_pyutils.zip_reader_errors import FileTooLargeError, InvalidFileName, \
    InvalidJSONError, NoSolutionsError, InvalidZipError, BadZipChecker
from .solution import Solution
from .solution_reader import SolutionReader, SolutionReaderError


def read_best_solutions_from_zip(
        zip: Union[BinaryIO, str, PathLike],
        discard_if_not_better: Dict[str, int]) -> BestSolutionSet:
    """
    Reads the best solutions from the zip.
    :param zip: Zip path or file
    :param discard_if_not_better: A dict possibly, e.g. {"night-0010": 8} if you want
        to discard all solutions for "night-0010" that have not less than 8 edges.
    :return: A BestSolutionSet with the best solutions for each instance
    """
    solutions = BestSolutionSet(old_bounds=discard_if_not_better)
    zsi = ZipSolutionIterator()
    for solution in zsi(zip):
        solutions.add(solution)
    return solutions


class ZipSolutionIterator:
    """
    Iterates over all solutions in a zip file.
    First initialize the class, then use call.
    e.g.,
    ```
    zsi = ZipSolutionIterator()
    for solution in zsi("./myzip.zip"):
        print(solution.instance_name)
    ```
    """

    def __init__(self, file_size_limit=150 * 1_000_000, solution_extensions=None):
        self._checker = BadZipChecker(file_size_limit)
        self._solution_extensions = solution_extensions if solution_extensions else [
            "json", "solution"]

    def _check_if_bad_zip(self, zipfile):
        self._checker(zipfile)

    def _is_solution_filename(self, name):
        extension = name.split(".")[-1].lower()
        # check extension
        if extension not in self._solution_extensions:
            return False
        # check for hidden file/directory
        if any(len(s) > 1 and s[0] == "." for s in name.split("/")):
            return False
        # any more checks?
        return True

    def _iterate_solution_filenames(self, zip_file):
        for filename in zip_file.namelist():
            if self._is_solution_filename(filename):
                yield filename

    def _robust_parse_json_from_bytes(self, bytes):
        """
        First tries to encode via 'UTF-8', otherwise it uses chardet.
        :param bytes: bytes of solution file
        :return: json
        """
        try:
            return json.loads(str(bytes, encoding="utf-8", errors='strict'))
        except UnicodeDecodeError as ude:
            encoding = chardet.detect(bytes)
            return json.loads(str(bytes, encoding=encoding["encoding"], errors='strict'))

    def _parse_file(self, solution_file, file_name, info):
        # read no more than the claimed file_size bytes (which we checked for limit violations)
        b = solution_file.read(info.file_size)
        try:
            return self._robust_parse_json_from_bytes(b)
        except UnicodeDecodeError as ude:
            raise InvalidZipError(
                f"Could not determine encoding of {file_name}. Please use utf-8.")
        except JSONDecodeError as e:
            raise InvalidJSONError(file_name, f"{e}") from e
        except RecursionError:
            raise InvalidJSONError(file_name, "Nesting level is too deep")

    def _iterate_solution_jsons(self, zip_file):
        for file_name in self._iterate_solution_filenames(zip_file):
            with zip_file.open(file_name, "r") as sol_file:
                info = zip_file.getinfo(file_name)
                yield self._parse_file(sol_file, file_name, info)

    def get_best_solutions(self,
                           zip: Union[BinaryIO, str, PathLike],
                           discard_if_not_better: Dict[str, int]=None) -> BestSolutionSet:

        """
        Reads the best solutions from the zip.
        :param zip: Zip path or file
        :param discard_if_not_better: A dict possibly, e.g. {"night-0010": 8} if you want
            to discard all solutions for "night-0010" that have not less than 8 edges.
        :return: A BestSolutionSet with the best solutions for each instance
        """
        solutions = BestSolutionSet(old_bounds=discard_if_not_better)
        for solution in self(zip):
            solutions.add(solution)
        return solutions

    def __call__(self, path_or_file: Union[BinaryIO, str, PathLike]) \
            -> Iterator[Solution]:
        """
        Iterates over all solutions in the zip.
        :param path_or_file: Zip or file
        :return:
        """
        try:
            with ZipFile(path_or_file) as zip_file:
                self._check_if_bad_zip(zip_file)
                for solution_json in self._iterate_solution_jsons(zip_file):
                    for solution in self._iterate_solutions_in_json(solution_json):
                        yield solution
        except BadZipFile as e:
            raise InvalidZipError(f"{e}")

    def _iterate_solutions_in_json(self, solution_json):
        solution_reader = SolutionReader()
        solutions = solution_reader.from_json_object(solution_json)
        if isinstance(solutions, list):
            for solution in solutions:
                yield solution
        else:
            yield solutions
