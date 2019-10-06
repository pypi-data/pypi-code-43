import logging

import functools
import operator
import logging
import re
import tinydb

from collections     import namedtuple
from collections.abc import Iterable
from lark            import v_args

from mnectar.library.LarkSearchEngine import Grammar
from mnectar.registry                 import Plugin, Registry

import Registry.Library.SearchEngine

_logger = logging.getLogger(__name__)

class LogicEngineGrammar(Registry, parent=Registry.Library.SearchEngine):
    pass

class LogicQuery(tinydb.Query):
    def _iterable(self, value):
        return type(value) != str and isinstance(value, Iterable)

    def startswith(self, rhs, ignorecase=True):
        """
        Test the start of a dictionary value against a string (optionally ignoring case)

        >>> Query().f1.startswith('Start Str')

        :param rhs: The string the dictionary value must start with
        """

        # Startswith always uses string comparisons
        # Use case:  String style matching for years
        #     e.g.:  '201' matches ('2010', '2011', ... '2019')
        rhs = str(rhs)

        if ignorecase:
            rhs = rhs.lower()

        cmp = lambda value: (
            ignorecase and not self._iterable(value) and str(value).lower().startswith(rhs)
            or not self._iterable(value) and str(value).startswith(rhs)
            or self._iterable(value) and any(cmp(_) for _ in value)
        )

        return self._generate_test(
            cmp,
            ('startswith', self._path, rhs, ignorecase)
        )

    def contains(self, rhs, ignorecase=True):
        """
        Test the start of a dictionary value against a string (optionally ignoring case)

        >>> Query().f1.contains('Start Str')

        :param rhs: The string the dictionary value must start with
        """

        if ignorecase and type(rhs) == str:
            rhs = rhs.lower()

        cmp = lambda value: (
            ignorecase and type(value) == str and rhs in value.lower()
            or type(value) == str and rhs in value
            or self._iterable(value) and any(cmp(_) for _ in value)
        )

        return self._generate_test(
            cmp,
            ('startswith', self._path, rhs, ignorecase)
        )

    def equals(self, rhs, ignorecase=True):
        """
        Test the start of a dictionary value against a string (optionally ignoring case)

        >>> Query().f1.equals('other')

        :param rhs: The value to compare to
        """

        if ignorecase and type(rhs) == str:
            rhs = rhs.lower()

        cmp = lambda value: (
            ignorecase and type(value) == str and value.lower() == rhs
            or not self._iterable(value) and value == rhs
            or self._iterable(value) and any(cmp(_) for _ in value)
        )

        return self._generate_test(
            cmp,
            ('equals', self._path, rhs, ignorecase)
        )

    def search(self, regex, flags=0):
        """
        Run a regex test against a dict value (only substring string has to
        match).

        >>> Query().f1.search(r'^\w+$')

        :param regex: The regular expression to use for matching
        """

        def cmp(value):
            try:
                return (
                    not self._iterable(value) and re.search(regex, value, flags)
                    or self._iterable(value) and any(cmp(_) for _ in value)
                )
            except re.error:
                return False

        return self._generate_test(
            cmp,
            ('search', self._path, regex, flags)
        )


class AutoColumnGrammar(Grammar, registry=LogicEngineGrammar):
    _grammar = {
        "?start":       ['auto_search'],
        "?auto_search": [('AUTO_STRING',    'auto_contains'),
                         ('"/" AUTO_REGEX', 'auto_regex'),
                         ],

        "AUTO_STRING":  """/([a-z](?![a-z]* *[:<>=\/]).*)|([A-Z0-9'"].*)/""",
        "AUTO_REGEX":   """/.+/"""
    }

    @v_args(inline=True)
    def auto_contains(self, rhs):
        columns = self.app.columns.names(filterAuto=True)
        return functools.reduce(
            operator.or_,
            (LogicQuery()[column].contains(str(rhs), ignorecase=True) for column in columns))

    @v_args(inline=True)
    def auto_regex(self, rhs):
        columns = self.app.columns.names(filterAuto=True)
        return functools.reduce(
            operator.or_,
            (LogicQuery()[column].search(str(rhs), flags=re.IGNORECASE) for column in columns))

