# -*- coding: utf-8 -*-
from chaoslib.types import Configuration
from logzero import logger
from typing import Dict

from toxiproxy.api import APIConsumer
from toxiproxy import Toxiproxy

__all__ = [
    "get_proxies",
    "get_proxy",
    "server_running",
    "api_version",
    "get_num_toxics"
]


def get_num_toxics(
        proxy_name: str,
        server: Dict = {"host": "localhost", "port": 8474},
        configuration: Configuration = {}):
    APIConsumer.host = configuration.get('toxiproxy_host', server["host"])
    APIConsumer.port = configuration.get('toxiproxy_port', server["port"])
    c = Toxiproxy()
    proxy = c.get_proxy(proxy_name)
    return len(proxy.toxics())


def api_version(
        server: Dict = {"host": "localhost", "port": 8474},
        configuration: Configuration = {}):
    APIConsumer.host = configuration.get('toxiproxy_host', server["host"])
    APIConsumer.port = configuration.get('toxiproxy_port', server["port"])
    client = Toxiproxy()
    version = client.version()
    return version.decode('utf-8')


def get_proxies(
        server: Dict = {"host": "localhost", "port": 8474},
        configuration: Configuration = {}):
    APIConsumer.host = configuration.get('toxiproxy_host', server["host"])
    APIConsumer.port = configuration.get('toxiproxy_port', server["port"])
    client = Toxiproxy()
    proxies = list(client.proxies())
    return proxies


def get_proxy(
        proxy_name: str,
        server: Dict = {"host": "localhost", "port": 8474},
        configuration: Configuration = {}):
    APIConsumer.host = configuration.get('toxiproxy_host', server["host"])
    APIConsumer.port = configuration.get('toxiproxy_port', server["port"])
    client = Toxiproxy()
    proxies = client.proxies()
    if proxy_name in proxies:
        return proxy_name
    else:
        return None


def server_running(
        server: Dict = {"host": "localhost", "port": 8474},
        configuration: Configuration = {}):
    APIConsumer.host = configuration.get('toxiproxy_host', server["host"])
    APIConsumer.port = configuration.get('toxiproxy_port', server["port"])
    logger.info("Toxiproxy host: {}".format(APIConsumer.host))
    client = Toxiproxy()
    return client.running()
