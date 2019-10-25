"""unified logging scripts for mdk"""
# pylint: disable=too-many-arguments
from typing import Any, List

import click
from colorama import Fore, Style


def error(context, message):
    """error formatting"""
    click.echo("{}ERROR {}:{}".format(Fore.RED, context, Style.RESET_ALL))
    click.echo(indent(message, 2))


def notify(message, indent_depth=0):
    """generic message formatting"""
    click.echo(indent(message, indent_depth))


def indent(text: str, indent_depth: int) -> str:
    """add indentation to beginning of string"""
    indentation = "  " * indent_depth
    return indentation + text


def options(
        data: List[Any],
        label_prop: str,
        extra_option=None,
        indent_depth=1,
        label_prefix=None,
        start_index=0):
    """display a list of options"""
    idx = start_index
    for option in data:
        option_builder = "[{}]  ".format(idx)
        if label_prefix:
            option_builder += label_prefix
        option_builder += option[label_prop]
        click.echo(indent(option_builder, indent_depth))
        idx += 1
    if extra_option:
        extra_option_text = "[{}] {}".format(idx, extra_option)
        click.echo(indent(extra_option_text, indent_depth))

def success(context):
    """success formatting"""
    click.echo("{}SUCCESS: {}{}".format(Fore.GREEN, Style.RESET_ALL, context))
