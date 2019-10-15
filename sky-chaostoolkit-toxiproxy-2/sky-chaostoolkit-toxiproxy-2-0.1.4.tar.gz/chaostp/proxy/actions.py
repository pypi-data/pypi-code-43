# -*- coding: utf-8 -*-
# WARNING: This module exposes actions that have rather strong impacts on your
# cluster. While Chaos Engineering is all about disrupting and weaknesses,
# it is important to take the time to fully appreciate what those actions
# do and how they do it.
from typing import Dict
from future.utils import raise_with_traceback
from random import randrange

from chaoslib.types import Configuration

from logzero import logger

from toxiproxy import Toxiproxy, Proxy
from toxiproxy.api import APIConsumer
from toxiproxy.utils import can_connect_to
from toxiproxy.exceptions import ProxyExists, InvalidToxic, NotFound

from chaostp import get_servers
from chaostp.proxy.probes import get_proxies

__all__ = [
    "disable_proxy",
    "enable_proxy",
    "add_toxic",
    "delete_toxic",
    "delete_all_toxics",
    "populate",
    "delete_all_proxies",
    "create_proxy",
    "delete_proxy",
    "reset_server",
    "reset_all"
]


# Exceptions
ProxyNameNotDefined = type("ProxyNameNotDefined", (Exception,), {})


def reset_server(
        server: Dict = {"host": "localhost", "port": 8474},
        configuration: Configuration = {}):
    """
    Enable all proxies and remove all active toxics
    """

    APIConsumer.host = configuration.get('toxiproxy_host', server["host"])
    APIConsumer.port = configuration.get('toxiproxy_port', server["port"])
    c = Toxiproxy()
    return c.reset()


def reset_all(configuration: Configuration = {}):
    """
    Enable all proxies and remove all active toxics for all servers
    """
    servers = get_servers(configuration)
    for server in servers:
        APIConsumer.host = server["host"]
        APIConsumer.port = server["port"]
        c = Toxiproxy()
        c.reset()
    return 1


def delete_proxy(
        proxy_name: str,
        server: Dict = {"host": "localhost", "port": 8474},
        all_servers: bool = False,
        configuration: Configuration = {}):

    if (all_servers):
        servers = get_servers(configuration)
    else:
        servers = [server]

    ret: bool = True

    for server in servers:

        APIConsumer.host = configuration.get('toxiproxy_host', server["host"])
        APIConsumer.port = configuration.get('toxiproxy_port', server["port"])
        c = Toxiproxy()

        proxy = c.get_proxy(proxy_name)
        if isinstance(proxy, Proxy):
            proxy.destroy()
        else:
            ret = False
    return ret


def create_proxy(
        proxy_name,
        upstream,
        listen,
        enabled: bool = True,
        server: Dict = {"host": "localhost", "port": 8474},
        all_servers: bool = False,
        configuration: Configuration = {}):

    if (all_servers):
        servers = get_servers(configuration)
    else:
        servers = [server]
    
    ret: bool = True

    for server in servers:

        logger.debug("create_proxy on server {s}".format(s=server))

        APIConsumer.host = configuration.get('toxiproxy_host', server["host"])
        APIConsumer.port = configuration.get('toxiproxy_port', server["port"])
        c = Toxiproxy()
        try:
            c.create(
                upstream=upstream,
                name=proxy_name,
                listen=listen,
                enabled=enabled)
        except ProxyExists:
            logger.error("[ERROR]: proxy {p} already exists on server {s}".format(p=proxy_name,s=server))
            ret = False
    return ret


def delete_all_proxies(
        server: Dict = {"host": "localhost", "port": 8474},
        all_servers: bool = False,
        configuration: Configuration = {}):
    
    if (all_servers):
        servers = get_servers(configuration)
    else:
        servers = [server]

    for server in servers:

        logger.debug("delete_all_proxies on server {s}".format(s=server))
        APIConsumer.host = configuration.get('toxiproxy_host', server["host"])
        APIConsumer.port = configuration.get('toxiproxy_port', server["port"])
        c = Toxiproxy()
        c.destroy_all()
    return True


def disable_proxy(
        server: Dict = {"host": "localhost", "port": 8474},
        all_servers: bool = False,
        proxy_name: str = None,
        configuration: Configuration = {}):

    if (all_servers):
        servers = get_servers(configuration)
    else:
        servers = [server]
        
    ret: bool = True

    for server in servers:

        logger.debug("disable_proxy: Proxy: '{p}' on server {s}".format(p=proxy_name,s=server))

        APIConsumer.host = configuration.get('toxiproxy_host', server["host"])
        APIConsumer.port = configuration.get('toxiproxy_port', server["port"])
        client = Toxiproxy()
        proxy = client.get_proxy(proxy_name)

        if isinstance(proxy, Proxy):
            proxy.disable()
            logger.debug("disable_proxy: Proxy disabled on server {s}".format(s=server))
        else:
            ret = False

    return ret


def enable_proxy(
        server: Dict = {"host": "localhost", "port": 8474},
        all_servers: bool = False,
        proxy_name: str = None,
        configuration: Configuration = {}):
    
    if (all_servers):
        servers = get_servers(configuration)
    else:
        servers = [server]

    retL: bool = True

    for server in servers:

        logger.debug("enable_proxy: Proxy: '{p}' on server {s}".format(p=proxy_name,s=server))

        APIConsumer.host = configuration.get('toxiproxy_host', server["host"])
        APIConsumer.port = configuration.get('toxiproxy_port', server["port"])
        client = Toxiproxy()
        proxy = client.get_proxy(proxy_name)
        if isinstance(proxy, Proxy):
            proxy.enable()
            logger.debug("enable_proxy: Proxy enabled on server {s}".format(s=server))
        else:
            ret: bool = False
    return ret


