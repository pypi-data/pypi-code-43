#!/usr/bin/env python
from __future__ import print_function
import io
import fnmatch
import os
import re
import sys
import time
import argparse
import binascii
import scandir

BUFSIZE = 4*1024*1024
TAILSIZE = BUFSIZE

from . import __version__
from .hexdump import *

try:
    range = xrange
except NameError:
    pass

def hex_pattern(expr):
    m = re.match(r"^\s*((?:[0-9a-f?]{2}|\*|\s*)*)\s*$", expr, re.I)
    if m:
        # parse hex pattern
        groups = re.findall(r"([0-9a-f?]{2}|\*)", m.group(1), re.I)
        pat = []
        for b in groups:
            if b == "??":
                pat.append('.')
            elif b == "*":
                pat.append(".*?")
            elif '?' in b:
                pat.append("[%s]" % "".join(br"\x%s" % b.replace('?', i).lower() for i in HEXDIGITS))
            else:
                pat.append(r"\x%s" % b.lower())
        return re.compile(''.join(pat).encode('ascii'), re.S)
    else:
        raise ValueError("Invalid hex pattern: `%s'" % expr)

def fblocks(fobj, start=0, length=None, chunksize=BUFSIZE, tailsize=None):
    if tailsize is None:
        tailsize = chunksize
    assert tailsize <= chunksize

    buf = bytearray(chunksize + tailsize)
    head = memoryview(buf)[tailsize:]
    tail = memoryview(buf)[:tailsize]
    total = 0

    while length is None or total < length:
        if total == 0:
            tailsize = fobj.readinto(tail)
        read = fobj.readinto(head)

        if read < chunksize:
            yield total + start, buf[:tailsize + read]
            break
        else:
            yield total + start, buf

        tail[:] = head[-tailsize:]
        total += read

def multisearch(block, patterns):
    for i, p in enumerate(patterns):
        for m in p.finditer(block):
            yield m

def list_recursively(dirnames):
    for d in dirnames:
        if os.path.isfile(d):
            yield d
        for path, dirs, files in scandir.walk(d):
            for f in files:
                yield os.path.normpath(os.path.join(path, f))

def filename_filter(filenames, include_filters, exclude_filters):
    for fn in filenames:
        if include_filters:
            for pattern in include_filters:
                if fnmatch.fnmatch(fn, pattern):
                    break
            else:
                continue
        for pattern in exclude_filters:
            if fnmatch.fnmatch(fn, pattern):
                break
        else:
            yield fn

def open_files(filenames):
    for fn in filenames:
        try:
            yield io.open(fn, "rb", buffering=0)
        except IOError as e:
            print("Error opening file: `%s`: %s" % (e.filename, e.strerror), file=sys.stderr)

def file_size(f):
    try:
        s = f.tell()
        f.seek(0, 2)
        res = f.tell()
        f.seek(s, 0)
        return res
    except IOError:
        return float('inf')

def format_match(filename, block, offset, match, fmt):
    match_hex = binascii.hexlify(block[match.start():match.end()]).decode('ascii')
    start = offset + match.start()
    return "{}:{:{fmt}}:{}".format(filename, start, match_hex, fmt=fmt)

def colorscheme(mark_on, mark_off, unprintable, unprintable_marked, seperator):
    return {
        ord(MARK_ON): mark_on,
        ord(MARK_OFF): mark_off,
        ord(UNPRINTABLE): unprintable,
        ord(UNPRINTABLE_MARKED): unprintable_marked,
        ord(SEPERATOR): seperator
    }

COLORSCHEME_DEFAULT = colorscheme(
    mark_on = u"\x1b[31;1m",
    mark_off = u"\x1b[0m",
    unprintable = u"\x1b[90m.\x1b[0m",
    unprintable_marked = u".",
    seperator = u'\x1b[34m|\x1b[0m',
)

COLORSCHEME_MONOCHROME = colorscheme(
    mark_on = u"\x1b[4;1m",
    mark_off = u"\x1b[0m",
    unprintable = u"\x1b[90m.\x1b[0m",
    unprintable_marked = u".",
    seperator = u'\x1b[1m|\x1b[0m',
)

COLORSCHEME_NO_COLOR = colorscheme(
    mark_on = u"",
    mark_off = u"",
    unprintable = u".",
    unprintable_marked = u".",
    seperator = u'|',
)

def get_progress_meter(progress):
    if progress:
        try:
            import tqdm
            return tqdm.tqdm
        except ImportError:
            print("WARNING: tqdm not available, progress display disabled")

    class DummyProgress:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def update(self, n):
            pass
        def set_description(self, s):
            pass
        def write(self, *args, **kwargs):
            print(*args, **kwargs)
        def close(self):
            pass
        fake = True
    return DummyProgress

