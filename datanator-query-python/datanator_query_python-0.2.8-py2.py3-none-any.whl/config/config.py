from dotenv import load_dotenv
from pathlib import Path, PurePath
import os

home_path = PurePath(Path.home(), '.wc/datanator.env')
root_path = "/.wc/danatator.env"
if os.path.exists(home_path):
    dotenv_path = home_path
else:
    dotenv_path = root_path

load_dotenv(dotenv_path)


class Config:
    '''
        API for frontend with read permission to 'datanator'
    '''
    PRODUCTION = os.getenv("PRODUCTION", False)
    USERNAME = os.getenv("MONGO_USERNAME")
    PASSWORD = os.getenv("MONGO_PASSWORD")
    SERVER = os.getenv("MONGO_DATANATOR_SERVER")
    PORT = os.getenv("MONGO_PORT")
    REPLSET = os.getenv("MONGO_REPL")
    AUTHDB = os.getenv("MONGO_AUTHDB")
    SESSION_KEY = os.getenv("FLASK_SESSION_KEY")
    READ_PREFERENCE = os.getenv("READ_PREFERENCE")

class ProductionConfig(Config):

    PRODUCTION = True

class TestConfig(Config):
    '''
        test user with read permission to 'datanator' and
        readWrite permission to 'test'
    '''
    MONGO_TEST_USERNAME = os.getenv("MONGO_TEST_USERNAME")
    MONGO_TEST_PASSWORD = os.getenv("MONGO_TEST_PASSWORD")
    MONGO_TEST_PASSWORD_READ_PREFERENCE = os.getenv("MONGO_TEST_PASSWORD_READ_PREFERENCE")

class UserAccountConfig(Config):
    '''
        API user account manager with readWrite permission
        to 'registered_users'
    '''

    USERDAEMON = os.getenv("MONGO_USER_DAMON")
    USERDAEMON_PASSWORD = os.getenv("MONGO_USER_PASSWORD")
    USERDAEMON_AUTHDB = os.getenv("MONGO_USER_AUTHDB")


class FlaskProfiler(UserAccountConfig):
    '''
        API performance tracker with readWrite permission
        to 'flask_profiler'
    '''
    url = ('mongodb://' + os.getenv("MONGO_AP_USER") + ':' + os.getenv("MONGO_AP_PASSWORD")
           + '@' + os.getenv("MONGO_DATANATOR_SERVER") + '/?readPreference=' + os.getenv('READ_PREFERENCE'))
    FLASKPROFILER = {
        "enabled": True,
        "storage": {
            "engine": "mongodb",
            "MONGO_URL": url,
            "DATABASE": 'flask_profiler',
            "COLLECTION": 'measurements'
        },
        "basicAuth": {
            "enabled": True,
            "username": os.getenv("MONGO_AP_USER"),
            "password": os.getenv("FLASK_PROFILER_PASSWORD")
        },
        "ignore": [
            "^/static/.*"
        ],
        "endpointRoot": "performance"
    }
