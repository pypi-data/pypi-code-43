"""dtool annotation CLI commands."""

import sys

import dtoolcore
import click
import json

from dtool_cli.cli import base_dataset_uri_argument


def _force_bool(s):
    s = s.strip().lower()
    if s == "0" or s == "false" or s == "f":
        return False
    return True


def _force_json(s):
    return json.loads(s)


TYPE_CHOICES = ["str", "int", "float", "bool", "json"]
TYPE_FUNCTION_LOOKUP = {
    "str": str,
    "int": int,
    "float": float,
    "bool": _force_bool,
    "json": _force_json
}


def _validate_name(name):
    if not dtoolcore.utils.name_is_valid(name):
        click.secho("Invalid annotation name '{}'".format(name), fg="red")
        click.secho(
            "Name must be 80 characters or less",
        )
        click.secho(
            "Names may only contain the characters: {}".format(
                " ".join(dtoolcore.utils.NAME_VALID_CHARS_LIST)
            ),
        )
        click.secho("Example: citation-index")
        sys.exit(400)


@click.group()
def annotation():
    """Annotations provide per dataset key/value metadata."""


@annotation.command(name="set")
@base_dataset_uri_argument
@click.argument("key")
@click.argument("value")
@click.option(
    "-t",
    "--type",
    type=click.Choice(TYPE_CHOICES),
    default="str"
)
def set_annotation(dataset_uri, key, value, type):
    """Set dataset annotation (key/value pair)."""
    try:
        dataset = dtoolcore.ProtoDataSet.from_uri(
            uri=dataset_uri,
            config_path=dtoolcore.utils.DEFAULT_CONFIG_PATH
        )
    except dtoolcore.DtoolCoreTypeError:
        dataset = dtoolcore.DataSet.from_uri(
            uri=dataset_uri,
            config_path=dtoolcore.utils.DEFAULT_CONFIG_PATH
        )

    _validate_name(key)

    try:
        value = TYPE_FUNCTION_LOOKUP[type](value)
    except ValueError as e:
        click.secho(str(e).capitalize(), err=True, fg="red")
        sys.exit(402)
    dataset.put_annotation(key, value)


@annotation.command(name="get")
@base_dataset_uri_argument
@click.argument("key")
def get_annotation(dataset_uri, key):
    """Get dataset annotation (value associated with the input key)."""
    try:
        dataset = dtoolcore.ProtoDataSet.from_uri(
            uri=dataset_uri,
            config_path=dtoolcore.utils.DEFAULT_CONFIG_PATH
        )
    except dtoolcore.DtoolCoreTypeError:
        dataset = dtoolcore.DataSet.from_uri(
            uri=dataset_uri,
            config_path=dtoolcore.utils.DEFAULT_CONFIG_PATH
        )
    try:
        click.secho(str(dataset.get_annotation(key)))
    except dtoolcore.DtoolCoreKeyError:
        click.secho(
            "No annotation named: '{}'".format(key),
            err=True,
            fg="red"
        )
        sys.exit(401)


@annotation.command(name="ls")
@base_dataset_uri_argument
def list_annotations(dataset_uri):
    """List the dataset annotations."""
    try:
        dataset = dtoolcore.ProtoDataSet.from_uri(
            uri=dataset_uri,
            config_path=dtoolcore.utils.DEFAULT_CONFIG_PATH
        )
    except dtoolcore.DtoolCoreTypeError:
        dataset = dtoolcore.DataSet.from_uri(
            uri=dataset_uri,
            config_path=dtoolcore.utils.DEFAULT_CONFIG_PATH
        )
    for name in sorted(dataset.list_annotation_names()):
        value = str(dataset.get_annotation(name))
        click.secho("{}\t{}".format(name, value))
