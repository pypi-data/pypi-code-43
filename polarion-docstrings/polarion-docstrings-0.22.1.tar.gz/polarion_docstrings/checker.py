"""Check Polarion docstrings."""

import os
import re
import sys
from collections import namedtuple

from polarion_tools_common import utils

from polarion_docstrings import parser

DocstringsError = namedtuple("DocstringsError", "lineno column message checker")
FieldRecord = namedtuple("FieldRecord", "lineno column field")
ValidatedDocstring = namedtuple("ValidatedDocstring", "unknown invalid missing markers ignored")

# regex for valid initialEstimate values
_NUM_INT = "[1-9][0-9]*"
_NUM_FRAC = "{nint}/{nint}".format(nint=_NUM_INT)
_NUM_INT_OR_FRAC = "{nint}(/{nint})?".format(nint=_NUM_INT)
INITIAL_ESTIMATE_RE = re.compile(
    "^(({num}d {num}h)|({nint} {frac}[dh])|{num}[dh])$".format(
        num=_NUM_INT_OR_FRAC, nint=_NUM_INT, frac=_NUM_FRAC
    )
)


# pylint: disable=too-many-instance-attributes
class DocstringsChecker:
    """Checker for Polarion docstrings."""

    PARSING_ERROR = "P663"
    IGNORED_FIELD = "P664"
    UNKNOWN_FIELD = "P666"
    INVALID_VALUE = "P667"
    MARKER_FIELD = "P668"
    MISSING_FIELD = "P669"

    def __init__(self, tree, filename, config, checker):
        self.tree = tree
        self.filename = filename
        self.config = self.get_valid_config(config)
        self.checker = checker or "DocstringsChecker"
        self.set_compiled_lists()

    def set_compiled_lists(self):
        """Set compiled regular expressions for whitelist and blacklist.

        Uses values set in config if available so the compilation doesn't need to
        be repeated with every instantiation.
        """
        if "_compiled_blacklist" in self.config:
            self._compiled_whitelist = self.config.get("_compiled_whitelist")
            self._compiled_blacklist = self.config.get("_compiled_blacklist")
        else:
            self._compiled_whitelist, self._compiled_blacklist = self.get_compiled_lists(
                self.config
            )

    @staticmethod
    def get_valid_config(config):
        """Return valid configuration if available."""
        cfg_valid = config.get("docstrings") or {}
        cfg_valid = cfg_valid.get("valid_values")
        if not (cfg_valid and config.get("default_fields")):
            return {}
        return config

    @staticmethod
    def get_compiled_lists(config):
        """Return compiled regular expressions for whitelist and blacklist."""
        compiled_whitelist, compiled_blacklist = None, None
        if config.get("whitelisted_tests"):
            compiled_whitelist = re.compile("(" + ")|(".join(config.get("whitelisted_tests")) + ")")
        if config.get("blacklisted_tests"):
            compiled_blacklist = re.compile("(" + ")|(".join(config.get("blacklisted_tests")) + ")")
        return compiled_whitelist, compiled_blacklist

    @staticmethod
    def validate_value(docstring_dict, key, valid_values):
        record = docstring_dict.get(key)
        if record is not None:
            return record.value in valid_values[key]
        return True

    @staticmethod
    def get_unknown_fields(docstring_dict, known_fields):
        unknown = [
            FieldRecord(docstring_dict[key].lineno, docstring_dict[key].column, key)
            for key in docstring_dict
            if key not in known_fields and not key.startswith("_errors_")
        ]
        return unknown

    @classmethod
    def get_invalid_fields(cls, docstring_dict, valid_values):
        results = {
            key: cls.validate_value(docstring_dict, key, valid_values) for key in valid_values
        }

        for section in (parser.DOCSTRING_SECTIONS.steps, parser.DOCSTRING_SECTIONS.results):
            # if "value" is present, the section wasn't parsed correctly into a list
            if hasattr(docstring_dict.get(section), "value"):
                results[section] = False

        invalid = [
            FieldRecord(docstring_dict[key].lineno, docstring_dict[key].column, key)
            for key, result in results.items()
            if not result
        ]
        return invalid

    @staticmethod
    def get_missing_fields(docstring_record, required_keys, all_docstrings):
        """Look for required keys, and validate their value is not None."""
        missing = []

        if not required_keys:
            return missing

        # skip file-level docstrings and class docstrings
        if all_docstrings[docstring_record.nodeid].level != parser.LEVELS.function:
            return missing

        components = docstring_record.nodeid.split("::")
        all_components = [components.pop(0)]
        for component in components:
            joined_component = "{}::{}".format(all_components[-1], component)
            all_components.append(joined_component)
        all_components.reverse()

        for key in required_keys:
            value_record = None
            for nodeid in all_components:
                docstring_dict = all_docstrings.get(nodeid) or None
                docstring_dict = getattr(docstring_dict, "value", {})
                value_record = docstring_dict.get(key, None)
                if value_record is not None:
                    break
            if value_record is None or value_record.value is None:
                missing.append(key)

        return missing

    @staticmethod
    def get_markers_fields(docstring_dict, marker_fields):
        if not marker_fields:
            return []
        markers = [
            FieldRecord(docstring_dict[key].lineno, docstring_dict[key].column, key)
            for key in marker_fields
            if key in docstring_dict
        ]
        return markers

    @staticmethod
    def get_ignored_fields(docstring_dict, ignored_fields):
        if not ignored_fields:
            return []
        ignored = [
            FieldRecord(docstring_dict[key].lineno, docstring_dict[key].column, key)
            for key in ignored_fields
            if key in docstring_dict
        ]
        return ignored

    def validate_docstring(self, docstring_record, all_docstrings):
        """Return tuple with lists of problematic fields."""
        docstring_dict = docstring_record.value or {}
        cfg_docstrings = self.config["docstrings"]
        unknown = self.get_unknown_fields(docstring_dict, self.config.get("default_fields"))
        invalid = self.get_invalid_fields(docstring_dict, cfg_docstrings.get("valid_values"))
        missing = self.get_missing_fields(
            docstring_record, cfg_docstrings.get("required_fields"), all_docstrings
        )
        markers = self.get_markers_fields(docstring_dict, cfg_docstrings.get("marker_fields"))
        ignored = self.get_ignored_fields(docstring_dict, cfg_docstrings.get("ignored_fields"))
        return ValidatedDocstring(unknown, invalid, missing, markers, ignored)

    def get_parsing_errors(self, docstring_dict, lineno=0):
        """Produce parsing errors for the flake8 checker."""
        docstring_dict = docstring_dict or {}
        if "_errors_parsing" not in docstring_dict:
            return []
        parsing_errors = [
            DocstringsError(
                lineno + err.lineno,
                err.column,
                "{} {}".format(self.PARSING_ERROR, err.message),
                self.checker,
            )
            for err in docstring_dict["_errors_parsing"]
        ]
        return parsing_errors

    # pylint:disable=too-many-locals
    def get_fields_errors(self, validated_docstring, docstring_dict, lineno=0, column=0):
        """Produce fields errors for the flake8 checker."""
        errors = []
        cfg_docstrings = self.config["docstrings"]
        marker_fields = cfg_docstrings.get("marker_fields") or {}
        ignored_fields = cfg_docstrings.get("ignored_fields") or {}

        for num, col, field in validated_docstring.unknown:
            errors.append(
                DocstringsError(
                    lineno + num,
                    col,
                    '{} Unknown field "{}"'.format(self.UNKNOWN_FIELD, field),
                    self.checker,
                )
            )
        for num, col, field in validated_docstring.invalid:
            errors.append(
                DocstringsError(
                    lineno + num,
                    col,
                    '{} Invalid value "{}" of the "{}" field'.format(
                        self.INVALID_VALUE, docstring_dict[field].value, field
                    ),
                    self.checker,
                )
            )
        for num, col, field in validated_docstring.markers:
            errors.append(
                DocstringsError(
                    lineno + num,
                    col,
                    '{} Field "{}" should be handled by the "{}" marker'.format(
                        self.MARKER_FIELD, field, marker_fields.get(field)
                    ),
                    self.checker,
                )
            )
        for num, col, field in validated_docstring.ignored:
            errors.append(
                DocstringsError(
                    lineno + num,
                    col,
                    '{} Ignoring field "{}": {}'.format(
                        self.IGNORED_FIELD, field, ignored_fields.get(field)
                    ),
                    self.checker,
                )
            )
        for field in validated_docstring.missing:
            errors.append(
                DocstringsError(
                    lineno,
                    column,
                    '{} Missing required field "{}"'.format(self.MISSING_FIELD, field),
                    self.checker,
                )
            )
        return errors

    def check_initial_estimate(self, docstring_dict, lineno=0):
        """Check format of initialEstimate value."""
        initial_estimate = docstring_dict.get("initialEstimate")
        if not initial_estimate:
            return None

        if INITIAL_ESTIMATE_RE.sub("", initial_estimate.value):
            return DocstringsError(
                lineno + initial_estimate.lineno,
                initial_estimate.column,
                "{} Invalid estimate; "
                "Examples (d=days, h=hours): 1d, 3d, 1/2h, 2 1/2h, 3d 1h".format(
                    self.INVALID_VALUE
                ),
                self.checker,
            )
        return None

    @staticmethod
    def print_errors(errors):
        """Print errors without using flake8."""
        for err in errors:
            print("line: {}:{}: {}".format(err.lineno, err.column, err.message), file=sys.stderr)

    def check_docstrings(self, docstrings_in_file):
        """Run checks on each docstring."""
        errors = []
        for docstring in docstrings_in_file.values():
            if not self.is_nodeid_whitelisted(docstring.nodeid):
                continue
            valdoc = self.validate_docstring(docstring, docstrings_in_file)
            errors.extend(
                self.get_fields_errors(
                    valdoc, docstring.value, lineno=docstring.lineno, column=docstring.column
                )
            )
            errors.extend(self.get_parsing_errors(docstring.value, lineno=docstring.lineno))
            errors.append(self.check_initial_estimate(docstring.value, lineno=docstring.lineno))

        errors = [e for e in errors if e is not None]
        if errors:
            errors = sorted(errors, key=lambda tup: tup[0])
        return errors

    def run_checks(self):
        """Check docstrings in python source file."""
        docstrings_in_file = parser.get_docstrings_in_file(self.filename, tree=self.tree)
        errors = self.check_docstrings(docstrings_in_file)
        return errors

    def is_nodeid_whitelisted(self, nodeid):
        """Check if the nodeid is whitelisted."""
        if not nodeid:
            return True
        if self._compiled_whitelist and self._compiled_whitelist.search(nodeid):
            return True
        if self._compiled_blacklist and self._compiled_blacklist.search(nodeid):
            return False
        return True

    def is_file_for_check(self):
        """Decide if the file should be checked."""
        if not self.config:
            return False

        abs_filename = os.path.abspath(self.filename)
        head, tail = os.path.split(abs_filename)

        # check only test files under polarion tests path
        if not (tail.startswith("test_") and utils.find_tests_marker(head or ".")):
            return False

        return True

    def get_errors(self):
        """Get errors in docstrings in python source file."""
        if not self.is_file_for_check():
            return []

        return self.run_checks()
