import argparse
import json

from . import parsewhen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('text', help='The text to parse.')
    parser.add_argument('--tree', '-t', action='store_true', default=False,
                        help='Output the parsed tree, no evaluating.')
    parser.add_argument('--values', '-V', action='store_true', default=False,
                        help='Only output the values when using tree mode.')
    parser.add_argument('--json', '-j', action='store_true', default=False,
                        help='Output the parsed tree as valid JSON')
    args = parser.parse_args()

    if args.tree:
        tree = list(parsewhen.tree(args.text))
        if args.values:
            tree = list(parsewhen.parser.tree_values(tree))
        if args.json:
            tree = json.dumps(tree)
        print(tree)
    else:
        print(parsewhen.replace(args.text))
    return None

if __name__ == '__main__':
    main()
