# Basic Flattening Utility
# Author: Spencer Hanson, for Swimlane


import re
import six
from types import FunctionType, LambdaType, MethodType, CodeType, GeneratorType, TracebackType, FrameType
from types import GetSetDescriptorType, MemberDescriptorType
from dict_plus import SortedDictPlus
import pendulum
import warnings


BinaryType = six.binary_type
TextType = six.text_type

if six.PY3:  # Remapping of types from py2 to py3
    import types
    from builtins import str as unicode
    NoneType = type(None)
    TypeType = NoneType
    BooleanType = type(True)
    IntType = six.integer_types
    LongType = float
    FloatType = LongType
    ComplexType = NoneType
    ClassType = type
    InstanceType = getattr(types, "InstanceType", object)
    UnboundMethodType = types.FunctionType
    ModuleType = NoneType
    FileType = NoneType
    XRangeType = NoneType
    BufferType = NoneType
    SliceType = NoneType
    EllipsisType = NoneType
    DictProxyType = NoneType
    NotImplementedType = NoneType
    StringTypes = six.string_types
    TupleType = tuple
    ListType = list
    DictType = dict

else:
    from types import *


"""
Flattener file to provide utilites for dealing with messy JSON
"""


class BasicList(object):
    """Class to keep track of Lists of Basic Types
    """
    def __init__(self, v):
        self.v = v


