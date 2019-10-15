# -*- coding: utf-8 -*-
"""A chaostoolkit driver for toxiproxy."""
from typing import List

from chaoslib.discovery.discover import discover_actions, discover_probes, \
    initialize_discovery_result
from chaoslib.types import Discovery, DiscoveredActivities, Configuration

name = "chaostp"
__author__ = """Leslie Lintott"""
__email__ = 'leslie.lintott@sky.uk'
__all__ = ["create_tp_client", "discover", "__version__"]
__version__ = '0.1.3'


class ProxyServers:
    """
    A singleton class to keep the proxies/servers topology (if defined in the
    configuration file).
    """
    class __singleton:
        def __init__(self, conf):
            self.servers = conf

    instance = None

    def __init__(self, conf):
        if not ProxyServers.instance:
            ProxyServers.instance = ProxyServers.__singleton(conf)
        else:
            ProxyServers.instance.servers = conf

    def get_servers(self):
        """ returns the list of configured servers """
        return ProxyServers.instance.servers


def get_servers(configuration: Configuration = {}):
    """
    Returns the list of all toxiproxy servers defined
    """
    if "toxiproxy" in configuration:
        # get the list of configured servers
        proxiservers = ProxyServers(configuration["toxiproxy"])
        return proxiservers.get_servers()
    else:
        server = [{
            "host": configuration.get('toxiproxy_host', 'localhost'),
            "port": configuration.get('toxiproxy_port', 8474)
        }]
        return server


def discover(discover_system: bool = True) -> Discovery:

    discovery = initialize_discovery_result(
        "chaostoolkit-toxiproxy", __version__, "toxiproxy")
    discovery["activities"].extend(load_exported_activities())
    return discovery


###############################################################################
# Private functions
###############################################################################
def load_exported_activities() -> List[DiscoveredActivities]:
    """
    Extract metadata from actions and probes exposed by this extension.
    """
    activities = []
    activities.extend(discover_actions("chaostp.proxy.actions"))
    activities.extend(discover_probes("chaostp.proxy.probes"))
    return activities
