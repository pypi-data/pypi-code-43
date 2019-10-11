import pytest
from pprint import pprint
import dataclasses
import builtins

@pytest.fixture(autouse=True, scope='session')
def extrabuiltins():
    builtins.__dict__['pprint'] = pprint
    builtins.__dict__['asdict'] = dataclasses.asdict
    builtins.__dict__['dcprint'] = lambda dc: pprint(asdict(dc))
    yield

@pytest.fixture
def last(history):
    return history[-1]

@pytest.fixture
def prelast(history):
    return history[-2]