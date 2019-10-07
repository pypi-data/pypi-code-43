"""
Rich actor types
"""

from __future__ import annotations

import importlib
import inspect
import logging
import sys
import threading
from types import FunctionType
from typing import Any
from typing import Mapping
from typing import Type

import pykka

from healer.support.typing import override
from healer.support.wired.typing import WiredBytes

logger = logging.getLogger(__name__)


class ProperRef(
        pykka._ref.ActorRef,
    ):
    "rich actor reference"

    actor_id:WiredBytes = None

    def __init__(self, actor:'Actor'):
        super().__init__(actor)
        self.actor_id = actor.actor_id

    def tell(self, message:Any, reply_to:pykka._ref.ActorRef=None) -> None:
        if self.is_alive():
            self.actor_inbox.put(pykka._envelope.Envelope(message, reply_to=reply_to))
        else:
            logger.warning(f"dead letter: {self} :: {message}")

#     def query(self, message:Any) -> None:
#         self.tell(message, reply_to=self)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"ActorRef->{self.actor_class.__name__}({self.actor_urn}, {self.actor_id})"


class Proper:
    ""
    # startup verificator
    start_namer = "proper@start"
    start_check = object()


class ProperActor(
        pykka.ThreadingActor,
    ):
    """
    base type for rich actor
    """

    use_daemon_thread = True  # use only daemon actors

    actor_id:WiredBytes  # local actor id
    message_type_receiver_map:Mapping[Type, FunctionType]  # message type -> method
    message_basetype_receiver_map:Mapping[Type, FunctionType]  # message subtype -> method

    @classmethod
    def __init_subclass__(cls, **kwargs):
        "register available derived actors"
        super().__init_subclass__(**kwargs)
        ProperSupport.register_actor_class(cls)

    @classmethod
    def start(cls, **kwargs) -> ProperRef:
        kwargs[Proper.start_namer] = Proper.start_check
        actor_ref = super().start(**kwargs)
        ProperRegistry.proper_register(actor_ref)
        return actor_ref

    @override
    def __init__(self, **kwargs):
        start_check = kwargs.pop(Proper.start_namer, None)
        assert start_check == Proper.start_check, f"use only Actor.start()"
        self.actor_id = ProperSupport.produce_actor_id()
        super().__init__(**kwargs)

    #
    #
    #

    @override
    def _stop(self):
        ProperRegistry.proper_unregister(self.actor_ref)
        super()._stop()

    @override
    def __str__(self):
        return f"{self.__class__.__name__}({self.actor_urn}, {self.actor_id})"

    @override
    def _actor_loop(self):
        try:
            self.on_start()
        except Exception:
            self._handle_failure(*sys.exc_info())

        while not self.actor_stopped.is_set():
            envelope = self.actor_inbox.get()
            try:
                self.reply_to = envelope.reply_to
                response = self._handle_receive(envelope.message)
                self.reply_to = None
                has_future = isinstance(envelope.reply_to, pykka._future.Future)
                has_return = response is not None and isinstance(envelope.reply_to, pykka._ref.ActorRef)
                if has_future:
                    envelope.reply_to.set(response)
                elif has_return:
                    envelope.reply_to.tell(response, reply_to=self.actor_ref)
            except Exception:
                if has_future:
                    logger.info(
                        'Exception returned from {} to caller:'.format(self),
                        exc_info=sys.exc_info(),
                    )
                    envelope.reply_to.set_exception()
                else:
                    self._handle_failure(*sys.exc_info())
                    try:
                        self.on_failure(*sys.exc_info())
                    except Exception:
                        self._handle_failure(*sys.exc_info())
            except BaseException:
                exception_value = sys.exc_info()[1]
                logger.debug(
                    '{!r} in {}. Stopping all actors.'.format(
                        exception_value, self
                    )
                )
                self._stop()
                pykka._registry.ActorRegistry.stop_all()

    @override
    def on_receive(self, message:Any) -> Any:
        "dispatch message based on type match"
        message_type = type(message)
        receive_method = self.message_type_receiver_map.get(message_type, None)
        if receive_method:
            return receive_method(self, message)
        for message_basetype, receive_method in self.message_basetype_receiver_map.items():
            if issubclass(message_type, message_basetype):
                return receive_method(self, message)
        return self.on_receive_default(message)

    def on_receive_default(self, message:Any) -> Any:
        "dispatch message with type mismatch"
        return super().on_receive(message)

    @override
    def on_start(self):
        logger.debug(f"@ {self}")

    @override
    def on_stop(self):
        logger.debug(f"@ {self}")

    @override
    def on_failure(self, *_):
        logger.warning(f"@ {self}")

    def tell(self, message:Any) -> None:
        "send to self"
        self.actor_ref.tell(message)

    def query(self, send_to:pykka._ref.ActorRef, message:Any) -> None:
        "send to other, expect reply to self"
        send_to.tell(message, reply_to=self.actor_ref)