class ColumnGrammar(Grammar, registry=LogicEngineGrammar):
    LogicOp = namedtuple('LogicOp', ('op', 'lhs', 'rhs', 'binary'), defaults=(None, False))

    _grammar = {
        # Column Search Definitions
        "?column_expr": [('column ":"  column_logic_expr ("/" flags?)?', 'startswith'),
                         ('column ":"',                                  'startswith'),
                         ('column "="  column_logic_expr ("/" flags?)?', 'equals'),
                         ('column "="',                                  'equals'),
                         ('column "/"  regex_string      ("/" flags?)?', 'search'),
                         ('column "/"',                                  'search'),
                         ('column "<"  numeric', 'lt'),
                         ('column ">"  numeric', 'gt'),
                         ('column "<=" numeric', 'le'),
                         ('column ">=" numeric', 'ge'),
                         ],

        # Logic Value Rules
        "?column_logic_expr": ['column_logic_and',
                               ('column_logic_expr "|" column_logic_and', 'column_or')
                               ],

        "?column_logic_and":  ['column_logic_term',
                               ('column_logic_and "&" column_logic_term', 'column_and')
                               ],

        "?column_logic_term": ['"(" column_logic_expr ")"',
                               ('"!" column_logic_term','column_not'),
                               'atom'
                               ],

        # Supporting Rules
        "flags":              ['CASE_INSENSITIVE'],
        "?regex_string":      [('REGEX_STRING', 'unquoted_string')],

        "CASE_INSENSITIVE":   "/[Ii]/",
        "REGEX_STRING":       "/((?<=\/).+?(?=(?<!\\\)\/))|([A-Za-z][A-Za-z0-9:_. -]*\\b)/",
    }

    @v_args(inline=True)
    def column_and(self, lhs, rhs):
        return self.LogicOp(operator.and_, lhs, rhs, True)

    @v_args(inline=True)
    def column_or(self, lhs, rhs):
        return self.LogicOp(operator.or_, lhs, rhs, True)

    @v_args(inline=True)
    def column_not(self, value):
        return self.LogicOp(operator.invert, value)

    @v_args(inline=True)
    def startswith(self, column, rhs = "", flags = ""):
        if type(rhs) == str and len(rhs) == 0:
            return LogicQuery()[column]

        elif isinstance(rhs, self.LogicOp):
            if rhs.binary:
                return rhs.op(self.startswith(column, rhs.lhs, flags),
                              self.startswith(column, rhs.rhs, flags)
                              )
            else:
                return rhs.op(self.startswith(column, rhs.lhs, flags))
        else:
            if 'i' in flags:
                ignorecase = True
            elif 'I' in flags:
                ignorecase = False
            else:
                ignorecase = True

            return LogicQuery()[column].startswith(rhs, ignorecase)

    @v_args(inline=True)
    def equals(self, column, rhs = "", flags = ""):
        if type(rhs) == str and len(rhs) == 0:
            return LogicQuery()[column].equals("") | (~ LogicQuery()[column].exists())

        elif isinstance(rhs, self.LogicOp):
            if rhs.binary:
                return rhs.op(self.equals(column, rhs.lhs, flags),
                              self.equals(column, rhs.rhs, flags)
                              )
            else:
                return rhs.op(self.equals(column, rhs.lhs, flags))
        else:
            if 'i' in flags:
                ignorecase = True
            elif 'I' in flags:
                ignorecase = False
            else:
                ignorecase = True

            return LogicQuery()[column].equals(rhs, ignorecase)

    @v_args(inline=True)
    def search(self, column, regex = "", flags = ""):
        if type(regex) == str and len(regex) == 0:
            return LogicQuery()[column].exists()

        if 'i' in flags:
            reflags = re.IGNORECASE
        else:
            reflags = 0

        return LogicQuery()[column].search(regex, reflags)

    @v_args(inline=True)
    def lt(self, column, rhs):
        return tinydb.Query()[column] < rhs

    @v_args(inline=True)
    def gt(self, column, rhs):
        return tinydb.Query()[column] > rhs

    @v_args(inline=True)
    def le(self, column, rhs):
        return tinydb.Query()[column] <= rhs

    @v_args(inline=True)
    def ge(self, column, rhs):
        return tinydb.Query()[column] >= rhs

