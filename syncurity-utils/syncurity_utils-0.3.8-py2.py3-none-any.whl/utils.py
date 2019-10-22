""" syncurity_utils.utils

This module provides static utility functions - these are the functions in the irflow_integrations.utils module in the
current integrations framework, tuned to be used from this module.

Examples:
    The following function calls require this import statement at the top of the Python file::

        from irflow_integrations import utils

    Setting up logging configurations::

        response = utils.setup_logging()

    Getting a fact group ID::

        id = utils.get_fact_group_id(<IRFlowClient>, <alert_num>, '<description>')

    Retrieving a Fully Qualified Domain Name (FQDN)::

        fqdn = utils.find_domain('<domain>')

    This function can be passed any string that may be either an email address, domain, fully qualified domain,
    or URL, and will return either the FQDN, Domain or Hostname if found. This function is not guaranteed to
    function just as the navigation bar in a browser would, but some assumptions will be made to parse a domain from
    otherwise malformed values. For example, values that are meant as urls that do not contain a protocol (i.e.,
    domains that contain paths or other URI-like elements) will be successfully parsed. URLs that do not have
    a trailing forward slash before query/parameter data will also be successfully parsed.

        >>> from irflow_integrations.utils import find_domain
        >>> find_domain('test@syncurity.net')
        'syncurity.net'
        >>> find_domain('https://google.com/')
        'google.com'
        >>> find_domain('https://docs.google.com/')
        'docs.google.com'
        >>> find_domain('https://docs.google.com/', only_domain=True)
        'google.com'
        >>> find_domain('https://docs.google.com/', only_hostname=True)
        'docs'
        >>> find_domain('google.com/docs')
        'google.com'
        >>> find_domain('http://google.com?q=some_query')
        'google.com'
        >>> find_domain('test.syncurity.net')
        'test.syncurity.net'
        >>> find_domain('test.syncurity.net', only_domain=True)
        'syncurity.net'
        >>> find_domain('test.syncurity.net', only_hostname=True)
        'test'

    Submitting to IR-Flow::

        response = utils.submit_to_irflow(<IRFlowClient>, <fact_group_id>, <fact_data>)

    Getting a list of image extensions::

        file_extensions = utils.FileExtensions()
        image_extensions = file_extensions.IMAGE_EXTENSIONS

    Decoding a Proofpoint URL::

        decoded = utils.DecodeProofpointURL('<URL>')
        url = decoded.url

    Decodes Proofpoint rewritten URLs modified from
    `help.proofpoint.com <https://help.proofpoint.com/Threat_Insight_Dashboard/Concepts/How_do_I_decode_a_rewritten_URL%3F>`_
    and then modified from `this github link <https://github.com/tunisj/urldecode/blob/master/proofpointurldecode.py>`_
    for py2 support due to Flanker

:copyright: (c) 2019 Syncurity
:license: Apache 2.0, see LICENSE.txt for more details
"""

import json
import validators
import logging
import logging.config
import sys
import os
import re

__all__ = ['find_domain', 'get_fact_group_id', 'setup_logging', 'DecodeProofpointURL']

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

try:
    from urllib.parse import parse_qs, urlparse
    attempt_compat = False
except ImportError:
    if sys.version_info[0] < 3:
        logger.error('This utilities package is intended for python3 only')
        attempt_compat = True
        from urlparse import parse_qs, urlparse


def setup_logging(default_path=None,
                  default_level=logging.INFO,
                  env_key='LOG_CFG'):
    """Setup logging configuration

    Args:
        default_path (str): Default path to use for the logging configuration file
        default_level (int): Default logging level
        env_key (str): Environment variable name to search for, for setting logfile path

    Returns:
        bool: True if the configuration file was found and applied, False otherwise
    """
    # Find logging.json if not provided
    if default_path:
        default_path = default_path
    else:
        default_path = '/home/irflow/irflow-integrations/integrations/logging.json'

    paths = [
        default_path,
        'logging.json',
        '../logging.json',
        '../../logging.json',
        '../integrations/logging.json',
        'integrations/logging.json'
    ]

    path = None

    for config_path in paths:
        if os.path.exists(config_path):
            path = config_path
            break

    if path is None:
        print('Unable to find logging.json configuration file')
        print('Make sure a valid logging configuration file is referenced in the default_path argument or available at '
              'one of the following file-paths:')
        print(str(paths[1:]))
        logging.basicConfig(level=default_level)
        logger.warning('The IR-Flow logging configuration was not found - using a basic configuration.'
                       'Please check the integrations directory for "logging.json".')
        return False

    value = os.getenv(env_key, None)
    if value and os.path.exists(value):
        path = value

    with open(path, 'rt') as f:
        config = json.load(f)

    try:
        logging.config.dictConfig(config)
    except ValueError as e:
        print('Failed to find file - make sure your integrations log file is properly configured')
        print(e)

    return True


