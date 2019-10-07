"""Fortran linter"""
import os
import argparse
from flint.formatting import (_parse_format_line,
                              _init_format_rules)

def flint_file(filename):
    file_stats = dict()
    file_stats['modifs'] = 0
    file_stats['errors'] = 0
    with open(filename, 'r') as fin:
        lines = fin.readlines()
    file_stats['total_lines'] = len(lines)

    format_rules = _init_format_rules()
    for i, line in enumerate(lines, 1):
        line_stats = _parse_format_line(filename, line, i, format_rules)
        file_stats['errors'] += line_stats["errors"]
        file_stats['modifs'] += line_stats["modifs"]
    rate = (float(file_stats['errors']) / file_stats['total_lines']) * 10
    rate = 10.0 - rate
    print(50*'-')
    print("Your code has been rated %2.2f/10" %rate)
    return rate

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('input', help='Input file(s)', nargs='+')
    args = parser.parse_args()
    for file in set(args.input):
        file = os.path.abspath(file)
        print('************* Module %s' % file.replace('/', '.'))
        flint_file(file)

#todo: add other rules : refactoring and warning
# Reogranize stats 
# Label error messages
# Revise rating formula
# get total file length(without comments)
# find number of arguments for each function
# find number of local variables for each function
# find tabs and replace them with spaces

if __name__ == '__main__':
    main()
