#!/usr/bin/env python3
import subprocess
import argparse
import sys
from string import Template
import os


def get_para():
    desc = """
    To run command line by line, and check each exit status.

    Then optionally check for the existences of result files.

    Each line format:

    echo "Hello world" && echo "Where are you?" ;Result-files: /path/to/resultfile1 /path/to/resultfile2

    Internally, each line will be split by ";Result-files:" delimiter,
    and the part before ";Result-files:" will be treated as a shell command,
    the part after ";Result-files:" will be regardeds as result files.

    Multiple result files are allowed, seperated by blank space(s).

    See https://github.com/linzhi2013/batch-run-cmd for more details.
    """

    parser = argparse.ArgumentParser(description=desc,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-f', dest='cmd_file', metavar='<file>',
        required=False,
        help="commands in a file.")

    parser.add_argument('-e', dest='continueOnReturnCode', nargs='+',
        metavar='<int>', type=int, default=[0],
        help="continue On Return Code for a shell command. [%(default)s]")

    parser.add_argument('-E', dest='resultFileStatus', metavar='<str>',
    choices=['a', 'e', 'o'], default='o',
    help="""continue On: 'a': all files must exist;
    'e': at least one file must exist;
    'o': omitted, i.e. do not check for existences of files [%(default)s]""")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    return args


def check_existences_of_files(files=None, resultFileStatus='a'):
    """
    'a': all files must exist;
    'e': at least one file must exist;
    'o': omitted, i.e. do not check for existences of files

    """
    file_num = len(files)

    # omitted or not result files to check
    if resultFileStatus == 'o' or file_num == 0:
        return True

    file_found_num = 0
    for f in files:
        if os.path.exists(f):
            file_found_num += 1

    if resultFileStatus == 'a' and file_num == file_found_num:
        return True

    elif resultFileStatus == 'e' and file_found_num >= 1:
        return True

    else:
        return False


def batch_run_cmd(cmd_file=None, continueOnReturnCode=[0], resultFileStatus='a'):
    with open(cmd_file, 'r') as fh:
        for i in fh:
            i = i.strip()
            if not i:
                continue
            line = i.split(';Result-files:')
            cmd = line[0]
            result_files = []
            if len(line) > 1:
                result_files = line[1].split()

            run_single_cmd(
                cmd=cmd,
                continueOnReturnCode=continueOnReturnCode
            )

            if not check_existences_of_files(files=result_files, resultFileStatus=resultFileStatus):
                print(cmd, file=sys.stderr)
                print('Some result files are not present: {result_files} Exit!'.format(
                    result_files=result_files), file=sys.stderr)
                sys.exit(1)



def run_single_cmd(cmd=None, continueOnReturnCode=[0]):
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, shell=True, check=True, encoding='utf8')
    except subprocess.CalledProcessError as e:
        print('{0}\nGot returncode {1}'.format(cmd, e.returncode), file=sys.stderr)
        if e.returncode in continueOnReturnCode:
            pass
        else:
            raise e
    else:
        print(cmd, flush=True, file=sys.stdout)
        print(result.stdout, flush=True, file=sys.stdout)
        if result.returncode not in continueOnReturnCode:
            print('Got returncode {}'.format(result.returncode), file=sys.stderr)
            sys.exit(result.returncode)


def main():
    args = get_para()

    batch_run_cmd(
        cmd_file=args.cmd_file,
        continueOnReturnCode=args.continueOnReturnCode,
        resultFileStatus = args.resultFileStatus
    )


if __name__ == '__main__':
    main()
