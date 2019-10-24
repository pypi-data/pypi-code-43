# Copyright (c) 2019 Applied Nonprofit Research. All rights reserved.
# Requires Python 3.7+.

import itertools
from typing import Dict, Tuple, List, Iterator, Optional, Any, Union

import pytest

data_types: Dict = {
    "folder_in_root": "Folder",
    "text_in_root": "Simple",
    "list_in_folder": "List",
    "text_in_list_in_folder": "Simple",
    "int_in_list_in_folder": "Simple",
    "list_in_root": "List",
    "text_in_list": "Simple",
    "outer_nested_list": "List",
    "text_in_outer_nested_list": "Simple",
    "inner_nested_list": "List",
    "text_in_inner_nested_list": "Simple",
    "dictionary_in_inner_nested_list": "Dictionary",
    "text_in_dictionary_in_inner_nested_list": "Simple",
    "dictionary_in_root": "Dictionary",
    "text_in_dictionary": "Simple",
    "int_in_dictionary": "Simple",
    "outer_nested_dictionary": "Dictionary",
    "text_in_outer_nested_dictionary": "Simple",
    "inner_nested_dictionary": "Dictionary",
    "text_in_inner_nested_dictionary": "Simple",
    "list_in_inner_nested_dictionary": "List",
    "text_in_list_in_inner_nested_dictionary": "Simple",
    "dictionary_in_list_in_inner_nested_dictionary": "Dictionary",
    "text_in_dictionary_in_list_in_inner_nested_dictionary": "Simple"
}

@pytest.fixture()
def common_values() -> Dict:
    return {
        "text_in_folder": "foo",
        "list_in_folder": [
            {
                "text_in_list_in_folder": "a"
            },
            {
                "text_in_list_in_folder": "b",
                "int_in_list_in_folder": 2
            },
            {
                "text_in_list_in_folder": "c",
                "int_in_list_in_folder": 3
            }
        ],
        "outer_nested_list": [
            {
                "text_in_outer_nested_list": "a"
            },
            {
                "text_in_outer_nested_list": "b",
                "inner_nested_list": [
                    {}
                ]
            },
            {
                "text_in_outer_nested_list": "c",
                "inner_nested_list": [
                    {
                        "text_in_inner_nested_list": "foo"
                    },
                    {
                        "text_in_inner_nested_list": "bar",
                        "dictionary_in_inner_nested_list": {
                            "black": {"text_in_dictionary_in_inner_nested_list": "white"},
                            "green": {"text_in_dictionary_in_inner_nested_list": "red"}
                        }
                    }
                ]
            }
        ],
        "dictionary_in_root": {
            "peter": {
                "text_in_dictionary": "a"
            },
            "paul": {
                "text_in_dictionary": "b",
                "int_in_dictionary": 2
            },
            "mary": {
                "text_in_dictionary": "c",
                "int_in_dictionary": 3
            }
        },
        "outer_nested_dictionary": {
            "peter": {
                "text_in_outer_nested_dictionary": "a"
            },
            "paul": {
                "text_in_outer_nested_dictionary": "b",
                "inner_nested_dictionary": {
                    "red": {}
                }
            },
            "mary": {
                "text_in_outer_nested_dictionary": "c",
                "inner_nested_dictionary": {
                    "orange": {
                        "text_in_inner_nested_dictionary": "foo"
                    },
                    "yellow": {
                        "text_in_inner_nested_dictionary": "bar",
                        "list_in_inner_nested_dictionary": [
                            {"text_in_list_in_inner_nested_dictionary": "black"},
                            {
                                "text_in_list_in_inner_nested_dictionary": "white",
                                "dictionary_in_list_in_inner_nested_dictionary": {
                                    "this is extreme": {
                                        "text_in_dictionary_in_list_in_inner_nested_dictionary": "but it works"
                                    },
                                    "another one": {
                                        "text_in_dictionary_in_list_in_inner_nested_dictionary": "also ok"
                                    }
                                }
                            },
                        ]
                    }
                }
            }
        }
    }

def find_columns_num(block: Union[Tuple, str, List]) -> int:
    num = 0
    for elem in block:
        if isinstance(elem, Tuple):
            num += find_columns_num(elem)
        else:
            elem_type = data_types[elem]
            if elem_type == "Simple":
                num += 1
            elif elem_type == "Dictionary":
                num += 1
    return num

