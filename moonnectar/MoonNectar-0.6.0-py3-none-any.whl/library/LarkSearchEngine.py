import collections
import copy
import functools
import inspect
import operator
import logging
import re
import tinydb

from collections.abc import Iterable
from lark            import Lark, Transformer
from lark.visitors   import VisitError
from lark.exceptions import ParseError, UnexpectedCharacters
from ..registry      import Plugin, Registry

import Registry.Library.SearchEngine

_logger = logging.getLogger(__name__)

def transform(func):
    """Decorator used to indicate a function is a transformation"""
    func.is_transform = True
    return func

class Grammar(Plugin, registry=None):
    """Define a Lark grammar component.

    This is a base class for portions of a Lark grammar designed to be added together in
    a mix-and-match manner.
    """

    _entry   = None
    _grammar = None

    def __init__(self, *grammars, **kw):
        super().__init__(**kw)
        for grammar in grammars:
            self._add(grammar)

        self._validate()

    @property
    def dict(self):
        """Return the grammar dictionary"""
        return self._grammar

    @property
    def transforms(self):
        """Return the list of transformation functions"""
        # Manually construct a list of possible candidates
        # ... because any access to this property will cause infinite recursion

        tfuncs = []
        for name in dir(self):
            if not name.startswith('_') and name != 'transforms':
                attr = getattr(self, name)
                if callable(attr) and getattr(attr, 'is_transform', False):
                    tfuncs.append((name,attr))
                elif callable(attr) and getattr(attr, 'vargs_applied', False):
                    tfuncs.append((name,attr))
        return tfuncs

    @property
    def entry(self):
        return self._entry

    @property
    def grammar(self):
        return self._dict_to_grammar()

    def _add(self, other):
        if not isinstance(other,Grammar):
            raise ValueError(f"Cannot combine '{type(other)}' object with a 'Grammar' object!")

        else:
            # Combine the entry points
            self._entry = self._entry or other._entry
            if self._entry != other._entry and other._entry is not None:
                raise ValueError("Entry points must be identical or None to combine grammars!")

            # Combine transform functions
            # ... check for errors first so that nothing happens before aborting
            for name,func in other.transforms:
                if hasattr(self, name):
                    raise ValueError(f"Transformation '{name}' defined multiple times, cannot combine grammars")
            for name,func in other.transforms:
                setattr(self, name, func)

            # Combine the grammars
            if self._grammar is None:
                self._grammar = copy.deepcopy(other._grammar)
            else:
                for key,value in other._grammar.items():
                    if type(value) == str:
                        self._grammar[key] = value
                    elif key in self._grammar:
                        for val in value:
                            if val not in self._grammar[key]:
                                self._grammar[key].append(val)
                    else:
                        self._grammar[key] = copy.deepcopy(other._grammar[key])

                # Revalidate the grammar structure if grammars were combined
                self._validate()

    def _validate(self):
        if self._grammar is None:
            raise ValueError("No Grammar Defined")
        elif type(self._grammar) != dict:
            raise ValueError("Grammar must be a dictionary!")

        for name, value in self._grammar.items():
            # Perform error checks
            if type(name) != str:
                raise ValueError("A grammar component name must be a string (not '{type(name)}'")

            elif name[0] == '%' and not all(
                type(_) == str
                or (
                    isinstance(_, Iterable)
                    and len(_) == 2
                    and type(_[0]) == str
                    and type(_[1]) == str
                )
                for _ in value
            ):
                raise ValueError("Lark directive content must be strings or size 2 iterables of strings!")

            elif name.isupper() and type(value) != str:
                raise ValueError("Terminal values must be a string")

            elif name.islower() and not isinstance(value, Iterable) and not type(value) == str:
                raise ValueError("Rule values must a non-string iterable")

            elif name.islower() and not all(
                type(_) == str
                or (
                    isinstance(_, Iterable)
                    and len(_) == 2
                    and type(_[0]) == str
                    and type(_[1]) == str
                )
                for _ in value
            ):
                raise ValueError("Rule list content must be strings or size 2 iterables of strings!")

            elif not name.isupper() and not name.islower() and not name[0] == '%':
                raise ValueError("Invalid Lark Statement")

    def _dict_to_grammar(self):
        grammar    = self._grammar
        indent     = max(len(_) for _ in grammar.keys())
        directives = []
        rules      = []
        terminals  = []

        for name,value in grammar.items():
            if name[0] == '%':
                dindent = max([len(_) for _ in value if type(_) == str]+[len(_[0]) for _ in value if type(_) != str])
                for directive in value:
                    if type(directive) == str:
                        directives.append(f"{name} {directive}")
                    else:
                        directives.append(f"{name} {directive[0]:{dindent}s} -> {directive[1]}")

            elif name.isupper():
                terminals.append(f"{name:{indent}s} : {value}")

            elif name.islower():
                ruleval    = []
                ruleindent = max([0]+[len(_) for _ in value if type(_) == str]+[len(_[0]) for _ in value if type(_) != str])

                for ruledef in value:
                    if type(ruledef) == str:
                        ruleval.append(ruledef)
                    else:
                        ruleval.append(f"{ruledef[0]:{ruleindent}s} -> {ruledef[1]}")

                rules.append(f"{name:{indent}s} : " + f"\n{' '*indent} | ".join(ruleval))

        grammar = ["\n".join(rules),
                   "\n".join(terminals),
                   "\n".join(directives),]

        return "\n\n".join(grammar)

