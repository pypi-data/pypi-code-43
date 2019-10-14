#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modules that contains utility functions related with Python
"""


from __future__ import print_function, division, absolute_import

import os
import sys
import imp
import ast
import uuid
import time
import types
import traceback
import collections

from tpPyUtils import strings


# region Classes
class RollbackImporter(object):
    """
    This class is used to restore the loaded modules in a certain time after the rollback is instantiated
    It does by storing the list of loaded Python modules when rollback is initialized and if the rollback
    is uninstalled, the modules loaded after rollback creation will be deleted, forcing Python to reload
    them when the module is next imported
    """

    def __init__(self):
        """
        Creates an instance and installs and store the current imported modules list
        """

        self._prev_modules = set (sys.modules.keys())

    def uninstall(self):
        """
        Removes current loaded modules loaded after RollbackImporter was instantiated
        """

        for mod_name in sys.modules.keys():
            if mod_name not in self._prev_modules:
                del sys.modules[mod_name]


class classproperty(object):
    """
    Simplified way of creating getter and setters in Python
    """

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)
# endregion


# region Functions
def add_to_python_path(path):
    """
    Adds a path to the Python path, only if it is not present in the Python path
    :param path: str, path to add to the Python path
    """

    if not path:
        return

    if not path in sys.path:
        sys.path.append(path)


def load_python_module(module_name, directory):
    """
    Loads a given module name located in the given directory
    NOTE: After loading a module you can access programmatically to all functions and attributes of the module
    :param module_name: str, name of the module we want to load
    :param directory: str, directory path where the module is located
    :return: mod, loaded module
    """

    from tpPyUtils import path, fileio

    if path.is_dir(directory):
        full_path = path.join_path(directory, module_name)
        if path.is_file(full_path):
            split_name = module_name.split('.')
            file_path, path_name, description = imp.find_module(split_name[0], [directory])
            try:
                module = imp.load_module(module_name, file_path, path_name, description)
            except Exception as e:
                file_path.close()
                return traceback.format_exc()
            finally:
                if file_path:
                    file_path.close()

            return module

    return None


def import_python_module(module_name, directory):
    """
    Imports the given module
    :param module_name: str, name of the module
    :param directory: str, path where the module is located
    :return: mod, imported module
    """

    from tpPyUtils import path, fileio

    if not path.is_dir(directory=directory):
        return

    module = None
    full_path = path.join_path(directory, module_name)
    if path.is_file(full_path):
        if not directory in sys.path:
            sys.path.append(directory)

        split_name = module_name.split('.')
        script_name = split_name[0]

        exec('import {}'.format(script_name))
        exec('reload({})'.format(script_name))

        module = eval(script_name)
        sys.path.remove(directory)

    return module


def source_python_module(module_file):
    """
    Sources the python module located in the given directory
    :param module_file: str
    :return: variant, sourced module || None
    """

    try:
        try:
            module_in = open(module_file, 'rb')
            import md5
            return imp.load_source(md5.new(module_file).hexdigest(), module_file, module_in)
        except:
            return traceback.format_exc()
        finally:
            try:
                module_in.close()
            except:
                pass
    except ImportError:
        traceback.print_exc(file=sys.stderr)
        return None


def get_version():
    """
    Return current Python version used
    :return: SemanticVersion, python version
    """

    from tpPyUtils import version
    py_version = sys.version_info
    current_version = version.SemanticVersion(
        major=py_version.major,
        minor=py_version.minor,
        patch=py_version.micro
    )

    return current_version


def is_python2():
    """
    Returns whether or not current version is Python 2
    :return: bool
    """

    return get_version().major == 2


def is_python3():
    """
    Returns whether or not current version is Python 3
    :return: bool
    """

    return get_version().major == 3


def clear_list(list_to_clear):
    """
    Clears given Python list
    :param list_to_clear: list
    """

    from tpPyUtils import version
    if get_version() < version.SemanticVersion(3, 2, 0):
        del list[:]
    else:
        list_to_clear.clear()


def list_diff(list1, list2):
    """
    Returns a a list with all the elements of second list that are not contained in the first list
    :param list1: list
    :param list2: list
    :return: list
    """

    return [i for i in list1 if not i in list2]


def list_to_string(list_):
    """
    Returns a string from the given list
    >>> list_to_string(['1,', '2', '3'])
    >>> # 1, 2, 3
    :param list_: list
    :return:str
    """

    list_ = [str(item) for item in list_]
    list_ = str(list_).replace("[", "").replace("]", "")
    list_ = list_.replace("'", "").replace('"', "")

    return list_


def string_to_list(str_):
    """
    Returns a list from the given string
    >>> string_to_list(['1', '2', '3'])
    >>> # ['1', '2', '3']
    :param str_:
    :return: list
    """

    str_ = '["' + str(str_) + '"]'
    str_ = str_.replace(' ', '')
    str_ = str_.replace(',', '","')

    return eval(str_)


def force_list(var):
    """
    Returns the given variable as list
    :param var: variant
    :return: list
    """

    if var is None:
        return []

    if type(var) is not list:
        if type(var) in [tuple]:
            var = list(var)
        else:
            var = [var]

    return var


def force_tuple(var):
    """
    Returns the given variable as tuple
    :param var: variant
    :return: list
    """

    if type(var) is not tuple:
        var = tuple(var)

    return var


def force_sequence(var, sequence_type=list):
    """
    Returns the given variable as sequence
    If the given variable is list or tuple and sequence_type is different, a conversion will be forced
    :param var: variant
    :return: sequence (tuple || list)
    """

    if type is not list or not tuple:
        sequence_type = list

    if type(var) == list and sequence_type == tuple:
        var = tuple(var)
    if type(var) == tuple and sequence_type == list:
        var = list(var)

    if not type(var) == sequence_type:
        return sequence_type(var)

    return var


def rotate_sequence(seq, current):
    """
    Rotates sequence in given index
    :param seq: list
    :param current: int
    :return: list
    """

    n = len(seq)
    for i in range(n):
        yield seq[(i + current) % n]


def index_of(obj, seq):
    """
    Returns the index of the first occurrence of obj in seq
    """

    try:
        if get_version() < 2.6:
            for index in (i for i in range(len(seq)) if seq[i] == obj):
                return index
            else:
                return next((i for i in range(len(seq)) if seq[i] == obj), None)
    except Exception:
        raise


def last_index_of(obj, seq):
    """
    Returns the index of the last occurrence of obj in seq
    """

    try:
        if get_version() < 2.6:
            for index in (i for i in range(len(seq) - 1, -1, -1) if seq[i] == obj):
                return index
        else:
            return next((i for i in range(len(seq) - 1, -1, -1) if seq[i] == obj), None)
    except Exception:
        raise


def zip_dict(*dcts):
    """
    Custom zip for dictionaries
    """

    for i in set(dcts[0]).intersection(*dcts[1:]):
        yield (i,) + tuple(d[i] for d in dcts)


def module_exists(moduleName):
    """
    Checks if a Python module exists (passing module name)
    :param moduleName: str, Name of module to be checked
    """
    try:
        module_info = imp.find_module(moduleName)
        module = imp.load_module(moduleName, *module_info)
        imp.find_module('__init__', module.__path__)
        has_module = True
    except:
        has_module = False
    return has_module


def find_missing_items(intList):
    """
    Returns missing integers numbers from a list of integers
    :param intList: list(int), list of integers
    :return: list(int),  sorted list of missing integers numbers of the original list
    """

    original_set = set(intList)
    smallest_item = min(original_set)
    largest_item = max(original_set)
    full_set = set(range(smallest_item, largest_item + 1))
    return sorted(list(full_set - original_set))


def safe_code_exec(cmd, env=dict()):
    """
    Safely execute code with specified dictionary
    """

    try:
        exec(cmd in env)
    except Exception:
        raise (sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])


def remove_dupes(iterable):
    """
    Removes duplicate items from iterable object preserving original iterable order
    :param iterable: iterable
    :return: iterable
    """

    unique = set()
    new_iter = iterable.__class__()
    for item in iterable:
        if item not in unique:
            new_iter.append(item)
        unique.add(item)
    return new_iter


def iter_by(iterable, count):
    """
    Returns a generator which will yield certain elements of the iterable. This elements are defined
    by the count steps
    for obj in iter_by(range(7), 3):
        print(obj)
    [0, 1, 2]
    [3, 4, 5]
    [6]
    :param iterable: iterable
    :param count: int, num of
    :return: generator
    """

    i = iter(iterable)
    while True:
        to_yield = list()
        try:
            for n in range(count):
                to_yield.append(i.next())
                yield to_yield
        except StopIteration:
            if to_yield:
                yield to_yield
            break


def enum(*sequential, **named):
    """
    Enum implementation that supports automatic generation and also supports converting the values
    of the enum back to names
    >>> nums = enum('ZERO', 'ONE', THREE='three')
    >>> nums.ZERO
    # 0
    >>> nums.reverse_mapping['three']
    # 'THREE'
    """

    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.items())
    enums['reverse_mapping'] = reverse
    return type(str('Enum'), (), enums)


def generate_uuid():
    """
    Returns a unique UUID
    :return: str
    """

    return str(uuid.uuid4().upper())


def itersubclasses(cls, _seen=None):
    """
    http://code.activestate.com/recipes/576949-find-all-subclasses-of-a-given-class/
    Iterator to yield full inheritance from a given class, including subclasses. This
    """

    if _seen is None:
        _seen = set()
    try:
        subs = cls.__subclasses__()
    except TypeError:
        subs = cls.__subclasses__(cls)

    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub


def get_inheritance_map(class_to_process):
    """
    Return the inheritance mapping of the given class
    :param class_to_process: class
    """

    import inspect
    return inspect.getmro(class_to_process)


def user_message(message, prefix='RigLib'):
    """
    Writes teh given prefix + message in the Python output
    :param message: str
    :param prefix: str
    """
    sys.stdout.write(prefix + ': ' + message + '\n')


def is_none(s):
    """
    Returns True if the given object has None type or False otherwise
    :param s: object
    :return: bool
    """

    return type(s).__name__ == 'NoneType'


def is_string(s):
    """
    Returns True if the given object has None type or False otherwise
    :param s: object
    :return: bool
    """
    return type(s) in [str, unicode]


def is_number(s):
    """
    Returns True if given string is int or float, False otherwise
    :param s: object
    :return: bool
    """
    if is_bool(s):
        return False
    return isinstance(s, int) or isinstance(s, float)


def is_bool(s):
    """
    Returns True if the given object has None type or False otherwise
    :param s: object
    :return: bool
    """
    return isinstance(s, bool) or str(s).lower() in ['true', 'false']


def is_list(s):
    """
    Returns True if the given object has list type or False otherwise
    :param s: object
    :return: bool
    """
    return type(s) in [list, tuple]


def is_dict(s):
    """
    Returns True if the given object has dict type or False otherwise
    :param s: object
    :return: bool
    """
    from collections import OrderedDict
    return type(s) in [dict, OrderedDict]


def return_list_without_duplicates(lst):
    """
    Removes duplicates from a list and return the new ilst
    :param lst: list
    :return: list
    """

    new_list = list()
    for item in lst:
        if item not in new_list:
            new_list.append(item)

    return new_list


def delete_pyc_file(python_script):
    """
    Deletes the .pyc file that corresponds to the given .py file
    :param python_script: str
    """

    from tpPyUtils import path, fileio

    script_name = path.get_basename(python_script)
    if not python_script.endswith('.py'):
        print('WARNING: Could not delete .pyc file for {}!'.format(script_name))
        return

    compile_script = python_script + 'c'
    if path.is_file(compile_script):
        compile_name = path.get_basename(compile_script)
        compile_dir_name = path.get_dirname(compile_script)
        if not compile_name.endswith('.pyc'):
            return

        fileio.delete_file(name=compile_name, directory=compile_dir_name)


def convert_list_to_string(*args):
    """
    Given a list returns a string
    :param args:
    :return: str
    """

    try:
        if args is None:
            return 'None'
        if not args:
            return ''
        new_args = list()
        for arg in args:
            if arg is not None:
                new_args.append(str(arg))
        args = new_args
        if not args:
            return  ''
        string_value = strings.join(args)
        string_value = string_value.replace('\n', '\t\n')
        if string_value.endswith('\t\n'):
            string_value = string_value[:-2]

        return string_value
    except Exception:
        raise(RuntimeError)


def get_class_parent_classes(base_class=None, parent_class=None):
    """
    Returns all base class parent classes
    :param base_class: obj, Base class
    :param parent_class: obj, Parent class
    :return: list<str>, parent class names
    """

    base_classes = list()
    cl = parent_class if parent_class is not None else base_class
    for b in cl.__bases__:
        if b.__name__ not in ['object']:
            base_classes.append(b)
            base_classes.extend(get_class_parent_classes(parent_class=b))

    return base_classes


def get_dict_ordered_keys_from_values(d):
    """
    Returns a list of keys from dict, ordered based on their values
    :param d: dict, dictionary to construct list from
    :return: list<variant>
    """

    return [i[0] for i in sorted(list(d.items()), key=lambda k, v: v)]


def get_dict_ordered_values_from_keys(d):
    """
    Returns a list of dictionary values, ordered based on their keys
    :param d: dict, dictionary to construct list from
    :return: list<variant>
    """

    return [d[key] for key in sorted(list(d.keys()))]


def flatten_list(list_to_flatten):
    """
    Returns a flattened version of the given list
    :param list_to_flatten: list, list to flatten
    :return: list
    """

    elems = list()
    for i in list_to_flatten:
        if isinstance(i, types.ListType):
            elems.extend(i)
        else:
            elems.append(i)

    return elems


def string_to_dictionary(string):
    """
    Converts a dictionary string representation into a dictionary
    :param string: str
    :return: dict
    """

    return ast.literal_eval(string)


def path_to_dictionary(path):
    """
    Returns the tree hierarchy of the given path as a Python dictionary
    :param path: str
    :return: dict
    """

    d = {'name': os.path.basename(path)}
    if os.path.isdir(path):
        d['type'] = 'directory'
        d['children'] = [path_to_dictionary(os.path.join(path, x)) for x in os.listdir(path)]
    else:
        d['type'] = 'file'

    return d


def to_3_list(item):
    """
    Converts item into a 3 item list
    :param item: var
    :return: list<var, var, var>
    """

    if not isinstance(item, list):
        item = [item] * 3

    return item


def u_print(msg, **kwargs):
    """
    `print` with encoded unicode.
    `print` unicode may cause UnicodeEncodeError
    or non-readable result when `PYTHONIOENCODING` is not set.
    this will fix it.
    :param msg: unicode, message to print
    :param kwargs: dict
    """

    from six import text_type

    if isinstance(msg, text_type):
        encoding = None
        try:
            encoding = os.getenv('PYTHONIOENCODING', sys.stdout.encoding)
        except AttributeError:
            # `sys.stdout.encoding` may not exists.
            pass
        msg = msg.encode(encoding or 'utf-8', 'replace')
    print(msg, **kwargs)


def dict_merge(dict, merge_dict):
    """
    Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.

    :param dict: dict onto which the merge is executed
    :param merge_dict: dct merged into dct
    :return: None
    """

    for k, v in merge_dict.iteritems():
        if (k in dict and isinstance(dict[k], dict)
                and isinstance(merge_dict[k], collections.Mapping)):
            dict_merge(dict[k], merge_dict[k])
        else:
            dict[k] = merge_dict[k]


def current_processor_time():
    """
    Retunrs the current processor time
    :return: float
    """

    if is_python2():
        return time.clock()
    else:
        return time.process_time()
