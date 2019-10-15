
import boto3
import os
import json
import logging

from enum import Enum

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ProperlyEvents(str, Enum):
    USER_CREATED = 'userCreated'
    STAGE_CHANGED_OFFER = 'stageChangedOffer'
    USER_ENTERED_ALL_OFFER_INFO = 'userEnteredAllOfferInfo'


STREAM_BY_STAGE = {
    'staging': 'staging-events-002',
    'prod': 'prod-events-002',
}


class EventBus:

    def __init__(self, kinesis=None):
        stage = os.environ.get('PROPERLY_STAGE', 'staging')
        self.kinesis = kinesis or boto3.client('kinesis')
        self.stream_name = STREAM_BY_STAGE.get(stage, STREAM_BY_STAGE['staging'])

    def send_event(self, properly_user_id: str, event_name: ProperlyEvents, data_block_name: str, data_block: dict):

        event_to_send = {
            'eventName': event_name,
            data_block_name: data_block
        }

        logger.info("event_to_send: {}".format(event_to_send))

        event_as_json = json.dumps(event_to_send)

        event_as_bytes = event_as_json.encode('utf-8')
        # bytes are base64 encoded inside the put_record call

        logger.info("event_as_bytes: {}".format(event_as_bytes))

        self.kinesis.put_record(
            StreamName=self.stream_name,
            Data=event_as_bytes,
            PartitionKey=properly_user_id
        )