# SO 10823877
def flatten(container: Union[List, Tuple]) -> Iterator:
    """Flattens an arbitrarily nested list."""
    for i in container:
        if isinstance(i, (list, tuple)):  # I didn't know you could supply a tuple of classes...
            for j in flatten(i):
                yield j
        else:
            yield i

def _cartesian(block_values: List) -> Iterator[List[Optional[Any]]]:
    """Starts with an arbitrarily nested list of lists, where each singly nested list represents all observed values for
    one or more columns in a spreadsheet column block. Yields lists representing rows of the column block."""
    for nested in itertools.product(*block_values):
        yield list(flatten(nested))

def _unpack_as_singleton(var_id: str, values: Dict) -> Iterator[List[str]]:
    value: Optional[Any] = values.get(var_id)
    yield [[value]]

def _unpack_as_dictionary(block: Tuple, values: Dict) -> Iterator[List[Optional[Any]]]:
    if values is None:
        yield [[None] * (find_columns_num(block) + 1)]
        return
    for i, (key, element) in enumerate(values.items()):
        yield from _cartesian([[key]] + [list(as_block_value(block, element))])

def as_block_value(block: Tuple, values: Dict) -> Iterator[List[Optional[Any]]]:
    """Takes a block of variable IDs representing a primitive, a list, or a keyed list (including nested lists and
    keyed lists) and yields lists of column values, where the columns represent a block of a larger CSV."""
    block_values: List = [None] * len(block)
    for i, subblock in enumerate(block):
        if isinstance(subblock, str):
            block_values[i] = _unpack_as_singleton(subblock, values)
        elif isinstance(subblock, tuple):
            root_id: str = subblock[0]
            dt: str = data_types[root_id]
            if dt == "List":
                nested_values: Optional[List] = values.get(root_id)
                if nested_values is None:
                    block_values[i] = [[None] * find_columns_num(subblock)]
                else:
                    cur = []
                    for k, elem in enumerate(nested_values):
                        cur.extend(list(as_block_value(subblock[1:], elem)))
                    block_values[i] = cur
            elif dt == "Dictionary":
                nested_values: Optional[Dict] = values.get(root_id)
                block_values[i] = _unpack_as_dictionary(subblock[1:], nested_values)
            else:
                raise ValueError('Variable "%s" (%s) is not a List or Dictionary root' % (root_id, dt))
    yield from _cartesian(block_values)

def test_singleton(common_values):
    block: Tuple = ("text_in_folder",)
    expected: List = [["foo"]]
    actual: List = list(as_block_value(block, common_values))
    assert expected == actual

def test_list(common_values):
    block: Tuple = (("list_in_folder", "int_in_list_in_folder", "text_in_list_in_folder"),)
    expected: List = [[None, "a"], [2, "b"], [3, "c"]]
    actual: List = list(as_block_value(block, common_values))
    assert expected == actual

def test_list_with_initial_singleton(common_values):
    block: Tuple = ("text_in_folder", ("list_in_folder", "int_in_list_in_folder", "text_in_list_in_folder"))
    expected: List = [["foo", None, "a"], ["foo", 2, "b"], ["foo", 3, "c"]]
    actual: List = list(as_block_value(block, common_values))
    assert expected == actual

def test_list_with_final_singleton(common_values):
    block: Tuple = (("list_in_folder", "int_in_list_in_folder", "text_in_list_in_folder"), "text_in_folder")
    expected: List = [[None, "a", "foo"], [2, "b", "foo"], [3, "c", "foo"]]
    actual: List = list(as_block_value(block, common_values))
    assert expected == actual

def test_list_with_no_columns(common_values):
    block: Tuple = (("list_in_folder",),)
    expected: List = [[], [], []]
    actual: List = list(as_block_value(block, common_values))
    assert expected == actual

def test_empty_list():
    block: Tuple = (("list_in_folder", "int_in_list_in_folder", "text_in_list_in_folder"),)
    expected: List = [[None, None]]
    actual: List = list(as_block_value(block, {}))
    assert expected == actual

def test_dictionary(common_values):
    block: Tuple = (("dictionary_in_root", "int_in_dictionary", "text_in_dictionary"),)
    expected: List = [["peter", None, "a"], ["paul", 2, "b"], ["mary", 3, "c"]]
    actual: List = list(as_block_value(block, common_values))
    assert expected == actual

