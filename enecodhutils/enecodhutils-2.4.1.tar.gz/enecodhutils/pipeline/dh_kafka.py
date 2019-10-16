"""
.. module:: dh_kafka
   :platform: Unix, Windows
   :synopsis: A module which contains the boiler plate methods to be used
   for producing data to Kafka.

.. moduleauthor:: Dharmateja Yarlagadda <dharmateja.yarlagadda@eneco.com>

"""

import os
import json
import hashlib
import logging
from datetime import datetime
from pykafka import KafkaClient
from pykafka.exceptions import KafkaException
from azure.storage.blob import BlockBlobService
from azure.common import AzureMissingResourceHttpError


def produce_msg_to_kafka(bootstrap_server, topic, message, hash_column=None):
    """
    Produce the input message to the given kafka topic.

    :param hash_column: Boolean to know if we need to generate uid or not.
    :type hash_column: Boolean
    :param message: JSON array containing the messages
    :type message: JSON String
    :param bootstrap_server: The location of the kafka bootstrap server
    :type bootstrap_server: String
    :param topic: The topic to which the message is produced
    :type topic: String
    :return: No return
    """
    logging.info('DH_Utils: Producing message to Kafka')
    container_name = topic.replace('_', '')
    blob_service = BlockBlobService(account_name=os.environ['KAFKA_FT_BLOB_ACCOUNT_NAME'],
                                    account_key=os.environ['KAFKA_FT_BLOB_ACCOUNT_KEY'])
    try:
        blob_service.list_blobs(container_name)
    except AzureMissingResourceHttpError:
        blob_service.create_container(container_name)
    blobs = blob_service.list_blobs(container_name)
    records = json.loads(message)
    if len(list(blobs)) > 0:
        logging.info('DH_Utils: Loading data from previous failed runs.')
        for blob in blobs:
            file_name = blob.name
            data = json.loads(blob_service.get_blob_to_text(container_name, file_name).content)
            records = records + data
            blob_service.delete_blob(container_name, file_name)
        logging.info('DH_Utils: Finished loading data from previous failed runs.')
    try:
        client = KafkaClient(bootstrap_server)
        topic = client.topics[topic.encode()]
        producer = topic.get_producer(sync=False, min_queued_messages=1)
        processed_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        for record in records:
            if hash_column:
                record.update({'uid': generate_hash(record),
                              'processed_time': processed_time})
            producer.produce(json.dumps(record).encode())
        logging.info('DH_Utils: Finished producing message to Kafka')
        producer.stop()
    except KafkaException:
        logging.info('DH_Utils: Kafka error: Loading data to blob storage.')
        blob_service.create_blob_from_text(container_name, container_name, json.dumps(records).encode())
        logging.info('DH_Utils: Kafka error: Finished loading data to blob storage.')
    except Exception as normal_err:
        raise Exception(normal_err)


def generate_partition_col(record_time):
    """
    Generate the partition column value based on the time.

    :param record_time: The datetime value for the record.
    :type record_time: String
    :return: partition_col: Integer
    """
    partition_col = int(datetime.strptime(record_time, "%Y-%m-%d %H:%M:%S").strftime('%m%d%H'))
    return partition_col


def generate_hash(record):
    """
    Generate a hash object for the record to maintain uniqueness.

    :param record: The json record for whose columns the hash has to be generated.
    :type record: Dictionary
    :return: hash_object: String
    """
    hash_string = json.dumps(record)
    hash_object = hashlib.md5(hash_string.encode()).hexdigest()
    return hash_object
