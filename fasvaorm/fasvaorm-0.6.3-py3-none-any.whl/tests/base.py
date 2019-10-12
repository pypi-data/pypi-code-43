# check if running in gitlab-ci
import os
import unittest

from sqlalchemy.exc import IntegrityError

from fasvaorm import init_engine, init_session_factory, initialize_engine, get_engine
from fasvaorm.models import Base

host = os.environ.get('GITLAB_CI')

if host is None:
    # local testing
    host = '127.0.0.1'
    user = 'testing'
else:
    host = 'mysql'
    user = 'root'

TEST_DB_CONFIG = {
    'user': user,
    'host': host,
    'database': 'testing',
    'password': 'mysql'
}

DB_URL = url = "mysql+pymysql://{user}:{password}@{host}/{database}".format(**TEST_DB_CONFIG)


class EngineTestCase(unittest.TestCase):

    def setUp(self):

        self.engine = init_engine(DB_URL,
                                  # unlimited number of connections
                                  pool_size=0,
                                  # set connection timeout to 50 minutes
                                  pool_timeout=300)

        # create the test database
        initialize_engine(self.engine)

        self.session_factory = init_session_factory(self.engine)

    def tearDown(self):

        self.session_factory.close_all()

        try:
            Base.metadata.drop_all()
        except IntegrityError as err:

            get_engine().connect().execute("DROP DATABASE {}".format(TEST_DB_CONFIG['database']))