def get_fact_group_id(irflow_client, alert_num, description):
    """Helper function to return the fact_group_id of a step on an alert whose description matches exactly with the
        description provided.

    Args:
        irflow_client (IRFlowClient): Instance of irflow_client
        alert_num (int): The IR-Flow Assigned Alert Number corresponding to the alert whose steps to check
        description (str): The exact description of the desired step

    Returns:
        int: Fact group ID if a matching fact group was found, ``None`` otherwise
    """
    alert = irflow_client.get_alert(alert_num)

    # response = irflow_client.get_version()
    response = '4.5'
    if response is None:
        logger.warning('Unable to get IR-Flow version - continuing')
    else:
        logger.debug('Detected IR-Flow server version: ' + response)

        version = response.split('.')
        if int(version[0]) > 4 or (int(version[0]) == 4 and int(version[1]) >= 5):
            logger.warning('Syncurity IR-Flow: Getting fact group ID from alerts discouraged in v4.6+.'
                           'Will be deprecated in a future release')

    fact_group_id = None
    if 'errors' not in alert['data']:
        for playbook in alert['data']['alert']['playbooks']:
            for task in playbook['tasks']:
                for step in task['steps']:
                    if step['description'] == description:
                        fact_group_id = step['fact_group_id']
                        break
    else:
        logger.error('Query to IR-Flow returned errors')
        logger.error(json.dumps(alert['data']['errors']))

    return fact_group_id


def find_domain(target, only_domain=False, only_hostname=False):
    """Utility to extract a fully qualified domain from a string that may contain a domain name

    Args:
        target (str): The string that may contain a domain
        only_domain (bool): Optional - return only the domain name of a FQDN
        only_hostname (bool): Optional - return only the hostname in an FQDN

    Raises:
        TypeError: If the value passed as ``target`` is not of type ``str``
        ValueError: If both ``only_domain`` and ``only_hostname`` are found to be ``True``
        ValueError: If ``only_hostname`` is passed as ``True`` for a target that is not an FQDN
            e.g. target is an email address
    Returns:
        str: The domain, if found
    """

    def _parse_from_email(email):
        """ Hidden inner function to perform parsing from values determined to be email addresses """
        # only_domain option ignored in email parsing
        if only_hostname:
            raise ValueError('The value provided ({}) was an email address, no hostname can be returned'.format(email))
        return email.split('@')[1]

    def _parse_from_domain(domain):
        """ Hidden inner function to perform parsing from values determined to be existing domains """
        if only_domain:
            return '.'.join(domain.split('.')[-2:])
        if only_hostname:
            # only return hostname if a hostname is present (len('hostname.domain.tld'.split('.')) will return 3)
            if len(domain.split('.')) >= 3:
                return '.'.join(domain.split('.')[:-2])
            else:
                raise ValueError('The domain provided ({}) was not an FQDN'.format(domain))
        return domain

    def _parse_from_url(url):
        """ Hidden inner function to perform parsing from values determined to be URLs """
        fqdn = url.split('://')[1].split('/')[0].split('?')[0]
        if only_domain:
            return '.'.join(fqdn.split('.')[-2:])
        if only_hostname:
            if len(fqdn.split('.')) >= 3:
                return '.'.join(fqdn.split('.')[:-2])
            else:
                raise ValueError('The URL provided ({}) did not contain an FQDN'.format(url))
        return fqdn

    if not isinstance(target, str):
        raise TypeError('Value provided was of type {}, must be of type str'.format(type(target)))
    if only_domain and only_hostname:
        raise ValueError('The \'only_domain\' and \'only_hostname\' optional arguments are mutually exclusive, only one'
                         ' should be evaluated to True')
    if validators.email(target):
        return _parse_from_email(target)
    if validators.domain(target):
        return _parse_from_domain(target)
    if validators.url(target):
        return _parse_from_url(target)

    # No validation succeeded, attempt once more prepended with a protocol and try to parse as url
    #
    # This is useful in the case that someone passes something like google.com/images, which is not a proper domain or
    # url without the protocol
    protocol_target = 'http://{}'.format(target)

    if validators.url(protocol_target):
        logger.info('Provided value appears to be url without protocol - assuming form \'{}\''.format(protocol_target))
        return _parse_from_url(protocol_target)

    raise ValueError('The value provided ({}) was not an email address, domain, fully qualified domain name, '
                     'or URL'.format(target))


class DecodeProofpointURL(object):
    """Decodes Proofpoint rewritten URLs

    Args:
        url(str): Encoded Proofpoint URL

    Attributes:
        self.pplink (str): The endcoded Proofpoint URL
        self.arguments (dict): Parse a query string given as a string argument
            (data of type application/x-www-form-urlencoded)
        self.url (str): The decoded Proofpoint URL
    """

    def __init__(self, url):
        if attempt_compat:
            logger.error('This class\' functionality is python3 only')
        else:
            self.pplink = url
            self.arguments = parse_qs(urlparse(url).query)
            self.url = self._decodeurl()
            self._parse()

    def _decodeurl(self):
        """Private Method to decode URL

        Returns:
            str: If the URL could be decoded, ``None`` otherwise
        """
        try:
            tmp = self.arguments['u'][0].replace("_", "/")
            for x in list(set(re.findall('-[0-9A-F]{2,2}', tmp))):
                tmp = tmp.replace(x, chr(int(x[1:3], 16)))
            return tmp
        # If KeyError then not a rewritten URL
        except KeyError:
            return None

    def _parse(self):
        """Private method to decode ``recipient`` and ``site``

        Attributes:
            self.recipient (str): The ``recipient`` in ``self.arguments``
            self.site (str): The ``site`` in ``self.arguments``
        """
        if 'r' in self.arguments:
            self.recipient = self.arguments['r'][0]
        if 'c' in self.arguments:
            self.site = self.arguments['c'][0]
