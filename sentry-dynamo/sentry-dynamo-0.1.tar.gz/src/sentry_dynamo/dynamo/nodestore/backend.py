"""
sentry_dynamo.dynamo.nodestore.backend
:copyright: (c) 2015 Flipboard
"""

import json

import boto3
from sentry.nodestore.base import NodeStorage


class DynamoNodeStorage(NodeStorage):
    """
    A DynamoDB-based backend for storing node data.

    AWS's boto3 library is used for communicating with dynamo.
    https://boto3.readthedocs.org/en/latest/reference/services/dynamodb.html

    Look at sentry.nodestore.base.NodeStorage for usage information
    """

    def __init__(
            self,
            region_name,
            aws_access_key_id,
            aws_secret_access_key,
            table_name,
            primary_key_name,
            use_consistent_reads=False):
        """
        Creates a new instance of DynamoNodeStorage and connects to the dynamo table

        :param region_name: the AWS region where the Dynamo table lives
        :param aws_access_key_id: aws access key id
        :param aws_secret_access_key: aws secret access key
        :param table_name: Dynamo table name
        :param primary_key_name: the primary key of the Dynamo table.
        :param use_consistent_reads: whether or not to use consistent reads when reading from Dynamo
        :return: a newly created DynamoNodeStorage instance
        """
        self.primary_key_name = primary_key_name
        self.data_key_name = 'data'
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key)
        # Lower level client for doing batch reads
        self.client = boto3.client(
            'dynamodb',
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key)
        self.table_name = table_name
        # Higher level client used for most operations
        self.table = self.dynamodb.Table(table_name)
        self.use_consistent_reads = use_consistent_reads
        super(DynamoNodeStorage, self).__init__()

    @staticmethod
    def _serialize_data(data):
        """Serializes the data to a string"""
        return json.dumps(data)

    @staticmethod
    def _deserialize_data(serialized_data):
        """Deserializes the data from a string"""
        return json.loads(serialized_data)

    def get(self, id):
        response = self.table.get_item(
            Key={self.primary_key_name: id},
            ConsistentRead=self.use_consistent_reads)
        if 'Item' in response:
            return self._deserialize_data(response['Item'][self.data_key_name])
        else:
            return None

    def get_multi(self, id_list):
        # For batch reading we have to use the more complicated lower-level dynamo client
        # https://boto3.readthedocs.org/en/latest/reference/services/dynamodb.html#DynamoDB.Client.batch_get_item
        keys = [{self.primary_key_name: {'S': id}} for id in id_list]
        response = self.client.batch_get_item(
            RequestItems={
                self.table_name: {
                    'Keys': keys,
                    'ConsistentRead': self.use_consistent_reads}})
        results_dict = dict.fromkeys(id_list)
        for result in response['Responses'][self.table_name]:
            results_dict[result[self.primary_key_name]['S']] = self._deserialize_data(
                result[self.data_key_name]['S'])
        return results_dict

    def set(self, id, data):
        self.table.put_item(
            Item={
                self.primary_key_name: id,
                self.data_key_name: self._serialize_data(data)})

    def set_multi(self, values):
        with self.table.batch_writer() as batch:
            for id, data in values.iteritems():
                batch.put_item(
                    Item={
                        self.primary_key_name: id,
                        self.data_key_name: self._serialize_data(data)})

    def delete(self, id):
        self.table.delete_item(Key={self.primary_key_name: id})

    def delete_multi(self, id_list):
        with self.table.batch_writer() as batch:
            for id in id_list:
                batch.delete_item(Key={self.primary_key_name: id})

    def cleanup(self, cutoff_timestamp):
        pass
