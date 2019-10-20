import argparse
import fnmatch
import logging
import os
import re
import sys

from smoke_test.main import smoke_test
from smoke_test.utils import get_test_stats


__version__ = '1.0.0'


COMPUTER_RE = re.compile(r's\d{3}$')

DEFAULT_EXTRACT_DIR = 'extracted'
STUDENT_DIR_INFO_SEPARATOR = '_'


def validate_computer_name(computer):
    if not COMPUTER_RE.match(computer):
        raise argparse.ArgumentTypeError("'%s' doesn't seem to be a valid computer name (provide it in sxyz format)" % computer)

    return computer

def find_filenames(path, filename_pattern):
    file_list = sorted(os.listdir(path))
    for name in fnmatch.filter(file_list, filename_pattern):
        yield os.path.join(path, name)

def get_student_index(dir_name):
    return dir_name.rsplit(STUDENT_DIR_INFO_SEPARATOR)[-1]

def find_student_dir(extract_dir, computer):
    dirs = list(find_filenames(extract_dir, "%s%s*" % (computer, STUDENT_DIR_INFO_SEPARATOR)))

    num_dirs = len(dirs)
    if num_dirs == 0:
        logging.error("No student found at computer %s, or s/he has not saved any assignments", computer)
        sys.exit(1)
    elif num_dirs > 1:
        raise RuntimeError("BUG: Found multiple dirs %s that match computer %s" % (dirs, computer))
    else:
        student_dir = dirs[0]
        logging.info("Found student %s at computer %s, in '%s'", get_student_index(student_dir), computer, student_dir)
        return student_dir

def find_student_assignment(student_dir, filename_pattern):
    assignments = list(find_filenames(student_dir, filename_pattern))

    num_assignments = len(assignments)
    if num_assignments == 0:
        raise RuntimeError("BUG: No student assignment found in '%s'" % student_dir)
    elif num_assignments > 1:
        logging.error("Student has saved multiple assignments %s", assignments)
        sys.exit(2)
    else:
        code_path = assignments[0]
        logging.info("Found student's assignment at '%s'", code_path)
        return code_path

def examine_student_assignment(extract_dir, computer):
    student_dir = find_student_dir(extract_dir, computer)
    student_assignment = find_student_assignment(student_dir, '*.c')

    results = smoke_test(student_assignment)
    num_ok, num_failed, success_rate = get_test_stats(results)
    if logging.getLogger().level <= logging.INFO:
        logging.info("Test stats: ok = %d, failed = %d, success rate = %d %%", num_ok, num_failed, success_rate)
    else:
        print success_rate

def main():
    # Setup command line option parser
    parser = argparse.ArgumentParser(
        description='Automated assignment examination of our ACS students',
    )
    parser.add_argument(
        'computer',
        type=validate_computer_name,
        help='Computer to examine the assignment on'
    )
    parser.add_argument(
        '-e',
        '--extract-dir',
        metavar='DIRECTORY',
        default=DEFAULT_EXTRACT_DIR,
        help="Search the selected DIRECTORY for extracted student assignments, '%s' by default" % DEFAULT_EXTRACT_DIR,
    )
    parser.add_argument(
        '-q',
        '--quiet',
        action='store_const',
        const=logging.WARN,
        dest='verbosity',
        help='Be quiet, show only warnings and errors',
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_const',
        const=logging.DEBUG,
        dest='verbosity',
        help='Be very verbose, show debug information',
    )
    parser.add_argument(
        '--version',
        action='version',
        version="%(prog)s " + __version__,
    )
    args = parser.parse_args()

    # Configure logging
    log_level = args.verbosity or logging.INFO
    logging.basicConfig(level=log_level, format="[%(levelname)s] %(message)s")

    examine_student_assignment(args.extract_dir, args.computer)

if __name__ == '__main__':
    main()
