import json
import struct
import time

from abc import ABC, abstractmethod
from google.protobuf import json_format
from . import agent_pb2
from typing import List, Optional
from typing import Union
from . import uri
from .protostuff import dictToProto, protoToDict
from .uri import Context
from .schema import Description
from .query import Query
from .messages import PROPOSE_TYPES, CFP_TYPES

class OefProtoBase(object):
    def __init__(self, **kwargs):
        pass

    def make_message(self, bytes=None, conn=None, json=None, message_class=None, data=None, pb=None):
        if data:
            pb = message_class()
            dictToProto(pb, data)
        if json:
            #print("OefProtoBase.make_message: json -> pb")
            pb = message_class()
            json_format.Parse(json, pb, ignore_unknown_fields=True)
        if pb:
            #print("OefProtoBase.make_message: pb -> bytes")
            bytes = pb.SerializeToString()
        if bytes:
            #print("OefProtoBase.make_message: yield bytes")
            return bytes
        raise ValueError("invalid data/json/pb/bytes fed to OefProtoBase.make_message")

    def decode_message(self, x, bytes):
        inbound = x()
        inbound.ParseFromString(bytes)
        contents = protoToDict(inbound)
        #json_string = json_format.MessageToJson(inbound, including_default_value_fields=True)
        #contents = json.loads(json_string)
        return contents

    @abstractmethod
    def output(self, **kwargs):
        pass

    @abstractmethod
    def incoming(self, data, connection_name, conn):
        pass

    @abstractmethod
    def handle_failure(self, exception, conn):
        pass

    @abstractmethod
    def handle_disconnection(self, conn):
        pass


class OefConnectionHandler(OefProtoBase):
    def __init__(self, conn=None,
                     success=None, failure=None,
                     **kwargs):
        self.success = success
        self.failure = failure

        if not self.failure:
            self.failure = lambda x,y: None
        if not self.success:
            self.success = lambda x,y: None

        self.conn = conn

    def output(self, data, target):
        target . send(data)

    def incoming(self, data, connection_name=None, conn=None):
        raise ValueError("Messages arrived before connection was complete.")

    def handle_failure(self, exception, conn):
        self.failure(conn=conn, url=conn.url, ex=exception, conn_name=conn.name)
        conn.close()

    def handle_disconnection(self, conn):
        pass

class OefMessageHandler(OefProtoBase):
    def __init__(self, logger=None, **kwargs):
        self.logger = logger or print
        self.on_message = None

    def output(self, bytes=None, conn=None, json=None, message_class=agent_pb2.Envelope, data=None, pb=None):
        bytes = self.make_message(
            bytes=bytes,
            json=json,
            message_class=message_class,
            data=data,
            pb=pb
        )
        conn . send(bytes)

    def handle_disconnection(self, conn):
        pass

    def incoming(self, data, connection_name=None, conn=None):
        am = self.decode_message(agent_pb2.Server.AgentMessage, data)
        return self.incomingAgentMessage(am, connection_name=connection_name, conn=conn)

    def incomingAgentMessage(self, agentMessage, connection_name=None, conn=None):
        if 'ping' in agentMessage:
            self.output(
                message_class=agent_pb2.Envelope,
                data={
                    "msg_id": 0,
                    "pong": {
                        "dummy": 77,
                        }
                },
                conn=conn
            )
            #self.logger("OefMessageHandler[{}].incoming:handled:".format(id(self)), connection_name, agentMessage)
            return True

        return False


class ValueBag(object):
    def __init__(self, sd=[], data={}):
        for d,s in sd:
            if callable(s):
                setattr(self, d, s(data))
            else:
                setattr(self, d, data.get(s, None))

    def __str__(self):
        return json.dumps({
            k: getattr(self, k)
            for k
            in dir(self)
        })


