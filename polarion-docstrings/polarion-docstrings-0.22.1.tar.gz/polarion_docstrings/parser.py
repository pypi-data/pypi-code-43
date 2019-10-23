"""Parse Polarion docstrings."""

import ast
from collections import namedtuple

FORMATED_KEYS = ("setup", "teardown")

DocstringRecord = namedtuple("DocstringRecord", "lineno column value nodeid level")
ValueRecord = namedtuple("ValueRecord", "lineno column value")
ErrorRecord = namedtuple("ErrorRecord", "lineno column type message")


def get_section_start(doc_list, section):
    """Find the line with "section" (e.g. "Polarion", "testSteps", etc.)."""
    section = "{}:".format(section)
    for index, line in enumerate(doc_list):
        if section != line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        return index + 1, indent
    return None, None


def add_errors(docstring_dict, errors):
    """Add new `ErrorRecord`(s) to `_errors_parsing`."""
    if not errors:
        return

    if "_errors_parsing" not in docstring_dict:
        docstring_dict["_errors_parsing"] = []

    if isinstance(errors, ErrorRecord):
        docstring_dict["_errors_parsing"].append(errors)
    else:
        docstring_dict["_errors_parsing"].extend(errors)


# pylint: disable=too-few-public-methods,invalid-name
class LEVELS:  # noqa
    """Valid values for levels of Polarion docstrings."""

    file = "file"
    klass = "class"
    function = "function"


# pylint: disable=too-few-public-methods,invalid-name
class DOCSTRING_SECTIONS:  # noqa
    """Valid sections in Polarion docstring."""

    polarion = "Polarion"
    steps = "testSteps"
    results = "expectedResults"