class Flattener(object):
    """
    Flattener class to easily flatten JSON
    """

    BASIC_TYPES = (NoneType, TypeType, BooleanType, IntType, LongType, FloatType, ComplexType, FunctionType, LambdaType,
                   GeneratorType, CodeType, ClassType, InstanceType, MethodType, UnboundMethodType, ModuleType,
                   FileType, XRangeType, SliceType, EllipsisType, TracebackType, FrameType, BufferType, DictProxyType,
                   NotImplementedType, GetSetDescriptorType, MemberDescriptorType, StringTypes, BinaryType, TextType,
                   BasicList)

    LIST_TYPES = (TupleType, ListType, set, frozenset)

    DICT_TYPES = (DictType, SortedDictPlus)

    def __init__(self, prefix=None, stringify_lists=True, shallow_flatten=False,
                 keep_simple_lists=True, autoparse_dt_strs=True, special_dt_formats=None, oldest_dt_allowed=None,
                 ignore_dt_formats=None):
        """
        Create a new Flattener object with specific options

        Args:
            prefix: Prefix to add to the data after flattening
            stringify_lists: Should we turn lists with basic types into CSVs? Defaults to True
            shallow_flatten: Should we ignore the first level of nesting, and only flatten each element within it?
            Used for lists of dictionaries
            keep_simple_lists: If a list in the resulting flattened dict is only integers or only strings, even if
            stringify_lists is True, keep this list
            autoparse_dt_strs: Do we attempt to automatically parse datetime looking strings/ints/floats to ISO8601?
            special_dt_formats: List of string formats to attempt parsing on for auto DT parsing. Will be ignored if
            autoparse_dt_strs is False
            oldest_dt_allowed: String of the oldest datetime that is allowed to be parsed. Defaults to 2005
            ignore_dt_formats: A list of formats to ignore when autoconverting a string to a timestamp
        """

        self.prefix = prefix
        self.stringify_lists = stringify_lists
        self.shallow_flatten = shallow_flatten
        self.keep_simple_lists = keep_simple_lists
        self.autoparse_dt_strs = autoparse_dt_strs

        if ignore_dt_formats:
            if not isinstance(ignore_dt_formats, list):
                raise ValueError("Invalid ignored datetime format!, Must be list!")
            self.ignore_dt_formats = ignore_dt_formats
        else:
            self.ignore_dt_formats = [
                "\d+/\d+$"  # Don't match stuff like 5/67
            ]

        if special_dt_formats:
            if not isinstance(special_dt_formats, list):
                raise ValueError("Invalid special datetime format!, Must be list!")

            self.special_dt_formats = special_dt_formats
        else:
            self.special_dt_formats = []

        if oldest_dt_allowed:
            self.oldest_dt_allowed = pendulum.parse(oldest_dt_allowed)
        else:
            self.oldest_dt_allowed = pendulum.parse("2005")

    def _try_parse_dt(self, value, is_number=False):
        """
        Try to parse a given value into a pendulum object, then return the iso string
        Works with strings and numbers that look like datestamps
        Ignores anything not parsed, returning it without parsing
        Ignores any datetime that is too old (could just be a really big numerical value) (anything past 2005)
        Uses self.special_dt_formats for other formats that could be specific to the data

        Args:
            value: Value to attempt to parse into a datetime
            is_number: Is the value a number and should be treated as a timestamp?

        """
        dt = None

        try:
            value = int(value)
            is_number = True
        except ValueError:
            # Attempt to parse the value as a number, in case it's a string
            pass

        if self.ignore_dt_formats and not is_number:
            for fmt in self.ignore_dt_formats:
                if re.match(fmt, value):
                    return value

        try:
            if is_number:
                dt = pendulum.from_timestamp(value)
            else:
                dt = pendulum.parse(value)
        except Exception:  # Broad exception clause to be picky about dates and parsing errors
            if is_number:  # Can't parse number with format, must be unparsable
                return value

            for fmt in self.special_dt_formats:  # Try special formats
                try:
                    dt = pendulum.from_format(value, fmt)
                except Exception:
                    continue

        if dt:
            diff = self.oldest_dt_allowed.diff(dt)
            signed_diff = diff.years * (1 if diff.invert else -1)
            if signed_diff <= 0:
                # Difference between datetime and oldest_dt is negative, which means it's oldest_dt+
                return dt.to_iso8601_string()
            else:
                # Difference is positive, earlier than oldest_dt, probably not a timestamp
                return value
        else:
            return value

    def combine_list(self, data, key):
        """Combine a list or listdict into a dict entry to be flattened.

        Examples:

            Combine a list into a key::

                >>>combine_list([1,2,3], "a")
                {"a": "1,2,3"}

                >>>combine_list(["A","B"], "test")
                {"test": "A,B"}

                >>>combine_list([{"a": 1, "b": 2}, {"a": 3, "b": 4}])
                {"a": [1,3], "b": [2,4]}

        Args:
            data: List data to combine
            key: Key to combine the data into

        Returns:
            Dict with combined data from the list

        """
        if not isinstance(data, ListType):
            raise Exception("Can't combine non-list!")
        if len(data) > 0 and isinstance(data[0], DictType):
            return combine_listdict(data)
        else:
            return {key: data}

    def flatten(self, data, prefix=None, shallow_flatten=None):
        """General flattening function
        Method to flatten a dict like or listdict

        Makes the keys lowercase, removes .'s and replaces spaces with underscores::

            a["b C.D"] = {"e": f} -> a["b_cd_e"] = f


        All values are basic types of string or integer
        Lists will be flattened into CSV strings
        Works recursively on list-dicts and inner dicts

        Args:
            data: List of dictionaries or dictionary to flatten
            prefix: Prefix to add to the data after flattening
            shallow_flatten: Should we ignore the first level of nesting, and only flatten each element within it?
            Used for lists of dictionaries

        Returns:
            Single level dictionary/List of single level dictionaries

        """

        if self.prefix and prefix is None:  # prefix has priority over self.prefix
            prefix = self.prefix

        if shallow_flatten is None:  # Same with shallow flatten
            shallow_flatten = self.shallow_flatten

        if shallow_flatten:
            return [self.flatten(item, prefix=prefix, shallow_flatten=False) for item in data]

        # result = None
        is_basictype = False
        if isinstance(data, Flattener.DICT_TYPES):
            # Dict types
            data = SortedDictPlus(data)
            result = self.flatten_dict(data, prefix)
            for k, v in result.iteritems():  # Convert BasicList back to regular list to complete flattening
                if isinstance(v, BasicList):
                    result[k] = v.v

        elif isinstance(data, Flattener.LIST_TYPES):
            # Complex list-like types
            listd = [self.flatten(item, prefix=prefix) for item in list(data)]
            result = combine_listdict(listd)

        elif isinstance(data, Flattener.BASIC_TYPES):
            result = data  # Basic types
            is_basictype = True
        else:
            raise Exception("Don't know how to flatten {}".format(data.__class__))  # Unknown type

        # Assumes that the dict has been flattened at least a bit, before attempting to stringify lists
        if self.stringify_lists and not is_basictype:
            if isinstance(result, DictType):  # if there is a list within the dict
                for k, v in result.items():
                    if isinstance(result[k], list):
                        stringify_list = True

                        if self.keep_simple_lists:
                            stringify_list = not is_simplelist(v)
                        
                        if stringify_list:
                            result[k] = ",".join(unicode(vi) for vi in v)

            else:
                new_result = []
                basictype_list = True  # Is our list something like [1, 2] or ["a", "b"] not [{"a": 1}, "b"]
                for item in iter(result):
                    if not isinstance(item, Flattener.BASIC_TYPES):
                        basictype_list = False
                    if isinstance(item, list):
                        new_result.append(",".join(unicode(vi) for vi in item))
                    else:
                        new_result.append(item)

                if basictype_list:
                    if self.keep_simple_lists and not is_simplelist(result):
                        new_result = ",".join([str(el) for el in new_result])

                result = new_result

        return result
    
    def flatten_dict(self, data, prefix=None):
        """Internal single dict flattening function used recursively

        Args:
            data: data to flatten
            prefix: Key prefix

        Returns:
            Flattened dict

        """
        flat_dict = SortedDictPlus()

        for k, v in data.items():
            k = k.replace('.', '').replace(' ', '_')  # Reformat the key
            k = prefix + "_" + k if prefix else k

            if isinstance(v, DictType):  # Dict within dict
                sub_dict = self.flatten_dict(v, prefix=k)
                # Combine the flat_dict with the flattened sub_dict
                flat_dict = merge_dicts(sub_dict, flat_dict)
                flat_dict = flatten_single_lists(flat_dict)

            elif isinstance(v, ListType):
                if self.keep_simple_lists and is_simplelist(v):  # If it's a basic list, it's a base case
                    flat_dict[k] = BasicList(v)
                else:
                    # Not a simple list, could still be a basic list after flattening elements
                    flat_els = []
                    for el in v:
                        flat_els.append(self.flatten(el, prefix=k))

                    if len(flat_els) > 0 and isinstance(flat_els[0], DictType):  # List of dicts
                        flat_dict = merge_dicts(flat_dict, self.combine_list(flat_els, k))
                    else:
                        flat_dict[k] = BasicList(flat_els)  # Keep list

            else:  # Base case, unflattenable value
                if self.autoparse_dt_strs:
                    if isinstance(v, StringTypes):  # Attempt to parse string into datetime
                        v = self._try_parse_dt(v)
                    elif isinstance(v, (IntType, FloatType)):  # Attempt to parse int/float into a timestamp datetime
                        v = self._try_parse_dt(v, is_number=True)

                flat_dict[k] = v

        return flat_dict