def proper_receive_type(receive_method:FunctionType) -> FunctionType:
    "decorator for actor.on_receive for exact message type match"
    return ProperSupport.register_proper_type(receive_method, use_type=True)


def proper_receive_basetype(receive_method:FunctionType) -> FunctionType:
    "decorator for actor.on_receive for message type match by base type"
    return ProperSupport.register_proper_type(receive_method, use_type=False)


class ProperRegistry:
    """
    rich actor registry
    """

    proper_actor_id:int = 0
    proper_actor_map:Mapping = dict()
    proper_actor_lock:threading.Lock = threading.Lock()

    @staticmethod
    def find_by_uid(uid:WiredBytes) -> ProperRef:
        assert isinstance(uid, WiredBytes), f"wrong uid: {uid}"
        return ProperRegistry.proper_actor_map.get(uid, None)

    @staticmethod
    def find_by_class(actor_class:Type) -> ProperRef:
        return pykka.ActorRegistry.get_by_class(actor_class)

    @staticmethod
    def proper_register(actor_ref:ProperRef) -> None:
        with ProperRegistry.proper_actor_lock:
            ProperRegistry.proper_actor_map[actor_ref.actor_id] = actor_ref

    @staticmethod
    def proper_unregister(actor_ref:ProperRef) -> None:
        with ProperRegistry.proper_actor_lock:
            ProperRegistry.proper_actor_map.pop(actor_ref.actor_id, None)


class ProperSupport:
    """
    rich actor registration
    """

    proper_actor_type_set = set()

    # match message by exact type: receive method -> message type
    receiver_message_type_map:Mapping[FunctionType, Type] = dict()

    # match message by super type: receive method -> message base type
    receiver_message_basetype_map:Mapping[FunctionType, Type] = dict()

    @staticmethod
    def register_actor_class(actor_class:Type[ProperActor]) -> None:
        "register available derived actors"
        assert actor_class not in ProperSupport.proper_actor_type_set, f"need unique: {actor_class}"
        ProperSupport.proper_actor_type_set.add(actor_class)
        actor_class.message_type_receiver_map = ProperSupport.produce_receiver_type_map(actor_class)
        actor_class.message_basetype_receiver_map = ProperSupport.produce_receiver_basetype_map(actor_class)

    @staticmethod
    def produce_actor_id() -> WiredBytes:
        "generate unused actor id in range [1 ... limit]"
        limit = 1024 * 1024
        with ProperRegistry.proper_actor_lock:
            actor_id = ProperRegistry.proper_actor_id
            while True:
                actor_id += 1
                if actor_id <= 0:
                    actor_id = 1
                if actor_id >= limit:
                    actor_id = 1
                if not actor_id in ProperRegistry.proper_actor_map:
                    break
            ProperRegistry.proper_actor_id = actor_id
            return WiredBytes.from_int(actor_id)

    @staticmethod
    def register_proper_type(receive_method:FunctionType, use_type:bool) -> FunctionType:
        method_spec = inspect.getfullargspec(receive_method)
        assert len(method_spec.args) == 2, f"need 2 args: {method_spec}"
        assert method_spec.args[0] == 'self', f"need self arg0: {method_spec}"
        message_name = method_spec.args[1]
        assert message_name in method_spec.annotations, f"need type spec: {method_spec}"
        message_type = method_spec.annotations[message_name]
        if isinstance(message_type, str):  # resolve type from type name
            module = importlib.import_module(receive_method.__module__)
            globals_dict = dict(inspect.getmembers(module))
            message_type = eval(message_type , globals_dict)
        assert isinstance(message_type, type), f"need type: {message_type}"
        if use_type:
            ProperSupport.receiver_message_type_map[receive_method] = message_type
        else:
            ProperSupport.receiver_message_basetype_map[receive_method] = message_type
        return receive_method

    @staticmethod
    def produce_receiver_map(
            actor_class:Type[ProperActor],
            receiver_type_map:Mapping[Type, FunctionType],
        ) -> Mapping[Type, FunctionType]:
        receiver_map = dict()
        for receive_method, message_type in receiver_type_map.items():
            method_select = lambda method: method == receive_method
            member_list = inspect.getmembers(actor_class, method_select)
            if member_list:
                assert len(member_list) == 1, f"invalid member list: {member_list}"
                assert message_type not in receiver_map, f"duplicate message type: {message_type}"
                receiver_map[message_type] = receive_method
        return receiver_map

    @staticmethod
    def produce_receiver_type_map(actor_class:Type[ProperActor]) -> Mapping[Type, FunctionType]:
        receiver_type_map = ProperSupport.receiver_message_type_map
        return ProperSupport.produce_receiver_map(actor_class, receiver_type_map)

    @staticmethod
    def produce_receiver_basetype_map(actor_class:Type[ProperActor]) -> Mapping[Type, FunctionType]:
        receiver_type_map = ProperSupport.receiver_message_basetype_map
        return ProperSupport.produce_receiver_map(actor_class, receiver_type_map)
