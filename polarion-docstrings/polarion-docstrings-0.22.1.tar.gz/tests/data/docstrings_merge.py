# pylint: disable=missing-docstring,no-self-use
"""Test file

Polarion:
    assignee: mkourim
    foo: this is an unknown field
"""

import pytest


class TestClassFoo:
    """Test class

    Polarion:
        assignee: psegedy
        caseimportance: huge
        bar: this is an unknown field
        linkedWorkItems: FOO, BAR
            initialEstimate: 1/4h

        testSteps:
            1. Step with really long description
               that doesn't fit into one line
            2. Do that
    """

    def test_in_class_no_docstring(self):
        pass

    def test_in_class_no_polarion(self):
        """FOO"""

    @pytest.mark.skip
    def test_in_class_polarion(self):
        """FOO

        Polarion:
            assignee: mkourim
            caseimportance: low
            baz: this is an unknown field

            testSteps:
                1. Do that
        """


def test_standalone_no_docstring():
    pass
