import json
import subprocess
import configparser
import time
import sys
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
import dateutil

from ..awsumepy.lib.aws_files import get_aws_files, delete_section
from ..awsumepy.lib import exceptions
from .. import awsumepy

logger = logging.getLogger('autoawsume') # type: logging.Logger


def main():
    configure_logger()

    logger.debug('Getting credentials file')
    _, credentials_file = get_aws_files(None, None)
    logger.debug('Credentials file: {}'.format(credentials_file))

    while True:
        logger.info('Scanning profiles')
        credentials = configparser.ConfigParser()
        credentials.read(credentials_file)
        auto_profiles = {k: dict(v) for k, v in credentials._sections.items() if k.startswith('autoawsume-')}

        expirations = []
        for profile_name, auto_profile in auto_profiles.items():
            logger.info('Looking at profile [{}]: {}'.format(profile_name, json.dumps(auto_profile, default=str)))
            expiration = datetime.strptime(auto_profile['expiration'], '%Y-%m-%d %H:%M:%S')
            source_expiration = datetime.strptime(auto_profile['source_expiration'], '%Y-%m-%d %H:%M:%S')
            if source_expiration < datetime.now():
                logger.debug('Source is expired')
                if expiration < datetime.now():
                    logger.debug('Role credentials are expired')
                    delete_profile(profile_name, credentials_file)
                else:
                    logger.debug('Role credentials are not expired')
                    expirations.append(expiration)
            else:
                logger.debug('Source credentials are not expired')
                if expiration < datetime.now():
                    logger.debug('Role credentials are expired')
                    session = refresh_profile(auto_profile)
                    if session:
                        logger.debug('Received session from awsume call')
                        expirations.append(session.awsume_credentials.get('Expiration'))
                    else:
                        logger.debug('No session returned from awsume call')
                        delete_profile(profile_name, credentials_file)
                else:
                    logger.debug('Role credentials are not expired')
                    expirations.append(expiration)
                    expirations.append(source_expiration)
        logger.debug('Collected expirations: {}'.format(json.dumps(expirations, default=str)))

        if not expirations:
            break

        local_expirations = [_.astimezone(dateutil.tz.tzlocal()) for _ in expirations]
        earliest_expiration = min(local_expirations)
        logger.debug('Earliest expiration: {}'.format(earliest_expiration))
        time_to_sleep = (earliest_expiration - datetime.now().replace(tzinfo=earliest_expiration.tzinfo)).total_seconds() + 60
        logger.debug('Time to sleep: {}'.format(time_to_sleep))
        time.sleep(time_to_sleep)

    logger.info('Finished autoawsume')


def configure_logger():
    log_dir = str(Path('~/.awsume/logs/').expanduser())
    log_file = str(Path('~/.awsume/logs/autoawsume-{}'.format(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))).expanduser())

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    if not os.path.isfile(log_file):
        open(log_file, 'a').close()

    log_handler = logging.FileHandler(log_file)
    log_handler.setFormatter(logging.Formatter('[%(asctime)s] %(filename)s:%(funcName)s : [%(levelname)s] %(message)s'))
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)


def refresh_profile(auto_profile):
    logger.debug('Refreshing profile {}'.format(json.dumps(auto_profile, default=str)))
    try:
        session = awsumepy.awsume(*auto_profile.get('awsumepy_command').split(' '))
        return session
    except exceptions.AwsumeException:
        return None


def delete_profile(profile, credentials):
    logger.debug('Deleting profile [{}] from file: {}'.format(profile, credentials))
    delete_section(profile, credentials)
