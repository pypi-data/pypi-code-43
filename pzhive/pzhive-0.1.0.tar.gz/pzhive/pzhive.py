# !/usr/bin/env python
# coding=utf-8

import logging
import random
import sys

from kazoo.client import KazooClient

import hive

logging.basicConfig(
    level=logging.INFO
    , stream=sys.stdout
    , format='%(asctime)s %(pathname)s %(funcName)s %(lineno)d  %(levelname)s: %(message)s')


class ConnectionException(Exception):
    pass


def connect(host, port, username=None, database='default', auth=None,
           configuration=None, kerberos_service_name=None, kerberos_service_host=None, password=None,
           thrift_transport=None):
    try:
        # real_kerberos_service_host = validate_kerberos_service_host(kerberos_service_host, host_port[0])
        logging.info("Connecting to thrift server " + host + ":" + str(port))
        cursor = hive.connect(host=host,
                              port=port,
                              username=username,
                              password=password,
                              database=database,
                              auth=auth,
                              configuration=configuration,
                              kerberos_service_name=kerberos_service_name,
                              kerberos_service_host=kerberos_service_host,
                              thrift_transport=thrift_transport).cursor()
    except Exception:
        logging.error(
            "Can not connect " + host + ":" + str(port) + ", please check the connection config and the hiveserver")
        raise Exception
    return cursor


def connect_by_zk(zk_url, zk_name_space, username=None, database='default', auth=None,
                  configuration=None, kerberos_service_name=None, kerberos_service_host=None, password=None,
                  thrift_transport=None):
    host_list = discovery_thrift_service_host(zk_url, zk_name_space)
    host_length = host_list.__len__()
    random.seed()
    is_connected = False
    while is_connected is False and host_length > 0:
        index = random.randint(0, host_length - 1)
        host_port = host_list.pop(index).split(":")
        try:
            real_kerberos_service_host = validate_kerberos_service_host(kerberos_service_host, host_port[0])
            logging.info("Connecting to thrift server " + host_port[0] + ":" + host_port[1])
            cursor = hive.connect(host=host_port[0],
                                  port=host_port[1],
                                  username=username,
                                  password=password,
                                  database=database,
                                  auth=auth,
                                  configuration=configuration,
                                  kerberos_service_name=kerberos_service_name,
                                  kerberos_service_host=real_kerberos_service_host,
                                  thrift_transport=thrift_transport).cursor()
            is_connected = True
        except Exception:
            is_connected = False
            if host_length > 1:
                logging.error(
                    "Can not connect " + host_port[0] + ":" + host_port[1] + " .try another thrift server...")
            else:
                logging.error(
                    "Can not connect " + host_port[0] + ":" + host_port[
                        1] + ", please check the connection config and the hiveserver")
                raise Exception
        host_length -= 1
    return cursor


def validate_kerberos_service_host(kerberos_server_host, host_name):
    if kerberos_server_host is None:
        return host_name
    else:
        if kerberos_server_host.upper() == "_HOST":
            return host_name
        else:
            return kerberos_server_host


# discovery the thrift service host list
def discovery_thrift_service_host(zk_host, zk_name_space):
    zk_client = KazooClient(hosts=zk_host, logger=logging)
    zk_client.start()
    # get the children name of zonde
    if zk_name_space.startswith("/"):
        name_space_with_prefix = zk_name_space
    else:
        name_space_with_prefix = "/" + zk_name_space
    node_children = zk_client.get_children(name_space_with_prefix)
    host_list = list()
    for node in node_children:
        sub_node_name_space = name_space_with_prefix + "/" + node
        data, state = zk_client.get(sub_node_name_space)
        host_list.append(data)
    zk_client.stop()
    return host_list
