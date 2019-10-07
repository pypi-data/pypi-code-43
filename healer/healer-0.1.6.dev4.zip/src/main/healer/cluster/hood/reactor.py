"""
Node discovery event reactor
"""

from __future__ import annotations

import abc

from healer.cluster.talk import NodeInfo


class WithHoodReactor(abc.ABC):
    """
    Trait: react to node discovery events
    """

    @abc.abstractmethod
    def react_node_detected(self, node_info:NodeInfo):
        "remote node is now present"

    @abc.abstractmethod
    def react_node_undetected(self, node_info:NodeInfo):
        "remote node has gone missing"
