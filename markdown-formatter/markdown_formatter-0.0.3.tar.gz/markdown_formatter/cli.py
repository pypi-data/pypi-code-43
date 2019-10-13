import sys
import argparse
from io import StringIO
from pathlib import Path

import yaml
from mistune import Markdown

from markdown_formatter import __version__
from markdown_formatter.docdata import get_data
from markdown_formatter.renderer import CodeFormatter


def single_file(file):
    fs = Path(file)
    with open(file, 'r', encoding='utf-8') as f:
        raw = f.read()
    line_break = raw.splitlines(True)[0][-1]
    assert len(line_break) == 1

    doc, data = get_data(raw)
    content = Markdown(renderer=CodeFormatter(
        hard_wrap=True,
        line_break=line_break,
    )).render(doc)
    with StringIO(newline='') as f:
        if data:
            f.write('---' + line_break)
            yaml.safe_dump(
                data,
                f,
                allow_unicode=True,
                sort_keys=False,
                indent=2,
                line_break=line_break,
            )
            f.write('---' + line_break * 2)
        f.write(content)
        f.seek(0)
        content = f.read()
    if content.endswith(line_break * 2):
        content = content[:-1]
    with open(
        fs,
        'w+',
        encoding='utf-8',
        newline='',
    ) as f:
        f.write(content)


def main(argv):
    parser = argparse.ArgumentParser(description='Formatter for Markdown.')
    parser.add_argument(
        '-v', '--version', action='store_true', help='show version number and exit'
    )
    parser.add_argument(
        'files', nargs='*', help='reads from stdin when no files are specified.'
    )
    args = parser.parse_args(argv[1:])
    if args.version:
        print(__version__)
        exit()
    if len(args.files) == 0:
        print('at lease give one files')
        exit(1)
    for file in args.files:
        single_file(file)


def run_main():
    try:
        sys.exit(main(sys.argv))
    except Exception as e:
        sys.stderr.write('markdown_formatter: ' + str(e) + '\n')
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv)
