# mypy: allow-untyped-defs

import unittest
# from pathlib import Path
# import pandas as pd
from datasetmaker import validate
from datasetmaker import exceptions
from datasetmaker.path import ROOT_DIR


class TestValidate(unittest.TestCase):
    def setUp(self):
        self.path = ROOT_DIR.parent / 'tests/ddf/invalid_packages'

    def test_raises_missing_concepts(self):
        with self.assertRaises(exceptions.PackageMissingConceptsException):
            validator = validate.PackageValidator(self.path / 'missing_concepts')
            validator.valid_has_concepts()

    def test_raises_invalid_year(self):
        with self.assertRaises(exceptions.PackageInvalidYearException):
            validator = validate.PackageValidator(self.path / 'invalid_year')
            validator.valid_year_format()

    def test_raises_invalid_day(self):
        with self.assertRaises(exceptions.PackageInvalidDayException):
            validator = validate.PackageValidator(self.path / 'invalid_day')
            validator.valid_day_format()

    def test_raises_invalid_domain_constraint(self):
        with self.assertRaises(exceptions.PackageInvalidDomainConstraint):
            validator = validate.PackageValidator(self.path / 'invalid_domain_constraint')
            validator.valid_domain_constraint()
