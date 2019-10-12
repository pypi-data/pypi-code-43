#!/usr/bin/env python
"""
Functions related to finding changed variables in a given frame.

These are specialised inferrence functions which try to determine whether the
variables in the function are unreliable as the passed variables.
"""

import linecache
import re


def changed_vars(frame):
    """
    Report the variables that may have changed between the function start and frame.

    Return a dictionary of variables which are assigned or otherwise manipulated
    between the start of the function and our current line in the frame. This is
    intended to give an indication of which variables have been modified since the
    call (and therefore the function call given is probably not correct).
    """
    filename = frame.f_code.co_filename
    linecache.checkcache(filename)
    line_start = frame.f_code.co_firstlineno
    line_here = frame.f_lineno
    in_code = False
    changed = {}
    for lno in range(line_start, line_here + 1):
        line = linecache.getline(filename, lno, frame.f_globals)
        if not in_code:
            if '):' in line:
                in_code = True
            continue

        # We're in the code section now
        if '#' in line:
            line = line[0:line.index('#')]

        # Look for a inplace update or assignment of variable or tuple
        match = re.search(r"(?<![,.\]\)\"])\s*"                         # not preceded by ,.])"
                          r"(([A-Za-z_][A-Za-z0-9_]*)\s*"               # symbol name (initial one)
                          r"(?:,\s*[A-Za-z_][A-Za-z0-9_]*\s*)*)\s*"     # symbol name (subsequent ones)
                          r"(\+|-|/|//|\*|%|\*\*|>>|<<|\||&|^)?=",      # assignment or inplace update
                          line)
        if match:
            if match.group(3) is None:
                change_type = '='
            else:
                change_type = match.group(3) + '='
            vars_list = match.group(1)
            split_vars = [var.strip() for var in vars_list.split(',')]
            for var in split_vars:
                changed.setdefault(var, []).append({
                    'var': var,
                    'type': change_type,
                    'subject': None,
                    'line': lno
                })

        # 'with' or 'except' assignment
        match = re.search(r"^\s*(with|except)\s+"
                          r"([A-Za-z_][A-Za-z0-9_]*).*?"
                          r"\sas\s+([A-Za-z_][A-Za-z0-9_]*)",
                          line)
        if match:
            change_type = match.group(1)
            subject = match.group(2)
            var = match.group(3)
            changed.setdefault(var, []).append({
                'var': var,
                'type': change_type,
                'subject': subject,
                'line': lno
            })

        # 'for' assignment
        match = re.search(r"^\s*(for)\s+"
                          r"([A-Za-z_][A-Za-z0-9_]*)"
                          r"\s+in",
                          line)
        if match:
            change_type = match.group(1)
            var = match.group(2)
            changed.setdefault(var, []).append({
                'var': var,
                'type': change_type,
                'subject': None,
                'line': lno
            })

    return changed
