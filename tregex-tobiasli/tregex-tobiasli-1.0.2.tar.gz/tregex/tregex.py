"""Tregex is a module for parsing sorting outputs from regular expressions."""

import re
import difflib
from typing import Union, List, Dict, Tuple, Iterable

NUMBER = Union[int, float]
DEFAULT_FLAG = re.UNICODE | re.DOTALL
NAMED_GROUP_DETECTION = r'(\(\?P<\w+>)'
NAMED_GROUP_REFERENCE_DETECTION = r'\(\?\(\w+\)'
DEFAULT_SEARCH_SCORE_CUTOFF = 0.6
CONTENT_MATCH_DEFAULT_SCORE = 0.01
if hasattr(re, 'Pattern'):
    re_pattern_type = re.Pattern  # Python 3.7
else:
    re_pattern_type = re._pattern_type  # Python 3.6
# noinspection PyUnresolvedReferences
REGEX_PATTERN = Union[str, re_pattern_type]


class TregexUnknownMethodError(Exception):
    """Error raised when we _process encounters an output argument with that does not match any known output
    parsings."""
    pass


class TregexMismatchError(Exception):
    """Error encountered when Tregex does not find a match."""
    pass


class GenericPropertyClass:
    """Class for containing a dictionary and presenting its contents as properties of the class."""

    def __init__(self, **kwargs) -> None:
        self.dict = kwargs

    def __getattr__(self, item) -> object:
        if item not in self.dict:
            raise AttributeError(f'Attribute {item} not present in GenericPropertyClass.')
        return self.dict[item]

    def __bool__(self) -> bool:
        return bool(self.dict)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        arg_pairs = [f"{k}={repr(v)}" for k, v in self.dict.items()]
        return f'{GenericPropertyClass.__name__}({", ".join(arg_pairs)})'

    def __dir__(self) -> Iterable:
        return list(self.dict.keys())

    def __eq__(self, other) -> bool:
        return self.dict == other.dict


def _process(pattern: REGEX_PATTERN, string: str, output='smart', flags: re.RegexFlag = DEFAULT_FLAG) \
        -> List[Union[Tuple[str], Dict[str, str], str]]:
    """Compile and run a regular expression and posprocess the results depending of the [output].

    Args:
        pattern: The pattern string for the regex.
        string: The string being matched with the pattern.
        output: Which post proccesing to run on the output, se Below.
        flags: The input arguments for the regex parse. Defaults to re.UNICODE | re.DOTALL.

    Returns:
        '': Assumes simple match, and returns a list of matching pattern in string.
        'tuple': Assumes capture groups, and returns a list of tuples for each pattern group for each pattern match.
        'name': Assumes named capture groups in pattern, and returns a list of dictionaries matching the named groups.
        'smart': Scans the pattern for named groups, groups or nothing, and returns the appropriate structure.

    Raises:
        TregexUnknownMethodError when arg 'output' does not match any output type.
    """

    if isinstance(pattern, str):
        r = re.compile(pattern, flags)
    else:
        r = pattern
    result = [found for found in r.finditer(string)]
    if result:
        return_list = []

        if output == 'smart':
            if result[0].groupdict():
                output = 'dict'
            elif result[0].groups():
                output = 'tuple'
            else:
                output = ''

        if not output:
            for m in result:
                return_list += [m.group()]
        elif output == 'dict':
            for m in result:
                return_list += [m.groupdict()]
        elif output == 'tuple':
            for m in result:
                return_list += [m.groups()]
        else:
            raise TregexUnknownMethodError("Unknown method {} for argument 'output'.".format(output))

        return return_list
    else:
        return []


def to_dict(pattern: REGEX_PATTERN, string: str, flags: re.RegexFlag = DEFAULT_FLAG) -> List[Dict]:
    """Identifies named capture groups in pattern, and outputs matches as a list of dictionaries with named capture
    groups as keys."""

    return _process(pattern, string, output='dict', flags=flags)


def to_object(pattern: REGEX_PATTERN, string: str, flags: re.RegexFlag = DEFAULT_FLAG) -> List[GenericPropertyClass]:
    """Identifies named capture groups in pattern, and outputs matches as a list of objects with named capture groups as
    properties."""

    result = _process(pattern, string, output='dict', flags=flags)
    return [GenericPropertyClass(**dictionary) for dictionary in result]


def to_tuple(pattern: REGEX_PATTERN, string: str, flags: re.RegexFlag = DEFAULT_FLAG) -> List[Tuple[str]]:
    """Identifies capture groups in pattern, and outputs matches as a list of tuples of strings matching the pattern."""

    return _process(pattern, string, output='tuple', flags=flags)


def match(pattern: REGEX_PATTERN, string: str, flags: re.RegexFlag = DEFAULT_FLAG) -> List[str]:
    """Returns the string if it matches. will remove any named groups from pattern
    before compiling."""

    return _process(pattern, string, output='', flags=flags)