class DocstringParser:
    """Parser for single docstring."""

    SECTIONS = DOCSTRING_SECTIONS

    def __init__(self, docstring):
        self.docstring = docstring

    @staticmethod
    def _get_key_value(line):
        """Get the key and value out of docstring line."""
        data = line.split(":")
        if len(data) == 1:
            data.append("")

        key = data[0].strip()

        value = ":".join(data[1:]).strip()
        if value.lower() in ("none", "null"):
            value = None

        return key, value

    # pylint: disable=too-many-locals
    def lines_to_dict(self, lines, start=0, lineno_offset=0, stop=None):
        """Create dictionary out of docstring lines.

        Includes column and line number info for each record.
        """
        if stop:
            lines = lines[start:stop]
        else:
            lines = lines[start:]

        docstring_dict = {}
        indent = len(lines[0]) - len(lines[0].lstrip(" "))
        is_multiline = False
        prev_key = None
        for num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if not line_stripped:
                continue

            curr_indent = len(line) - len(line.lstrip(" "))

            if curr_indent < indent:
                break

            # check if the line should be appended to previous key
            is_first_multiline = False
            if not is_multiline:
                is_first_multiline = line_stripped[-1] == ">"
                is_first_multiline = is_first_multiline and len(line_stripped.split(" ")) <= 2
                if is_first_multiline:
                    # we might want to append this very line to `prev_key` if it's in a list
                    is_multiline = True
                    # remove the ">"
                    line_stripped = line_stripped[:-1].strip()

            first_word = line_stripped.split(" ")[0] or line_stripped
            is_keyword = first_word[-1] == ":"
            if prev_key and curr_indent > indent and (not is_keyword or is_multiline):
                prev_lineno, prev_indent, prev_value = docstring_dict[prev_key]
                sep = ""
                if prev_value:
                    sep = "\n" if prev_key in FORMATED_KEYS else " "
                docstring_dict[prev_key] = ValueRecord(
                    prev_lineno, prev_indent, "{}{}{}".format(prev_value, sep, line_stripped)
                )
                continue

            prev_key = None
            # if we are here we are either at the very beginning of multiline
            # (and `is_first_multiline` is True) or it's no longer multiline
            is_multiline = is_first_multiline

            if curr_indent > indent:
                add_errors(
                    docstring_dict,
                    ErrorRecord(
                        num + lineno_offset,
                        curr_indent,
                        "indent",
                        "Wrong indentation, line ignored",
                    ),
                )
                continue

            key, value = self._get_key_value(line_stripped)
            docstring_dict[key] = ValueRecord(num + lineno_offset, indent, value.strip())
            prev_key = key

        return docstring_dict

    @staticmethod
    def lines_to_list(lines, start=0, lineno_offset=0, stop=None):
        """Create list out of docstring lines.

        Includes column and line number info for each line.
        """
        if stop:
            lines = lines[start:stop]
        else:
            lines = lines[start:]

        lines_list = []
        is_multiline = False
        indent = len(lines[0]) - len(lines[0].lstrip(" "))
        for num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if not line_stripped:
                continue
            curr_indent = len(line) - len(line.lstrip(" "))
            if curr_indent < indent:
                break

            # check if the line should be appended to previous key
            is_first_multiline = False
            if not is_multiline:
                is_first_multiline = line_stripped[-1] == ">"
                is_first_multiline = is_first_multiline and len(line_stripped.split(" ")) <= 2
                if is_first_multiline:
                    # remove the ">"
                    line_stripped = line_stripped[:-1].strip()

            first_word = line_stripped.split(" ")[0] or line_stripped
            is_keyword = first_word[-1] == ":"
            if curr_indent > indent and (not is_keyword or is_multiline):
                prev_lineno, prev_indent, prev_value = lines_list.pop()
                lines_list.append(
                    ValueRecord(prev_lineno, prev_indent, "{} {}".format(prev_value, line_stripped))
                )
                continue

            # if we are here we are either at the very beginning of multiline
            # (and `is_first_multiline` is True) or it's no longer multiline
            is_multiline = is_first_multiline

            if curr_indent > indent:
                continue
            lines_list.append(ValueRecord(num + lineno_offset, indent, line_stripped))

        return lines_list

    def strip_polarion_data(self):
        """Remove the Polarion section from the docstring."""
        docstring_list = self.docstring.split("\n")
        new_docstring_list = []
        polarion_section = "{}:".format(self.SECTIONS.polarion)
        indent = 0
        in_polarion = False

        for line in docstring_list:
            # find beginning of Polarion section
            if line.strip() == polarion_section:
                indent = len(line) - len(line.lstrip(" "))
                in_polarion = True
                continue
            # skip blank lines and lines more indented than the beginning of
            # Polarion section
            if in_polarion:
                if not line.strip():
                    continue
                curr_indent = len(line) - len(line.lstrip(" "))
                if curr_indent > indent:
                    continue
                in_polarion = False
            new_docstring_list.append(line.rstrip())

        new_docstring = "\n".join(new_docstring_list)
        return new_docstring.strip("\n")

    def parse(self):
        """Parse docstring to dictionary.

        E.g.:

        Polarion:
            assignee: mkourim
            casecomponent: nonexistent
            testSteps:
                1. Step with really long description
                   that doesn't fit into one line
                2. Do that
            expectedResults:
                1. Success outcome with really long description
                   that doesn't fit into one line
                2. 2
            caseimportance: low
            title: Some test with really long description
                   that doesn't fit into one line
            setup: Do this:
                   - first thing
                   - second thing

        This is not included.
        """
        doc_list = self.docstring.split("\n")

        polarion_start, __ = get_section_start(doc_list, self.SECTIONS.polarion)
        if not polarion_start:
            return None

        docstring_dict = self.lines_to_dict(doc_list, start=polarion_start)

        if self.SECTIONS.steps in docstring_dict and docstring_dict[self.SECTIONS.steps].value:
            steps_start, __ = get_section_start(doc_list, self.SECTIONS.steps)
            if steps_start:
                steps_list = self.lines_to_list(
                    doc_list, start=steps_start, lineno_offset=steps_start - polarion_start
                )
                docstring_dict[self.SECTIONS.steps] = steps_list

        if self.SECTIONS.results in docstring_dict and docstring_dict[self.SECTIONS.results].value:
            results_start, __ = get_section_start(doc_list, self.SECTIONS.results)
            if results_start:
                results_list = self.lines_to_list(
                    doc_list, start=results_start, lineno_offset=results_start - polarion_start
                )
                docstring_dict[self.SECTIONS.results] = results_list

        return docstring_dict