def do_flatten(data, prefix=None, stringify_lists=True, shallow_flatten=False,
               keep_simple_lists=True, autoparse_dt_strs=True):
    """Simple alias for creating a flattener then running flatten() with options"""

    fl = Flattener(prefix=prefix, stringify_lists=stringify_lists, shallow_flatten=shallow_flatten,
                   keep_simple_lists=keep_simple_lists, autoparse_dt_strs=autoparse_dt_strs)

    return fl.flatten(data)


def hoist_key(key, from_list):
    """Hoist out a specific key within a given listdict

    Examples:

        To hoist the key "a"::

            >>>hoist_key("a", [{"a": 1, "b": 4},{"a": 2}, ..])
            [1,2,3]

    Args:
        key: Key to grab from each dict within the list of dictionaries
        from_list: listdict to source from

    Returns:
        list of hoisted values

    """
    hoisted = []
    for element in from_list:
        if key not in element:
            raise Exception("Key {} not found in dict {}".format(key, element))
        hoisted.append(element[key])
    return hoisted


def hoist_keys(key_list, from_list):
    """Hoist out a specific keys within a given listdict

    Examples:

        To hoist out multiple keys::

            >>>hoist_keys(["a", "b"], [{"a": 1, "b": 4},{"a": 2, "b": 2, "c": 3}, ..])
            [[1,2],[4,2]]  #[[all a keys], [all b keys]]

    Args:
        key_list: List of keys to hoist from the list of dictionaries
        from_list: List of dictionaries that have the specified key in it

    Returns:
        List of the list of hoisted keys

    """
    hoisted = []
    for key in key_list:
        hoisted.append(hoist_key(key, from_list))
    return hoisted


