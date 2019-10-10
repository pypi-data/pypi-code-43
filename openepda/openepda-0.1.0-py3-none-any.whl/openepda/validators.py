# -*- coding: utf-8 -*-
"""openepda.validators.py

This file contains validators for the data formats defined by
the openEPDA.

Author: Dima Pustakhod
Copyright: TU/e

Changelog
---------
2019.05.25
    Add is_cdf_valid()
"""
import os

try:
    from ruamel.yaml import YAML

    yaml = YAML(typ='safe')
    safe_load = yaml.load
except ImportError:
    from yaml import safe_load


module_fpath = os.path.abspath(os.path.join(__file__, '..'))


CDF_VERSIONS = ['0.1']
CDF_SCHEMA_NAME_TEMPLATE = '/schemas/cdf_schema_v{version}.yaml'

UPDK_SBB_VERSIONS = ['0.2']
UPDK_SBB_SCHEMA_NAME_TEMPLATE = '/schemas/updk_sbb_schema_v{version}.yaml'


def is_cdf_valid(data, version='latest', raise_error=False, full_output=False):
    """Check if the data is a correct CDF of a given version.

    JSON Schema is used for validation. See http://json-schema.org

    Parameters
    ----------
    data : any
        data structure to be validated
    version : str
        CDF format version, 'X.Y' or 'latest'
    raise_error : bool
        If True, a jsonschema.ValidationError is raised in case of wrong
        format. If False, a boolean result will be returned (with
        optional message).
    full_output : bool
        If False, only resulting boolean value is returned. Otherwise,
        additional string with a validation message is returned.

    Returns
    -------
    bool
        validation result
    str
        validation message (optional)

    Examples
    --------
    >>> with open('tests/_test_data/cdf_correct_v0.1.cdf') as s: data = safe_load(s)
    >>> is_cdf_valid(data, raise_error=True)
    True

    """
    from jsonschema import validate, ValidationError

    allowed_versions = ['latest'] + CDF_VERSIONS
    if version not in allowed_versions:
        raise ValueError(
            'Unknown version of the CDF specified: {version}. '
            'Allowed versions: {allowed_versions}.'.format(
                version=version, allowed_versions=allowed_versions
            )
        )
    if version == 'latest':
        version = CDF_VERSIONS[-1]

    cdf_schema_file_name = module_fpath + CDF_SCHEMA_NAME_TEMPLATE.format(
        version=version
    )

    with open(cdf_schema_file_name) as s:
        schema = safe_load(s)

    # default reply
    result, msg = True, 'Data is valid CDF v.{version}.'.format(version=version)

    if raise_error:
        validate(instance=data, schema=schema)
    else:
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            result = False
            msg = str(e)

    if full_output:
        return result, msg
    else:
        return result


def is_updk_sbb_valid(data, version='latest', raise_error=False, full_output=False):
    """Check if the data structure is a correct uPDK SBB of a given version.

    JSON Schema is used for validation. See http://json-schema.org

    Parameters
    ----------
    data : any
        data structure to be validated
    version : str
        format version, 'X.Y' or 'latest'
    raise_error : bool
        If True, a jsonschema.ValidationError is raised in case of wrong
        format. If False, an boolean result will be returned (with
        optional message).
    full_output : bool
        If False, only resulting boolean value is returned. Otherwise,
        additional string with a validation message is returned.

    Returns
    -------
    bool
        validation result
    str
        validation message (optional)

    Examples
    --------
    >>> with open('tests/_test_data/sbb_correct_v0.2.yaml') as s: data = safe_load(s)
    >>> is_updk_sbb_valid(data, raise_error=True)
    True

    """
    from jsonschema import validate, ValidationError

    allowed_versions = ['latest'] + UPDK_SBB_VERSIONS
    if version not in allowed_versions:
        raise ValueError(
            'Unknown version of the uPDK specified: {version}. '
            'Allowed versions: {allowed_versions}.'.format(
                version=version, allowed_versions=allowed_versions
            )
        )
    if version == 'latest':
        version = UPDK_SBB_VERSIONS[-1]

    updk_schema_file_name = (
        module_fpath + UPDK_SBB_SCHEMA_NAME_TEMPLATE.format(version=version)
    )

    with open(updk_schema_file_name) as s:
        schema = safe_load(s)

    # default reply
    result, msg = True, 'Data is valid uPDK SBB v.{}.'.format(version)

    if raise_error:
        validate(instance=data, schema=schema)
    else:
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            result = False
            msg = str(e)

    if full_output:
        return result, msg
    else:
        return result


def main():
    import doctest

    os.chdir('{}/..'.format(module_fpath))
    doctest.testmod(verbose=False)


if __name__ == '__main__':
    main()
