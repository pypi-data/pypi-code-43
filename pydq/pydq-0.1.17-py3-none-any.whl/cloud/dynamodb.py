from pydq import _queue, TIME_FORMAT

import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
from time import sleep
from decimal import Decimal
from collections import deque
from itertools import islice


class DynamoDB(_queue):
    def __init__(self, name):
        name = name.replace(' ', '.')
        super().__init__(name)
        self.table = boto3.resource('dynamodb').Table(self.name)
        try:
            desc = self.table.load()
            if desc['TableDescription']['TableStatus'] != 'ACTIVE':
                raise Exception('Table %s not ready' % self.name)
        except Exception as e:
            if 'ResourceNotFoundException' in str(e):
                self.table = self._create_table()

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.table.batch_writer() as writer:
            for txn in self.get_log():
                action, qitem = txn
                if isinstance(qitem['val'], float):
                    qitem['val'] = Decimal(qitem['val'])
                if action == self.CREATE:
                    writer.put_item(Item=qitem)
                elif action == self.DELETE:
                    del (qitem['val'])
                    self.table.delete_item(Key=qitem)

    def __call__(self, qid=None, start_time=None, end_time=None, limit=0):
        start_time = datetime(1, 1, 1) if start_time is None else start_time
        end_time = datetime.utcnow() if end_time is None else end_time
        kwargs = {
            'Select': 'ALL_ATTRIBUTES',
            'ConsistentRead': True
        }
        table_operation = self.table.query
        if qid is not None:
            kwargs['KeyConditionExpression'] = Key('qid').eq(qid) & Key('ts').between(start_time.strftime(TIME_FORMAT),
                                                                                      end_time.strftime(TIME_FORMAT))
            kwargs['ScanIndexForward'] = False
            if limit > 0:
                # only add limit for queries since scans can't be in descending order
                kwargs['Limit'] = int(limit)
        else:
            kwargs['FilterExpression'] = Attr('ts').between(start_time.strftime(TIME_FORMAT),
                                                            end_time.strftime(TIME_FORMAT))
            table_operation = self.table.scan
        response = table_operation(**kwargs)
        with self.mutex:
            self.queue.extend(response['Items'])
        lek = response['LastEvaluatedKey'] if 'LastEvaluatedKey' in response else None
        while lek is not None:
            kwargs['ExclusiveStartKey'] = lek
            response = table_operation(**kwargs)
            with self.mutex:
                self.queue.extend(response['Items'])
            lek = response['LastEvaluatedKey'] if 'LastEvaluatedKey' in response else None
        with self.mutex:
            self.queue = deque(sorted(self.queue, key=lambda i: i['ts'], reverse=True))
            if 0 < limit < len(self.queue):
                # scans can't do descending order, so we have to get everything, reverse the order, then chop if off
                self.queue = deque(islice(self.queue, 0, limit))
            for item in self.queue:
                if isinstance(item['val'], Decimal):
                    item['val'] = float(item['val'])
        return self

    @staticmethod
    def list_all():
        client = boto3.client('dynamodb')
        resp = client.list_tables()
        tables = resp['TableNames']
        while 'LastEvaluatedTableName' in resp:
            resp = client.list_tables(ExclusiveStartTableName=resp['LastEvaluatedTableName'])
            tables.extend(resp['Tables'])
        return [t.replace('.', ' ') for t in tables]

    def _create_table(self):
        client = boto3.client('dynamodb')
        client.create_table(TableName=self.name, AttributeDefinitions=[
            {'AttributeName': 'qid', 'AttributeType': 'S'},
            {'AttributeName': 'ts', 'AttributeType': 'S'}
        ], KeySchema=[
            {'AttributeName': 'qid', 'KeyType': 'HASH'},
            {'AttributeName': 'ts', 'KeyType': 'RANGE'}
        ], BillingMode='PAY_PER_REQUEST')
        while True:
            sleep(0.2)
            resp = client.describe_table(TableName=self.name)
            if resp['Table']['TableStatus'] == 'ACTIVE':
                break
        return boto3.resource('dynamodb').Table(self.name)
