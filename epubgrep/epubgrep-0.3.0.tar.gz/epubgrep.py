#!/usr/bin/env python3
import argparse
import logging
import os.path
import re
import sys
import zipfile

from typing import Any, Dict, List, Optional, Tuple

import epub_meta

logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
                    level=logging.INFO)
log = logging.getLogger('epubgrep')


def get_chapter_title(mdata: List[Dict[str, Any]], fname: str) -> Optional[Tuple[str, int]]:
    if mdata is not None:
        found_list = [(x['title'], x['index']) for x in mdata if x['src'] == fname]
        if len(found_list) > 0:
            chap_title = found_list[0][0].strip(' \t.0123456789')
            return chap_title, found_list[0][1]
        else:
            return ('Unknown', 0)


def grep_book(filename: str, pattern: str, flags: int, counting: bool=False, color: bool=False):
    assert os.path.isfile(filename), "{} is not EPub file.".format(filename)
    sought_RE = re.compile('(' + pattern + ')', flags)
    count = 0

    mline = flags & re.M == re.M

    try:
        metadata = epub_meta.get_epub_metadata(filename)
    except epub_meta.EPubException as ex:
        log.exception('Failed to open {}'.format(filename))
    book = zipfile.ZipFile(filename)
    printed_booktitle = False

    for zif in book.infolist():
        with book.open(zif) as inf:
            if mline:
                decoded_str = inf.read().decode(errors='replace')
                res = sought_RE.search(decoded_str)
                if res:
                    if not printed_booktitle:
                        print('{}'.format(filename))
                        printed_booktitle = True
                    if counting:
                        count += 1
                    else:
                        chap_info = get_chapter_title(metadata.toc, zif.filename)
                        print("{}. {}:\n".format(chap_info[1], chap_info[0]))
                        print('{}\n'.format(res.group(0)))
            else:
                printed_title = False
                for line in inf:
                    decoded_line = line.decode(errors='replace').strip()
                    res = sought_RE.search(decoded_line)
                    if res:
                        if not printed_booktitle:
                            print('{}'.format(filename))
                            printed_booktitle = True
                        if counting:
                            count += 1
                        else:
                            if not printed_title:
                                chap_info = get_chapter_title(metadata.toc,
                                                              zif.filename)
                                if chap_info is not None:
                                    print("{}. {}:\n".format(chap_info[1], chap_info[0]))
                                    printed_title = True
                        # https://stackoverflow.com/a/33206814
                        # print("\033[31;1;4mHello\033[0m")
                        if not counting:
                            if color:
                                found_line = decoded_line.replace(
                                    res.group(1),
                                    "\033[31;1m" + res.group(1) + "\033[31;0m")
                                print('{}'.format(found_line))
                            else:
                                print(decoded_line)

    if count > 0:
        print('Found: {}'.format(count))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Grep through EPub book')
    parser.add_argument('pattern')
    parser.add_argument('files', nargs='+')
    parser.add_argument('-c', '--count',
                        action='store_true',
                        help="just counts of found patterns")
    parser.add_argument('-i', '--ignore-case',
                        action='store_true',
                        help="make search case insensitive")
    parser.add_argument('-o', '--color', '--colour',
                        action='store_false',
                        help="Do NOT mark found patterns with color")
    parser.add_argument('-m', '--multi-line',
                        action='store_true',
                        help="make search multi line")
    args = parser.parse_args()
    # log.debug('args = %s', args)

    search_flags = 0
    if args.ignore_case:
        search_flags |= re.I

    if args.multi_line:
        search_flags |= re.M | re.S

    for filename in args.files:
        book_fname = os.path.realpath(filename)
        try:
            grep_book(book_fname, args.pattern, search_flags, args.count, args.color)
        except BrokenPipeError:
            sys.exit()
