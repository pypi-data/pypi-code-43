import argparse
import fnmatch
import logging
import os
import re
import shutil
import tarfile


__version__ = '1.0.1'


COMPUTER_RE = re.compile(r'provera_.+_(?P<computer>s\d{3}).tgz$')
STUDENT_ASSIGNMENT_RE = re.compile(r'^home/provera/(?P<index>[a-z]{1,2}\d+.+)/(?:.+\.c)$')

DEFAULT_ARCHIVES_DIR = 'archives'
DEFAULT_EXTRACT_DIR = 'extracted'
STUDENT_DIR_INFO_SEPARATOR = '_'


def find_filenames(path, filename_pattern):
    file_list = sorted(os.listdir(path))
    for name in fnmatch.filter(file_list, filename_pattern):
        yield os.path.join(path, name)

def open_tar_archives(filenames):
    for name in filenames:
        yield tarfile.open(name, errorlevel=1)

def open_inner_tar_archives(tar_archives, filename_pattern):
    for tar in tar_archives:
        for name in fnmatch.filter(tar.getnames(), filename_pattern):
            inner_tar_fileobj = tar.extractfile(name)
            yield name, tarfile.open(fileobj=inner_tar_fileobj, errorlevel=1)

def find_student_code(tar_name, tar):
    for path in tar.getnames():
        match = STUDENT_ASSIGNMENT_RE.match(path)
        if not match:
            continue

        if tar.getmember(path).isdir():
            logging.error("Student in '%s' has saved a directory named '%s'!", tar_name, path)
            continue

        yield match.group('index'), path

def open_student_assignments(inner_tar_archives):
    for tar_name, tar in inner_tar_archives:
        computer = COMPUTER_RE.search(tar_name).group('computer')
        assignments = list(find_student_code(tar_name, tar))

        num_assignments = len(assignments)
        if num_assignments == 0:
            logging.warn("No student found in '%s', or s/he has not saved any assignments", tar_name)
        if num_assignments > 1:
            logging.error("Student in '%s' has saved %d assignments", tar_name, num_assignments)

        for index, code_path in assignments:
            yield computer, index, os.path.basename(code_path), tar.extractfile(code_path)

def find_student_assignments(archives_dir):
    tar_filenames = find_filenames(archives_dir, '*.tar')
    tar_archives = open_tar_archives(tar_filenames)
    inner_tar_archives = open_inner_tar_archives(tar_archives, '*.tgz')
    student_assignments = open_student_assignments(inner_tar_archives)

    return student_assignments

def store_student_assignments(student_assignments, to_path):
    for computer, index, code_filename, code_fileobj in student_assignments:
        code_path = os.path.join(to_path, computer + STUDENT_DIR_INFO_SEPARATOR + index, code_filename)
        logging.info("Extracting assignments for student %s at %s to '%s'", index, computer, code_path)
        if not os.path.exists(os.path.dirname(code_path)):
            os.makedirs(os.path.dirname(code_path))
        with open(code_path, 'wb') as out:
            out.write(code_fileobj.read())

def main():
    # Setup command line option parser
    parser = argparse.ArgumentParser(
        description='Extract assignments from exam archives of our ACS students',
    )
    parser.add_argument(
        '-a',
        '--archives-dir',
        metavar='DIRECTORY',
        default=DEFAULT_ARCHIVES_DIR,
        help="Search the selected DIRECTORY for TAR exam archives, '%s' by default" % DEFAULT_ARCHIVES_DIR,
    )
    parser.add_argument(
        '-e',
        '--extract-dir',
        metavar='DIRECTORY',
        default=DEFAULT_EXTRACT_DIR,
        help="Extract student assignments to selected DIRECTORY, '%s' by default" % DEFAULT_EXTRACT_DIR,
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

    if os.path.exists(args.extract_dir):
        logging.info("Directory '%s' already exists and will be deleted before continuing", args.extract_dir)
        shutil.rmtree(args.extract_dir)

    student_assignments = find_student_assignments(args.archives_dir)
    store_student_assignments(student_assignments, args.extract_dir)

if __name__ == '__main__':
    main()
