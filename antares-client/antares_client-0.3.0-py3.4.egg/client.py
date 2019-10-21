import itertools
import logging
import os
import re
import socket
import subprocess
import time
import zlib

import bson
import confluent_kafka
from confluent_kafka.cimpl import (  # pylint: disable=no-name-in-module
    KafkaError,
    KafkaException,
)

log = logging.getLogger(__name__)


class AntaresException(Exception):
    pass


class AntaresAlertParseException(AntaresException):
    pass


class Client:

    _DEFAULT_CONFIG = {
        "host": "pkc-epgnk.us-central1.gcp.confluent.cloud",
        "port": 9092,
    }
    _POLLING_FREQUENCY = 1.0

    def __init__(self, topics, **config):
        """
        Creates a new ``Client`` instance.

        Parameters
        ----------
        topics: list of str
            Kafka stream topics to subscribe to.
        api_key: str
            API Key
        api_secret: str
            API Secret
        group: str, optional
            Group to connect to Kafka stream with. Changing this will reset
            your partition offsets. If you don't know what that means, DON'T
            pass any arguments for this (default, socket.gethostname()).
        ssl_ca_location: str, optional
            Path to your root SSL CAs cert.pem file.
        """
        self._topics = topics
        config = _merge_dictionaries(self._DEFAULT_CONFIG, config)
        kafka_config = {
            "bootstrap.servers": "{}:{}".format(config["host"], config["port"]),
            "group.id": config.get("group", socket.gethostname()),
            "default.topic.config": {"auto.offset.reset": "smallest"},
            "api.version.request": True,
            "broker.version.fallback": "0.10.0.0",
            "api.version.fallback.ms": 0,
            "enable.auto.commit": config.get("enable_auto_commit", True),
        }
        if "api_key" in config and "api_secret" in config:
            kafka_config.update(
                {
                    "security.protocol": "SASL_SSL",
                    "sasl.username": config["api_key"],
                    "sasl.password": config["api_secret"],
                    "sasl.mechanisms": "PLAIN",
                    "ssl.ca.location": config.get("ssl_ca_location")
                    or _locate_ssl_certs_file(),
                }
            )
        self._consumer = confluent_kafka.Consumer(kafka_config)
        self._consumer.subscribe(self.topics)

    def iter(self, num_alerts=None):
        """
        Yield from ANTARES alert streams. 

        Parameters
        -----------
        num_alerts: int
            Maximum number of alerts to yield. If None, yield alerts
            indefinitely (default, None).

        Yields
        ----------
        (topic, alert): str, dict

        """
        for i in itertools.count(start=1, step=1):
            yield self.poll()
            if num_alerts and i >= num_alerts:
                return

    def _timed_poll(self, timeout):
        start_time = time.process_time()
        while (time.process_time() - start_time) < timeout:
            try:
                message = self._consumer.poll(timeout=self._POLLING_FREQUENCY)
                if message is not None:
                    alert = _parse_message(message)
                    return message.topic(), alert
            except KafkaException as kafka_exception:
                kafka_error = kafka_exception.args[0]
                # pylint: disable=protected-access
                if kafka_error == KafkaError._PARTITION_EOF:
                    pass
                else:
                    exception_fmt = "There was a problem parsing the message: {}"
                    raise AntaresException(exception_fmt.format(message))
        return None, None

    def poll(self, timeout=None):
        """
        Retrieve a single alert. This method blocks until ``timeout``
        seconds have elapsed (by default, an infinite amount of time).

        Parameters
        ----------
        timeout: int
            Number of seconds to block waiting for an alert. If None,
            block indefinitely (default, None).

        Returns
        ----------
        (topic, alert): (str, dict)
            Or ``(None, None)`` if ``timeout`` seconds elapse with no response

        """
        if timeout:
            return self._timed_poll(timeout)
        alert = None
        while alert is None:
            topic, alert = self._timed_poll(self._POLLING_FREQUENCY)
        return topic, alert

    def commit(self):
        """Commit to the underlying Kafka stream."""
        self._consumer.commit()

    def close(self):
        """Close the client's connection."""
        self._consumer.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._consumer.close()

    @property
    def topics(self):
        return self._topics


def _call(cmd):
    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    return_code = process.returncode
    return return_code, stdout, stderr


def _merge_dictionaries(*dictionaries):
    merged_dictionary = {}
    for dictionary in dictionaries:
        merged_dictionary.update(
            {key: val for key, val in dictionary.items() if val is not None}
        )
    return merged_dictionary


def _locate_ssl_certs_file():
    """
    Attempt to locate openssl's CA certs file. Attempts to search
    a list of known locations first. Failing that, calls ``openssl``
    and tries to parse the output for file location.

    Raises
    ----------
    FileNotFoundError
      If no SSL certs file can be located.
    
    """
    # Check known locations first
    known_locations = [
        "/opt/local/etc/openssl/cert.pem",
        "/usr/local/etc/openssl/cert.pem",
        "/etc/pki/tls/cert.pem",
        "/etc/ssl/certs/ca-certificates.crt",
    ]
    log.info("Looking for openssl certs file in known locations.")
    for path in known_locations:
        log.debug("Checking location {}".format(path))
        if os.path.exists(path):
            log.info("Found certs at {}".format(path))
            return path
    # Failing that, try calling openssl directly
    log.info("Didn't find certs file in known locations.")
    log.info("Attempting to locate certs using `openssl version -d`")
    return_code, stdout, stderr = _call("openssl version -d")
    if return_code != 0:
        log.info("openssl returned error code {}".format(return_code))
        log.error("Failed to locate openssl certs file.")
    else:
        regex = re.compile(r"OPENSSLDIR: \"(?P<path>.*)\"")
        log.debug("openssl stdout:")
        log.debug(stdout.decode())
        match = re.search(regex, stdout.decode())
        if match:
            path = os.path.join(match.group("path"), "cert.pem")
            if os.path.exists(path):
                log.info("Found certs at {}".format(path))
                return path
    # Failing that, raise an error
    raise FileNotFoundError("Could not locate SSL certificate")


def _parse_message(message):
    if message.error():
        raise KafkaException(message.error().code())
    alert = bson.loads(zlib.decompress(message.value()))
    return alert