def smart(pattern: REGEX_PATTERN, string: str, flags: re.RegexFlag = DEFAULT_FLAG)\
        -> List[Union[Tuple[str], Dict[str, str], str]]:
    """Identifies properties of the pattern, and outputs matches as a list of
    objects based on the properties of the pattern:
        capture groups => List of tuples.
        named capture groups  => List of dictionaries.
        no groups => List of strings
    """

    return _process(pattern, string, output='smart', flags=flags)


def similarity(string1: str, string2: str) -> float:
    """Returns a score based on the degree of match between string1 and string2. Is vulnerable for string length, as it
    will punish a difference in length harshly even if string1 is a subset of string2 or vice versa."""

    return difflib.SequenceMatcher(None, string1, string2).ratio()


def find_best(search_string, search_list, score_cutoff=0, case_sensitive=False):
    """Fuzzy name search from a list of strings using tregex.similarity().

    Args:
        search_string: The string used to find a sufficient match in the search_list.
        search_list: A list of strings where we search for one or more matches.
        score_cutoff: The score cutoff of the results
        case_sensitive: Specify if search is case sensitive or not.


    Returns:
        Returns the best match from the search_list
    """

    result = find(search_string=search_string,
                  search_list=search_list,
                  score_cutoff=score_cutoff,
                  case_sensitive=case_sensitive
                  )
    if result:
        return result[0]
    else:
        return None


def find(search_string: str, search_list: Iterable[str], score_cutoff: NUMBER = DEFAULT_SEARCH_SCORE_CUTOFF,
         case_sensitive: bool = False) -> List[str]:
    """Fuzzy name search from a list of strings using tregex.similarity().

    Args:
        search_string: The string used to find a sufficient match in the search_list.
        search_list: A list of strings where we search for one or more matches.
        score_cutoff: The score cutoff of the results
        case_sensitive: Specify if search is case sensitive or not.


    Returns:
        Returns a list of matching items for each item in search list with a score above score_cutoff, sorted by score.
    """

    result = find_scores(search_string=search_string, search_list=search_list, score_cutoff=score_cutoff,
                         case_sensitive=case_sensitive)

    return [item[1] for item in result]


def find_scores(search_string: str, search_list: Iterable[str], score_cutoff: NUMBER = DEFAULT_SEARCH_SCORE_CUTOFF,
                case_sensitive: bool = False) -> List[Tuple[float, str]]:
    """Fuzzy name search from a list of strings using tregex.similarity().

    Args:
        search_string: The string used to find a sufficient match in the search_list.
        search_list: A list of strings where we search for one or more matches.
        score_cutoff: The score cutoff of the results
        case_sensitive: Specify if search is case sensitive or not.


    Returns:
        Returns a list of tuples containing matching items (score, match) for each item in search list with a score
        above score_cutoff, sorted by score.
    """

    if not case_sensitive:
        search_string_p = search_string.lower()
        search_list_p = [s.lower() for s in search_list]
    else:
        search_string_p = search_string
        search_list_p = search_list

    similarity_scores = [similarity(search_string_p, item) for item in search_list_p]
    scores_cutoff = [(score, item) for score, item in zip(similarity_scores, search_list) if score >= score_cutoff]
    scores_sorted = sorted(scores_cutoff, key=lambda x: x[0], reverse=True)

    # Get the items which have a content match even if the score is too low:
    # Keep the length of the strings, so that the shortest strings get the highest match:
    contains_match = [orig for orig, case in zip(search_list, search_list_p)
                      if search_string_p in case
                      and orig not in [item[1] for item in scores_sorted]]
    contains_sorted = sorted(contains_match, key=lambda x: len(x), reverse=False)

    result = scores_sorted + [(CONTENT_MATCH_DEFAULT_SCORE, item) for item in contains_sorted]

    if not result:
        result = []

    return result


class TregexCompiled:
    """Class for containing a regex pattern, parsing strings and performing different operations on the output."""

    def __init__(self, pattern: str, flags: re.RegexFlag = DEFAULT_FLAG) -> None:
        """Compile a pattern and make it available for the underlying parsing functions."""

        self.r = re.compile(pattern, flags)

    def to_dict(self, string: str) -> List[Dict]:
        """Identifies named capture groups in pattern, and outputs matches as a list of dictionaries with named capture
        groups as keys."""

        return to_dict(self.r, string)

    def to_object(self, string: str) -> List[GenericPropertyClass]:
        """Identifies named capture groups in pattern, and outputs matches as a list of objects with named capture
        groups as properties."""

        return to_object(self.r, string)

    def to_tuple(self, string: str) -> List[Tuple[str]]:
        """Identifies capture groups in pattern, and outputs matches as a list of tuples of strings matching the
        pattern."""

        return to_tuple(self.r, string)

    def match(self, string: str) -> List[str]:
        """Finds matches of pattern in string, and returns the matched portion of the strings."""

        return match(self.r, string)