def replace_dict_prefix(prefix, replace_val, from_dict):
    """Change a similar prefix on keys within a dict to something else, say ``annoying_stuff_ -> a_``

    Examples:

        Remove the annoying_stuff prefix::

            >>>{"annoying_stuff_important_stuff": "data", "annoying_stuff_asdf": "data2"}
            {"a_important_stuff": "data", "a_asdf": "data2"}

    Args:
        prefix: Prefix to replace
        replace_val: Prefix to replace with
        from_dict: Dictionary to replace prefix on

    Returns:
        Changed from_dict

    """
    for k in from_dict.keys():
        if k.startswith(prefix):
            newk = k.replace(prefix, replace_val, 1)
            if newk in from_dict:
                raise Exception("Can't remove prefix, results in namespace collision!")
            from_dict[newk] = from_dict.pop(k)
    return from_dict


def merge_dicts(d1, d2):
    """Merge dict d1 with dict d2. If they share keys, treat it as a listdict

    Args:
        d1: dict1
        d2: dict2

    Returns:
        Combined dict result
    """

    # First, we check if they share any keys (could be a listdict)
    shared_keys = set(d1.keys()).intersection(set(d2.keys()))
    if shared_keys:
        # They share keys, so we must combine them accordingly
        return combine_listdict([d1, d2])
    else:
        # No shared keys, just merging dicts together
        d1.update(d2)
        return d1


def flatten_single_lists(data):
    """Flatten lists within a dict that only contain one element

    Examples:

        Flatten the data::

            >>>flatten_single_lists({"a": [1], "b": 2, "c":[3,4]})
            {"a": 1, "b": 2, "c": [3, 4]}

    Args:
        data: Dict data to flatten lists in

    Returns:
        More flattened data

    """
    if not isinstance(data, SortedDictPlus):
        data = SortedDictPlus(data)
    for k, v in data.items():
        if isinstance(v, ListType):
            if len(v) == 1:  # Single entry list, can reduce to basic type
                data[k] = v[0]
    return data


def is_simplelist(data):
    """Determine whether a list is a simple list. A simple list is a list of purely integers or purely strings
    Not to be confused with a basic list, which is a list of basic types
    Args:
        data: List to check

    Returns:
        True if it is a basic list, else False
    """
    if not len(data) > 0:
        return False  # Not a basic list because it's empty

    is_basic = True

    type_match = data[0]
    if not isinstance(type_match, int) and not isinstance(type_match, StringTypes):
        is_basic = False  # Type of data in list isnt int or str
    else:
        for datai in data:
            if not isinstance(datai, type(type_match)):
                is_basic = False

    return is_basic


