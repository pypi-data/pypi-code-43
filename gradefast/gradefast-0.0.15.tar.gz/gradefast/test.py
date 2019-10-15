"""
.. include:: ../recipes/test.rst
    :start-line: 5
    :end-line: 13

See the :ref:`tutorial <test-recipe>` for better understanding
"""
import os
import re
import json
import subprocess

from abc import ABC, ABCMeta, abstractmethod

from enum import Enum
from gradefast.exceptions import *
from gradefast.result import Result
    

class TestType(Enum):
    """
    An enum to indicate type of the test.

    Options are FILE, PKG and SCRIPT

    .. todo::

        SCRIPT is yet to be added
    """
    FILE=1
    PKG=2
    SCRIPT=3


class GFCliTest:
    def __init__(self, test_script_location, file_to_test, parameters=[], 
    test_type=TestType.FILE, plagiarism_check=False):
        # A test consists of a test_script file written by theme developers 
        # and a test entry point usually present in student submissions
        
        # The test script will be written in python. The test script will have 
        # a call to dependencies like :
        # 1. 

        # The Entry Points can be a:
        # 1. directory
        # 2. program file like .c or .py
        # 3. result.txt or result.png file
        
        self.test_script_location = test_script_location
        if not os.path.exists(test_script_location):
            raise FileNotFoundError("Test script not found")

        self.test_type = test_type
        if self.test_type == TestType.FILE:
            self.file_to_test = file_to_test

        self.parameters = parameters
        if len(self.parameters) == 0:
            raise InvalidParameterException("Provide atleast 1 parameter")

        for param in parameters:
            if type(param) != str:
                raise InvalidParameterException("Parameters should contain list of strings only")


    def parse_result_dict(self, output):
        if type(output) != str:
            raise Exception("Output from console should be string")
        pattern = re.compile("result=(\{.*\})")
        m = pattern.search(output)
        if m == None:
            raise ParseError("Result dictionary cannot be parsed")
        # parantheses can be used to group text inside pattern; group 0 is whole match
        try:
            result_dict = json.loads(m.group(1))
            return result_dict
        except json.decoder.JSONDecodeError:
            # log here
            raise ParseError("Output should be a json string")


    def __call__(self, submission):
        if self.test_type == TestType.FILE:
            working_dir = os.path.dirname(self.test_script_location)
            proc = subprocess.Popen([
                "python", self.test_script_location,
                "-f", submission.file_paths[self.file_to_test],
                "--team-id", str(submission.team_id)], 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=working_dir)
            stdout, stderr = proc.communicate()
            result = json.loads(stdout)
            
            if type(result) != dict:
                raise TypeError("Result should be a list")
            # result = Result(result)
            return result, stderr


class GFTest(ABC):
    """
    Represents a test that outputs a result, comment and exceptions encountered
    while evaluating the test

    Each class written by developer intended to be a test extends :class:`~GFTest`
    and implements the :attr:`~GFTest.__call__()` method. :attr:`~GFTest.__call__()`
    receives parameters according to the TestType.

    Parameters
    ----------
    test_type: :class:`TestType`
        Specifies the type of test. This option influences what parameters are passed to
        :attr:`~GFTest.__call__()` and extra configurations before evaluation.
    file_to_test: str
        File on which the test is evaluated. ``e.g. 'zip', 'txt', 'png2', 'unzipped3'``
    package_path: str, optional
        Path to the package if the test_type is `TestType.PKG`
    plagiarism_check: bool, optional
        To enable plagiarism checking on :attr:`~file_to_test`. Default is ``False``

    .. todo::

        Plagiarism check to be implemented

    Attributes
    ----------
    test_type: :class:`TestType`
    file_to_test: str
    package_path: str
    plagiarishm_check: bool

    """
    def __init__(self, test_type, file_to_test, package_path='', plagiarism_check=False):
        self.test_type = test_type
        self.file_to_test = file_to_test
        self.package_path = package_path
        if self.test_type == TestType.PKG:
            if self.package_path == None or self.package_path == '':
                raise PackagePathException()
        self.plagiarism_check = plagiarism_check
    
    @abstractmethod
    def __call__(self, *args):
        """
        Implements logic of test

        When :class:`GFTest` is subclassed, this method should be implemented.
        It receives parameters according to the selected test type.

        Following are the types and parameters the __call__() method receives: 
        
        TestType.FILE
            file_path, submission
        TestType.PKG
            submission

        """
        raise NotImplementedError()
