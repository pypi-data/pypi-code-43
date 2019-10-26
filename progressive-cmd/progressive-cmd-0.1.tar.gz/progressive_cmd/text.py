import re
from typing import Iterator, Set, Union


def positive_percentages(text: str,
                         lengths: Set[int] = None,
                         decimal_numbers: int = None) -> Iterator[Union[int, float]]:
    """Gets numbers postfixed with a '%' in strings with other characters.

    1)100% 2)56.78% 3)56 78.90% 4)34.6789% some text

    :param text: The text to search for.
    :param lengths: A set of lengths that the percentage
                    number should have to be considered valid.
                    Ex. {5,6} would validate '90.32' and '100.00'
    """
    # From https://regexr.com/3aumh
    for x in re.finditer(r'[\d|\.]+%', text):
        num = x.group()[:-1]
        if lengths:
            if not len(num) in lengths:
                continue
        if decimal_numbers:
            try:
                pos = num.rindex('.')
            except ValueError:
                continue
            else:
                if len(num) - pos - 1 != decimal_numbers:
                    continue
        yield float(num)
