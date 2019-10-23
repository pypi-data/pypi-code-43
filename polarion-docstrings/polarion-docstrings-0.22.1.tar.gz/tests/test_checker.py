# pylint: disable=missing-docstring

from polarion_docstrings import checker, parser

EXPECTED = [
    (7, 4, 'P669 Missing required field "assignee"'),
    (7, 4, 'P669 Missing required field "initialEstimate"'),
    (11, 8, 'P669 Missing required field "assignee"'),
    (11, 8, 'P669 Missing required field "initialEstimate"'),
    (17, 8, 'P669 Missing required field "initialEstimate"'),
    (19, 12, 'P667 Invalid value "nonexistent" of the "casecomponent" field'),
    (40, 12, 'P667 Invalid value "level1" of the "caselevel" field'),
    (40, 12, 'P668 Field "caselevel" should be handled by the "@pytest.mark.tier" marker'),
    (41, 12, 'P668 Field "caseautomation" should be handled by the "@pytest.mark.manual" marker'),
    (
        42,
        12,
        'P668 Field "linkedWorkItems" should be handled by the "@pytest.mark.requirements" marker',
    ),
    (43, 12, 'P666 Unknown field "foo"'),
    (44, 12, 'P664 Ignoring field "description": use test docstring instead'),
    (51, 0, 'P669 Missing required field "assignee"'),
    (51, 0, 'P669 Missing required field "initialEstimate"'),
    (55, 0, 'P669 Missing required field "assignee"'),
    (55, 0, 'P669 Missing required field "initialEstimate"'),
    (61, 4, 'P669 Missing required field "assignee"'),
    (61, 4, 'P669 Missing required field "initialEstimate"'),
    (72, 8, 'P667 Invalid value "wrong" of the "testSteps" field'),
    (75, 8, 'P667 Invalid value "" of the "expectedResults" field'),
    (90, 4, 'P669 Missing required field "assignee"'),
    (91, 8, "P667 Invalid estimate; Examples (d=days, h=hours): 1d, 3d, 1/2h, 2 1/2h, 3d 1h"),
    (92, 12, "P663 Wrong indentation, line ignored"),
    (97, 4, 'P669 Missing required field "assignee"'),
    (98, 8, "P667 Invalid estimate; Examples (d=days, h=hours): 1d, 3d, 1/2h, 2 1/2h, 3d 1h"),
    (102, 15, "P663 Wrong indentation, line ignored"),
]


def _strip_func(errors):
    return [(lineno, col, msg) for lineno, col, msg, __ in errors]


def test_checker(source_file, config):
    errors = checker.DocstringsChecker(None, source_file, config, "TestChecker").run_checks()
    errors = _strip_func(errors)
    assert errors == EXPECTED


def test_initial_estimate(config):
    doc_checker = checker.DocstringsChecker(None, None, config, "TestChecker")

    valid = ("1d", "3d", "1/2h", "2 1/2h", "3d 1h", "3 2/5h")
    for value in valid:
        err = doc_checker.check_initial_estimate(
            {"initialEstimate": parser.ValueRecord(0, 0, value)}
        )
        assert err is None, "value {}".format(value)

    invalid = ("3h 1/60h", "3m", "1/60", "3d 01/60h", "3d 4d", "2 3h", "1/5 1/2h")
    for value in invalid:
        err = doc_checker.check_initial_estimate(
            {"initialEstimate": parser.ValueRecord(0, 0, value)}
        )
        assert "Invalid estimate" in err.message, "value {}".format(value)
