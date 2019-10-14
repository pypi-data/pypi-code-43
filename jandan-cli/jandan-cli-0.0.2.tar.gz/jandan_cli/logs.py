# -*- encoding: utf-8 -*-

from contextlib import contextmanager
from datetime import datetime
import sys
from traceback import format_exception
import colorama

def warn(title):
  sys.stderr.write('{warn} [WARN] {title}{rest}\n'.format(
    warn=colorama.Back.RED + colorama.Fore.WHITE + colorama.Style.BRIGHT,
    title=title,
    reset=colorama.Style.RESET_ALL
  ))


def exception(title, exc_info):
  sys.stderr.write('{warn}[WARN] {title}:{reset}\n{trace}\n{warn}----------------------------{reset}\n\n'.format(
    warn=colorama.Back.RED + colorama.Fore.WHITE + colorama.Style.BRIGHT,
    title=title,
    reset=colorama.Style.RESET_ALL,
    trace=''.join(format_exception(*exc_info))
  ))


def failed(msg):
  sys.stderr.write('{red}{msg}{reset}\n'.format(
    red=colorama.Back.RED,
    msg=msg,
    reset=colorama.Style.RESET_ALL
  ))


def debug(msg):
  sys.stderr.write('{blue}{bold}DEBUG:{reset} {msg}\n'.format(
    blue=colorama.Fore.BLUE,
    bold=colorama.Style.BRIGHT,
    reset=colorama.Style.RESET_ALL,
    msg=msg,
  ))


@contextmanager
def debug_time(msg):
  started = datetime.now()
  try:
    yield
  finally:
    debug('{} took: {}'.format(msg, datetime.now() - started))


def version(cli_version, python_version, os_info):
  sys.stderr.write('jandan-py {} using Python {} on {}\n'.format(
    cli_version,
    python_version,
    os_info
  ))