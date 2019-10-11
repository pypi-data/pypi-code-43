#
# This file is a part of Typhoon HIL API library.
#
# Typhoon HIL API is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
This module provides functionality to execute tests.
Tests are written as ordinary Python source files.
"""
from __future__ import print_function, unicode_literals

from collections import namedtuple
import imp
from time import strftime
import io
import os
import webbrowser
import sys
import traceback
from datetime import datetime as date

import jinja2
from typhoon.api.test_executor.reporting import Report
from typhoon.api.test_executor.report_template import REPORT_TEMPLATE


class NotSupportedModule(Exception):
    # custom exception
    pass


__all__ = ["execute_tests"]


# Name of main test function
TEST_FUNCTION_NAME = "test"
LOG_DIR = "_logs"

# Named tuple for encapsulating test status and other information about test
TestInfo = namedtuple("TestInfo", "name description status start_time")

COLOR_MAPPING = {
    "Passed": "lightgreen",
    "Failed": "pink",
    "Error": "crimson",
    "Skipped": "cyan",
    "In progress": "yellow"
}


def get_test_module(test_filename):
    """
     Return python module which was built from test file.

     Arguments:
         test_filename(str): Python file which represents one test.

     Returns:
         Module object for Python test file or None if module cannot be found.
     """
    test_dir, test_file = os.path.split(os.path.abspath(test_filename))
    module_name, __ = os.path.splitext(test_file)

    module_file, pathname, description = imp.find_module(module_name,
                                                         [test_dir])
    module = imp.load_module(module_name, module_file, pathname, description)

    return module


def get_test_function(test_filename):
    """
     Return test function from test file.

     Arguments:
         test_filename(str): Test file name.
     Returns:
         Test function or None if test function cannot be found in module.
     """
    test_module = get_test_module(test_filename)
    return getattr(test_module, TEST_FUNCTION_NAME, None)


def get_test_name(test_filename):
    """
     Get test name.

     Arguments:
         test_filename(str): Test file.

     Returns:
         Returns name of the test or None.
     """
    module = get_test_module(test_filename)
    return getattr(module, "TEST_NAME", None)


def get_test_description(test_filename):
    """
     Get test description.

     Arguments:
         test_filename(str): Test file.

     Returns:
         Returns test description or None.
     """
    module = get_test_module(test_filename)
    return getattr(module, "TEST_DESCRIPTION", None)


def execute_test(test_filename, test_number, *parameters):
    """
     Execute test in test file.

     Arguments:
         test_filename(str): Python file with test function.
         parameters(list): List of parameters to call test function with.

     Returns:
         object of class Test with some test information
     """
    # Get test function from test file
    test_function = get_test_function(test_filename)
    test_name = get_test_name(test_filename)
    test_description = get_test_description(test_filename)

    if test_function is None:
        test = TestInfo(name=test_name,
                        description=test_description,
                        status="Error",
                        start_time=strftime("%d-%b-%Y %H:%M:%S"))
        print("ERROR: test file doesn't have correct main test function")
        return test

    #
    # All output from test function will be redirected to log file.
    #
    log_file_path = os.path.join(LOG_DIR, "test_{0}.log".format(test_number))
    if sys.version_info[0] < 3:
        output = io.open(file=log_file_path, mode="wb", buffering=0)
    else:
        output = io.open(file=log_file_path, mode="w", encoding="utf-8")

    #
    # Instantiate file object to
    #

    # Save standard output and error and redirect output to memory buffer
    sys.stdout = output
    sys.stderr = output

    #
    # First backup current path, path of caller and set current working
    # directory to directory in which test file is located
    #
    path_backup = os.getcwd()
    os.chdir(os.path.split(os.path.abspath(test_filename))[0])

    # Execute test function
    try:
        test_start_time = strftime("%d-%b-%Y %H:%M:%S")
        result = test_function(*parameters)
    except BaseException:
        # Print exception
        traceback.print_exc(file=sys.__stdout__)
        sys.__stdout__.flush()

        # Return error info to display in report
        error_info = TestInfo(
            name=test_name,
            description=test_description,
            status="Error",
            start_time=test_start_time,
        )
        return error_info
    finally:
        # Restore caller path
        os.chdir(path_backup)

        # Restore standard output and standard error streams
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    # Store all test information and return that
    if result in ("Skipped", "skipped"):
        status_message = result.capitalize()
    else:
        status_message = "Passed" if result else "Failed"

    test = TestInfo(name=get_test_name(test_filename),
                    description=get_test_description(test_filename),
                    status=status_message,
                    start_time=test_start_time)

    return test


def execute_tests_ex(tests, **kwargs):
    """
    Execute tests.

    Arguments:
        tests(list): List of test descriptor lists.

    Returns:
        None
    """
    _execute_tests(tests, **kwargs)


def execute_tests(*tests, **kwargs):
    """
     Execute one or more tests.

     Arguments:
         tests(list): Captures many test descriptors (lists).

     Returns:
         None
     """
    _execute_tests(tests, **kwargs)


def _execute_tests(tests, **kwargs):
    """
    Internal function for execution tests

    Arguments:
        tests(tuple): Tuple of test descriptors.
    """
    # get reporting info object if passed by user
    # if not create empty one
    arg = kwargs.get('report_info', None)
    reporting_info = arg if arg is not None else Report()

    num_of_tests = len(tests)

    # get time when tests are executed
    start_time = date.strftime(date.now(), "%d-%b-%Y %H:%M:%S")

    test_queue = []
    html_template = load_report_template()

    # Create log directory or clean it up if it exists
    prepare_log_directory(LOG_DIR)

    # create blank report file
    update_html_report(html_template,
                       finished=False,
                       tests=[],
                       report_info=reporting_info,
                       time=start_time,
                       num_tests=num_of_tests)

    # show report file
    try:
        webbrowser.open(os.path.join(os.getcwd(), "report.html"))
    except Exception:
        print("Exception: Web browser cannot be launched")

    for test_number, test_descriptor in enumerate(tests, 1):
        # First, build html report with current test as running
        test_file = test_descriptor[0]

        current = TestInfo(name=get_test_name(test_file),
                           description=get_test_description(test_file),
                           status="In progress",
                           start_time=strftime("%d-%b-%Y %H:%M:%S"))

        test_queue.append(current)

        update_html_report(html_template,
                           finished=False,
                           tests=test_queue,
                           report_info=reporting_info,
                           time=start_time,
                           num_tests=num_of_tests)

        # form log
        log = "[%s/%s] Executing test '%s'..." % (test_number,
                                                  len(tests),
                                                  os.path.split(
                                                      test_descriptor[0])[1])
        print(log)

        #
        # Test descriptor has the following format: [test_file, parameters]
        # Example ["test_something.py", 1, 2, 4] or ["test_two.py"]
        #
        test_info = execute_test(test_descriptor[0], test_number,
                                 *test_descriptor[1:])

        test_queue.remove(current)
        test_queue.append(test_info)

        update_html_report(html_template,
                           finished=False,
                           tests=test_queue,
                           report_info=reporting_info,
                           time=start_time,
                           num_tests=num_of_tests)
    else:
        #
        # Render html report file, but this time with finished indicator
        # set to True to disable html page auto-refresh
        #
        update_html_report(html_template,
                           finished=True,
                           tests=test_queue,
                           report_info=reporting_info,
                           time=start_time,
                           num_tests=num_of_tests)


def update_html_report(template, finished, tests, report_info=None, time=None,
                       num_tests=None):
    """
     Generate html report file.

     Arguments:
         template(jinja2.Template): Template used for rendering content.
         finished(bool): Indicator if this is final rendering.
         tests(iterable): Collection of test information's objects.

     Returns:
         None
     """
    rendered_content = template.render(finished=finished,
                                       tests=tests,
                                       colors=COLOR_MAPPING,
                                       report=report_info,
                                       time=time,
                                       num_tests=num_tests)

    with io.open("report.html", mode="w", encoding="utf-8") as out:
        out.write(rendered_content)


def load_report_template():
    """
     Load and return jinja2 template object for html report.

     Arguments:
         None

     Returns:
         Jinja2 template object for html report
     """
    return jinja2.Template(REPORT_TEMPLATE)


def prepare_log_directory(log_dir):
    """
     Prepare log directory (either create one if doesn't exists or if directory
     exists delete its contents).

     Arguments:
         log_dir(str): Name of log directory.

     Returns:
         None
     """
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    else:
        for filename in os.listdir(log_dir):
            os.remove(os.path.join(log_dir, filename))
