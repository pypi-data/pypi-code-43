import unittest, os, warnings, json
from cloudcms import CloudCMS

class AbstractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        warnings.filterwarnings('ignore')

        # Login as admin for testing
        with open('gitana.json') as f:
            config = json.load(f)
            config['username'] = 'admin'
            config['password'] = 'admin'

        client = CloudCMS()
        cls.platform = client.connect(**config)