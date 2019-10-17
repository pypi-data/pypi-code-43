#  Copyright (c) 2019 | Advancing Technology Systems, LLC
#  See LICENSE for any grants of usage, distribution, or modification

from collections import namedtuple
from json import load as load_json
from pathlib import Path
from pickle import dumps as pickle_dump

from email_validator import validate_email as val, EmailNotValidError, EmailSyntaxError, EmailUndeliverableError


def validate_email(email: str):
    """Validates and formats an email address as well as checking if it is
    deliverable

    Args:
        email (str): The email to validate

    Returns:
        DubiousEmail: [valid: (bool), email: valid email || None if invalid, error (str)]
    """
    validated_email = namedtuple(
        typename="ValidatedEmail",
        field_names=["valid", "email", "error"],
        defaults=[False, None, None],
        module="pawn_pay.helpers",
    )

    try:
        return validated_email(
            True, val(email, allow_smtputf8=False, check_deliverability=True, allow_empty_local=False)["email"], None
        )
    except (EmailNotValidError, EmailSyntaxError, EmailUndeliverableError) as err:
        return validated_email(False, None, str(err))


def quick_conf(json: any([str, type(Path)]), output: any([str, type(Path)])):
    """Pickles whatever is in the supplied JSON file to quickly create
    a pawnpay client configuration without having to go all the way through
    the configuration generator

    Args:
        json (str || Path): The JSON file containing the settings to pickle
        output (str || Path): The path to output the resulting pickled settings

    Returns:
        tuple: (True if successful else False, pickle results if successful else errors)
    """
    try:
        with Path(output).resolve().open("wb") as out:
            res = out.write(pickle_dump(load_json(Path(json).resolve().open("r"))))
        return True, res
    except Exception as err:
        return False, err

# Copyright (c) 2019 | Advancing Technology Systems, LLC
# See LICENSE for any grants of usage, distribution, or modification
