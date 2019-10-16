"""Convenience methods for printing to screen"""
import sys


def msg(user_msg):
    """Print"""
    print(user_msg)


def dashes(char='-'):
    """Dashed line"""
    msg(40*char)


def msgt(user_msg):
    """print message with dashed line before/after"""
    dashes()
    msg(user_msg)
    dashes()


def msgn(user_msg):
    """print message with dashed line before"""
    dashes()
    msg(user_msg)


def msgx(user_msg):
    """Print message and exit program--hard exit"""
    dashes('=')
    msg(user_msg)
    dashes('=')
    sys.exit(0)
