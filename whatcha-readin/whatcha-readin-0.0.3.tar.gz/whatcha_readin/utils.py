"""
Adapted from https://github.com/bmwant/podmena/blob/master/podmena/utils.py
"""

import click


def _warn(message: str) -> None:
    click.secho(message, fg="red")


def _note(message: str) -> None:
    click.secho(message, fg="green")


def _info(message: str) -> None:
    click.secho(message, fg="yellow")
