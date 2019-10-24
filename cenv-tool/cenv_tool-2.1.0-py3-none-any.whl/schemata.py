# -*- coding: utf-8 -*-
"""Contain schemata required by cenv-tool."""
from marshmallow import fields
from marshmallow import Schema
from marshmallow import validate


class SNPackage(Schema):
    """Contain the ``package``-section inside a ``meta.yaml``."""

    name = fields.String(strict=True, required=True)
    version = fields.String(strict=True, required=True)


class SNSource(Schema):
    """Contain the ``source``-section inside a ``meta.yaml``."""

    path = fields.String(strict=True, required=True)


class SNBuild(Schema):
    """Contain the ``build``-section inside a ``meta.yaml``.

    The ``build``-section requires to define the build-number, if the egg-dir
    should be preserved, the script to run on installation and if any
    entrypoints are defined for the package.
    """

    build = fields.String(strict=True, required=True)
    preserve_egg_dir = fields.String(
        strict=True,
        required=True,
        validate=validate.OneOf(['True', 'False']),
    )
    script = fields.String(strict=True, required=True)
    entry_points = fields.List(
        fields.String(strict=True, required=False),
        strict=True,
        required=False,
    )


class SNRequirements(Schema):
    """Contain ``requirements``-section inside a ``meta.yaml``.

    The underlying ``build``- and ``run``-sections have to be valid!
    """

    build = fields.List(
        fields.String(strict=True, required=True),
        strict=True,
        required=True,
    )
    run = fields.List(
        fields.String(
            strict=True,
            required=True,
            validate=lambda x: '=' in x if 'python' not in x else True,
            error_messages=dict(validator_failed='Version must be specified'),
        ),
        strict=True,
        required=True,
    )
    run_constrained = fields.List(
        fields.String(
            strict=True,
            required=False,
            validate=lambda x: '=' in x,
            error_messages=dict(validator_failed='Version must be specified'),
        ),
        strict=True,
        required=False,
    )


class SNTest(Schema):
    """Contain ``tests``-section inside a ``meta.yaml``."""

    imports = fields.List(
        fields.String(strict=True, required=False),
        strict=True,
        required=False,
    )
    commands = fields.List(
        fields.String(strict=True, required=False),
        strict=True,
        required=False,
    )


class SNExtra(Schema):
    """Contain the ``extra``-section inside a ``meta.yaml``.

    The ``extra``-section has to contains the information where to find the
    conda-folder, the name of the conda environment to use for the current
    project and the cenv-version used when the ``meta.yaml`` file was created.
    """

    env_name = fields.String(
        strict=True,
        required=True,
        validate=lambda x: ' ' not in x,
    )

    python = fields.String(
        strict=True,
        required=True
    )

    dev_requirements = fields.List(
        fields.String(
            strict=True,
            required=True,
            validate=lambda x: '=' in x,
            error_messages=dict(validator_failed='Version must be specified'),
        ),
        strict=True,
        required=False,
    )


class SMetaYaml(Schema):
    """Contain the representable of a complete ``meta.yaml`` file.

    Schema for a ``meta.yaml`` file to be used for cenv.
    Ensure the meta.yaml to load contains the relevant information about
    the ``package``, ``source``, ``build``, ``requirements`` and ``extra``.
    The ``test``-section is optional.
    """

    package = fields.Nested(SNPackage, strict=True, required=True)
    source = fields.Nested(SNSource, strict=True, required=True)
    build = fields.Nested(SNBuild, strict=True, required=True)
    requirements = fields.Nested(SNRequirements, strict=True, required=True)
    test = fields.Nested(SNTest, strict=True, required=False)
    extra = fields.Nested(SNExtra, strict=True, required=True)