def add_toxic(
        server: Dict = {"host": "localhost", "port": 8474},
        all_servers: bool = False,
        random_server: bool = False,
        proxy_name: str = None,
        toxic_name: str = None,
        type: str = None,
        stream: str = "downstream",
        toxicity: float = 1.0,
        attributes: str = None,
        configuration: Configuration = {}):
    """
    Add a toxic to a proxy
    The server can be specifically passed as parameter. Alternatively,
    if the "toxiproxy" configuration section is present, a random
    server is picked setting the "random_server" parameter to True.

    The name of the proxy to add the toxic to can be specified,
    otherwise a random proxy for the server is picked up
    """

    if (random_server):
        servers = get_servers(configuration)
        if (len(servers) > 1):
            servers = [servers[randrange(0, len(servers) - 1)]]

    if (all_servers):
        servers = get_servers(configuration)
    else:
        servers = [server]

    if (not proxy_name):
        proxies = get_proxies(server, configuration)
        if (len(proxies) > 1):
            proxy_name = proxies[randrange(0, len(proxies) - 1)]
        else:
            proxy_name = proxies[0]

        if (not proxy_name):
            raise_with_traceback(
                ProxyNameNotDefined("Proxy has to be defined"))

    for server in servers:
        logger.debug("""add_toxic:
                            Server: '{s} [random: {r}]'
                            Proxy: '{p}'
                            Toxic:
                                type: '{t}'
                                toxicity: '{to}'
                                attributes: '{a}'""".format(
            s=server,
            r=random_server,
            t=type,
            a=attributes,
            p=proxy_name,
            to=toxicity))

        APIConsumer.host = configuration.get('toxiproxy_host', server["host"])
        APIConsumer.port = configuration.get('toxiproxy_port', server["port"])
        client = Toxiproxy()
        proxy = client.get_proxy(proxy_name)
        if (not proxy):
            logger.error("[ERROR]: proxy {p} on {s} not found".format(p=proxy_name,s=server))
            return -1
        try:
            response = proxy.add_toxic(
                name=toxic_name,
                type=type,
                stream=stream,
                toxicity=toxicity,
                attributes=attributes)
        except InvalidToxic:
            logger.error("[ERROR]:Invalid Toxic: {}".format(response.text()))
            return -1

        logger.debug("add_toxic: Toxic added on server {s}".format(s=server))
    return 1


def delete_toxic(
        server: Dict = {"host": "localhost", "port": 8474},
        all_servers: bool = False,
        proxy_name: str = None,
        stream: str = "downstream",
        type: str = None,
        configuration: Configuration = {}):
    
    if (all_servers):
        servers = get_servers(configuration)
    else:
        servers = [server]

    for server in servers:

        logger.debug("delete_toxic: Server: '{s}', Proxy: '{p}', Toxic type '{t}'"
                    .format(s=server, t=type, p=proxy_name))

        APIConsumer.host = configuration.get('toxiproxy_host', server["host"])
        APIConsumer.port = configuration.get('toxiproxy_port', server["port"])
        client = Toxiproxy()
        proxy = client.get_proxy(proxy_name)
        label = type + "_" + stream
        try:
            proxy.destroy_toxic(label)
            logger.debug("delete_toxic: Toxic deleted on server {s}".format(s=server))
        except NotFound:
            logger.error("delete_toxic: toxic {l} not found on server {s}".format(l=label,s=server))
        except InvalidToxic:
            logger.error("delete_toxic: toxic {l} not valid on server {s}".format(l=label,s=server))

    return 1


def delete_all_toxics(
        server: Dict = {"host": "localhost", "port": 8474},
        all_servers: bool = False,
        proxy_name: str = None,
        configuration: Configuration = {}):

    if (all_servers):
        servers = get_servers(configuration)
    else:
        servers = [server]

    for server in servers:

        logger.info("delete_all_toxics: Server: '{s}', Proxy: '{p}'".format(
            s=server, p=proxy_name))
        APIConsumer.host = configuration.get('toxiproxy_host', server["host"])
        APIConsumer.port = configuration.get('toxiproxy_port', server["port"])
        logger.info("Toxiproxy host: {}".format(APIConsumer.host))
        client = Toxiproxy()
        proxy = client.get_proxy(proxy_name)

        toxics = proxy.toxics()

        for name in toxics:
            logger.debug("Found toxic " + name)
            proxy.destroy_toxic(name)

        logger.debug("delete_all_toxics: All toxics deleted on server {s}".format(s=server))

    return 1


def populate(
        proxies,
        server: Dict = {"host": "localhost", "port": 8474},
        all_servers: bool = False,
        configuration: Configuration = {}):

    if (all_servers):
        servers = get_servers(configuration)
    else:
        servers = [server]

    for server in servers:

        logger.debug("populate")

        APIConsumer.host = configuration.get('toxiproxy_host', server["host"])
        APIConsumer.port = configuration.get('toxiproxy_port', server["port"])
        client = Toxiproxy()
        proxies = client.populate(proxies)

        for proxy in proxies:
            host, port = proxy.listen.split(":")
            if not can_connect_to(host, int(port)):
                logger.warning(
                    "Can't connect to proxy {h}:{p}".format(h=host, p=port))
    return len(proxies)