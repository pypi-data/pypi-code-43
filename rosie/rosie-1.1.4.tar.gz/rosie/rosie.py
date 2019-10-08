# coding: utf-8
#  -*- Mode: Python; -*-                                              
# 
#  rosie.py     An interface to librosie from Python 2.7 and 3.6
# 
#  © Copyright IBM Corporation 2016, 2017, 2018.
#  LICENSE: MIT License (https://opensource.org/licenses/mit-license.html)
#  AUTHOR: Jenna N. Shockley
#  AUTHOR: Jamie A. Jennings

# Development environment:
#   Mac OS X Sierra (10.13.3)
#   Python 2.7.10 (distributed with OS X)
#   Python 3.6.5 (installed via brew on OS X)
#   cffi-1.11.4
# 

from __future__ import unicode_literals, print_function

import sys, json

from . import internal
from . import adapt23

# -----------------------------------------------------------------------------
# Rosie-specific

def librosie_path():
    return internal._librosie_path

def librosie_system():
    return internal.librosie_system

def librosie_local():
    return internal.librosie_local

def load(path = None, **kwargs):
    return internal.load(path, kwargs)

# -----------------------------------------------------------------------------
# re Flags
'''class RegexFlag(enum.IntFlag):
    ASCII = RE_FLAG_ASCII # assume ascii "locale"
    IGNORECASE = RE_FLAG_IGNORECASE # ignore case
    LOCALE = RE_FLAG_LOCALE # assume current 8-bit locale
    UNICODE = RE_FLAG_UNICODE # assume unicode "locale"
    MULTILINE = RE_FLAG_MULTILINE # make anchors look for newline
    DOTALL = RE_FLAG_DOTALL # make dot match newline
    VERBOSE = RE_FLAG_VERBOSE # ignore whitespace and comments
    A = ASCII
    I = IGNORECASE
    L = LOCALE
    U = UNICODE
    M = MULTILINE
    S = DOTALL
    X = VERBOSE'''

# -----------------------------------------------------------------------------
# Rosie Engine