class OefLoginHandler(OefProtoBase):
    def __init__(
            self,
            conn=None,
            public_key=None,
            success=lambda *args, **kwargs: None,
            failure=lambda *args, **kwargs: None,
            logger=None,
            **kwargs):
        super().__init__(**kwargs)
        self.success = success
        self.failure = failure
        self.logger = logger

        if not self.failure:
            self.failure = lambda x,y: None
        if not self.success:
            self.success = lambda x,y: None
        self.public_key = public_key or None
        self.output(
            self.make_message(
                message_class=agent_pb2.Agent.Server.ID,
                data={
                    "public_key": self.public_key,
                },
            ),
            conn
        )

    def output(self, data, conn):
        conn . send(data)

    def incoming(self, data, connection_name, conn):
        inp_chall = self.decode_message(agent_pb2.Server.Phrase, data)
        inp_conn = self.decode_message(agent_pb2.Server.Connected, data)

        if 'phrase' in inp_chall:
            self.output(
                self.make_message(
                    message_class=agent_pb2.Agent.Server.Answer,
                    data={
                        "answer": inp_chall['phrase'][::-1],
                        "capability_bits": {
                            "will_heartbeat": True,
                        },
                    },
                ),
                conn
            )
            return

        if 'failure' in inp_chall:
            self.handle_failure(ValueError("rejected before challenge"), conn)
            return

        if 'status' in inp_conn:
            if inp_conn['status']:
                conn.new_message_handler_type(OefMessageHandler, logger=self.logger)
                self.success(conn=conn, url=conn.url, conn_name=conn.name)
                return
            else:
                self.handle_failure(ValueError("bad challenge/response"), conn)
                return
        self.handle_failure(ValueError("bad login message from server"), conn)

    def handle_failure(self, exception, conn):
        self.failure(conn=conn, url=conn.url, ex=exception, conn_name=conn.name)
        conn.close()


from .core import AsyncioCore
from .core import Connection, SecureConnection

Message = dict
Propose = dict
Accept = dict
Decline = dict
BaseMessage = dict
AgentMessage = dict
RegisterDescription = dict
RegisterService = dict
UnregisterDescription = dict

UnregisterService = dict
SearchAgents = dict
SearchServices = dict
SearchServicesWide = dict
OEFErrorOperation = dict
SearchResult = dict
OEFErrorMessage = dict
DialogueErrorMessage = dict


class OEFAgent(OefMessageHandler):
    def __init__(self,
                     public_key,
                     logger=None,
                     core=None,
                     logger_debug=None,
                      oef_addr=None,
                      oef_port=None,
                      oef_url=None,
                     **kwargs):
        self.logger = logger or print
        self.logger_debug = logger_debug or self.my_logger_debug
        self.msg_id = 1
        self.state = "offline"
        self.public_key = public_key
        self.complete = False
        self.url = oef_url or ( "{}:{}".format(oef_addr, oef_port) if (oef_addr != None and oef_port != None) else None)
        self.core = core
        self. _warning_not_implemented_method = print
        self._context_store = {}
        self._error_details_store = {}

    def my_on_connect_ok(self, conn=None, url=None, conn_name=None, **kwargs):
        self.logger("on_connect_ok[{}] ".format(id(conn)), url)
        conn.set_message_handler(self)
        self.state = "connected"
        self.on_connect_success(url=url)

    def my_on_connect_fail(self, conn=None, url=None, conn_name=None, ex=None, **kwargs):
        self.logger("on_connect_fail[{}] ".format(id(conn)), url, " => ", ex)
        self.state = "failed"
        self.on_connect_failed(url=url, ex=ex)

    def my_on_connect_timeout(self, conn=None, url=None, conn_name=None, **kwargs):
        self.logger("on_connect_timeout[{}] ".format(id(conn)), url)
        self.state = "timedout"
        self.on_connect_timeout(url=url)

    def handle_disconnection(self, conn):
        if self.state == "terminated":
            return
        self.state = "terminated"
        self.on_connection_terminated(url=conn.url)

    def my_logger_debug(self, *args):
        self.logger("DEBUG: ", *args)

    def getContext(self, message_id: int, dialogue_id: int, origin: str):
        return self._context_store.get("{}:{}:{}".format(message_id, dialogue_id, origin), uri.Context())

    def getErrorDetail(self, answer_id):
        return self._error_details_store.get(answer_id, {})

    def is_connected(self):
        return self.get_state() == 'connected'

    def get_state(self):
        return self.state

    def incomingAgentMessage(self, agentMessage, connection_name=None, conn=None, **kwargs):
        if super().incomingAgentMessage(agentMessage, connection_name=connection_name, conn=conn):
            return True

        r = False
        for label, k,breaker in [
            ('wide', 'agents_wide', self.break_SearchResultWide),
            ('srch', 'agents', self.break_SearchResult),
            ('Xoef', 'oef_error', self.break_oef_error),
            ('Xdia', 'dialogue_error', self.break_dialogue_error),
            ('msg', lambda x: 'content' in x and 'content' in x['content'], self.break_message),
            ('f_cfp', lambda x: 'content' in x and 'fipa' in x['content'] and 'cfp' in x['content']['fipa'], self.break_fipa_cfp),
            ('f_pro', lambda x: 'content' in x and 'fipa' in x['content'] and 'propose' in x['content']['fipa'], self.break_fipa_propose),
            ('f_acc', lambda x: 'content' in x and 'fipa' in x['content'] and 'accept' in x['content']['fipa'], self.break_fipa_accept),
            ('f_dec', lambda x: 'content' in x and 'fipa' in x['content'] and 'decline' in x['content']['fipa'], self.break_fipa_decline),
        ]:
            if callable(k) and k(agentMessage):
                r = r or breaker(agentMessage)
                break
            elif k in agentMessage:
                r = r or breaker(agentMessage)
                break

        if not r:
            self.logger("OefAgent[{}].incoming:unknown:".format(id(self)), connection_name, agentMessage)
            return False
        else:
            return True

    def stop(self):
        self.complete = True

    def disconnect(self):
        self.conn.close()

    def connect(self, timeout=2) -> bool:
        self.state = "connecting"
        self.conn = Connection(self.core, logger=self.logger)
        self.conn.connect(url=self.url, success=self.my_on_connect_ok, failure=self.my_on_connect_fail, public_key=self.public_key)

        starttime = time.perf_counter();

        while self.state == "connecting":
            delta = time.perf_counter() - starttime;
            if delta > timeout:
                self.my_on_connect_timeout(self.conn, self.url)
            time.sleep(0.1)
        return self.state == "connected"

    def run(self):
        while not self.complete:
            time.sleep(1)

