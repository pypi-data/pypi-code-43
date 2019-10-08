from dotenv import load_dotenv

load_dotenv()

import os

try:
    from types import SimpleNamespace
except:
    from argparse import Namespace as SimpleNamespace

settings = SimpleNamespace(
    ITK_DB_CODE1=os.getenv('ITK_DB_CODE1', ''),
    ITK_DB_CODE2=os.getenv('ITK_DB_CODE2', ''),
    AUTH_URL=os.getenv('AUTH_URL', 'https://oidc.plus4u.net/uu-oidcg01-main/0-0/'),
    SITE_URL=os.getenv('SITE_URL', 'https://itkpd-test.unicorncollege.cz/'),
    CASSETTE_LIBRARY_DIR=os.getenv(
        'CASSETTE_LIBRARY_DIR', 'tests/integration/cassettes'
    ),
)