class engine (object):

    '''
    A Rosie pattern matching engine is used to load/import RPL code
    (patterns) and to do matching.  Create as many engines as you need.
    '''

    def __init__(self):
        self._engine = internal.engine()
    
    # -----------------------------------------------------------------------------
    # Compile an expression
    # -----------------------------------------------------------------------------

    def compile(self, exp):
        pat, errs = self._engine.compile(adapt23.bytes23(exp))
        if not pat:
            raise_rosie_error(errs)
        return rplx(self, exp, pat)


    # -----------------------------------------------------------------------------
    # Basic methods
    # included in python re
    # -----------------------------------------------------------------------------

    def match(self, pattern, string, **kwargs):
        """Try to apply the pattern at the start of the string, returning
        a match object, or None if no match was found."""
        #        errs = None
        pattern = self.compile(pattern)
        return pattern.match(string, **kwargs)
    
    def fullmatch(self, pattern, input, **kwargs):
        #        errs = None
        pattern = self.compile(pattern)
        return pattern.fullmatch(input, **kwargs)

    def trace(self, pattern, input, **kwargs):
        #        errs = None
        pattern = self.compile(pattern)
        return pattern.trace(input, **kwargs)

    def search(self, pattern, string, **kwargs):
        #        errs = None
        pattern = self.compile(pattern)
        return pattern.search(string, **kwargs)

    def findall(self, pattern, string, **kwargs):
        #        errs = None
        pattern = self.compile(pattern)
        return pattern.findall(string, **kwargs)

    def finditer(self, pattern, string, **kwargs):
        #        errs = None
        pattern = self.compile(pattern)
        return pattern.finditer(string, **kwargs)

    def sub(self, pattern, repl, string,**kwargs):
        #        errs = None
        pattern = self.compile(pattern)
        return pattern.sub(repl, string, **kwargs)

    def subn(self, pattern, repl, string,**kwargs):
        #        errs = None
        pattern = self.compile(pattern)
        return pattern.subn(repl, string, **kwargs)

    def purge(self):
        raise NotImplementedError("Purge is an 're' function that is not applicable to RPL.")


    # -----------------------------------------------------------------------------
    # Functions for loading statements/blocks/packages into an engine
    # this functionality not included in python re
    # -----------------------------------------------------------------------------

    def load(self, src):
        ok, pkgname, errs = self._engine.load(adapt23.bytes23(src))
        if not ok or errs:
            raise_rosie_error(errs)
        return pkgname

    def loadfile(self, filename):
        ok, pkgname, errs = self._engine.loadfile(adapt23.bytes23(filename))
        if not ok or errs:
            raise_rosie_error(errs)
        return pkgname

    def import_package(self, pkgname, as_name=None):
        ok, actual_pkgname, errs = self._engine.import_pkg(adapt23.bytes23(pkgname),
                                                           as_name and adapt23.bytes23(as_name))
        if not ok or errs:
            raise_rosie_error(errs)
        return actual_pkgname


    # -----------------------------------------------------------------------------
    # Functions for reading and processing rcfile (init file) contents
    # this functionality not included in python re
    # -----------------------------------------------------------------------------
    
    def read_rcfile(self, filename=None):
        return self._engine.read_rcfile(filename)

    def execute_rcfile(self, filename=None):
        return self._engine.execute_rcfile(filename)


    # -----------------------------------------------------------------------------
    # Functions that return a parse tree or fragments of one
    # this functionality not included in python re
    # -----------------------------------------------------------------------------

    def parse_expression(self, exp):
        return self._engine.parse_expression(exp)
        
    def parse_block(self, block):
        return self._engine.parse_block(block)
        
    def expression_refs(self, exp):
        return self._engine.expression_refs(exp)
        
    def block_refs(self, block):
        return self._engine.block_refs(block)
        
    def expression_deps(self, exp):
        return self._engine.expression_deps(exp)
        
    def block_deps(self, block):
        return self._engine.block_deps(block)

    # -----------------------------------------------------------------------------
    # Functions for reading and modifying various engine settings
    # this functionality not included in python re
    # -----------------------------------------------------------------------------

    def config(self):
        return json.loads(self._engine.config())

    def libpath(self, libpath=None):
        return self. _engine.libpath(libpath)

    def alloc_limit(self, newlimit=None):
        return self._engine.alloc_limit(newlimit)

    def __del__(self):
        self._engine = None


def raise_rosie_error(errs):
    raise RuntimeError('RPL error:\n{}'.format(errs))

def raise_halt_error():
    raise RuntimeError('Matching aborted due to pattern containing halt pattern')