# breakers
    def break_dialogue_error(self, data):
        self.on_dialogue_error(
            data.get('answer_id', -1),
            data.get('dialogue_error', {}).get('dialogue_id', -1),
            data.get('dialogue_error', {}).get('origin', ''),
            )
        return True

    def break_oef_error(self, data):
        self._error_details_store[data.get('answer_id', -1)] = {
            'cause': data.get('oef_error', {}).get('cause', 'unknown'),
            'detail': data.get('oef_error', {}).get('detail', 'unknown'),
        }
        self.on_oef_error(
            data.get('answer_id', -1),
            data.get('oef_error', {}).get('operation', -1),
            )
        self._error_details_store.pop(data.get('answer_id', -1), None)
        return True

    def break_fipa_START(self, data):
        entry_key = "{}:{}:{}".format(
            data.get('answer_id', -1),
            data.get('content', {}).get('dialogue_id', -1),
            data.get('content', {}).get('origin', -1),
        )
        self._context_store[entry_key] = uri.Context()
        self._context_store[entry_key].update(data.get('target_uri', {}), data.get('source_uri', {}))

    def break_fipa_FINISH(self, data):
        entry_key = "{}:{}:{}".format(
            data.get('answer_id', -1),
            data.get('content', {}).get('dialogue_id', -1),
            data.get('content', {}).get('origin', -1),
        )
        self._context_store.pop(entry_key, None)

    def break_fipa_accept(self, data):
        self.break_fipa_START(data)
        self.on_accept(
            data.get('answer_id', -1),
            data.get('content', {}).get('dialogue_id', -1),
            data.get('content', {}).get('origin', ''),
            data.get('content', {}).get('fipa', {}).get('target', -1)
            )
        self.break_fipa_FINISH(data)
        return True

    def break_fipa_decline(self, data):
        self.break_fipa_START(data)
        self.on_decline(
            data.get('answer_id', -1),
            data.get('content', {}).get('dialogue_id', -1),
            data.get('content', {}).get('origin', ''),
            data.get('content', {}).get('fipa', {}).get('target', -1)
            )
        self.break_fipa_FINISH(data)
        return True

    def break_fipa_cfp(self, data):
        self.break_fipa_START(data)
        self.on_cfp(
            data.get('answer_id', -1),
            data.get('content', {}).get('dialogue_id', -1),
            data.get('content', {}).get('origin', ''),
            data.get('content', {}).get('fipa', {}).get('target', -1),
            data.get('content', {}).get('fipa', {}).get('cfp', {}).get('content', b"")
            )
        self.break_fipa_FINISH(data)
        return True

    def break_message(self, data):
        self.break_fipa_START(data)
        self.on_message(
            data.get('answer_id', -1),
            data.get('content', {}).get('dialogue_id', -1),
            data.get('content', {}).get('origin', ''),
            data.get('content', {}).get('content', b"")
        )
        self.break_fipa_FINISH(data)
        return True

    def decodeConstraintValue(valueMessage):
        return {
            'bool':          lambda x: x.b,
            'string':        lambda x: x.s,
            'float':         lambda x: x.f,
            'double':        lambda x: x.d,
            'int32':         lambda x: x.i32,
            'int64':         lambda x: x.i64,

            'bool_list':     lambda x: x.b_s,
            'string_list':   lambda x: x.v_s,
            'float_list':    lambda x: x.v_f,
            'double_list':   lambda x: x.v_d,
            'int32_list':    lambda x: x.v_i32,
            'int64_list':    lambda x: x.v_i64,

            'data_model':    lambda x: x.dm,
            'dm':            lambda x: x.dm,
            'embedding':     lambda x: x.v_d,

            'address': lambda x: x.addr,

            'string_pair':      lambda x: (x.v_s[0], x.v_s[1],),
            'string_pair_list': lambda x: [ ( x.v_d[i], x.v_d[i+1], ) for i in range(0, len(x.v_d), 2) ],

            'string_range':  lambda x: (x.v_s[0], x.v_s[1],),
            'float_range':   lambda x: (x.v_f[0], x.v_f[1],),
            'double_range':  lambda x: (x.v_d[0], x.v_d[1],),
            'int32_range':   lambda x: (x.v_i32[0], x.v_i32[1],),
            'int64_range':   lambda x: (x.v_i64[0], x.v_i64[1],),

            'location':       lambda x: _get_location(x),
            'location_range': lambda x: (_get_location(x.v_l[0]), _get_location(x.v_l[1])),
            'location_list':  lambda x: [_get_location(y) for y in x.v_l],
        }.get(valueMessage.typecode, lambda x: None)(valueMessage)

    def break_fipa_propose(self, data):
        self.break_fipa_START(data)

        content = b''
        if 'content' in data.get('content', {}).get('fipa', {}).get('propose', {}):
            content = data.get('content', {}).get('fipa', {}).get('propose', {}).get('content')
        elif 'proposals' in data.get('content', {}).get('fipa', {}).get('propose', {}):
            Proposals_message = data.get('content', {}).get('fipa', {}).get('propose', {}).get('proposals', {})
            Actions_messages = Proposals_message.get('objects', [])
            content = [
                {
                    a.target_field_name: OEFAgent.decodeConstraintValue(a.query_field_value)
                    for a
                    in act.actions
                }
                for act
                in Actions_messages
            ]

        self.on_propose(
            data.get('answer_id', -1),
            data.get('content', {}).get('dialogue_id', -1),
            data.get('content', {}).get('origin', ''),
            data.get('content', {}).get('fipa', {}).get('target', -1),
            content
        )
        self.break_fipa_FINISH(data)
        return True

    def break_SearchResultWide(self, data):
        items = [
            ValueBag([
                ('public_key', 'agent',),
                ('core_key', 'key',),
                ('core_addr', 'ip',),
                ('core_port', 'port',),
                ('distance', 'distance',),
            ], {
                "agent": y.key,
                "key": x.key,
                "ip": x.ip,
                "port": x.port,
                "distance": x.distance
            })
            for x
            in data.get('agents_wide', {}).get('result', [])
            for y in x.agents
        ]
        self.on_search_result_wide(data.get('answer_id', -1), items)
        return True

    def break_SearchResult(self, data):
        items = [
            x
            for x
            in data.get('agents', {}).get('agents', [])
        ]
        self.on_search_result(data.get('answer_id', -1), items)
        return True