class LogicGrammar(Grammar, registry=LogicEngineGrammar):
    _grammar = {
        "?start"     : ['logic_expr'],
        "?logic_expr": ['logic_and',
                        ('logic_expr "|" logic_and', 'or_')
                        ],

        "?logic_and":  ['logic_atom',
                        ('logic_and "&" logic_atom', 'and_')
                        ],

        "?logic_atom": ['"(" logic_expr ")"',
                        ('"!" logic_atom', 'not_'),
                        'column_expr',
                        ],
    }

    not_ = v_args(inline=True)(operator.invert)
    and_ = v_args(inline=True)(operator.and_)
    or_  = v_args(inline=True)(operator.or_)

class TimeSearch(Grammar, registry=LogicEngineGrammar):
    _grammar = {
        "?atom":        ['time',],
        "?numeric":     ['time',],
        "?time":        ['time_minutes', 'time_hours',],
        "time_minutes": ['int ":" int',],
        "time_hours":   ['int ":" int ":" int',],
    }

    @v_args(inline=True)
    def time_minutes(self, minutes, seconds):
        return minutes * 60 + seconds

    @v_args(inline=True)
    def time_hours(self, hours, minutes, seconds):
        return hours * 3600 + minutes * 60 + seconds

class BaseGrammar(Grammar, registry=LogicEngineGrammar):
    _entry = "start"
    _grammar = {
        # SEARCHES:
        #   (hashtag:kap)
        #   (hashtag:kap|meditation)
        #   (hashtag:(kap|meditation)&(chakra|remix))
        #   (hashtag:kap&meditation)

        "?start"             : [],
        "?atom"              : ['int', 'float', 'quoted_string', 'unquoted_string',],

        "?string"            : ['quoted_string', 'unquoted_string'],
        "quoted_string"      : ['QUOTED_STRING',],
        "unquoted_string"    : ['UNQUOTED_STRING',],
        "column"             : ['COLUMN',],
        "?numeric"           : ['int', 'float'],
        "int"                : ['INT',],
        "float"              : ['FLOAT',],

        "QUOTED_STRING"      : """/(?P<quote>['"]).*?(?<!\\\)(?P=quote)/""",
        "UNQUOTED_STRING"    : """/[A-Za-z][A-Za-z0-9:_. -]*\\b/""",
        "INT"                : """/[+-]?\d+/""",
        "FLOAT"              : """/[+-]?(\d+\.\d+|\.\d+|\d+\.)/""",
        "COLUMN"             : """/[a-z]+/""",

        "%import"            : ["common.WS"],
        "%ignore"            : ["WS"],
    }

    int    = v_args(inline=True)(int)
    float  = v_args(inline=True)(float)
    column = v_args(inline=True)(str)
    flags  = v_args(inline=True)(str)

    @v_args(inline=True)
    def quoted_string(self, value):
        string = value[1:-1]
        string = string.replace("\\'","'")
        string = string.replace('\\"','"')
        return string

    @v_args(inline=True)
    def unquoted_string(self, string):
        string = string.replace("\\'","'")
        string = string.replace('\\"','"')
        return string

class LogicSearchEngine(Registry.Library.SearchEngine.LarkSearchEngine, registry=Registry.Library.SearchEngine):
    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)
        self._parser_type = 'lalr'

    def enable(self):
        for grammar in LogicEngineGrammar.plugins:
            self.add(grammar)
        self.compile()