class FileParser:
    """Parser for whole file."""

    SECTIONS = DOCSTRING_SECTIONS
    INDENT_STEP = 4

    def __init__(self, filename, tree=None, tests_only=True):
        self.filename = filename
        self.tests_only = tests_only
        self.tree = tree or self.get_tree()

    def get_tree(self):
        """Return ast tree."""
        with open(self.filename) as infile:
            source = infile.read()

        tree = ast.parse(source, filename=self.filename)
        return tree

    @staticmethod
    def get_docstring_from_node(node):
        """Get docstring from ast node."""
        docstring = None
        body = getattr(node, "body", None)
        body = body[0] if body else node

        try:
            if isinstance(body, ast.Expr) and isinstance(body.value, ast.Str):
                docstring = body.value.s
        # pylint: disable=broad-except
        except Exception:
            return None

        # for Python2
        try:
            docstring = docstring.decode("utf-8")
        except AttributeError:
            pass

        return docstring

    def _get_nodeid(self, node_name, class_name):
        components = [self.filename, class_name, node_name]
        if not class_name:
            components.pop(1)
        if not node_name:
            components.pop()
        nodeid = "::".join(components)
        return nodeid

    def process_docstring(self, docstring, node, nodeid=None, level=LEVELS.function):
        """Return parsed Polarion docstring."""
        body = getattr(node, "body", None)
        body = body[0] if body else node

        # test doesn't have docstring, i.e. it's missing also the Polarion section
        if not docstring:
            return DocstringRecord(
                lineno=body.lineno - 1, column=node.col_offset, value={}, nodeid=nodeid, level=level
            )

        doc_list = docstring.split("\n")
        docstring_start = (
            body.lineno - 1 if hasattr(body, "end_lineno") else body.lineno - len(doc_list)
        )
        polarion_start, polarion_column = get_section_start(doc_list, self.SECTIONS.polarion)

        if not polarion_start:
            # docstring is missing the Polarion section
            return DocstringRecord(
                lineno=docstring_start + 1,
                column=node.col_offset + self.INDENT_STEP,
                value={},
                nodeid=nodeid,
                level=level,
            )
        # calculate polarion_column if the Polarion section is at the very begining of the docstring
        if polarion_start == 1 and polarion_column == node.col_offset:
            polarion_column += self.INDENT_STEP

        polarion_offset = docstring_start + polarion_start
        return DocstringRecord(
            lineno=polarion_offset,
            column=polarion_column,
            value=parse_docstring(docstring),
            nodeid=nodeid,
            level=level,
        )

    def process_node(self, node, class_name, level):
        """Return parsed Polarion docstring present in the function."""
        docstring = self.get_docstring_from_node(node)
        nodeid = self._get_nodeid(getattr(node, "name", None), class_name)
        return self.process_docstring(docstring, node, nodeid, level)

    def process_ast_body(self, body, class_name=None, is_top=False):
        """Recursively iterate over specified part of ast tree to process functions."""
        docstrings = {}
        if is_top:
            docstring = self.process_node(body[0], None, LEVELS.file)
            if getattr(docstring, "value", None):
                docstrings[docstring.nodeid] = docstring
        for node in body:
            if isinstance(node, ast.ClassDef):
                if self.tests_only and not node.name.startswith("Test"):
                    continue
                docstring = self.process_node(node, None, LEVELS.klass)
                if getattr(docstring, "value", None):
                    docstrings[docstring.nodeid] = docstring
                docstrings.update(self.process_ast_body(node.body, node.name))
                continue

            if not isinstance(node, ast.FunctionDef):
                continue

            if self.tests_only and not node.name.startswith("test_"):
                continue

            docstring = self.process_node(node, class_name, LEVELS.function)
            docstrings[docstring.nodeid] = docstring

        return docstrings

    def get_docstrings(self):
        """Return parsed Polarion docstrings present in the python source file."""
        return self.process_ast_body(self.tree.body, is_top=True)


# convenience functions


def parse_docstring(docstring):
    """Parse docstring to dictionary."""
    return DocstringParser(docstring).parse()


def strip_polarion_data(docstring):
    """Remove the Polarion section from the docstring."""
    return DocstringParser(docstring).strip_polarion_data()


def get_docstrings_in_file(filename, tree=None, tests_only=True):
    """Return parsed Polarion docstrings present in the python source file."""
    return FileParser(filename, tree=tree, tests_only=tests_only).get_docstrings()


def _vrecords2dict(vrecord):
    vrecord = vrecord or {}
    converted = {}
    for key, value in vrecord.items():
        if key.startswith("_errors_"):
            continue
        converted[key] = [v.value for v in value] if isinstance(value, list) else value.value
    return converted


def _merge_components(docstrings_dict, nodeid):
    components = nodeid.split("::")

    merged_value = {}
    cur_components = []
    for component in components:
        cur_components.append(component)
        joined_components = "::".join(cur_components)
        merged_value.update(docstrings_dict.get(joined_components, {}))

    return merged_value


def merge_docstrings(docstrings):
    """Merge docstrings with their parents."""
    docstrings_dict = {}

    # create dict out of records
    for docstring in docstrings.values():
        if getattr(docstring, "value", False) is False:
            continue
        docstrings_dict[docstring.nodeid] = _vrecords2dict(docstring.value)

    # merge with parents
    for nodeid in docstrings_dict:
        # skip file-level docstrings and class docstrings
        if docstrings[nodeid].level != LEVELS.function:
            continue

        docstrings_dict[nodeid] = _merge_components(docstrings_dict, nodeid)

    return docstrings_dict


def merge_record(record, docstrings_dict, nodeid=None):
    """Merge single record with its parents based on nodeid."""
    merged_record = {}

    if isinstance(record, DocstringRecord):
        nodeid = nodeid or record.nodeid
        record = record.value

    if not nodeid:
        return merged_record

    merged_record = _merge_components(docstrings_dict, nodeid)
    merged_record.update(_vrecords2dict(record))
    return merged_record
