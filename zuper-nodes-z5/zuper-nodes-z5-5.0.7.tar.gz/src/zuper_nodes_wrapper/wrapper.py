import argparse
import json
import os
import socket
import time
import traceback
from dataclasses import dataclass
from typing import *

import yaml
from zuper_ipce import object_from_ipce, ipce_from_object, IESO

from contracts.utils import format_obs
from zuper_commons.text import indent
from zuper_commons.types import check_isinstance

from zuper_nodes import InteractionProtocol, InputReceived, OutputProduced, Unexpected, LanguageChecker
from zuper_nodes.structures import TimingInfo, local_time, TimeSpec, timestamp_from_seconds, DecodingError, \
    ExternalProtocolViolation, NotConforming, ExternalTimeout, InternalProblem
from .reading import inputs
from .streams import open_for_read, open_for_write
from .struct import RawTopicMessage, ControlMessage
from .utils import call_if_fun_exists
from .writing import Sink
from . import logger, logger_interaction
from .interface import Context
from .meta_protocol import basic_protocol, SetConfig, ProtocolDescription, ConfigDescription, \
    BuildDescription, NodeDescription


class ConcreteContext(Context):
    protocol: InteractionProtocol
    to_write: List[RawTopicMessage]

    def __init__(self, sink: Sink, protocol: InteractionProtocol,
                 node_name: str, tout: Dict[str, str]):
        self.sink = sink
        self.protocol = protocol
        self.pc = LanguageChecker(protocol.interaction)
        self.node_name = node_name
        self.hostname = socket.gethostname()
        self.tout = tout

        self.to_write = []
        self.last_timing = None

    def set_last_timing(self, timing: TimingInfo):
        self.last_timing = timing

    def get_hostname(self):
        return self.hostname

    def write(self, topic, data, timing=None, with_schema=False):
        if topic not in self.protocol.outputs:
            msg = f'Output channel "{topic}" not found in protocol; know {sorted(self.protocol.outputs)}.'
            raise Exception(msg)

        # logger.info(f'Writing output "{topic}".')

        klass = self.protocol.outputs[topic]
        if isinstance(klass, type):
            check_isinstance(data, klass)

        event = OutputProduced(topic)
        res = self.pc.push(event)
        if isinstance(res, Unexpected):
            msg = f'Unexpected output {topic}: {res}'
            logger.error(msg)
            return

        klass = self.protocol.outputs[topic]

        if isinstance(data, dict):
            data = object_from_ipce(data, klass)

        if timing is None:
            timing = self.last_timing

        if timing is not None:
            s = time.time()
            if timing.received is None:
                # XXX
                time1 = timestamp_from_seconds(s)
            else:
                time1 = timing.received.time
            processed = TimeSpec(time=time1,
                                 time2=timestamp_from_seconds(s),
                                 frame='epoch',
                                 clock=socket.gethostname())
            timing.processed[self.node_name] = processed
            timing.received = None

        topic_o = self.tout.get(topic, topic)
        ieso = IESO(use_ipce_from_typelike_cache=True, with_schema=with_schema)
        data = ipce_from_object(data, ieso=ieso)

        if timing is not None:
            ieso = IESO(use_ipce_from_typelike_cache=True, with_schema=False)
            timing_o = ipce_from_object(timing, ieso=ieso)
        else:
            timing_o = None

        rtm = RawTopicMessage(topic_o, data, timing_o)
        self.to_write.append(rtm)

    def get_to_write(self) -> List[RawTopicMessage]:
        """ Returns the messages to send and resets the queue"""
        res = self.to_write
        self.to_write = []
        return res

    def log(self, s):
        prefix = f'{self.hostname}:{self.node_name}: '
        logger.info(prefix + s)

    def info(self, s):
        prefix = f'{self.hostname}:{self.node_name}: '
        logger.info(prefix + s)

    def debug(self, s):
        prefix = f'{self.hostname}:{self.node_name}: '
        logger.debug(prefix + s)

    def warning(self, s):
        prefix = f'{self.hostname}:{self.node_name}: '
        logger.warning(prefix + s)

    def error(self, s):
        prefix = f'{self.hostname}:{self.node_name}: '
        logger.error(prefix + s)


