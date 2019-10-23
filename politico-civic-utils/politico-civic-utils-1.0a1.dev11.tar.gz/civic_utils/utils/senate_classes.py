# Imports from python.
from datetime import datetime


def senate_class_for_election_year(year, as_number=False):
    """Find which Senate class stood for regular election in a year."""
    # Class 1 Senators were first elected in 1790, then again in 1796.
    # Class 1 Senators were first elected in 1792, then again in 1798.
    # Class 1 Senators were first elected in 1794, then again in 1800.
    # The pattern repeats every six years.

    observed_year = int(year)

    if observed_year % 2 != 0:
        # If year is not even, raise a ValueError.
        raise ValueError(
            "Normal federal elections are only held in even years."
        )

    class_number = (((observed_year - 1790) % 6) // 2) + 1

    if as_number:
        return class_number

    return f"Class {''.join(['I' for x in range(class_number)])}"


def next_election_year_for_class(class_name, start_year=None):
    """Get the year a Senate class next stands for regular election."""
    class_number = len(class_name.replace("Class ", ""))

    if start_year:
        current_year = start_year
    else:
        current_year = datetime.now().year

    next_election_year = (
        current_year if current_year % 2 == 0 else current_year + 1
    )

    next_election_class = senate_class_for_election_year(
        next_election_year, as_number=True
    )

    per_class_differences = {
        (x % 3): ((x - next_election_class) * 2)
        for x in range(next_election_class, next_election_class + 3)
    }
    per_class_differences[3] = per_class_differences.pop(0)

    return next_election_year + per_class_differences[class_number]


def previous_election_year_for_class(class_name, start_year=None):
    """Get the last year a Senate class stood for regular election."""
    next_election_year = next_election_year_for_class(class_name, start_year)
    return next_election_year - 6
