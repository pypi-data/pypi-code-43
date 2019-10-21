import json
import logging
import os
import zlib

import bson
import click

from antares_client import Client

logger = logging.getLogger("cli")
logger.setLevel(logging.DEBUG)


@click.command()
@click.option("-v", "--verbose")
@click.option("-h", "--host", help="Hostname of Kafka cluster", type=str)
@click.option("-p", "--port", help="Port of Kafka cluster", type=int)
@click.option(
    "-g",
    "--group",
    help="Globally unique name of consumer group (default, hostname)",
    type=str,
)
@click.option(
    "-d",
    "--output-directory",
    type=str,
    help="Directory to save alerts in. If not passed, a message will be logged to STDOUT when alerts are received.",
)
@click.option("--api-key", help="ANTARES Kafka API Key", type=str)
@click.option("--api-secret", help="ANTARES Kafka API Secret", type=str)
@click.option(
    "--ssl-ca-location",
    help="Location of your SSL root CAs cert.pem file",
    type=click.Path(exists=True),
)
@click.argument("topics", nargs=-1, required=True)
def stream(**kwargs):
    """
    Stream alerts from ANTARES

    This command subscribes to ANTARES streams and writes alerts to ``*.json``
    files in a directory of your choice.

    For example, to save all alerts from the ``extragalactic`` stream to a
    folder in your home directory called ``antares/extragalactic``::

    \b
    antares stream extragalactic
        --output-directory ~/antares
        --api-key ********************
        --api-secret ********************

    The client creates a subdirectory in ``--output-directory`` named after the
    stream you're subscribing to and saves that stream's alerts there (in this
    case, ``~/antares/extragalactic``).

    You can also subscribe to multiple streams::

    \b
    antares stream extragalactic nuclear_transient
      --output-directory ~/antares
      --api-key ********************
      --api-secret ********************

    And this will save the alerts from the ``extragalactic`` and
    ``nuclear_transient`` streams in ``~/antares/extragalactic`` and
    ``~/antares/nuclear_transient``, respectively.

    """
    logger.info("Opening connection to ANTARES Kafka...")
    kwargs["topics"] = list(kwargs["topics"])
    if len(kwargs["topics"]) == 1:
        kwargs["topics"] = kwargs["topics"][0].split(",")
        if len(kwargs["topics"]) > 1:
            logger.warning(
                "comma-separated topics have been deprecated in favor of space-separated topics"
            )
    with Client(**kwargs) as client:
        for topic, alert in client.iter():
            if kwargs.get("output_directory", False):
                directory = os.path.join(kwargs["output_directory"], topic)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                alert_id = get_alert_id(alert)
                file_name = "{}.json".format(alert_id)
                file_path = os.path.join(directory, file_name)
                with open(file_path, "w") as f:
                    json.dump(alert, f, indent=4)
                logger.info("Saved alert {}".format(file_path))
            else:
                logger.info("Received alert on topic '{}'".format(topic))
        logger.info("Closing connection...")


def get_alert_id(alert):
    alert_id = alert["new_alert"].get("alert_id", None)
    if alert_id is None:
        alert_id = "{}-{}".format(
            alert["new_alert"]["survey"], alert["new_alert"]["original_id"]
        )
    return alert_id


def parse_antares_alert(payload):
    """
    Convert an ANTARES Alert message to a Python object.

    ANTARES Alerts are outputted in GZIP-compressed BSON format.

    :param payload: byte array of message
    :return: dict
    """
    try:
        return bson.loads(zlib.decompress(payload))
    except Exception:
        logger.error("Failed to parse message:")
        logger.error(payload)
        raise