class LarkSearchEngine(Plugin, registry=Registry.Library.SearchEngine):

    def __init__(self, *arg, parser='earley'):
        super().__init__(*arg)
        self._parser_type = parser
        self._grammars = []

    def compile(self):
        self._grammar     = Grammar(*self._grammars, app=self.app)
        self._parser      = Lark(self._grammar.grammar,
                                 start  = self._grammar.entry,
                                 parser = self._parser_type)
        self._transformer = Transformer()

        for name,func in self._grammar.transforms:
            setattr(self._transformer, name, func)

    def parse(self, searchstr): # pragma: no cover
            try:
                tree   = self._parser.parse(searchstr)
                search = self._transformer.transform(tree)
                _logger.debug3(f"Filter Tree:   {tree}")
                _logger.debug3(f"Filter Search: {search}")

            except ParseError as ex:
                _logger.debug3(f"Invalid Search String [ParseError]: '{searchstr}' : {ex}")
                return None

            except UnexpectedCharacters as ex:
                _logger.debug3(f"Invalid Search String [UnexpectedCharacters]: '{searchstr}' : {ex}")
                return None

            else:
                return search

    def filter(self, content, searchstr, modifier = None):
        return list(self.filtered(content, searchstr, modifier))

    def filtered(self, content, searchstr, modifier = None):
        if searchstr.strip() == "":
            # Content to filter can be any interable type
            # ... but a generator should always be returned
            return iter(content)
        else:
            try:
                tree   = self._parser.parse(searchstr)
                search = self._transformer.transform(tree)
                _logger.debug3(f"Filter Tree:   {tree}\n{tree.pretty()}")
                _logger.debug3(f"Filter Search: {search}")

                if modifier is not None:
                    sfunc = lambda _: search(modifier(_))
                else:
                    sfunc = search
                return filter(sfunc, content)

            # NOTE:2019/06/10: Uncertain if VisitError occurs in normal operations.
            #                  ... left over from initial development
            #                  ... comment out until a need for it surfaces
            #except VisitError as ex:
            #   _logger.debug3(f"Invalid Search String [VisitError]: '{searchstr}' : {ex}")
            #   return []

            except ParseError as ex:
                _logger.debug3(f"Invalid Search String [ParseError]: '{searchstr}' : {ex}")
                return []

            except UnexpectedCharacters as ex:
                _logger.debug3(f"Invalid Search String [UnexpectedCharacters]: '{searchstr}' : {ex}")
                return []

    def add(self, grammar):
        self._grammars.append(grammar(app=self.app))

