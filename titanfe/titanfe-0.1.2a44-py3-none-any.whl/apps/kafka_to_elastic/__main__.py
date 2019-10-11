#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""
Simple consumer bridge for piping Ujo Containers reveived from a
Kafka topic to and Elasticsearch index
"""

import logging
import pickle
import sys
from argparse import ArgumentParser
from datetime import datetime

from elasticsearch import Elasticsearch
from kafka import KafkaConsumer

logging.basicConfig(stream=sys.stdout, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("KafkaToElastic")  # pylint: disable=C0103
logger.level = logging.WARNING
# logger.level = logging.INFO

# pylint: disable=broad-except, logging-fstring-interpolation


def parse_arguments():
    """Parse arguments from commandline call

    Returns:
       A namespace object of the arguments
    """
    parser = ArgumentParser()

    parser.add_argument(
        "kafka",
        type=str,
        nargs="?",
        help="Source Kafka server in Name/IP:Port notation",
        # default="192.168.171.131:9092",
        default="10.14.0.23:9092",
    )

    parser.add_argument(
        "topics",
        type=str,
        nargs="?",
        help="Name of topics to read from e.g. 'Topic-One Topic-Two'",
        default="titanfe.metrics",
    )

    parser.add_argument(
        "elastic",
        type=str,
        nargs="?",
        help="Destination Elasticsearch node's Name or IP",
        default="10.14.0.21",
    )

    result = parser.parse_args()
    logger.info(result)
    return result


def connect_to_kafka(kafka_host, topics):
    """Connect to Kafka Server an subscribe to topics

    Args:
        kafka_host (str): kafka boot strap server as "<Host>[optional<:Port>]"
        topics (str): whitespace separated topics e.g. "Topic1 Topic2"

    Returns:
        KafkaConsumer: A connected kafka consumer
    """
    kafka = KafkaConsumer(
        bootstrap_servers=kafka_host,
        group_id="kafka_to_elastic",
        # auto_offset_reset="earliest",
        consumer_timeout_ms=1000,
    )
    kafka.subscribe(*topics.split())
    return kafka


def connect_to_elasticsearch(elastic_host):
    """Connect to Elasticsearch server

    Args:
        elastic_host (str): Destination Elasticsearch node's Name or IP

    Returns:
        Elasticsearch: An Elasticsearch connection Object
    """
    elastic = Elasticsearch(elastic_host, sniff_on_start=False, sniff_on_connection_fail=False)
    return elastic


def process_messages(kafka, elastic):
    """Process messages from subscribe kafka topics and forward to
    an Elasticsearch index.

    Args:
        kafka (KafkaConsumer): Kafka consumer object
        elastic (Elasticsearch): Elasticsearch connection object
    """
    msgcounter = 0
    for message in kafka:
        msgcounter += 1
        try:
            content = pickle.loads(message.value)
        except Exception:
            logger.warning(f"Failed to load: {message.value}", exc_info=True)
            continue

        forward_message(content, elastic)

        if msgcounter > 100:
            msgcounter = 0
            logger.warning("Still sending...")


def forward_message(content, elastic):
    """ Forward a message to elastic

    Args:
        content (dict): message content,
            required fields: "content_type" (maps elastic index) and "timestamp"
        elastic (Elasticsearch): Elasticsearch connection object
    """
    try:
        doc_type = content["content_type"]
        content["@timestamp"] = content.pop("timestamp")
    except Exception:
        logger.warning(
            f"missing required fields 'content_type'/'timestamp': {content}", exc_info=True
        )
        return

    index = f"{doc_type}-{datetime.now():%Y-%m-%d}"

    try:
        elastic.index(index=index, doc_type=doc_type, body=content)
        logger.info(f"forwarded to elastic: index={index}, doc_type={doc_type}, body={content})")
    except Exception:
        logger.warning(
            f"failed forwarding to elastic: index={index}, doc_type={doc_type}, body={content})",
            exc_info=True,
        )


def main():
    """
    CLI for piping Ujo Containers from Kafka to Elasticsearch
    """

    logger.info("Starting Kafka to Elastic bridge")
    arguments = parse_arguments()

    kafka = connect_to_kafka(arguments.kafka, arguments.topics)

    elastic = connect_to_elasticsearch(arguments.elastic)

    # TODO: precreate indexes with correct types
    # for now send a dummy message so elastic wont guess a numeric type for input/output

    while True:
        try:
            process_messages(kafka, elastic)
        except KeyboardInterrupt:
            break

    kafka.close()


if __name__ == "__main__":
    main()
