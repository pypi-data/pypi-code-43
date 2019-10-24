"""
This file contains the ZipSolutionIterator which can read a zip and return all solutions
in it. It should be reasonably robust and have some basic security features.
"""
import json
from typing import BinaryIO, Union, Dict, Iterator, Optional
from os import PathLike, path
from zipfile import ZipFile, BadZipFile
from json import JSONDecodeError

import chardet

from cgshop2020_pyutils.solution_set import BestSolutionSet
from cgshop2020_pyutils.zip_reader_errors import InvalidJSONError, NoSolutionsError,\
    InvalidZipError, BadZipChecker, InvalidEncodingError
from .solution import Solution
from .solution_reader import SolutionReader


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

    def __init__(self, file_size_limit: int = 150 * 1_000_000,
                 zip_size_limit: int = 750 * 1_000_000,
                 solution_extensions=("json", "solution")):
        """
        Set the parameters in the constructor. Use the __call__ to actually iterate
        a zip file.
        :param file_size_limit: Limit the size of a single file within the zip.
        :param zip_size_limit: Limit the overall decompressed size of the zip.
        :param solution_extensions: What file extensions should be checked?
        """
        self._checker = BadZipChecker(file_size_limit=file_size_limit,
                                      zip_size_limit=zip_size_limit)
        self._solution_extensions = solution_extensions

    def _check_if_bad_zip(self, zipfile):
        self._checker(zipfile)

    def _is_hidden_folder_name(self, name):
        if len(name) > 1 and name[0] == ".":  # classic hidden unix files.
            return True
        if len(name) > 1 and name[:2] == "__":  # OS X does that.
            return True
        return False

    def _is_solution_filename(self, name):
        extension = name.split(".")[-1].lower()
        # check extension
        if extension not in self._solution_extensions:
            return False
        # check for hidden file/directory
        if any(self._is_hidden_folder_name(s) for s in name.split("/")):
            return False
        # any more checks?
        return True

    def _iterate_solution_filenames(self, zip_file):
        had_filename = False
        for filename in zip_file.namelist():
            if self._is_solution_filename(filename):
                had_filename = True
                yield filename
        if not had_filename:
            raise NoSolutionsError()

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
            raise InvalidEncodingError(file_name) from ude
        except JSONDecodeError as e:
            raise InvalidJSONError(file_name, f"{e}") from e
        except RecursionError as re:
            raise InvalidJSONError(file_name, "Nesting level is too deep") from re

    def _iterate_solution_jsons(self, zip_file):
        for file_name in self._iterate_solution_filenames(zip_file):
            with zip_file.open(file_name, "r") as sol_file:
                info = zip_file.getinfo(file_name)
                yield file_name, self._parse_file(sol_file, file_name, info)

    def get_best_solutions(self,
                           zip: Union[BinaryIO, str, PathLike],
                           discard_if_not_better: Optional[Dict[
                               str, int]] = None) -> BestSolutionSet:

        """
        Reads the best solutions from the zip.
        :param zip: Zip path or file
        :param discard_if_not_better: An optional dict, e.g. {"night-0010": 8} if you want
            to discard all solutions for "night-0010" that do not have fewer than 8 edges.
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
                for file_name, solution_json in self._iterate_solution_jsons(zip_file):
                    meta = {"zip_info": {"zip_file": zip_file.filename,
                                         "file_in_zip": file_name}}
                    for solution in self._iterate_solutions_in_json(solution_json, meta):
                        yield solution
        except BadZipFile as e:
            raise InvalidZipError(f"{e}")

    def _attach_meta_to_solution(self, solution: Solution, meta: dict):
        for key, value in meta.items():
            solution.meta_data[key] = value
        return solution

    def _iterate_solutions_in_json(self, solution_json, meta: dict = None):
        solution_reader = SolutionReader()
        solutions = solution_reader.from_json_object(solution_json, file_name=meta["zip_info"]["file_in_zip"])
        if isinstance(solutions, list):
            for solution in solutions:
                yield self._attach_meta_to_solution(solution, meta)
        else:
            yield self._attach_meta_to_solution(solutions, meta)
