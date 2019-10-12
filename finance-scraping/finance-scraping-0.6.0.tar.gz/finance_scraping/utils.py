import argparse
from dateutil import parser
import os


def remove_header(text, separator=os.linesep):
    """
    Remove the first line containing headers from text data.

    :param str text: text content of a file
    :param str separator: line separator, optional (default to the OS default
                          line separator)
    :return str: input text with first line removed
    """
    no_header = text.split(separator)[1:]
    return separator.join(no_header)


def format_date(date):
    """
    Format a string representing a date into '%Y/%m/%d'.

    :param str date: date to format
    :return str: formatted date
    """
    date = parser.parse(date)
    return date.strftime('%Y/%m/%d')


def parse_cli():
    """
    Parse command-line interface arguments.

    :return: arguments
    """
    parser = argparse.ArgumentParser('Command-line interface for web scraper')

    parser.add_argument(
        '-c',
        '--configure',
        action='store_true',
        help='configure the scraper for manual use, requires user input')

    parser.add_argument(
        '-b',
        '--build',
        action='store_true',
        help='configure the Terraform provisioning script and then build the \
infrastructure (requires user input)')

    parser.add_argument(
        '-n',
        '--nuke',
        action='store_true',
        help='tear down the infrastructure')

    parser.add_argument(
        '-e',
        '--extract',
        action='store_true',
        help='run the extract step of the pipeline')

    parser.add_argument(
        '-t',
        '--transform',
        action='store_true',
        help='run the transform step of the pipeline')

    parser.add_argument(
        '-l',
        '--load',
        action='store_true',
        help='run the load step of the pipeline')

    parser.add_argument(
        '-d',
        '--date',
        type=str,
        help='specify date of data collection for transform or load')

    args = parser.parse_args()

    error_message = (
        "Do not specify options 'extract' and 'date' at the same time, "
        "'date' should only be specified when calling 'transform' and/or "
        "'load'.")

    assert not (args.extract and args.date), error_message

    return args
