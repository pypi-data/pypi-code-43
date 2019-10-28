import pytest
from faker import Factory as FakerFactory


@pytest.fixture(scope="session")
def faker():
    return FakerFactory.create(locale="en_GB")


@pytest.fixture(scope="function", autouse=True)
def stub_aws_credentials(monkeypatch):
    """Prevent accidentally firing off actual AWS commands
    
    This is a fail safe. All AWS calls should be stubbed already.
    """
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
