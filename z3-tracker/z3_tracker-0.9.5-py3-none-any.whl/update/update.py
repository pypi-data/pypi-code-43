'''
Update checker
'''

import http.client
import json

from .. import version

__all__ = 'check_update_availability',


def check_update_availability() -> str:
    '''
    Check whether update is available.

    Returns:
        str: version string if update is available, else False
    '''

    print('Current version is {0:s}.'.format(version.__version__))
    print('Checking for updates ...')
    request = http.client.HTTPSConnection('pypi.org')
    request.request('GET', '/pypi/z3-tracker/json')
    try:
        ret = request.getresponse()
    except http.client.HTTPException as err:
        print('   ... failed. Got: {0:s}'.format(str(err)))
        return False
    if ret.status != 200:
        print('   ... failed. Got: {0:d}-{1:s}'.format(
            ret.status, ret.reason))
        return False
    ret = ret.read()
    try:
        ret = ret.decode()
    except UnicodeError as err:
        print('   ... failed. Got: {0:s}'.format(str(err)))
        return False
    try:
        ret = json.loads(ret)
    except json.JSONDecoder as err:
        print('   ... failed. Got: {0:s}'.format(str(err)))
        return False
    try:
        newest = ret['info']['version']
    except KeyError:
        print('   ... failed. Could not find any version information.')
        return False
    print('   ... done.')
    if newest > version.__version__:
        print('Found newer version: {0:s}'.format(newest))
        return newest
    print('No newer version found.')
    return False
