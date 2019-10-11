#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""The BrickAdapter get's passed into the brick's module on execution"""
from titanfe.constants import DEFAULT_PORT
from .packet import Packet


class BrickAdapter:  # pylint: disable=too-few-public-methods
    """The BrickAdapter get's passed into the brick's module on execution

    Arguments:
            result_put_callback (Callable): callback to output a result to the runner
            log (logging.Logger): the logger instance of the parent runner

    Attributes
        log: a logging.logger instance to be used from within the brick's module
            if one wants to have something in the general application log.
    """

    def __init__(self, brick_name, result_put_callback, log):
        self.log = log.getChild(f"BrickAdapter.{brick_name}")
        self.__put_packet = result_put_callback
        # TODO: deprecate:
        self.terminated = False
        self.stop_processing = lambda: None

    def emit_new_packet(self, value, port=DEFAULT_PORT):
        """A new packet will be created from the given value and infused into the flow of data.

        Note:
            This will create and output a new packet into the flow.
            To modify the payload of an already travelling packet,
            simply return a value from the brick processing method.

        Args:
            value (Any): Any value
        """

        self.log.debug("brick output: %r , port: %s" % (value, port))
        self.__put_packet((Packet(payload=value), port))