def main():
    ap = argparse.ArgumentParser("hrep", 
        description="Search for binary sequences in files",
        epilog="Unless one of --files-with(out)-match, --count is specified, "
        "each output line corresponds to a match in the format: "
        "`<filename>:<offset>:<match>'")
    ap.add_argument("-x", "--hex", dest="hex", action="append", default=[],
        help="Search for a hexadecimal pattern"
             "('?' matches a single nibble, '*' matches any number of bytes)")
    ap.add_argument("-a", "--ascii", dest="ascii", action="append", default=[],
        help="Search for an ASCII string")
    ap.add_argument("-e", "--regex", dest="regex", action="append", default=[],
        help="Search for a regular expression")

    ap.add_argument("-i", "--ignore-case", action="store_true",
        help="Case-insensitive search (for regex/ascii searches only)")
    ap.add_argument("-r", "--recursive", action="store_true",
        help="Recursively search in directories")
    ap.add_argument("--chunk-size", type=int, default=BUFSIZE,
        help="Override default buffer size")
    ap.add_argument("-d", "--decimal-offset", action="store_const",
        default='#x', const='', dest='offset_fmt',
        help="Output decimal file offsets (by default prints hex)")
    ap.add_argument("-X", "--no-hexdump", action="store_false",
        dest='hexdump', help="Disable hex dump")
    ap.add_argument("-w", "--dump-width", type=int, default=16,
        help="Width of hex dump")
    ap.add_argument("-s", "--summary", action="store_true",
        help="Print summary at the end")
    ap.add_argument("-A", "--after", type=int, default=0,
        help="Number of additional bytes to display after match")
    ap.add_argument("-B", "--before", type=int, default=0,
        help="Number of additional bytes to display before match")
    ap.add_argument("-C", "--context", type=int, default=0,
        help="Number of additional bytes to display before and after match")

    ap.add_argument("-I", "--include", action="append", default=[],
        help="Filename pattern to include")
    ap.add_argument("-E", "--exclude", action="append", default=[],
        help="Filename pattern to exclude")

    ap.add_argument("-L", "--files-without-match", action="store_true",
        help="Only output unmatching filenames")
    ap.add_argument("-l", "--files-with-match", action="store_true",
        help="Only output matching filenames")
    ap.add_argument("-c", "--count", action="store_true",
        help="Only output number of matches for each input file")
    ap.add_argument("-m", "--max-count", metavar='NUM', default=float('inf'), type=int,
        help="Stop searching after NUM matches. ")
    ap.add_argument("-p", "--progress", action="store_true",
        help="Enable progress display")


    ap.add_argument("--no-color", action="store_const", const=COLORSCHEME_NO_COLOR,
        default=COLORSCHEME_DEFAULT, dest='colors', help="Disable color output")
    ap.add_argument("--monochrome", action="store_const", const=COLORSCHEME_MONOCHROME,
        dest='colors', help="Use monochrome color scheme")

    ap.add_argument("--version", action="version", version=__version__)
    ap.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)

    ap.add_argument(dest="hex_a", metavar="HEX", 
        nargs="?", help="Hex encoded binary sequence to search for")
    ap.add_argument(dest="filename", nargs="*",
        help="List of files to search in")
    args = ap.parse_args()

    args.before += args.context
    args.after += args.context

    if args.hex or args.ascii or args.regex:
        if args.hex_a is not None:
            args.filename.insert(0, args.hex_a)
    else:
        if args.hex_a is not None:
            args.hex.append(args.hex_a)
        else:
            ap.error("No pattern specified")

    if os.name == 'nt' or not sys.stdout.isatty():
        args.colors = COLORSCHEME_NO_COLOR
    if not sys.stderr.isatty():
        args.progress = False

    re_flags = re.IGNORECASE * args.ignore_case

    try:
        patterns = ([hex_pattern(x) for x in args.hex] +
                   [re.compile(re.escape(x.encode("ascii")), re_flags) for x in args.ascii] +
                   [re.compile(x.encode("ascii"), re_flags) for x in args.regex])
    except ValueError as e:
        ap.error(str(e))

    if args.debug:
        print('patterns:')
        for p in patterns:
            print(p.pattern)

    if args.recursive:
        if len(args.filename) == 0:
            args.filename = ['.']
        args.filename = list_recursively(args.filename)
    else:
        if len(args.filename) == 0:
            args.filename = [sys.stdin.fileno()]

    files = open_files(filename_filter(args.filename, args.include, args.exclude))
    matches = 0
    matched_files = set()

    dumper = HexDumper(
        width=args.dump_width, 
        align=args.dump_width, 
        before=args.before, 
        after=args.after)

    args.tail_size = args.chunk_size  # maybe change this sometime

    progress_meter = get_progress_meter(args.progress)
    prog_min_time = 0.1
    args.print_matches = True

    if args.files_with_match or args.files_without_match:
        args.max_count = 1
    if args.files_with_match or args.files_without_match or args.count:
        args.hexdump = args.print_matches = False

    total_matches = 0

    for f in files:
        fname = f.name
        if fname == 0:
            fname = '<stdin>'

        matches = 0

        prog = progress_meter(disable=True) # always start disabled

        try:
            start = time.time()
            for offset, block in fblocks(f, chunksize=args.chunk_size, tailsize=args.tail_size):
                if matches >= args.max_count:
                    break

                prog.update(len(block) - args.tail_size if len(block) > args.tail_size else len(block))

                if time.time() > start + prog_min_time:
                    prog = progress_meter(args.progress, 
                        total=file_size(f), 
                        initial=offset,
                        unit_scale=True,
                        unit='b',
                        dynamic_ncols=True,
                        leave=False,
                        desc=fname)
                    start = float('inf')

                for m in sorted(multisearch(block, patterns), key=lambda m: m.start()):
                    if matches >= args.max_count:
                        break

                    if m.start() > args.chunk_size:
                        # Already matched this one (in the tail)
                        continue

                    matches += 1

                    matched_files.add(f)
                    if args.print_matches:
                        prog.write(format_match(fname, block, offset, m, args.offset_fmt))

                    if args.hexdump:
                        prog.write(dumper.dump(block, offset, m.start(), m.end()).translate(args.colors), file=sys.stdout)
                        prog.write('', file=sys.stdout)
        finally:
            prog.close()

        if args.files_with_match and matches > 0:
            print(fname)
        elif args.files_without_match and matches == 0:
            print(fname)
        if args.count:
            print('{}:{}'.format(fname, matches))

        total_matches += matches

    if args.summary:
        print("{} match(es) accross {} file(s)".format(total_matches, len(matched_files)),
            file=sys.stdout)
    return 0 if total_matches > 0 else 1

if __name__ == '__main__':
    sys.exit(main())
