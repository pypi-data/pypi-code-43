import os
import logging
from sqlalchemy import engine_from_config
from configparser import ConfigParser

logger = logging.getLogger()


def get_url(db_name=None, schema_name=None):
    credential_filename = os.getenv("ACLIB_CREDENTIAL_FILENAME", os.path.expanduser("~") + "/.odbc.ini")
    credential_section = os.getenv("ACLIB_CREDENTIAL_SECTION", "datahub")
    # Create engine with credentials
    cred = ConfigParser(interpolation=None)
    if not os.path.exists(credential_filename):
        raise FileNotFoundError(f"Credentials file {credential_filename} not found")
    cred.read(credential_filename)
    credd = dict(cred.items(credential_section))
    snowflake_host = credd.get('host', "alphacruncher.eu-central-1")
    url = 'snowflake://' + credd['uid'] + ':' + credd['pwd'] + '@' + snowflake_host + '/?warehouse=' + credd['uid']
    masked_url = 'snowflake://' + credd['uid'] + ':********' + '@' + snowflake_host + '/?warehouse=' + credd['uid']
    if db_name:
        url = url + '&database=' + db_name
        masked_url = masked_url + '&database=' + db_name
        if schema_name:
            url = url + '&schema=' + schema_name
            masked_url = masked_url + '&schema=' + schema_name
    logger.info('Built SQLAlchemy URL: ' + masked_url)
    return url


def get_engine(db_name, schema_name):
    return engine_from_config({'sqlalchemy.url': get_url(db_name, schema_name), 'sqlalchemy.echo': False})