def get_translation_table(t: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    tout = {}
    tin = {}
    for t in t.split(','):
        ts = t.split(':')
        if ts[0] == 'in':
            tin[ts[1]] = ts[2]

        if ts[0] == 'out':
            tout[ts[1]] = ts[2]

    return tin, tout


def check_variables():
    for k, v in os.environ.items():
        if k.startswith('AIDO') and k not in KNOWN:
            msg = f'I do not expect variable "{k}" set in environment with value "{v}".'
            msg += ' I expect: %s' % ", ".join(KNOWN)
            logger.warn(msg)


from .constants import *


def run_loop(node, protocol: InteractionProtocol, args: Optional[List[str]] = None):
    parser = argparse.ArgumentParser()

    check_variables()

    data_in = os.environ.get(ENV_DATA_IN, '/dev/stdin')
    data_out = os.environ.get(ENV_DATA_OUT, '/dev/stdout')
    default_name = os.environ.get(ENV_NAME, None)
    translate = os.environ.get(ENV_TRANSLATE, '')
    config = os.environ.get(ENV_CONFIG, '{}')

    parser.add_argument('--data-in', default=data_in)
    parser.add_argument('--data-out', default=data_out)

    parser.add_argument('--name', default=default_name)
    parser.add_argument('--config', default=config)
    parser.add_argument('--translate', default=translate)
    parser.add_argument('--loose', default=False, action='store_true')

    parsed = parser.parse_args(args)

    tin, tout = get_translation_table(parsed.translate)

    # expect in:name1:name2, out:name2:name1

    fin = parsed.data_in
    fout = parsed.data_out

    fi = open_for_read(fin)
    fo = open_for_write(fout)

    node_name = parsed.name or type(node).__name__

    logger.name = node_name

    config = yaml.load(config, Loader=yaml.SafeLoader)
    try:
        loop(node_name, fi, fo, node, protocol, tin, tout,
             config=config)
    except BaseException as e:
        msg = f'Error in node {node_name}'
        logger.error(f'Error in node {node_name}: \n{traceback.format_exc()}')
        raise Exception(msg) from e
    finally:
        fo.flush()
        fo.close()
        fi.close()


def loop(node_name: str, fi, fo, node, protocol: InteractionProtocol, tin, tout, config: dict):
    logger.info(f'Starting reading')
    initialized = False
    context_data = None
    sink = Sink(fo)
    try:
        context_data = ConcreteContext(sink=sink, protocol=protocol,
                                       node_name=node_name, tout=tout)
        context_meta = ConcreteContext(sink=sink, protocol=basic_protocol,
                                       node_name=node_name + '.wrapper', tout=tout)

        wrapper = MetaHandler(node, protocol)
        for k, v in config.items():
            wrapper.set_config(k, v)

        waiting_for = 'Expecting control message or one of:  %s' % context_data.pc.get_expected_events()

        for parsed in inputs(fi, waiting_for=waiting_for):
            if isinstance(parsed, ControlMessage):
                expect = [CTRL_CAPABILITIES]
                if parsed.code not in expect:
                    msg = f'I expect any of {expect}, not "{parsed.code}".'
                    sink.write_control_message(CTRL_NOT_UNDERSTOOD, msg)
                    sink.write_control_message(CTRL_OVER)
                else:

                    if parsed.code == CTRL_CAPABILITIES:
                        my_capabilities = {
                            'z2': {
                                CAPABILITY_PROTOCOL_REFLECTION: True
                            }
                        }
                        sink.write_control_message(CTRL_UNDERSTOOD)
                        sink.write_control_message(CTRL_CAPABILITIES, my_capabilities)
                        sink.write_control_message(CTRL_OVER)
                    else:
                        assert False

            elif isinstance(parsed, RawTopicMessage):

                parsed.topic = tin.get(parsed.topic, parsed.topic)
                logger_interaction.info(f'Received message of topic "{parsed.topic}".')
                if parsed.topic.startswith('wrapper.'):
                    parsed.topic = parsed.topic.replace('wrapper.', '')
                    receiver0 = wrapper
                    context0 = context_meta

                else:
                    receiver0 = node
                    context0 = context_data

                if receiver0 is node and not initialized:
                    try:
                        call_if_fun_exists(node, 'init', context=context_data)
                    except BaseException as e:
                        msg = "Exception while calling the node's init() function."
                        msg += '\n\n' + indent(traceback.format_exc(), '| ')
                        context_meta.write('aborted', msg)
                        raise Exception(msg) from e
                    initialized = True

                if parsed.topic not in context0.protocol.inputs:
                    msg = f'Input channel "{parsed.topic}" not found in protocol. '
                    msg += f'\n\nKnown channels: {sorted(context0.protocol.inputs)}'
                    sink.write_control_message(CTRL_NOT_UNDERSTOOD, msg)
                    sink.write_control_message(CTRL_OVER)
                    raise ExternalProtocolViolation(msg)

                sink.write_control_message(CTRL_UNDERSTOOD)
                try:
                    handle_message_node(parsed, receiver0, context0)
                    to_write = context0.get_to_write()
                    # msg = f'I wrote {len(to_write)} messages.'
                    # logger.info(msg)
                    for rtm in to_write:
                        sink.write_topic_message(rtm.topic, rtm.data, rtm.timing)
                    sink.write_control_message(CTRL_OVER)
                except BaseException as e:
                    msg = f'Exception while handling a message on topic "{parsed.topic}".'
                    msg += '\n\n' + indent(traceback.format_exc(), '| ')
                    sink.write_control_message(CTRL_ABORTED, msg)
                    sink.write_control_message(CTRL_OVER)
                    raise InternalProblem(msg) from e  # XXX
            else:
                assert False

        res = context_data.pc.finish()
        if isinstance(res, Unexpected):
            msg = f'Protocol did not finish: {res}'
            logger_interaction.error(msg)

        if initialized:
            try:
                call_if_fun_exists(node, 'finish', context=context_data)
            except BaseException as e:
                msg = "Exception while calling the node's finish() function."
                msg += '\n\n' + indent(traceback.format_exc(), '| ')
                context_meta.write('aborted', msg)
                raise Exception(msg) from e

    except BrokenPipeError:
        msg = 'The other side closed communication.'
        logger.info(msg)
        return
    except ExternalTimeout as e:
        msg = 'Could not receive any other messages.'
        if context_data:
            msg += '\n Expecting one of:  %s' % context_data.pc.get_expected_events()
        sink.write_control_message(CTRL_ABORTED, msg)
        sink.write_control_message(CTRL_OVER)
        raise ExternalTimeout(msg) from e
    except InternalProblem:
        raise
    except BaseException as e:
        msg = f"Unexpected error:"
        msg += '\n\n' + indent(traceback.format_exc(), '| ')
        sink.write_control_message(CTRL_ABORTED, msg)
        sink.write_control_message(CTRL_OVER)
        raise InternalProblem(msg) from e  # XXX


class MetaHandler:
    def __init__(self, node, protocol):
        self.node = node
        self.protocol = protocol

    def set_config(self, key, value):
        if hasattr(self.node, ATT_CONFIG):
            config = self.node.config
            if hasattr(config, key):
                setattr(self.node.config, key, value)
            else:
                msg = f'Could not find config key {key}'
                raise ValueError(msg)

        else:
            msg = 'Node does not have the "config" attribute.'
            raise ValueError(msg)

    def on_received_set_config(self, context, data: SetConfig):
        key = data.key
        value = data.value

        try:
            self.set_config(key, value)
        except ValueError as e:
            context.write('set_config_error', str(e))
        else:
            context.write('set_config_ack', None)

    def on_received_describe_protocol(self, context):
        desc = ProtocolDescription(data=self.protocol, meta=basic_protocol)
        context.write('protocol_description', desc)

    def on_received_describe_config(self, context):
        K = type(self.node)
        if hasattr(K, '__annotations__') and ATT_CONFIG in K.__annotations__:
            config_type = K.__annotations__[ATT_CONFIG]
            config_current = getattr(self.node, ATT_CONFIG)
        else:
            @dataclass
            class NoConfig:
                pass

            config_type = NoConfig
            config_current = NoConfig()
        desc = ConfigDescription(config=config_type, current=config_current)
        context.write('config_description', desc, with_schema=True)

    def on_received_describe_node(self, context):
        desc = NodeDescription(self.node.__doc__)

        context.write('node_description', desc, with_schema=True)

    def on_received_describe_build(self, context):
        desc = BuildDescription()

        context.write('build_description', desc, with_schema=True)


def handle_message_node(parsed: RawTopicMessage,
                        agent, context: ConcreteContext):
    protocol = context.protocol
    topic = parsed.topic
    data = parsed.data
    pc = context.pc

    klass = protocol.inputs[topic]
    try:
        ob = object_from_ipce(data,  klass)
    except BaseException as e:
        msg = f'Cannot deserialize object for topic "{topic}" expecting {klass}.'
        try:
            parsed = json.dumps(parsed, indent=2)
        except:
            parsed = str(parsed)
        msg += '\n\n' + indent(parsed, '|', 'parsed: |')
        raise DecodingError(msg) from e

    if parsed.timing is not None:
        timing = object_from_ipce(parsed.timing,  TimingInfo)
    else:
        timing = TimingInfo()

    timing.received = local_time()

    context.set_last_timing(timing)
    # logger.info(f'Before push the state is\n{pc}')

    event = InputReceived(topic)
    expected = pc.get_expected_events()

    res = pc.push(event)

    # names = pc.get_active_states_names()
    # logger.info(f'After push of {event}: result \n{res} active {names}' )
    if isinstance(res, Unexpected):
        msg = f'Unexpected input "{topic}": {res}'
        msg += f'\nI expected: {expected}'
        msg += '\n' + format_obs(dict(pc=pc))
        logger.error(msg)
        raise ExternalProtocolViolation(msg)
    else:
        expect_fn = f'on_received_{topic}'
        call_if_fun_exists(agent, expect_fn, data=ob, context=context, timing=timing)


def check_implementation(node, protocol: InteractionProtocol):
    logger.info('checking implementation')
    for n in protocol.inputs:
        expect_fn = f'on_received_{n}'
        if not hasattr(node, expect_fn):
            msg = f'Missing function {expect_fn}'
            msg += f'\nI know {sorted(type(node).__dict__)}'
            raise NotConforming(msg)

    for x in type(node).__dict__:
        if x.startswith('on_received_'):
            input_name = x.replace('on_received_', '')
            if input_name not in protocol.inputs:
                msg = f'The node has function "{x}" but there is no input "{input_name}".'
                raise NotConforming(msg)
