from pydq import _queue, TIME_FORMAT

import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
from time import sleep


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
        if limit > 0:
            kwargs['Limit'] = int(limit)
        if qid is not None:
            kwargs['KeyConditionExpression'] = Key('qid').eq(qid) & Key('ts').between(start_time.strftime(TIME_FORMAT),
                                                                                      end_time.strftime(TIME_FORMAT))
            kwargs['ScanIndexForward'] = False
        else:
            kwargs['FilterExpression'] = Attr('ts').between(start_time.strftime(TIME_FORMAT),
                                                            end_time.strftime(TIME_FORMAT))
            table_operation = self.table.scan
        response = table_operation(**kwargs)
        with self.mutex:
            self.queue.extend(response['Items'])
        lek = response['LastEvaluatedKey'] if 'LastEvaluatedKey' in response else None
        while (limit == 0 or len(self.queue) < limit) and lek is not None:
            kwargs['ExclusiveStartKey'] = lek
            response = table_operation(**kwargs)
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
