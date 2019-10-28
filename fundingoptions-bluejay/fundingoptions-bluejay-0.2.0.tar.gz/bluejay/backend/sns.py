import gzip
from base64 import b64encode

from .command import SendEvent, SendResponse
from .encode import JSONEncoder


class SNSBackend:
    def __init__(self, client, topic_arn: str):
        self.client = client
        self.topic_arn = topic_arn

    @classmethod
    def build(cls, topic_arn: str) -> "SNSBackend":
        try:
            import boto3  # type: ignore
        except ImportError:
            raise NotImplemented("Boto3 is required to use the SNS Backend")
        client = boto3.client("sns")
        return cls(client, topic_arn)

    @classmethod
    def compress(cls, payload: str) -> str:
        compressed_payload = gzip.compress(payload.encode())
        b64_payload = b64encode(compressed_payload)
        return b64_payload.decode()

    def send(self, message: SendEvent) -> SendResponse:
        payload = JSONEncoder().encode(message.payload)
        compressed_payload = self.compress(payload)
        self.client.publish(
            TopicArn=self.topic_arn,
            MessageStructure="json",
            Subject=message.event_name,
            Message=compressed_payload,
        )
        return SendResponse(success=True)
