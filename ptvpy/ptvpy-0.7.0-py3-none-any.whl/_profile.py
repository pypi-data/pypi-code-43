"""Tools for profile management."""


import re
import glob
from pathlib import Path

import toml
import cerberus

from .utils import ChainedKeyMap, natural_sort_key
from ._schema import SCHEMA


#: Default name used for newly created profiles.
DEFAULT_PROFILE_NAME = "ptvpy.toml"


def template_path() -> Path:
    """Get the path to the file profile template."""
    return Path(__file__).with_name("profile_template.toml")


def create_profile_file(path, data_files):
    """Create a file with the default profile at the desired location.

    Parameters
    ----------
    path : str or Path
        Specifies the folder and name of the new file.
    data_files : str
        Set value of field ``data_files`` in the profile.
    """
    with open(template_path()) as stream:
        template = stream.read()
    regex = r"data_files = \"(?P<path>.*)\""
    content = re.sub(regex, f'data_files = "{data_files}"', template)
    with open(path, "x") as stream:
        stream.write(content)


def pattern_matches(pattern, no_files=None, no_dirs=None):
    """Check if a glob pattern matches.

    Parameters
    ----------
    pattern : str
        A glob like pattern. Recursive globs using "``**``" are supported.
    no_files : bool, optional
        If true must match no files.
    no_dirs : bool, optional
        If true must match no directories.

    Returns
    -------
    out : bool
        Result of the evaluation.
    """
    matches = glob.glob(pattern, recursive=True)

    # Using any() allows the evaluation to return early
    if no_dirs and any(map(lambda x: Path(x).is_dir(), matches)):
        return False
    if no_files and any(map(lambda x: Path(x).is_file(), matches)):
        return False

    return len(matches) > 0


class ProfileValidator(cerberus.Validator):
    """Extended validator for profile validation and normalization.

    This class extends_ Cerberus's Validator class with new rules which are
    used in the profile schema:

    * Rule: *odd* may be ``True`` or ``False``

      - ``True``: evaluates if the number is odd.
      - ``False``: evaluates if the number is even.

    * Rule: *path* may contain one or a list of the following values:

      - "file": evaluates if a value points to a valid file.
      - "directory": evaluates if a value points to a valid directory.
      - "parent": evaluates if the value points to a file or directory
        within a valid directory (its parent).
      - "absolute": evaluates if a value is an absolute path.

    * Rule: *glob* may contain one of the following values:

      - "any": evaluates if the pattern matches at least once.
      - "no_files": evaluates if the pattern matches at least once and none of
        the matches are a file.
      - "no_dirs": evaluates if the pattern matches at least once and none of
        the matches are a directory.
      - "never": evaluates if the pattern matches never.

    .. _extends: http://docs.python-cerberus.org/en/stable/customize.html
    """

    def _validate_odd(self, rule_values, field, field_value):
        """Custom rule to validate if an integer is odd.

        The rule's arguments are validated against this schema:

        {'type': 'boolean'}
        """
        is_odd = bool(field_value & 1)
        if rule_values is True and not is_odd:
            self._error(field, "must be an odd number")
        elif rule_values is False and is_odd:
            self._error(field, "must be an even number")

    def _validate_glob(self, rule_value, field, field_value):
        """Custom rule to validate strings as glob patterns.

        See class documentation for a full explanation of the rule.
        The rule's arguments are validated against this schema:

        {'type': 'string', 'allowed': ['any', 'no_files', 'no_dirs', 'never']}
        """
        if rule_value == "any":
            if not pattern_matches(field_value):
                self._error(field, "must match at least once")
        elif rule_value == "no_files":
            if not pattern_matches(field_value, no_files=True):
                self._error(field, "must match at least once and never a file")
        elif rule_value == "no_dirs":
            if not pattern_matches(field_value, no_dirs=True):
                self._error(field, "must match at least once and never a directory")
        elif rule_value == "never":
            if pattern_matches(field_value):
                self._error(field, "must never match")
        else:  # pragma: no cover
            # Should never reach this line
            raise ValueError("rule_value not supported")

    def _validate_path(self, rule_values, field, field_value):
        """Custom rule to validate strings as file system paths.

        See class documentation for a full explanation of the rule.
        The rule's arguments are validated against this schema:

        {'oneof': [{'type': 'string', 'allowed': ['file', 'directory',
        'parent', 'absolute']}, {'type': 'list', 'minlength': 1, 'schema': {
        'type': 'string', 'allowed': ['file', 'directory', 'parent',
        "absolute"]}}]}
        """
        path = Path(str(field_value))

        if isinstance(rule_values, str):
            rule_values = [rule_values]
        for rule_value in rule_values:
            if rule_value == "parent" and not path.parent.is_dir():
                self._error(
                    field, f"parent directory doesn't exist: " f"'{path.parent}'"
                )
            elif rule_value == "directory" and not path.is_dir():
                self._error(field, f"directory doesn't exist: '{path}'")
            elif rule_value == "file" and not path.is_file():
                self._error(field, f"file doesn't exist: '{path}'")
            elif rule_value == "absolute" and not path.is_absolute():
                self._error(field, f"path is not absolute: '{path}'")

    @property
    def violations(self):
        """
        A list of rule violations if the last validation wasn't successful
        (list[str], read-only).
        """

        def flatten(node, path):
            if isinstance(node, dict):
                for field, sub_node in node.items():
                    yield from flatten(sub_node, path + [str(field)])
            elif isinstance(node, list):
                assert len(node) == 1
                yield from flatten(node[0], path)
            elif isinstance(node, str):
                yield f"{'.'.join(path)}: {node}"
            else:  # pragma: no cover
                raise TypeError(f"unexpected node type: {type(node)}")

        error_tree = self.errors
        return list(flatten(error_tree, path=[]))


