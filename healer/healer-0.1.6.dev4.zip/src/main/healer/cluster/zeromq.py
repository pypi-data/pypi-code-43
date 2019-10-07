"""
"""

from __future__ import annotations

import logging

import zmq

from healer.config import CONFIG

from .config import ClusterConfig

logger = logging.getLogger(__name__)


class SupportZMQ:
    """
    """

    flask_context:zmq.Context = zmq.Context().instance()

    @staticmethod
    def socket_dealer() -> zmq.Socket:
        section = CONFIG['cluster/zeromq/dealer']
        option_hwm = int(section['option_hwm'])
        socket = SupportZMQ.flask_context.socket(zmq.DEALER)
        socket.set(zmq.RCVHWM, option_hwm)
        socket.set(zmq.SNDHWM, option_hwm)
#         socket.setsockopt(zmq.PROBE_ROUTER, 1)
        return socket

    @staticmethod
    def socket_router() -> zmq.Socket:
        section = CONFIG['cluster/zeromq/router']
        option_hwm = int(section['option_hwm'])
        socket = SupportZMQ.flask_context.socket(zmq.ROUTER)
        socket.set(zmq.RCVHWM, option_hwm)
        socket.set(zmq.SNDHWM, option_hwm)
#         socket.setsockopt(zmq.PROBE_ROUTER, 1)
        return  socket

    @staticmethod
    def perform_local_bind(socket:zmq.Socket) -> str:
        local_bind = ClusterConfig.cluster_local_bind()
        scheme = local_bind.scheme
        host_addr = local_bind.host_addr
        for host_port in local_bind.port_range:
            point_request = ClusterConfig.point_format.format(scheme, host_addr, host_port)
            try:
                socket.bind(point_request)
                point_response = socket.get_string(zmq.LAST_ENDPOINT)
                return point_response
            except zmq.error.ZMQError as error:
                if error.errno == zmq.EADDRINUSE:
                    continue
                else:
                    raise error
        raise RuntimeError(f"Failed to bind:")
