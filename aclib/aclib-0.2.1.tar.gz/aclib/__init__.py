import os
import logging
from sqlalchemy import engine_from_config
from configparser import ConfigParser
import re

logger = logging.getLogger()


def get_dbpath():
    path_filename = os.getenv("ACLIB_DBPATH_FILE", "/lifecycle/.dbpath")
    if not os.path.exists(path_filename):
        logger.debug(f"Could not find dbpath file {path_filename}")
        return None, None
    with open(path_filename, 'r') as path_file:
        lines = path_file.readlines()
        if len(lines) == 0:
            logger.warning(f"Could not parse dbpath file: {path_filename} is empty")
            return None, None
        first_line = lines[0]
        # Remove end of line character
        first_line = re.sub('`\n', '', first_line)
        # Split at "." character
        # This should have resulted in two substrings
        split_arr = re.split("\".\"", first_line)
        if len(split_arr) != 2:
            logger.warning(
                f"Could not parse dbpath file: pattern \".\" not found in {path_filename}. Are the names escaped with double quotes?")
            return None, None
        # Split removes the two quotes
        db_name = split_arr[0] + "\""
        schema_name = "\"" + split_arr[1]
        logger.debug(f"Found database = {db_name}, schema = {schema_name} in dbpath file {path_filename}")

        return db_name, schema_name


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
    app_db_name, app_schema_name = get_dbpath()
    db_name = db_name or app_db_name
    schema_name = schema_name or app_schema_name
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
