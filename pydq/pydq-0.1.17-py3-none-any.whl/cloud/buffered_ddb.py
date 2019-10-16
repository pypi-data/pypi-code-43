from pydq import _queue, TIME_FORMAT

import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
from time import sleep
import json


class BufferedDDB(_queue):
    def __init__(self, name):
        super().__init__(name)
        self.table = boto3.resource('dynamodb').Table(self.name)
        try:
            desc = self.table.load()
            if desc['TableDescription']['TableStatus'] != 'ACTIVE':
                raise Exception('Table %s not ready' % self.name)
            self.buffer_queue = boto3.resource('sqs').get_queue_by_name(self.name)
        except Exception as e:
            if 'ResourceNotFoundException' in str(e):
                self.table = self._create_table()
                self.buffer_queue = self._create_buffer_queue()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            with self.table.batch_writer() as writer:
                for txn in self.get_log():
                    action, qitem = txn
                    if action == self.CREATE:
                        writer.put_item(Item=qitem)
                    elif action == self.DELETE:
                        del (qitem['val'])
                        self.table.delete_item(Key=qitem)
        except Exception as e:
            if 'ProvisionedThroughputExceededException' in str(e):
                # If we can't save it try writing to the buffer queue
                try:
                    for action, qitem in self.get_log():
                        if action == self.CREATE:
                            self.buffer_queue.send_message(MessageBody=json.dumps(qitem))
                except:
                    pass

    def __call__(self, qid=None, start_time=None, end_time=None, limit=0):
        start_time = datetime(1, 1, 1) if start_time is None else start_time
        end_time = datetime.utcnow() if end_time is None else end_time
        kwargs = {
            'Select': 'ALL_ATTRIBUTES',
            'KeyConditionExpression': Key('ts').between(start_time.strftime(TIME_FORMAT),
                                                        end_time.strftime(TIME_FORMAT)),
            'ConsistentRead': True,
            'ScanIndexForward': False
        }
        if qid is not None:
            kwargs['KeyConditionExpression'] &= Key('qid').eq(qid)
        if limit > 0:
            kwargs['Limit'] = int(limit)
        response = self.table.query(**kwargs)
        with self.mutex:
            self.queue.extend(response['Items'])
        lek = response['LastEvaluatedKey'] if 'LastEvaluatedKey' in response else None
        while lek is not None:
            kwargs['ExclusiveStartKey'] = lek
            response = self.table.query(**kwargs)
            with self.mutex:
                self.queue.extend(response['Items'])
            lek = response['LastEvaluatedKey'] if 'LastEvaluatedKey' in response else None
        return self

    @staticmethod
    def list_all():
        client = boto3.client('dynamodb')
        resp = client.list_tables()
        tables = resp['TableNames']
        while 'LastEvaluatedTableName' in resp:
            resp = client.list_tables(ExclusiveStartTableName=resp['LastEvaluatedTableName'])
            tables.extend(resp['Tables'])
        return tables

    def _create_table(self):
        client = boto3.client('dynamodb')
        client.create_table(TableName=self.name, AttributeDefinitions=[
            {'AttributeName': 'qid', 'AttributeType': 'S'},
            {'AttributeName': 'ts', 'AttributeType': 'S'}
        ], KeySchema=[
            {'AttributeName': 'qid', 'KeyType': 'HASH'},
            {'AttributeName': 'ts', 'KeyType': 'RANGE'}
        ], ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        })
        while True:
            sleep(0.2)
            resp = client.describe_table(TableName=self.name)
            if resp['Table']['TableStatus'] == 'ACTIVE':
                break
        return boto3.resource('dynamodb').Table(self.name)

    def _create_buffer_queue(self):
        boto3.client('sqs').create_queue(QueueName=self.name)
        while True:
            sleep(0.2)
            try:
                return boto3.resource('sqs').get_queue_by_name(self.name)
            except:
                pass