def test_dictionary_with_no_columns(common_values):
    block: Tuple = (("dictionary_in_root",),)
    expected: List = [["peter"], ["paul"], ["mary"]]
    actual: List = list(as_block_value(block, common_values))
    assert expected == actual

def test_empty_dictionary():
    block: Tuple = (("dictionary_in_root", "int_in_dictionary", "text_in_dictionary"),)
    expected: List = [[None, None, None]]
    actual: List = list(as_block_value(block, {}))
    assert expected == actual

def test_nested_list(common_values):
    block: Tuple = (
        (
                        "outer_nested_list",
                        (
                            "inner_nested_list",
                            "text_in_inner_nested_list"
                        ),
                        "text_in_outer_nested_list"
                    ),
    )
    expected: List = [
        [None, "a"],
        [None, "b"],
        ["foo", "c"],
        ["bar", "c"]
    ]
    actual: List = list(as_block_value(block, common_values))
    assert expected == actual

def test_nested_dictionary(common_values):
    block: Tuple = (
        (
                        "outer_nested_dictionary",
                        (
                            "inner_nested_dictionary",
                            "text_in_inner_nested_dictionary"
                        ),
                        "text_in_outer_nested_dictionary"
                    ),
    )
    expected: List = [
        ["peter", None, None, "a"],
        ["paul", "red", None, "b"],
        ["mary", "orange", "foo", "c"],
        ["mary", "yellow", "bar", "c"]
    ]
    actual: List = list(as_block_value(block, common_values))
    assert expected == actual

def test_dictionary_in_nested_list(common_values):
    block: Tuple = (
        (
            "outer_nested_list",
            (
                "inner_nested_list",
                "text_in_inner_nested_list",
                (
                    "dictionary_in_inner_nested_list",
                    "text_in_dictionary_in_inner_nested_list"
                )
            ),
            "text_in_outer_nested_list"
        ),
    )
    expected: List = [
        [None, None, None, "a"],
        [None, None, None, "b"],
        ["foo", None, None, "c"],
        ["bar", "black", "white", "c"],
        ["bar", "green", "red", "c"],
    ]
    actual: List = list(as_block_value(block, common_values))
    assert expected == actual

def test_empty_nested_dictionary():
    values: Dict = {}
    block: Tuple = (
        (
            "outer_nested_dictionary",
            (
                "inner_nested_dictionary",
                "text_in_inner_nested_dictionary"
            ),
            "text_in_outer_nested_dictionary"
        ),
    )
    expected: List = [[None, None, None, None]]
    actual: List = list(as_block_value(block, values))
    assert expected == actual

def test_list_in_nested_dictionary(common_values):
    block: Tuple = (
        (
            "outer_nested_dictionary",
            (
                "inner_nested_dictionary",
                "text_in_inner_nested_dictionary",
                (
                    "list_in_inner_nested_dictionary",
                    "text_in_list_in_inner_nested_dictionary"
                )
            ),
            "text_in_outer_nested_dictionary"
        ),
    )
    expected: List = [
        ["peter", None, None, None, "a"],
        ["paul", "red", None, None, "b"],
        ["mary", "orange", "foo", None, "c"],
        ["mary", "yellow", "bar", "black", "c"],
        ["mary", "yellow", "bar", "white", "c"],
    ]
    actual: List = list(as_block_value(block, common_values))
    assert expected == actual

def test_quadruple_nesting(common_values):
    block: Tuple = (
        (
            "outer_nested_dictionary",
            (
                "inner_nested_dictionary",
                "text_in_inner_nested_dictionary",
                (
                    "list_in_inner_nested_dictionary",
                    "text_in_list_in_inner_nested_dictionary",
                    (
                        "dictionary_in_list_in_inner_nested_dictionary",
                        "text_in_dictionary_in_list_in_inner_nested_dictionary"
                    )
                )
            ),
            "text_in_outer_nested_dictionary"
        ),
    )
    expected: List = [
        ["peter", None, None, None, None, None, "a"],
        ["paul", "red", None, None, None, None, "b"],
        ["mary", "orange", "foo", None, None, None, "c"],
        ["mary", "yellow", "bar", "black", None, None, "c"],
        ["mary", "yellow", "bar", "white", "this is extreme", "but it works", "c"],
        ["mary", "yellow", "bar", "white", "another one", "also ok", "c"],
    ]
    actual: List = list(as_block_value(block, common_values))
    assert expected == actual
