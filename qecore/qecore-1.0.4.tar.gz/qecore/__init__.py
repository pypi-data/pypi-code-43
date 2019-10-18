#!/usr/bin/env python3
import os
import shlex
import types
import logging
from time import sleep, time
from subprocess import CalledProcessError, check_output, STDOUT
from functools import partial
from dogtail.rawinput import holdKey, releaseKey


__author__ = """Michal Odehnal <modehnal@redhat.com>"""
__version__ = "1.0.0"
__copyright__ = "Copyright © 2018-2020 Red Hat, Inc."
__license__ = "GPL"
__all__ = ("application", "common_steps", "get_node", "image_matching", "sandbox", "time_limit")


QE_LOGGER = logging.getLogger("DESKTOPQE")
FORMAT = "[%(filename)s:%(lineno)3s] %(message)s"
logging.basicConfig(format=FORMAT)
QE_LOGGER.setLevel(logging.INFO)

QE_DEVELOPMENT = not os.path.isdir("/mnt/tests/")


def get_application(context, application):
    """
    Get <accessibility_object> of application root, based upon given name.

    @param context : <context_object>
        Context object that is passed from common steps.
    @param application : str
        String of application identification: name.
    @return : <accessibility_object>
        Return root object of application.
    """

    app_class_to_return = None
    try:
        app_class_to_return = getattr(context, application)
    except AttributeError:
        for app in context.sandbox.applications:
            if app.component == application:
                app_class_to_return = app
                break
    except TypeError:
        app_class_to_return = context.sandbox.default_application
        assert context.sandbox.default_application is not None, \
            "Default application was not found. Check your environment file!"

    assert app_class_to_return is not None, \
        "Application was not found. Check your environment or feature file!"
    assert not isinstance(app_class_to_return, str), \
        "Application class was not found. Usually indication of not installed application."

    return app_class_to_return


def run(command, verbose=False):
    """
    Execute a command and get output.

    @param command : str
        Command to be executed.
    @param verbose : bool
        Boolean value for verbose option.
    @return : str
        Return string value of command output.
    @return : list
        Return list value of command upon verbose option \
        set in format (output, return code, exception).
    """

    try:
        output = check_output(command, shell=True, stderr=STDOUT, encoding="utf-8")
        return output if not verbose else (output, 0, None)
    except CalledProcessError as error:
        return error.output if not verbose else (error.output, error.returncode, error)

#behave-common-steps leftover
def wait_until(tested, element=None, timeout=30, period=0.25, params_in_list=False):
    """
    This function keeps running lambda with specified params until the
    result is True or timeout is reached. Instead of lambda, Boolean variable
    can be used instead.
    Sample usages:
     * wait_until(lambda x: x.name != 'Loading...', context.app.instance)
       Pause until window title is not 'Loading...'.
       Return False if window title is still 'Loading...'
       Throw an exception if window doesn't exist after default timeout

     * wait_until(lambda element, expected: x.text == expected,
           (element, 'Expected text'), params_in_list=True)
       Wait until element text becomes the expected (passed to the lambda)

     * wait_until(dialog.dead)
       Wait until the dialog is dead

    """

    if isinstance(tested, bool):
        curried_func = lambda: tested
    # or if callable(tested) and element is a list or a tuple
    elif isinstance(tested, types.FunctionType) and \
            isinstance(element, (tuple, list)) and params_in_list:
        curried_func = partial(tested, *element)
    # or if callable(tested) and element is not None?
    elif isinstance(tested, types.FunctionType) and element is not None:
        curried_func = partial(tested, element)
    else:
        curried_func = tested

    exception_thrown = None
    mustend = int(time()) + timeout
    while int(time()) < mustend:
        try:
            if curried_func():
                return True
        except Exception as error:  # pylint: disable=broad-except
            # If lambda has thrown the exception we'll re-raise it later
            # and forget about if lambda passes
            exception_thrown = error
        sleep(period)
    if exception_thrown is not None:
        raise exception_thrown  # pylint: disable=raising-bad-type
    else:
        return False


KEY_VALUE = {
    "Alt" : 64, "Alt_L" : 64, "Alt_R" : 108,
    "Shift" : 50, "Shift_L" : 50, "Shift_R" : 62,
    "Ctrl" : 37, "Tab" : 23, "Super" : 133,
}

class HoldKey:
    def __init__(self, key_name):
        self.key_name = key_name
        holdKey(self.key_name)
    def __enter__(self):
        return self
    def __exit__(self, my_type, value, traceback):
        releaseKey(self.key_name)


class Tuple(tuple):
    def __add__(self, other):
        return Tuple(x + y for x, y in zip(self, other))
    def __rmul__(self, other):
        return Tuple(other * x for x in self)
    def __eq__(self, other):
        return (x == y for x, y in zip(self, other))
    def __lt__(self, other):
        return self[0] < other[0] or self[1] < other[1]
    def __gt__(self, other):
        return self[0] > other[0] or self[1] > other[1]


def validate_command(command):
    # Lets take care of any scripts user would like to try. Test
    parsed_command = shlex.split(command)
    valid_command = ""
    for command_part in parsed_command:
        for character in command_part:
            valid_command += f"\\{character}" if not character.isalpha() else character
        valid_command += " "
    return valid_command


def verify_path(template_path):
    try:
        assert os.path.isfile(template_path)
    except Exception as error:
        assert False, f"Desired file was not found: {error}"
    return template_path


SPACER = ' '
def plain_dump(node):
    def crawl(node, depth):
        dump(node, depth)
        for child in node.children:
            crawl(child, depth + 1)

    def dump_std_out(item, depth):
        # str wont possibly work in p3
        print(SPACER * depth + str(item) + \
            f"     [p:{item.position}, s:{item.size}, vis:{item.visible}, show:{item.showing}]")

    dump = dump_std_out
    crawl(node, 0)
