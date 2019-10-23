# pylint: disable=missing-docstring

from polarion_docstrings import checker

EXPECTED = [
    (6, 4, 'P666 Unknown field "foo"'),
    (17, 8, 'P667 Invalid value "huge" of the "caseimportance" field'),
    (18, 8, 'P666 Unknown field "bar"'),
    (
        19,
        8,
        'P668 Field "linkedWorkItems" should be handled by the "@pytest.mark.requirements" marker',
    ),
    (20, 12, "P663 Wrong indentation, line ignored"),
    (28, 4, 'P669 Missing required field "initialEstimate"'),
    (32, 8, 'P669 Missing required field "initialEstimate"'),
    (38, 8, 'P669 Missing required field "initialEstimate"'),
    (41, 12, 'P666 Unknown field "baz"'),
    (48, 0, 'P669 Missing required field "initialEstimate"'),
]


def _strip_func(errors):
    return [(lineno, col, msg) for lineno, col, msg, __ in errors]


def test_checker(source_file_merge, config):
    errors = checker.DocstringsChecker(None, source_file_merge, config, "TestChecker").run_checks()
    errors = _strip_func(errors)
    assert errors == EXPECTED
