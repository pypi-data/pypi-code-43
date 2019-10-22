""" syncurity_utils.api

This file contains functions that will provide some ORM-like functionality to the IR-Flow SDK

:copyright: (c) 2019 Syncurity
:license: Apache 2.0, see LICENSE.txt for more details
"""

import logging
from irflow_client import IRFlowClient

from .exceptions import SubmissionError

logger = logging.getLogger(__name__)

__all__ = ['send_facts']


def send_facts(fact_group_id, fact_data, client=None, address=None, api_user=None, api_key=None):
    """ Send a fact group into a fact_group_id in IR-Flow, handle the response, and return
    accordingly

    Args:
        fact_group_id (int): The IR-Flow assigned ID of the fact group to which the provided facts
         will be submitted
        fact_data (dict): key, value pairs of facts to submit
        client (irflow_client.IRFlowClient): A pre-existing client object
        address (str): The IP address or hostname of an IR-Flow instance
        api_user (str): The username of a user with API permissions
        api_key (str): The generated api key for the provided user

    Raises:
        RuntimeError: If a client is not provided, and one could not be constructed
        SubmissionError: If the fact data was not successfully submitted to IR-Flow
    Returns:
        dict: The full JSON response from the API call, if successful
    """
    if client is None:
        logger.error('No client was provided - attempting to build from parameters')
        if address is None or api_user is None or api_key is None:
            logger.error('Unable to construct an API client')
            raise RuntimeError('Could not construct an API client due to missing parameters')

        config_args = {
            'address': address,
            'api_user': api_user,
            'api_key': api_key,
            'protocol': 'https',
            'debug': False,
            'verbose_level': 0,
        }
        irfc = IRFlowClient(config_args=config_args)
    else:
        irfc = client

    response = irfc.put_fact_group(fact_group_id, fact_data)

    if not response['success']:
        logger.error('Unable to submit to IR-Flow: {}'.format(response['message']))
        errors = response['data'].get('errors', [])

        buff = 'Error Summary:\n'
        for error in errors:
            buff += '\t{}'.format(error['messages'])

        logger.debug(buff)

        raise SubmissionError('Could not submit facts to the fact group with id {}'
                              .format(fact_group_id))
    else:
        return response
