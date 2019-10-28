import pytest

from bluejay.backend.sns import SNSBackend

try:
    import boto3
    from botocore.stub import Stubber

    has_boto3 = True
except ImportError:
    has_boto3 = False


@pytest.fixture(scope="function", autouse=has_boto3)
def sns_stub(sns_client):
    with Stubber(sns_client) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()


@pytest.fixture(scope="function")
def sns_client(aws_region):
    return boto3.client("sns", region_name=aws_region)


@pytest.fixture
def aws_region():
    return "eu-west-1"


@pytest.fixture
def topic_arn(faker):
    account_id = faker.pyint()
    topic_name = faker.pystr()
    return "arn:aws:sns:eu-west-1:{account_id}:{topic_name}".format(
        account_id=account_id, topic_name=topic_name
    )


@pytest.fixture
def backend(sns_client, topic_arn):
    return SNSBackend(client=sns_client, topic_arn=topic_arn)
