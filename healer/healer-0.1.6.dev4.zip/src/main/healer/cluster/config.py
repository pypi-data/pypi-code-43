
from __future__ import annotations

from dataclasses import dataclass

from healer.config import CONFIG
from healer.support.parser import parser_produce_range


@dataclass(frozen=True)
class ClusterLocalBind:
    scheme:str
    host_addr:str
    port_range:range


class ClusterConfig:
    """
    """

    # tcp://*:1234
    point_format = "{}://{}:{}"

    @staticmethod
    def cluster():
        return CONFIG['cluster']

    @staticmethod
    def cluster_local_bind() -> ClusterLocalBind:
        section = CONFIG['cluster/local_bind']
        port_range = parser_produce_range(section['port_range'])
        return ClusterLocalBind(
            scheme=section['scheme'],
            host_addr=section['host_addr'],
            port_range=port_range,
        )