def combine_listdict(data):
    """Combine a listdict into a single dictionary, NOT flattening.

    Examples:

        If you have data like so::

            [{"e": f_0, "g": h_0, ..}, {"e": f_1, "g": h_1, ..}]

        You will get a new dict c, like::

            c["e"] =  [f0, f1, ...]
            c["g"] =  [h0, h1, ...]

        If your data is incomplete, such as::

            [{"a": a_0, "b": b_0}, {"a": a_1}, {"a": a_2, "b": b_2}, ..]

        The resulting dict c will look like::

            c["a"] = [a_0, a_1, a_2]
            c["b"] = [b_0, None, b_2]


    Args:
        data: List of DictPlus's to combine into a single dictionary

    Returns:
        Combined dictionary
    """
    if not isinstance(data, ListType) or (len(data) > 0 and not isinstance(data[0], DictType)):
        return data  # Can't combine non-listdict, so return base list

    all_keys = set()  # Set of all keys within the entire listdict
    for el in data:
        for k, v in el.items():
            all_keys.add(k)

    result = SortedDictPlus()
    for el in data:
        # If an element of the list is not a dict, this isn't a true listdict and cannot be flattened
        if not isinstance(el, DictType):
            raise Exception("Cannot flatten nonpure listdict!")
        seen_keys = []

        def add_key_to_result(nk, nv, res):
            if nk in res:
                if isinstance(nv, ListType):
                    """
                    Special case when:
                    {
                    "a_id": val,
                    "a": {
                        "id": val,
                        "other": [list val]
                    }
                    Collision of sub-listdict and and reformatted superkey lead to two keys being mapped to 'a_id'.
                    One option is to combine like [val1, val2] but can lead to [val, []] which isn't flattened
                    Other option is to extend like [val1].extend([val2]) but those "a_id" and "a": "id" might not be
                     related.
                    Current solution is to take the inner key ("a": "id") and turn it into "a_id_" appending '_'
                    until no collision - UPDATE implementation will now raise an Exception

                    The "other": [] is required, since the flattening treats "a" like as a dict-list, therefore "id"
                    is turned into a list (until flattening of subdict "a" is complete) which causes this error

                    """
                    raise Exception("Too nested data, will result in collision, must manually simplify")
                else:
                    res[nk].append(nv)
            else:
                if isinstance(nv, ListType):
                    res[nk] = nv
                else:
                    res[nk] = [nv]

        for k, v in el.items():
            seen_keys.append(k)
            add_key_to_result(k, v, result)

        # Add None to keys that didn't show up
        none_keys = list(all_keys.difference(seen_keys))
        for k in none_keys:
            add_key_to_result(k, None, result)

    return result


def clean_xmltodict_result(data, to_remove_list=None):
    """Helper method to clean the output of an xmltodict with messy '#' and '@' trailing

    Args:
        data: dict
        to_remove_list: list of strings to replace with underscores in the resulting dict

    Returns:
        Cleaned dictionary

    """
    keys_to_delete = []
    pairs_to_add = []

    for k, v in six.iteritems(data):
        match = re.match(".*_([@#].*$)", k)  # Ends with _#text or _@property
        if match:
            # Remove the '#' or '@' ie  asdf_@property -> asdf_property
            pairs_to_add.append((k.replace(match.groups()[0], match.groups()[0][1:]), v))
            keys_to_delete.append(k)

    for k in keys_to_delete:
        data.pop(k)

    for k, v in pairs_to_add:
        if k in data:
            raise Exception("Cannot clean {}, results in namespace collision".format(k))
        data[k] = v

    data = SortedDictPlus(data)
    if not to_remove_list:
        to_remove_list = []
    
    to_remove_list.extend(["@", "-", ":", "#", "$", "%"])
    to_remove_list = list(set(to_remove_list))  # Make sure we don't have duplicates
    
    def new_kv(k, v):  # Replace all invalid characters with underscores
        for to_remove in to_remove_list:
            k = k.replace(to_remove, "_")
        return k, v

    data.map(new_kv)

    return data