# Verbs

    def register_service(self, msg_id: int, service_description: Description, service_id: str = "") -> None:
        """Register a service. See :func:`~oef.core.OEFCoreInterface.register_service`."""
        self . output(
            data = {
                "msg_id": msg_id,
                "register_service": {
                    "description": service_description
                },
            },
            conn=self.conn
        )

    def unregister_service(self, msg_id: int, service_description: Description, service_id: str = "") -> None:
        """Unregister a service. See :func:`~oef.core.OEFCoreInterface.unregister_service`."""
        self . output(
            data = {
                "msg_id": msg_id,
                "unregister_service": {
                    "description": service_description
                },
            },
            conn=self.conn
        )

    def search_agents(self, search_id: int, query: Query) -> None:
        """Search agents. See :func:`~oef.core.OEFCoreInterface.search_agents`."""
        self . output(
            data = {
                "msg_id": search_id,
                "search_services": {
                "query": query.to_dict()
                }
            },
            conn=self.conn
        )

    def search_services(self, search_id: int, query: Query) -> None:
        """Search services. See :func:`~oef.core.OEFCoreInterface.search_services`."""
        self . output(
            data = {
                "msg_id": search_id,
                "search_services": {
                "query": query.to_dict()
                }
            },
            conn=self.conn
        )

    def search_services_wide(self, search_id: int, query: Query) -> None:
        """Search services widely. See :func:`~oef.core.OEFCoreInterface.search_services_wide`."""
        self . output(
            data = {
                "msg_id": search_id,
                "search_services_wide": {
                "query": query.to_dict()
                }
            },
            conn=self.conn
        )

    def send_message(self, msg_id: int, dialogue_id: int, destination: str, msg: bytes, context=uri.Context()) -> None:
        """Send a simple message. See :func:`~oef.core.OEFCoreInterface.send_message`."""
        self.logger_debug("Agent {}: msg_id={}, dialogue_id={}, destination={}, msg={}"
                     .format(self.public_key, msg_id, dialogue_id, destination, msg))
        self . output(
            data = {
                "msg_id": msg_id,
                "agent_uri": destination,
                "send_message": {
                    "dialogue_id": dialogue_id,
                    "destination": destination,
                    "target_uri": context.targetURI.toString(),
                    "source_uri": context.sourceURI.toString(),
                    "content": msg
                }
            },
            conn=self.conn
        )

    def send_cfp(self, msg_id: int, dialogue_id: int, destination: str, target: int, query: CFP_TYPES, context=uri.Context()) -> None:
        """Send a CFP. See :func:`~oef.core.OEFCoreInterface.send_cfp`."""
        self.logger_debug("Agent {}: msg_id={}, dialogue_id={}, destination={}, target={}, query={}"
                     .format(self.public_key, dialogue_id, destination, query, msg_id, target))
        self . output(
            data = {
                "msg_id": msg_id,
                "agent_uri": destination,
                "send_message": {
                    "dialogue_id": dialogue_id,
                    "destination": destination,
                    "target_uri": context.targetURI.toString(),
                    "source_uri": context.sourceURI.toString(),
                    "fipa": {
                        "target": target,
                        "cfp": {
                            "content": query
                        }
                    }
                }
            },
            conn=self.conn
        )

    def send_propose(self, msg_id: int, dialogue_id: int, destination: str, target: int,
                     proposals: PROPOSE_TYPES, context=uri.Context()) -> None:
        """Send a Propose. See :func:`~oef.core.OEFCoreInterface.send_propose`."""
        self.logger_debug("Agent {}: msg_id={}, dialogue_id={}, destination={}, target={}, proposals={}"
                     .format(self.public_key, msg_id, dialogue_id, destination, target, proposals))
        self . output(
            data = {
                "msg_id": msg_id,
                "agent_uri": destination,
                "send_message": {
                    "dialogue_id": dialogue_id,
                    "destination": destination,
                    "target_uri": context.targetURI.toString(),
                    "source_uri": context.sourceURI.toString(),
                    "fipa": {
                        "target": target,
                        "propose": {
                            ("content" if type(proposals)==bytes else None): proposals,
                            ("proposals" if  type(proposals)!=bytes else None): {
                                "objects": proposals,
                            },
                        }
                    }
                }
            },
            conn=self.conn
        )


    def send_accept(self, msg_id: int, dialogue_id: int, destination: str, target: int, context=uri.Context()) -> None:
        """Send an Accept. See :func:`~oef.core.OEFCoreInterface.send_accept`."""
        self.logger_debug("ACCEPT Agent {}: dialogue_id={}, destination={}, msg_id={}, target={}"
                     .format(self.public_key, msg_id, dialogue_id, destination, target))
        self . output(
            data = {
                "msg_id": msg_id,
                "agent_uri": destination,
                "send_message": {
                    "dialogue_id": dialogue_id,
                    "destination": destination,
                    "target_uri": context.targetURI.toString(),
                    "source_uri": context.sourceURI.toString(),
                    "fipa": {
                        "target": target,
                        "accept": {
                        }
                    }
                }
            },
            conn=self.conn
        )


    def send_decline(self, msg_id: int, dialogue_id: int, destination: str, target: int, context=uri.Context()) -> None:
        """Send a Decline. See :func:`~oef.core.OEFCoreInterface.send_decline`."""
        self.logger_debug("Agent {}: dialogue_id={}, destination={}, msg_id={}, target={}"
                     .format(self.public_key, msg_id, dialogue_id, destination, target))
        self . output(
            data = {
                "msg_id": msg_id,
                "agent_uri": destination,
                "send_message": {
                    "dialogue_id": dialogue_id,
                    "destination": destination,
                    "target_uri": context.targetURI.toString(),
                    "source_uri": context.sourceURI.toString(),
                    "fipa": {
                        "target": target,
                        "decline": {
                        }
                    }
                }
            },
            conn=self.conn
        )


