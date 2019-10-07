import time
import pytest
import inspect

import healer.support.actor.proper

from healer.support.actor.proper import *
from dataclasses import dataclass

for entry in inspect.getmembers(healer.support.actor.proper):
    ""
#     print(entry)


@dataclass
class ControlMessage:
    pass


@dataclass
class PeerMessage(ControlMessage):
    actor:pykka.ActorRef


@dataclass
class PlayerMessage:
    count:int = 0


class PingPongActor(ProperActor):

    @proper_receive_basetype
    def on_peer_message(self, message:ControlMessage) -> None:
        print(f"on_peer: {message}")
        assert isinstance(message, PeerMessage)
        self.peer = message.actor
        assert self.peer != self.actor_ref
        self.peer.tell(PlayerMessage(), self.actor_ref)

    @proper_receive_type
    def on_player_message(self, message:PlayerMessage) -> PlayerMessage:
        print(f"reply_to: {self.reply_to} message: {message}")
        assert self.reply_to != self.actor_ref
        if self.peer.is_alive():
            count = message.count + 1
            if count > 3:
                return
            else:
                return PlayerMessage(count)
        else:
            self.stop()


def test_patch():
    print(f"test_patch")

    class_type = pykka._envelope.Envelope
    print(f"type: {class_type}")

    instance = class_type(message='hello')
    print(f"instance: {instance}")


def test_no_start():
    print(f"test_no_start")

    with pytest.raises(AssertionError):
        ProperActor()


def test_ping_pong():
    print(f"test_ping_pong")

    player_one = PingPongActor.start()
    player_two = PingPongActor.start()

    assert player_one == ProperRegistry.find_by_uid(player_one.actor_id)
    assert player_two == ProperRegistry.find_by_uid(player_two.actor_id)

    player_one.tell(PeerMessage(player_two))
    player_two.tell(PeerMessage(player_one))

    time.sleep(0.5)

    player_one.stop()
    player_two.stop()


def test_actor_id():
    print(f"test_actor_id")

    for index in range(3):
        actor_id = ProperSupport.produce_actor_id()
        print(f"actor_id={actor_id}")

    for index in range(3):
        actor_ref = ProperActor.start()
        print(f"actor_ref={actor_ref}")
        actor_ref.stop()
