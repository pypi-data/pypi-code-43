# pylint: disable=missing-docstring

from polarion_docstrings.parser import (
    DocstringRecord,
    ValueRecord,
    get_docstrings_in_file,
    merge_docstrings,
    merge_record,
)

EXPECTED = {
    "tests/data/docstrings_merge.py": {"assignee": "mkourim", "foo": "this is an unknown field"},
    "tests/data/docstrings_merge.py::TestClassFoo": {
        "assignee": "psegedy",
        "caseimportance": "huge",
        "bar": "this is an unknown field",
        "linkedWorkItems": "FOO, BAR",
        "testSteps": [
            "1. Step with really long description that doesn't fit into one line",
            "2. Do that",
        ],
    },
    "tests/data/docstrings_merge.py::TestClassFoo::test_in_class_no_docstring": {
        "assignee": "psegedy",
        "foo": "this is an unknown field",
        "caseimportance": "huge",
        "bar": "this is an unknown field",
        "linkedWorkItems": "FOO, BAR",
        "testSteps": [
            "1. Step with really long description that doesn't fit into one line",
            "2. Do that",
        ],
    },
    "tests/data/docstrings_merge.py::TestClassFoo::test_in_class_no_polarion": {
        "assignee": "psegedy",
        "foo": "this is an unknown field",
        "caseimportance": "huge",
        "bar": "this is an unknown field",
        "linkedWorkItems": "FOO, BAR",
        "testSteps": [
            "1. Step with really long description that doesn't fit into one line",
            "2. Do that",
        ],
    },
    "tests/data/docstrings_merge.py::TestClassFoo::test_in_class_polarion": {
        "assignee": "mkourim",
        "foo": "this is an unknown field",
        "caseimportance": "low",
        "bar": "this is an unknown field",
        "linkedWorkItems": "FOO, BAR",
        "testSteps": ["1. Do that"],
        "baz": "this is an unknown field",
    },
    "tests/data/docstrings_merge.py::test_standalone_no_docstring": {
        "assignee": "mkourim",
        "foo": "this is an unknown field",
    },
}

TO_MERGE = (
    "tests/data/docstrings_merge.py::TestClassFoo::test_record_merge",
    DocstringRecord(
        lineno=72,
        column=4,
        value={
            "assignee": ValueRecord(lineno=1, column=8, value="bender"),
            "testSteps": ValueRecord(lineno=3, column=8, value="wrong"),
        },
        nodeid="tests/data/docstrings_merge.py::TestClassFoo::test_record_merge",
        level="function",
    ),
)

EXPECTED_MERGED_RECORD = {
    "assignee": "bender",
    "foo": "this is an unknown field",
    "caseimportance": "huge",
    "bar": "this is an unknown field",
    "linkedWorkItems": "FOO, BAR",
    "testSteps": "wrong",
}

EXPECTED_MERGED_EMPTY_RECORD = {
    "assignee": "psegedy",
    "foo": "this is an unknown field",
    "caseimportance": "huge",
    "bar": "this is an unknown field",
    "linkedWorkItems": "FOO, BAR",
    "testSteps": [
        "1. Step with really long description that doesn't fit into one line",
        "2. Do that",
    ],
}


def test_parser_merged(source_file_merge):
    docstrings = get_docstrings_in_file(source_file_merge)
    merged_docstrings = merge_docstrings(docstrings)
    assert merged_docstrings == EXPECTED


def test_parser_docstrings_record_merge(source_file_merge):
    docstrings = get_docstrings_in_file(source_file_merge)
    merged_docstrings = merge_docstrings(docstrings)
    merged_record = merge_record(TO_MERGE[1], merged_docstrings)
    assert merged_record == EXPECTED_MERGED_RECORD


def test_parser_value_merge(source_file_merge):
    docstrings = get_docstrings_in_file(source_file_merge)
    merged_docstrings = merge_docstrings(docstrings)
    merged_record = merge_record(TO_MERGE[1].value, merged_docstrings, TO_MERGE[0])
    assert merged_record == EXPECTED_MERGED_RECORD


def test_parser_empty_merge(source_file_merge):
    docstrings = get_docstrings_in_file(source_file_merge)
    merged_docstrings = merge_docstrings(docstrings)
    merged_record = merge_record({}, merged_docstrings, TO_MERGE[0])
    assert merged_record == EXPECTED_MERGED_EMPTY_RECORD