class rplx(object):  #object for a compiled pattern  

    def __init__(self, engine, exp, internal_rplx):
        self.pattern = exp                                  # bytes or str
        self._internal_rplx = internal_rplx
        self.engine = engine
    
    def valid(self):
        return self._internal_rplx.valid
    
    # TODO: support endpos in rosie
    def match(self, string, pos=1, endpos=None, **kwargs):
        if endpos is not None:
            endposIndex = endpos - 1
        else:
            endposIndex = len(string)
        encoder = kwargs['encoder'] if 'encoder' in kwargs else 'json'
        m, l, a, ttotal, tmatch = self._internal_rplx.engine.match(self._internal_rplx,
                                                        adapt23.bytes23(string[:endposIndex]),
                                                        pos,
                                                        adapt23.bytes23(encoder))
        if a and m == False: #check if matching was halted and no match found before
            raise_halt_error()
        elif m == False:
            return None
        if 'encoder' in kwargs:
            dict = {'match':m, 'leftover':l, 'abend':a}
            return dict
        else:
            match_value = json.loads(m)
            matchObject = Match(match_value, self, string, a, pos, endpos)
            return matchObject

    # TODO: support endpos in rosie
    def fullmatch(self, string, pos=1, endpos=None, **kwargs):
        if endpos is not None:
            endposIndex = endpos - 1
        else:
            endposIndex = len(string)
        m, l, a, ttotal, tmatch = self._internal_rplx.engine.match(self._internal_rplx,
                                                        adapt23.bytes23(string[:endposIndex]),
                                                        pos,
                                                        adapt23.bytes23('json'))
        if a and m == False: #check if matching was halted and no match found before
            raise_halt_error()
        elif m == False or l != 0:
            return None
        match_value = json.loads(m)
        matchObject = Match(match_value, self, string, a, pos, endpos)
        return matchObject

    # TODO: support endpos in rosie
    def trace(self, string, pos=1, endpos=None, **kwargs):
        if endpos is not None:
            endposIndex = endpos - 1
        else:
            endposIndex = len(string)
        encoder = kwargs['encoder'] if 'encoder' in kwargs else 'json'
        matched, trace_data = self._internal_rplx.engine.trace(self._internal_rplx,
                                                               adapt23.bytes23(string[:endposIndex]),
                                                               pos,
                                                               adapt23.bytes23(encoder))
        if 'encoder' in kwargs:
            return {'matched': matched, 'trace': trace_data}
        else:
            trace_value = json.loads(trace_data)
            return Trace(matched, trace_value)

    def search(self, string, pos=1, endpos=None, **kwargs):
        pattern = "find:{{({})}}".format(self.pattern)
        rplx_object = self.engine.compile(pattern)
        match_object = rplx_object.match(string, pos, endpos, **kwargs)
        if match_object is None:
            return None
        m = match_object.rosie_match
        for s in m['subs']:
            return Match(s, rplx_object, string, match_object.abend(), pos, endpos)

    def findall(self, string, pos=1, endpos=None, **kwargs):
        pattern = "findall:{{({})}}".format(self.pattern)
        rplx_object = self.engine.compile(pattern)
        match_object = rplx_object.match(string, pos, endpos, **kwargs)
        if match_object is None:
            return None
        m = match_object.rosie_match
        subs = []
        if 'subs' in m:
            for s in m['subs']:
                subs.append(s['data'])
        return subs

    def finditer(self, string, pos=1, endpos=None, **kwargs):
        pattern = "findall:{{({})}}".format(self.pattern)
        rplx_object = self.engine.compile(pattern)
        match_object = rplx_object.match(string, pos, endpos, **kwargs)
        if match_object is None:
            return None
        m = match_object.rosie_match
        subs = []
        if 'subs' in m:
            for s in m['subs']:
                subs.append(s['data'])
        return iter(subs)
    
    def sub(self, repl, string, count = 0):
        pattern = "find:{{({})}}".format(self.pattern)
        rplx_object = self.engine.compile(pattern)
        match_object = rplx_object.match(string)
        found = (match_object != None)
        while (found):
            m = match_object.rosie_match['subs'][0]
            string = string[0:m['s'] - 1] + repl + string[(m['e'] - 1):]
            match_object = rplx_object.match(string)
            found = (match_object != None)
        return string

    def subn(self, repl, string, count = 0):
        pattern = "find:{{({})}}".format(self.pattern)
        rplx_object = self.engine.compile(pattern)
        count_of_subs = 0
        match_object = rplx_object.match(string)
        found = (match_object != None)
        while (found):
            m = match_object.rosie_match['subs'][0]
            string = string[0:m['s'] - 1] + repl + string[(m['e'] - 1):]
            count_of_subs += 1
            match_object = rplx_object.match(string)
            found = (match_object != None)
        return (string, count_of_subs)



class Trace(object):
    def __init__(self, matchedValue, trace):
        self.matchedValue = matchedValue
        self.trace = trace

    def trace_value(self):
        return self.trace

    def matched(self):
        return self.matchedValue