# Callbacks

    def on_connect_success(self, url=None):
        pass

    def on_connect_timeout(self, url=None):
        self.on_connect_failed(url=url, ex=Exception('timeout'))

    def on_connect_failed(self, url=None, ex=None):
        pass

    def on_connection_terminated(self, url=None):
        pass

    def on_message(self, msg_id: int, dialogue_id: int, origin: str, content: bytes):
        self.logger_debug("on_message: msg_id={}, dialogue_id={}, origin={}, content={}"
                     .format(msg_id, dialogue_id, origin, content))
        self._warning_not_implemented_method(self.on_message.__name__)

    def on_cfp(self, msg_id: int, dialogue_id: int, origin: str, target: int, query: CFP_TYPES):
        self.logger_debug("on_cfp: msg_id={}, dialogue_id={}, origin={}, target={}, query={}"
                     .format(msg_id, dialogue_id, origin, target, query))
        self._warning_not_implemented_method(self.on_cfp.__name__)

    def on_propose(self, msg_id: int, dialogue_id: int, origin: str, target: int, proposals: PROPOSE_TYPES):
        self.logger_debug("on_propose: msg_id={}, dialogue_id={}, origin={}, target={}, proposals={}"
                     .format(msg_id, dialogue_id, origin, target, proposals))
        self._warning_not_implemented_method(self.on_propose.__name__)

    def on_accept(self, msg_id: int, dialogue_id: int, origin: str, target: int):
        self.logger_debug("on_accept: msg_id={}, dialogue_id={}, origin={}, target={}"
                     .format(msg_id, dialogue_id, origin, target))
        self._warning_not_implemented_method(self.on_accept.__name__)

    def on_decline(self, msg_id: int, dialogue_id: int, origin: str, target: int):
        self.logger_debug("on_accept: msg_id={}, dialogue_id={}, origin={}, target={}"
                     .format(msg_id, dialogue_id, origin, target))
        self._warning_not_implemented_method(self.on_decline.__name__)

    def on_oef_error(self, answer_id: int, operation: OEFErrorOperation):
        self.logger_debug("on_oef_error: answer_id={}, operation={}".format(answer_id, operation))
        self._warning_not_implemented_method(self.on_oef_error.__name__)

    def on_dialogue_error(self, answer_id: int, dialogue_id: int, origin: str):
        self.logger_debug("on_dialogue_error: answer_id={}, dialogue_id={}, origin={}"
                     .format(answer_id, dialogue_id, origin))
        self._warning_not_implemented_method(self.on_dialogue_error.__name__)

    def on_search_result(self, search_id: int, agents: List[str]):
        self.logger_debug("on_search_result: search_id={}, agents={}".format(search_id, agents))
        self._warning_not_implemented_method(self.on_search_result.__name__)

    def on_search_result_wide(self, search_id: int, agents: List[ValueBag]):
        self.logger_debug("on_search_result_wide: search_id={}, agents={}".format(search_id, agents))
        self._warning_not_implemented_method(self.on_search_result_wide.__name__)

class OEFSecureAgent(OEFAgent):
    def __init__(self,
                     public_key,
                     prv_key_file,
                     logger=None,
                     core=None,
                     logger_debug=None,
                      oef_addr=None,
                      oef_port=None,
                      oef_url=None,
                     **kwargs):
        super().__init__(public_key, logger, core, logger_debug, oef_addr, oef_port, oef_url, **kwargs)
        self.private_key_file = prv_key_file

    def connect(self) -> bool:
        self.state = "connecting"
        self.conn = SecureConnection(self.private_key_file, self.core, logger=self.logger)
        self.conn.connect(url=self.url, success=self.my_on_connect_ok, failure=self.my_on_connect_fail, public_key=self.public_key)

        while self.state == "connecting":
            time.sleep(0.1)
        return self.state == "connected"

Agent = OEFAgent
