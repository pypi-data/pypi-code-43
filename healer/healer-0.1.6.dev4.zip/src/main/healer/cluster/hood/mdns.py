"""
Zeroconf neighbourhood discovery
"""

from __future__ import annotations

import ipaddress
import logging
from typing import Mapping

import zeroconf

from healer.cluster.hood.reactor import WithHoodReactor
from healer.cluster.talk import NodeInfo
from healer.config import CONFIG
from healer.support.typing import override
from healer.support.typing import unused
from healer.support.wired.typing import WiredBytes
from healer.support.wired.typing import WiredSupport

logger = logging.getLogger(__name__)

class ListenerMDNS(
        zeroconf.ServiceListener,
    ):
    """
    """

    reactor:WithHoodReactor = None
    sevice_map:Mapping[str, NodeInfo] = None  # remote

    def __init__(self, reactor:WithHoodReactor):
        super().__init__()
        assert isinstance(reactor, WithHoodReactor)
        self.reactor = reactor
        self.sevice_map = dict()

    @override
    def add_service(self, zc:zeroconf, kind:str, name:str):
        service_info:zeroconf.ServiceInfo = zc.get_service_info(kind, name)
        node_info = SupportMDNS.produce_node_info(service_info)
        if not name in self.sevice_map:
            logger.debug(f"create: {name}")
            self.sevice_map[name] = node_info
            self.reactor.react_node_detected(node_info)
        else:
            logger.debug(f"present: {name}")

    @override
    def remove_service(self, zc:zeroconf, kind:str, name:str):
        unused(zc, kind)
        if name in self.sevice_map:
            logger.debug(f"delete: {name}")
            node_info = self.sevice_map.pop(name)
            self.reactor.react_node_undetected(node_info)
        else:
            logger.debug(f"missing: {name}")


class BrowserMDNS(zeroconf.ServiceBrowser):
    """
    """

    def __init__(self, listener:ListenerMDNS):
        super().__init__(
            zc=SupportMDNS.zeroconf_manager,
            type_=SupportMDNS.service_type,
            listener=listener,
        )


class SupportMDNS:

    logger = logging.getLogger(__name__)

    service_type = CONFIG['cluster/hood/mdns']['service_type']

    zeroconf_manager = zeroconf.Zeroconf()

    service_registry:Mapping[str, zeroconf.ServiceInfo] = dict()  # local

    @staticmethod
    def issue_node_enable(node_info:NodeInfo) -> None:
        guid = node_info.guid
        if not guid in SupportMDNS.service_registry:
            SupportMDNS.logger.debug(f"create: {node_info}")
            service_info = SupportMDNS.produce_service_info(node_info)
            SupportMDNS.zeroconf_manager.register_service(service_info)
            SupportMDNS.service_registry[guid] = service_info
        else:
            SupportMDNS.logger.debug(f"present: {node_info}")

    @staticmethod
    def issue_node_disable(node_info:NodeInfo) -> None:
        guid = node_info.guid
        if guid in SupportMDNS.service_registry:
            SupportMDNS.logger.debug(f"delete: {node_info}")
            service_info = SupportMDNS.service_registry.pop(guid, None)
            SupportMDNS.zeroconf_manager.unregister_service(service_info)
        else:
            SupportMDNS.logger.debug(f"missing: {node_info}")

    @staticmethod
    def issue_service_terminate() -> None:
        for service_info in SupportMDNS.service_registry.values():
            SupportMDNS.zeroconf_manager.unregister_service(service_info)
        SupportMDNS.service_registry.clear()

    @staticmethod
    def produce_node_info(service_info:zeroconf.ServiceInfo) -> NodeInfo:
        assert service_info.type == SupportMDNS.service_type, f"invalid service: {service_info}"
        prop_dict = WiredSupport.string_dict(service_info.properties)
        guid = prop_dict['guid']
        bin_guid = WiredBytes.from_hex(guid)
        net_addr = service_info.addresses[0]
        str_addr = str(ipaddress.ip_address(net_addr))
        bin_port = service_info.port
        node_info = NodeInfo(
            guid=bin_guid,
            addr=str_addr,
            port=bin_port,
        )
        return node_info

    @staticmethod
    def produce_service_info(node_info:NodeInfo) -> zeroconf.ServiceInfo:
        guid = node_info.guid
        str_guid = guid.to_hex()
        name = f"{str_guid}.{SupportMDNS.service_type}"
        net_addr = ipaddress.ip_address(node_info.addr)
        bin_addr = net_addr.packed
        bin_port = node_info.port
        prop_dict = {
            'guid': str_guid,
        }
        service_info = zeroconf.ServiceInfo(
            type_=SupportMDNS.service_type,
            name=name,
            addresses=[bin_addr],
            port=bin_port,
            properties=WiredSupport.binary_dict(prop_dict),
        )
        return service_info
