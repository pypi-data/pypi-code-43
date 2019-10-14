import sys
import argparse
from io import StringIO
from pathlib import Path

import yaml
from mistune import Markdown

from markdown_formatter import __version__
from markdown_formatter.types import FormatConfig
from markdown_formatter.utils import (
    get_differ, get_line_breaker, read_file_with_chardet
)
from markdown_formatter.docdata import get_data
from markdown_formatter.renderer import CodeFormatter


def format_content(raw, line_break, matter_data, config: FormatConfig):
    content = Markdown(
        renderer=CodeFormatter(
            config=config,
            hard_wrap=True,
            line_break=line_break,
        )
    ).render(raw)

    with StringIO(newline='') as f:
        if matter_data:
            f.write('---' + line_break)
            yaml.safe_dump(
                matter_data,
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

    return content


def single_file(file, config: FormatConfig):
    fs = Path(file)

    raw = read_file_with_chardet(file)
    raw_lines = raw.splitlines(True)
    line_break = get_line_breaker(raw_lines)

    doc, data = get_data(raw)
    content = format_content(doc, line_break, data, config)

    if config.inplace:
        with open(
            fs,
            'w+',
            encoding='utf-8',
            newline='',
        ) as f:
            f.write(content)

    if content != raw:
        if not config.inplace:
            for line in get_differ(raw.splitlines(), content.splitlines()):
                print(line)
            return 0
        return 1
    return 0


def main(argv):
    parser = argparse.ArgumentParser(description='Formatter for Markdown.')
    parser.add_argument(
        '-v', '--version', action='store_true', help='show version number and exit'
    )

    parser.add_argument(
        'files', nargs='*', help='reads from stdin when no files are specified.'
    )

    parser.add_argument(
        '--not-format-py-code',
        action='store_false',
        help='show version number and exit',
    )

    parser.add_argument(
        '--diff',
        action='store_true',
        help='show version number and exit',
    )

    args = parser.parse_args(argv[1:])
    if args.version:
        print(__version__)
        exit()
    if len(args.files) == 0:
        print('at lease give one files')
        exit(1)

    config = FormatConfig(
        format_py_code=not bool(args.not_format_py_code),
        inplace=not bool(args.diff),
    )

    exit_code = 0

    for file in args.files:
        exit_code |= single_file(file, config=config)
    return exit_code


def run_main():
    try:
        sys.exit(main(sys.argv))
    except Exception as e:
        sys.stderr.write('markdown_formatter: ' + str(e) + '\n')
        sys.exit(2)


if __name__ == '__main__':
    main(sys.argv)