class Match(object):

    def __init__(self, rosie_match, rplx_object, stringObject, a, position, endposition):
        self.re = rplx_object
        self.string = stringObject
        self.rosie_match = rosie_match
        self.a = a
        self.matches = []
        self.pos = position
        if (endposition == None):
            self.endpos = len(self.string)
        else:
            self.endpos = endposition

    #convert subs tree into list
    def _convertSubsToGroups(self, m):
        list = []
        match = Match(m,self.re,self.string,self.a,self.pos,self.endpos)
        list.append(match)
        if 'subs' in m:
            for s in m['subs']:
                list.extend(self._convertSubsToGroups(s))
        return list

    def expand(self, template):
        '''Return the string obtained by doing backslash substitution on the 
        template string template, as done by the sub() method. Escapes such 
        as \n are converted to the appropriate characters, and numeric 
        backreferences (\1, \2) and named backreferences (\g<1>, \g<name>) 
        are replaced by the contents of the corresponding group. Changed in 
        version 3.5: Unmatched groups are replaced with an empty string.'''
        new_string = template
        new_engine = engine()
        pattern1 = r'find:{"\\"[0-9]+}'
        pattern2 = r'find:{"\\" "g<" ([0-9]+) ">"}'
        pattern3 = r'find:{"\\" "g<" ([[0-9][a-z][A-Z]]+) ">"}'

        #pattern1
        match_object = new_engine.match(pattern1, new_string)
        found = (match_object != None)
        while (found):
            m = match_object.rosie_match['subs'][0]
            group_num = int(new_engine.search("[0-9]+", m['data']).group())
            item = self.group(group_num)
            new_string = new_string[0:m['s'] - 1] + item + new_string[(m['e'] - 1):]
            match_object = new_engine.match(pattern1, new_string)
            found = (match_object != None)

        #pattern2
        match_object = new_engine.match(pattern2, new_string)
        found = (match_object != None)
        while (found):
            m = match_object.rosie_match['subs'][0]
            group_num = int(new_engine.search("[0-9]+", m['data']).group())
            item = self.group(group_num)
            new_string = new_string[0:(m['s'] - 1)] + item + new_string[(m['e'] - 1):]
            match_object = new_engine.match(pattern2, new_string)
            found = (match_object != None)

        #pattern3
        match_object = new_engine.match(pattern3, new_string)
        found = (match_object != None)
        while (found):
            m = match_object.rosie_match['subs'][0]
            group_num = int(new_engine.search("[0-9]+", m['data']).group())
            item = self.group(group_num)
            new_string = new_string[0:(m['s'] - 1)] + item + new_string[(m['e'] - 1):]
            match_object = new_engine.match(pattern3, new_string)
            found = (match_object != None)
        return new_string


    def __getitem__(self, groupIdentifier):
        return self.group(groupIdentifier)

    def group(self, *args):
        #return original match
        if (not args):
            return self.rosie_match['data']
        else: 
            if (len(self.matches) is 0):
                self.matches.extend(self._convertSubsToGroups(self.rosie_match))
        #find capture by number
        if isinstance(args[0], int):
            if (len(args) is 1):
                m = self.matches[args[0]]
                return m.rosie_match['data']
            list = []
            for groupIndex in args:
                m = self.matches[groupIndex]
                list.append(m.rosie_match['data'])
            return tuple(list)

        #find capture by name
        #assume that isinstance(args[0], str) or isinstance(args[0], unicode) or isinstance(args[0], bytes):
        if (len(args) is 1):
            for match in self.matches:
                if match.rosie_match['type'] == args[0]:
                    return match.rosie_match['data']
            return None
        list = []
        for namedCapture in args:
            found = False
            for match in self.matches:
                if match.rosie_match['type'] == namedCapture:
                    list.append(match.rosie_match['data'])
                    found = True
            if found is False:
                list.append(None)
        return tuple(list)
            

    def groups(self):
        '''Return a tuple containing all the subgroups of the match, from 1 up to however many groups are in the pattern. 
        The default argument is used for groups that did not participate in the match; it defaults to None'''
        if (len(self.matches) is 0):
            self.matches.extend(self._convertSubsToGroups(self.rosie_match))
        list = []
        for match in self.matches:
            list.append(match.rosie_match['data'])
        del list[0]
        return tuple(list)

    def groupdict(self):
        '''Return a dictionary containing all the named subgroups of the match, keyed by the subgroup name. 
        The default argument is used for groups that did not participate in the match; it defaults to None.'''
        if (len(self.matches) is 0):
            self.matches.extend(self._convertSubsToGroups(self.rosie_match))
        dict = {}
        for match in self.matches:
            dict[match.rosie_match['type']] = match.rosie_match['data']
        return dict

    def subs(self, *args):
        if (len(self.matches) is 0):
                self.matches.extend(self._convertSubsToGroups(self.rosie_match))

        #return original match
        if (not args):
            subs = []
            for match in self.matches:
                subs.append(match.rosie_match['data'])
            return subs

        #find capture by number
        if isinstance(args[0], int):
            if (len(args) is 1):
                if (len(args[0].matches) is 0):
                    args[0].matches.extend(args[0]._convertSubsToGroups(args[0].rosie_match))
                subs = []
                for match in args[0].matches:
                    subs.append(match.rosie_match['data'])
                return subs
            else:
                raise_rosie_error("Invalid arguments: must be one argument")

        #find capture by name
        #elif isinstance(args[0], str):
        else:
            if (len(args) is 1):
                for match in self.matches:
                    if match.rosie_match['type'] == args[0]:
                        if (len(match.matches) is 0):
                            match.matches.extend(match._convertSubsToGroups(match.rosie_match))
                        subs = []
                        for submatch in match.matches:
                            subs.append(submatch.rosie_match['data'])
                        return subs
                return None

            raise_rosie_error("Invalid arguments: must be one argument")
        #else:
        #    raise_rosie_error("Invalid arguments: must be type int or string")

    def start(self, *args):
        if (not args):
            return self.rosie_match['s']
        else:
            if (len(self.matches) is 0):
                self.matches.extend(self._convertSubsToGroups(self.rosie_match))

        if isinstance(args[0], int):
            if (len(args) is 1):
                m = self.matches[args[0]]
                return m.rosie_match['s']
            else:
                raise_rosie_error("Invalid arguments: only 0-1 arguments")
        #assume isinstance(args[0], str) or isinstance(args[0], unicode) or isinstance(args[0], bytes):
        if (len(args) is 1):
            for match in self.matches:
                if match.rosie_match['type'] == args[0]:
                    return match.rosie_match['s']
        else:
            raise_rosie_error("Invalid arguments: only 0-1 arguments")

    def end(self, *args):
        if (not args):
            return self.rosie_match['e']
        else:
            if (len(self.matches) is 0):
                self.matches.extend(self._convertSubsToGroups(self.rosie_match))

        if isinstance(args[0], int):
            if (len(args) is 1):
                m = self.matches[args[0]]
                return m.rosie_match['e']
            else:
                raise_rosie_error("Invalid arguments: only 0-1 arguments")
        #assume isinstance(args[0], str):
        if (len(args) is 1):
            for match in self.matches:
                if match.rosie_match['type'] == args[0]:
                    return match.rosie_match['e']
        else:
            raise_rosie_error("Invalid arguments: only 0-1 arguments")

    def span(self, *args):
        if (not args):
            return (self.start(), self.end())
        else:
            return (self.start(*args), self.end(*args))

    def lastindex(self):
        #integer index of the last matched capturing group, or None if no group was matched at all
        if (len(self.matches) is 0):
                self.matches.extend(self._convertSubsToGroups(self.rosie_match))
        return len(self.matches) - 1

    def lastgroup(self):
        #name of the last matched capturing group, or None if the group didn’t have a name,
        #or if no group was matched at all
        if (len(self.matches) is 0):
                self.matches.extend(self._convertSubsToGroups(self.rosie_match))
        return self.matches[len(self.matches) - 1].rosie_match['type']

    def abend(self):
        return self.a

    
    