class Profile(ChainedKeyMap):
    """In-memory representation of a profile file.

    This class tries to make accessing profiles and their content convenient. This class
    supports dictionary-like indexing (see the base class) to access profile fields.

    Parameters
    ----------
    path : path_like
        Path to the profile file.

    Examples
    --------
    >>> from ptvpy._profile import create_profile_file, Profile
    >>> create_profile_file("ptvpy.toml", data_files="*.tiff")  # doctest: +SKIP
    >>> profile = Profile("ptvpy.toml")  # doctest: +SKIP
    >>> profile  # doctest: +SKIP
    <Profile: "ptvpy.toml", invalid>
    >>> print(profile.report_validation())  # doctest: +SKIP
    'ptvpy.toml' is not a valid profile:
        general.data_files: must match at least once and never a directory
    >>> profile["general.data_files"]  # doctest: +SKIP
    '*.tiff'
    >>> profile["general"]  # doctest: +SKIP
    ChainedKeyMap(
    {'data_files': '*.tiff',
     'default_steps': ['locate', 'link', 'diff'],
     'storage_file': './ptvpy.h5',
     'subset': {'start': None, 'step': None, 'stop': None}},
    delimiter='.')
    """

    #: The default pattern used to find profile files (class attribute, str).
    DEFAULT_PATTERN = "*ptvpy*.toml"

    @classmethod
    def from_pattern(cls, pattern):
        """Load multiple profiles matching a pattern.

        Parameters
        ----------
        pattern : str or path_like, optional
            Path / glob pattern used to detect a files inside a directory.

        Returns
        -------
        profiles : list[Profile]
            The profiles that were found.
        """
        paths = glob.glob(str(pattern))
        paths = sorted(paths, key=natural_sort_key)
        profiles = [cls(path) for path in paths]
        return profiles

    def __init__(self, path):
        #: Pah to the file this profile was created from (str or Path or None).
        self.path = Path(path)
        #: Stores the reasons if a profile is invalid (list[str]).
        self._violations = []

        try:
            content = toml.load(self.path)
        except (toml.TomlDecodeError, UnicodeDecodeError) as error:
            content = {}
            self._violations.append(str(error))
        else:
            validator = ProfileValidator(SCHEMA, require_all=True)
            content = validator.normalized(content, always_return_document=True)
            validator.validate(content)
            if validator.errors:
                self._violations.extend(validator.violations)

        super().__init__(content)

    def __repr__(self):
        cls_name = type(self).__name__
        validity = "valid" if self.is_valid else "invalid"
        return f'<{cls_name}: "{self.path!s}", {validity}>'

    def __str__(self):
        return f"{repr(self)}\n{super().__str__()}"

    @property
    def is_valid(self) -> bool:
        """True if the profile is valid (bool, read-only)."""
        return len(self._violations) == 0

    def report_validation(self):
        """Summarize the validation state in a human readable way.

        Returns
        -------
        report : str
            The summary.
        """
        if self.is_valid:
            return f"'{self.path}' is a valid profile"
        else:
            violations = "\n".join(f"    {e}" for e in self._violations)
            return f"'{self.path}' is not a valid profile:\n{violations}"
