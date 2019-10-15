import select
import time
from typing import *

from zuper_ipce.json2cbor import read_next_cbor

from zuper_commons.text import indent

from zuper_nodes.structures import ExternalTimeout
from zuper_nodes_wrapper.struct import interpret_control_message, RawTopicMessage, ControlMessage
from . import logger
from .constants import *

M = Union[RawTopicMessage, ControlMessage]


def inputs(f, give_up: Optional[float] = None, waiting_for: str = None) -> Iterator[M]:
    last = time.time()
    intermediate_timeout = 3.0
    intermediate_timeout_multiplier = 1.5
    while True:
        readyr, readyw, readyx = select.select([f], [], [f], intermediate_timeout)
        if readyr:
            try:
                parsed = read_next_cbor(f, waiting_for=waiting_for)
            except StopIteration:
                return

            if not isinstance(parsed, dict):
                msg = f'Expected a dictionary, obtained {parsed!r}'
                logger.error(msg)
                continue

            if FIELD_CONTROL in parsed:
                m = interpret_control_message(parsed)
                yield m
            elif FIELD_TOPIC in parsed:

                if not FIELD_COMPAT in parsed:
                    msg = f'Could not find field "compat" in structure "{parsed}".'
                    logger.error(msg)
                    continue

                l = parsed[FIELD_COMPAT]
                if not isinstance(l, list):
                    msg = f'Expected a list for compatibility value, found {l!r}'
                    logger.error(msg)
                    continue

                if not CUR_PROTOCOL in parsed[FIELD_COMPAT]:
                    msg = f'Skipping message because could not find {CUR_PROTOCOL} in {l}.'
                    logger.warn(msg)
                    continue

                rtm = RawTopicMessage(parsed[FIELD_TOPIC],
                                      parsed.get(FIELD_DATA, None),
                                      parsed.get(FIELD_TIMING, None))
                yield rtm

        elif readyx:
            logger.warning('Exceptional condition on input channel %s' % readyx)
        else:
            delta = time.time() - last
            if give_up is not None and (delta > give_up):
                msg = f'I am giving up after %.1f seconds.' % delta
                raise ExternalTimeout(msg)
            else:
                intermediate_timeout *= intermediate_timeout_multiplier
                msg = f'Input channel not ready after %.1f seconds. Will re-try.' % delta
                if waiting_for:
                    msg += '\n' + indent(waiting_for, '> ')
                msg = 'I will warn again in %.1f seconds.' % intermediate_timeout
                logger.warning(msg)
