"""Utils used in the dbispipeline implementation."""
from email.mime.text import MIMEText
from os.path import basename
from os.path import splitext
import configparser
import datetime
import json
import logging
import numpy as np
import os
import pickle
import platform
import smtplib
import traceback

from . import store

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(name)-16s %(message)s',
    level=logging.INFO,
)
LOGGER = logging.getLogger('dbispipeline')


def load_project_config():
    """Loads the project configuration."""
    config_files = ['/usr/local/etc/dbispipeline.ini']
    user_home = os.getenv('HOME')
    if user_home:
        config_files.append(user_home + '/.config/dbispipeline.ini')
    config_files.append('dbispipeline.ini')
    config = configparser.ConfigParser()

    if os.getenv("DBISPIPELINE_ENV") == "ci":
        # Sets default values if the environment is a ci
        config.read_dict({
            'database': {
                'host': 'postgres',
                'port': 5432,
                'user': 'runner',
                'password': 'runner_password',
                'database': 'pipelineresults',
            },
        })
        LOGGER.debug(f'detected CI environment')

    parsed_files = config.read(config_files)
    LOGGER.debug(f'loaded configuration from files: {parsed_files}')

    if not config.has_section('database'):
        raise KeyError('no database section found in the configuration')

    return config


def prefix_path(path, default_prefix=None):
    """
    Returns the path prefixed with the pipeline global path prefix.

    Args:
        path: that has to be prefixed.
        default_prefix: used if the pipelines path_prefix is not set.
    """
    if store.get('path_prefix', None):
        return os.path.join(store['path_prefix'], path)
    else:
        if default_prefix:
            return os.path.join(default_prefix, path)
        else:
            raise ValueError('path_prefix of the pipeline store is not set.')


def load_result_backup(path):
    """
    Loads results from a pickle backup.

    Args:
        path: to the backup file.
    """
    with open(path, 'rb') as f:
        return pickle.load(f)


def restore_backup(path, output_handlers):
    """
    Reads a backup file and handles it with the given handlers.

    Args:
        path: to the backup file.
        output_handlers: an iterable containing output handlers
    """
    backup = load_result_backup(path)

    for handler in output_handlers:
        handler.handle_result(backup)


def store_prediction(model, dataloader, file_name_prefix=None):
    if not file_name_prefix:
        file_name_prefix = type(model).__name__

    if store['config_path']:
        if file_name_prefix[-1] != '_':
            file_name_prefix += '_'
        file_name_prefix += splitext(basename(store['config_path']))[0]

    if file_name_prefix[-1] != '_':
        file_name_prefix += '_'

    x_test, _ = dataloader.load_test()

    try:
        y_pred = model.predict(x_test)
        np.save(file_name_prefix + 'predict.npy', y_pred)
    except AttributeError:
        LOGGER.warning('Model does not support predict.')

    try:
        y_pred = model.predict_proba(x_test)
        np.save(file_name_prefix + 'predict_proba.npy', y_pred)
    except AttributeError:
        LOGGER.warning('Model does not support predict_proba.')


def notify_success(configuration_name,
                   times,
                   result=None,
                   run=None,
                   subject='DBIS Pipeline: successfully finished',
                   loader_config=None):
    run_string = ''
    if run is not None:
        run_string = f' run #{run}'

    result_string = 'The results are available in the database.'
    if result and isinstance(result, dict) or isinstance(result, str):
        try:
            pretty_printed_json = json.dumps(result, indent=2, sort_keys=True)
            result_string = f'Your results are:\n\n{pretty_printed_json}'
        except Exception:
            LOGGER.warn('could not write result as pretty json string')
            pass
    computer_name = platform.node()
    duration = datetime.timedelta(seconds=int(times['eval'] - times['start']))
    message = f'''\
Hello,
your configuration file {configuration_name} running on {computer_name}\
        has finished{run_string}.
The calculation took {duration}.'''

    if loader_config:
        message += f'''
The configuration of the dataloader was:
    {loader_config}'''

    message += '\n' + result_string

    _notify(message, subject)


def notify_error(configuration_name,
                 error_stage,
                 error_object,
                 subject='DBIS Pipeline: error',
                 run=None,
                 loader_config=None):
    run_string = ''
    if run is not None:
        run_string = f' on run #{run}'
    message = f'''Hello,
unfortunately, your configuration file {configuration_name} caused an error on
the pipeline running on {platform.node()} during {error_stage}{run_string}.
'''
    if loader_config:
        message += f'''
The configuration of the dataloader was:
    {loader_config}'''

    if error_object:
        message += f'''
The error message is:
    {traceback.format_tb(error_object.__traceback__)}'''

    _notify(message, subject)


def _notify(message, subject):
    cfg = load_project_config()
    if 'mail' not in cfg:
        LOGGER.debug(f'missing mail configuration: not sending success message'
                     ': {message}')
        return

    required_fields = ['recipient', 'sender', 'smtp_server']
    for field in required_fields:
        if field not in cfg['mail']:
            LOGGER.error(f'missing field in mail configuration: {field}')
            return

    # required
    recipient = cfg['mail']['recipient']
    sender = cfg['mail']['sender']
    host = cfg['mail']['smtp_server']

    LOGGER.info(f'sending mail to {recipient}')
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    if cfg['mail'].getboolean('authenticate', fallback=False):

        more_required_fields = ['username', 'password']
        for field in more_required_fields:
            if field not in cfg['mail']:
                LOGGER.error(f'missing field in mail configuration: {field}')
                return

        # optional
        usernam = cfg['mail']['username']
        password = cfg['mail']['password']
        port = cfg.getint('mail', 'port', fallback=465)
        s = smtplib.SMTP_SSL(host, port)
    else:
        s = smtplib.SMTP(host)

    s.sendmail(sender, [recipient], msg.as_string())
