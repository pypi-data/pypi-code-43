# -*- coding: utf-8 -*-

import sys
import re
import itertools

__all__ = ('split', 'quote')

__version__ = '0.2.0'

def iter_arg(peek, i):
    quote_mode = False
    for m in itertools.chain([peek], i):
        space, slashes, quotes, text = m.groups()
        if space:
            if quote_mode:
                yield space
            else:
                return
        elif quotes:
            n_slashes = len(slashes)
            n_quotes = len(quotes)
            slashes_odd = bool(n_slashes % 2)
            yield '\\' * (n_slashes // 2)
            magic_sum = n_quotes + quote_mode + 2*slashes_odd
            yield '"' * (magic_sum // 3)
            quote_mode = (magic_sum % 3) == 1
        else:
            yield text

def iter_args(s):
    i = re.finditer(r'(\s+)|(\\*)(\"+)|(.[^\s\\\"]*)', s.lstrip())
    for m in i:
        yield ''.join(iter_arg(m, i))


def split(s, like_cmd=True):
    """
    Split a string of command line arguments like DOS and Windows do.

    On windows, before a command line argument becomes a char* in a
    program's argv, it must be parsed by both cmd.exe, and by
    CommandLineToArgvW.

    If like_cmd is true, then this will emulate both cmd.exe and
    CommandLineToArgvW.   Since cmd.exe is a shell, and can run
    external programs, this function obviously cannot emulate
    everything it does.   However if the string passed in would
    be parsed by cmd as a quoted literal, without command
    invocations like `&whoami`, and without string substitutions like
    `%PATH%`, then this function will split it accurately.

    if like_cmd is false, then this will split the string like
    CommandLineToArgvW does.
    """
    if like_cmd and re.search(r'[\%\!\^]', s):
        def i():
            quote_mode = False
            for m in re.finditer(r'(\^.)|(\")|([^\^\"]+)', s):
                escaped, quote, text = m.groups()
                if escaped:
                    if quote_mode:
                        yield escaped
                    else:
                        yield escaped[1]
                elif quote:
                    yield '"'
                    quote_mode = not quote_mode
                else:
                    yield text
        s = ''.join(i())
        # def i(parts):
        #     quote_mode = False
        #     for part in parts:
        #         if quote_mode:
        #             yield re.sub(r'\^(.)', r'\1', part)
        #         else:
        #             yield part
        #         quote_mode = not quote_mode
        #s = '"'.join(i(s.split('"')))
    return list(iter_args(s))

cmd_meta = r'([\"\^\&\|\<\>\(\)\%\!])'
cmd_meta_or_space = r'[\s\"\^\&\|\<\>\(\)\%\!]'


def quote(s, for_cmd=True):
    """
    Quote a string for use as a command line argument in DOS or Windows.

    On windows, before a command line argument becomes a char* in a
    program's argv, it must be parsed by both cmd.exe, and by
    CommandLineToArgvW.

    If for_cmd is true, then this will quote the string so it will
    be parsed correctly by cmd.exe and then by CommandLineToArgvW.

    If for_cmd is false, then this will quote the string so it will
    be parsed correctly when passed directly to CommandLineToArgvW.

    For some strings there is no way to quote them so they will
    parse correctly in both situations.
    """
    if not s:
        return '""'
    if not re.search(cmd_meta_or_space, s):
        return s
    if for_cmd and re.search(cmd_meta, s):
        return re.sub(cmd_meta, r'^\1', quote(s, for_cmd=False))
    i = re.finditer(r'(\\*)(\"+)|(\\+)|([^\\\"]+)', s)
    def parts():
        yield '"'
        for m in i:
            pos,end = m.span()
            slashes, quotes, onlyslashes, text = m.groups()
            if quotes:
                yield slashes
                yield slashes
                yield r'\"' * len(quotes)
            elif onlyslashes:
                if end == len(s):
                    yield onlyslashes
                    yield onlyslashes
                else:
                    yield onlyslashes
            else:
                yield text
        yield '"'
    return ''.join(parts())

def split_cli():
    import argparse

    parser = argparse.ArgumentParser(
        description='split a file into strings using windows-style quoting ')
    parser.add_argument('filename', nargs='?',
                        help='file to split')
    args = parser.parse_args()

    if args.filename:
        input = open(args.filename, 'r')
    else:
        input = sys.stdin

    for s in iter_args(input.read()):
        print(s)
