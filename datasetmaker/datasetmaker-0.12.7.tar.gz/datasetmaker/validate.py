import re
from pathlib import Path
from typing import Union
from functools import lru_cache
import pandas as pd
from datasetmaker import exceptions


def test_constraint(val: Union[float, int, str], constraint: str) -> bool:
    """
    Check if a value meets a mathematical comparison constraint.
    E.g. latitude: -90 < x < 90.

    Parameters
    ----------
    val
        Value to check.
    constraint
        Mathematical equality comparison.

    Returns
    -------
    bool
        Whether the constraint was met or not.

    Examples
    --------
    >>> test_constraint(50, '-90<x<90')
    True
    >>> test_constraint(105, 'x<=100')
    False
    >>> test_constraint(100, 'x<100')
    False
    >>> test_constraint(100, 'x>100')
    False
    >>> test_constraint(5, '10<x')
    False
    """
    val = float(val)

    pat = (r'(?P<left_val>-?\d+)?'
           r'(?P<left_comp><=?)?'
           r'(x)'
           r'(?P<right_comp>[<>]=?)?'
           r'(?P<right_val>-?\d+)?')
    match = re.match(pat, constraint.strip())
    if not match:
        return True
    els = match.groupdict()

    if els['left_comp']:
        if els['left_comp'] == '<':
            if not val > float(els['left_val']):
                return False
        if els['left_comp'] == '<=':
            if val < float(els['left_val']):
                return False

    if els['right_comp']:
        if els['right_comp'] == '<':
            if not val < float(els['right_val']):
                return False
        if els['right_comp'] == '<=':
            if val > float(els['right_val']):
                return False
        if els['right_comp'] == '>':
            if not val > float(els['right_val']):
                return False
        if els['right_comp'] == '>=':
            if val >= float(els['right_val']):
                return False

    return True


def validate_package(path: Path) -> None:
    validator = PackageValidator(path)
    validator.validate()


class PackageValidator:
    def __init__(self, path: Path):
        self.path = path

    @lru_cache()
    def _read_csv(self, name: Path) -> pd.DataFrame:
        return pd.read_csv(name, dtype=str)

    def validate(self) -> None:
        self.valid_has_concepts()
        self.valid_year_format()
        self.valid_day_format()
        self.valid_domain_constraint()

    def valid_has_concepts(self) -> None:
        if not (self.path / 'ddf--concepts.csv').exists():
            raise exceptions.PackageMissingConceptsException

    def valid_year_format(self) -> None:
        """Year value is max 4 chars long"""
        files = [x for x in self.path.glob('*.csv') if '--year' in str(x.stem)]
        for file in files:
            df = self._read_csv(file)
            if not (df.year.astype(str).str.len() < 5).all():
                wrong = df[df.year.astype(str).str.len() >= 5].year.iloc[0]
                raise exceptions.PackageInvalidYearException(f'Invalid year {wrong} in {file}')

    def valid_day_format(self) -> None:
        """Day values are 10 chars long and contain only digits"""
        files = [x for x in self.path.glob('*.csv') if '--day' in str(x.stem)]
        for file in files:
            df = self._read_csv(file)
            if not (df.day.astype(str).str.len() == 10).all():
                error = df[df.day.astype(str).str.len() != 10].iloc[0].day
                raise exceptions.PackageInvalidDayException(error)
            if not (df.day.astype(str).str.replace('-', '').str.isdigit()).all():
                error = df[~df.day.astype(str).str.isdigit()].iloc[0].day
                raise exceptions.PackageInvalidDayException(error)

    def valid_domain_constraint(self) -> None:
        """Domain constraint is met"""
        concepts = self._read_csv(self.path / 'ddf--concepts.csv')
        constrained = concepts[concepts.domain.str.contains('>|<', na=False)]
        constrained = constrained[['concept', 'domain']].values
        for concept, constraint in constrained:
            files = [x for x in self.path.glob('*.csv') if 'datap' in str(x) or 'entit' in str(x)]
            dfs = [self._read_csv(x) for x in files]
            dfs = [x for x in dfs if concept in x]
            for df in dfs:
                if not df[concept].apply(test_constraint, args=(constraint,)).all():
                    raise exceptions.PackageInvalidDomainConstraint
