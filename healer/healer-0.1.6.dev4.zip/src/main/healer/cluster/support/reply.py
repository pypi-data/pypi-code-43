"""
"""

from __future__ import annotations

from healer.cluster.talk import ActorRoute
from healer.support.actor.proper import ProperActor
from healer.support.wired.typing import WiredBytes


class WithRouteReply(
        ProperActor,
    ):

    def route_to_node(self, dst:WiredBytes) -> ActorRoute:
        return ActorRoute(
            src=WiredBytes.empty(),
            src_id=self.actor_id,
            dst=dst,
            dst_id=WiredBytes.empty(),
        )

    def route_to_actor(self, origin:ActorRoute) -> ActorRoute:
        return ActorRoute(
            src=WiredBytes.empty(),
            src_id=self.actor_id,
            dst=origin.src,
            dst_id=origin.src_id,
        )
