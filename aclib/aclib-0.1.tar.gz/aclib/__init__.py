import os
import logging
from sqlalchemy import engine_from_config
from configparser import ConfigParser

logger = logging.getLogger()


def get_engine(db_name, schema_name):
    credential_filename = os.getenv("ACLIB_CREDENTIAL_FILENAME", os.path.expanduser("~") + "/.odbc.ini")
    credential_section = os.getenv("ACLIB_CREDENTIAL_SECTION", "datahub")
    # Create engine with credentials
    cred = ConfigParser(interpolation=None)
    if not os.path.exists(credential_filename):
        raise FileNotFoundError(f"Credentials file {credential_filename} not found")
    cred.read(credential_filename)
    credd = dict(cred.items(credential_section))
    snowflake_host = credd.get('host', "alphacruncher.eu-central-1")
    config_dict = {}
    config_dict['sqlalchemy.url'] = 'snowflake://' + credd['uid'] + ':' + credd['pwd'] + \
                                    '@' + snowflake_host + '/?warehouse=' + credd['uid'] + \
                                    '&database=' + db_name + '&schema=' + schema_name
    config_dict['sqlalchemy.echo'] = False
    logger.info('Connecting to ' + 'snowflake://' + credd['uid'] + ':*************' +
                '@' + snowflake_host + '/?warehouse=' + credd['uid'] +
                '&database=' + db_name + '&schema=' + schema_name)

    return engine_from_config(config_dict)

