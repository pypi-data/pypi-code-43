"""
Safe.py by Dalofeco

Safe.py provides convenience safety and reliability assuring methods
that make convenient safety features easy to access from any project.
"""
import logging
import re
from typing import List

# Verbose logging option
VERBOSE = False

# Define logger for module
logger = logging.getLogger(__name__)


def keys_in_dict(dict_object: dict, key_values: List[str]) -> bool:
    """Checks whether the keys are provided in the dict object.

    Checks for the existence of each key specified in keyValues array in the specified dictObject.
    Returns true if all keys were found, false if at least was not.

    :param dict_object: dict object to check for key existence in
    :param key_values: string keys to check for existence in the dict object
    :return: boolean indicating whether all keys were found
    """
    # Values should be an array of key values

    # Check that input variables are of expected type
    if type(key_values) is not list or type(dict_object) is not dict:
        if VERBOSE:  # pragma: no cover
            logger.warning(
                f'Invalid parameters: expected dict and array, '
                f'got {type(dict_object)} and {type(key_values)}',
            )
        return False

    # Iterate through all key values
    for key_value in key_values:

        # Make sure key value is a string
        if type(key_value) is not str:
            if VERBOSE:  # pragma: no cover
                logger.warning(
                    'Invalid value in key values array parameter: expected a string',
                )
            return False

        # Check that v is in the dict object
        if key_value not in dict_object:
            if VERBOSE:  # pragma: no cover
                logger.warning(
                    f'{key_value} is not in dict ({dict_object.keys()})',
                )
            return False

    return True


def which_key_in_dict(dict_object: dict, key_values: List[str]) -> str:
    """Checks for the existence of each key specified in keyValues array in the specified dictObject.

    :param dict_object: dict object to check for key presence
    :param key_values: key value options to check
    :return: key value of the first key found, empty string if none were.
    """

    # Check that input variables are of expected type
    if not isinstance(key_values, list) or not isinstance(dict_object, dict):
        if VERBOSE:  # pragma: no cover
            logger.warning(
                f'Invalid parameters: expected dict and array,'
                f' got {type(dict_object)} and {type(key_values)}',
            )
        return ''

    # Iterate through all values
    for v in key_values:

        # Make sure v is a string
        if not isinstance(v, str):
            if VERBOSE:  # pragma: no cover
                logger.warning(
                    'Invalid value in key values array parameter: expected a string.',
                )
            return ''

        # Check that v is in the dictObject
        if v in dict_object:
            return v

    return ''


# Define local part regex for emails


def is_email(email: str) -> bool:
    """Makes sure email is a valid email within proper format

    :param email: email address to check with regex
    :return: success value of check
    """

    # Make sure email has a value and is string
    if not email or type(email) is not str:
        return False

    # Split email by @
    email_parts = email.split('@')

    # Must be two parts, otherwise not an email
    if len(email_parts) != 2:
        return False

    # Check both the local part and domain part with class methods
    return is_email_localpart(email_parts[0]) and \
        (is_domain(email_parts[1]) or is_ip_address(email_parts[1]))


def is_domain(domain: str) -> bool:
    """Makes sure domain is valid with proper format."""

    # Make sure domain is specified as proper type
    if not domain or type(domain) is not str:
        return False

    # Define regex for domain validation
    domain_regex = r'[a-z0-9]+([a-z0-9\-]+\.)+([a-z]+[a-z0-9]?)+$'

    # Match regular expression to input
    if not (re.match(r'^' + domain_regex + r'$', domain.lower()) is None):
        return True

    return False


def is_email_localpart(localpart: str) -> bool:
    """Validates the local part of an email address."""

    # Make sure localpart is of proper type and specified
    if not localpart or type(localpart) is not str:
        return False

    # Define the local part regular expression
    localpart_regex = r"[a-z0-9!#\$%&'\*\+\-/=\?\^_`\{\|\}~]+" \
                      + r"([a-z0-9!#\$%&'\*\+\-/=\?\^_`\{\|\}~]+\.?)" \
                      + r"+[a-z0-9!#\$%&'\*\+\-/=\?\^_`\{\|\}~]+"

    # Match input to regex
    if not (re.match(r'^' + localpart_regex + r'$', localpart.lower()) is None):
        return True

    return False


def is_ip_address(ipaddress: str) -> bool:
    """Validates that the string is a valid IP address."""

    # Make sure ip address is of proper type
    if not ipaddress or type(ipaddress) is not str:
        return False

    # Define ip address regular expression
    ipaddress_regex = r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'

    # Match regular expression
    if not (re.match(r'^' + ipaddress_regex + r'$', ipaddress.lower()) is None):
        return True

    return False


def is_valid_namespace_email(email: str, namespace: str) -> bool:
    """Makes sure email is valid and has provided namespace

    :param email: email address to check for namespace
    :param namespace: namespace of email address (gmail.com)
    :return: success value of validation
    """

    # Make sure email has a value and is string
    if not email or type(email) is not str:
        if VERBOSE:  # pragma: no cover
            logger.warning('Email type is expected to be string!')
        return False

    # Make sure namespace has a value and is string
    if not namespace or type(namespace) is not str:
        if VERBOSE:  # pragma: no cover
            logger.warning('Namespace type is expected to be string!')
        return False

    # Check that the namespace is valid
    if not re.match(r'^[a-z0-9]+(\.[a-z0-9\-]+)*$', namespace.lower()):
        if VERBOSE:  # pragma: no cover
            logger.info('Namespace validation failed!')
        return False

    # Check if regex matches lp email format
    if re.match(
        r'^[a-z]+(\.?[a-z0-9_])*[a-z0-9]+@' + re.escape(namespace.lower()) +
        r'\.[a-z]{2,3}(\.([a-z]{2,3}))?$', email.lower(),
    ):
        return True

    # Otherwise regex didn't match
    return False
