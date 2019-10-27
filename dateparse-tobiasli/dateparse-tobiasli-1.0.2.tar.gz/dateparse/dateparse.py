"""Better package for parsing norwegian datestrings."""
import typing as ty
from itertools import groupby
from datetime import datetime

import tregex

Number = ty.Union[int, float]

SEPERATORS = {
    'group': r'\W(?:kl\.?\W?)?',
    'date': r'[\.\-\W\\/]',
    'time': r'[\.\-:]?',
}

PATTERN_COMPONENTS = {
    'year': (r'(?P<year>\d{4}|\d{2})', 'date'),
    'month': (r'(?P<month>\d{1,2}|\w{3,9})', 'date'),
    'day': (r'(?P<day>\d{1,2}|\w{1,7})\.?', 'date'),
    'hour': (r'(?P<hour>\d{1,2})', 'time'),
    'minute': (r'(?P<minute>\d{2})', 'time'),
    'second': (r'(?P<second>\d{2})(?:[\.,](?P<microsecond>\d+))?', 'time'),
    'microsecond': (r'', 'time'),  # microseconds are handled within the seconds pattern.
}

START_LIMITER = r'(:?(?<=\W)|^)'
END_LIMITER = r'(:?(?=\W)|$)'

YEAR = 'year'
MONTH = 'month'
DAY = 'day'
HOUR = 'hour'
MINUTE = 'minute'
SECOND = 'second'
MICROSECOND = 'microsecond'

COMPONENT_LIST = [YEAR, MONTH, DAY, HOUR, MINUTE, SECOND, MICROSECOND]

PATTERN_SEQUENCES = [
    (YEAR, MONTH, DAY, HOUR, MINUTE, SECOND),
    (DAY, MONTH, YEAR, HOUR, MINUTE, SECOND),
    (YEAR, MONTH, DAY, HOUR, MINUTE),
    (DAY, MONTH, YEAR, HOUR, MINUTE),
    (YEAR, MONTH, DAY, HOUR),
    (DAY, MONTH, YEAR, HOUR),
    (YEAR, MONTH, DAY),
    (DAY, MONTH, YEAR),
    (YEAR, DAY, MONTH),
    (YEAR, MONTH),
    (MONTH, YEAR),
    (YEAR,),
]

MONTHS = {
    'januar': 1,
    'februar': 2,
    'mars': 3,
    'april': 4,
    'mai': 5,
    'juni': 6,
    'juli': 7,
    'august': 8,
    'september': 9,
    'oktober': 10,
    'november': 11,
    'desember': 12,
    'january': 1,
    'february': 2,
    'march': 3,
    'may': 5,
    'june': 6,
    'july': 7,
    'october': 10,
    'december': 12,
    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'okt': 10,
    'nov': 11,
    'des': 12,
    'oct': 10,
    'dec': 12,
}

MONTH_DAYS = {
    1: 31,
    2: 29,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31
}


def pattern_builder(seq: ty.Sequence[str]) -> str:
    """Combine a pattern sequence to create a valid regex pattern"""
    pattern_groups = {k: list(v) for k, v in groupby([PATTERN_COMPONENTS[part] for part in seq], key=lambda x: x[1])}
    patterns = list()
    for group in pattern_groups:
        patterns.append(SEPERATORS[group].join([pat[0] for pat in pattern_groups[group]]))

    pattern = START_LIMITER + SEPERATORS['group'].join(patterns) + END_LIMITER
    return pattern


class DateParser:
    def __init__(self) -> None:
        self.patterns = [tregex.TregexCompiled(pattern=pattern_builder(seq)) for seq in PATTERN_SEQUENCES]

    def parse(self, datestr: str) -> ty.List[datetime]:
        """Parse a date string and try to find a valid datetime."""
        for pattern, seq in zip(self.patterns, PATTERN_SEQUENCES):
            # seq is only used for debugging.
            # print(datestr)
            # print(seq)
            result = pattern.to_dict(datestr)
            if result:
                results = list()
                for candidate in result:
                    datevec = self.verify_and_get_datevec(candidate)
                    if not datevec:
                        continue
                    else:
                        results.append(datevec)
                if results:
                    return [datetime(**res) for res in results]
        return []

    @staticmethod
    def verify_and_get_datevec(candidate: ty.Dict[str, str]) -> ty.Dict[str, Number]:
        """Check the contents of a match candidate from the regex patterns."""
        datevec = {}

        if YEAR in candidate:
            datevec[YEAR] = int(candidate[YEAR])

        if MONTH in candidate:
            """Check if numeric month is within 1-12 and alpha month is reasonable. Return month num."""
            try:
                num = int(candidate[MONTH])
                if num in range(1, 13):
                    datevec[MONTH] = num
                else:
                    return {}
            except ValueError:
                month_name = candidate[MONTH]
                if month_name in MONTHS:
                    datevec[MONTH] = MONTHS[month_name]
                else:
                    return {}

        if DAY in candidate:
            """Check if numeric day is within 1-31 and alpha day is reasonable. Return day num."""
            if MONTH not in datevec:  # Need month to evaluate day.
                return {}
            num = int(candidate[DAY])
            if num in range(1, MONTH_DAYS[datevec[MONTH]] + 1):
                datevec[DAY] = num
            else:
                return {}

        if HOUR in candidate:
            num = int(candidate[HOUR])
            if num in range(0, 25):
                datevec[HOUR] = num
            else:
                return {}
        if MINUTE in candidate:
            num = int(candidate[MINUTE])
            if num in range(0, 61):
                datevec[MINUTE] = num
            else:
                return {}
        if SECOND in candidate:
            datevec[SECOND] = int(candidate[SECOND])
            if MICROSECOND in candidate and candidate[MICROSECOND]:
                # Convert decimals to microseconds:
                datevec[MICROSECOND] = int(candidate[MICROSECOND]) * 10 ** (6 - len(candidate[MICROSECOND]))

        for prop in COMPONENT_LIST:
            if prop not in datevec:
                if PATTERN_COMPONENTS[prop][1] == 'date':
                    datevec[prop] = 1
                elif PATTERN_COMPONENTS[prop][1] == 'time':
                    datevec[prop] = 0

        return datevec


_DATE_PARSER = DateParser()


def parse(datestr: str) -> ty.List[datetime]:
    """Parse dates from the given datestring."""
    return _DATE_PARSER.parse(datestr)
