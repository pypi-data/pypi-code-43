#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyraii.close import close_multiple
from pyraii.resource_concept import is_resource


def iter_owned_resources(thing):
    return (value for name, value in thing.__dict__.items() if is_resource(value))


class ResourceOwner(object):
    """
    short hand resource destruction wrapping without any particular order
    .. code-block:: python
        class Server(ResourceOwner):
            def __init__():
                self.socket_a = get_socket()
                self.socket_b = get_other_socket()
                self._log_file = open_log_file()
                self._data = "asdasd"

        my_server = Server()
        my_server.close()
    in the example above will close in some order `socket_a` 'socket_b` `log_file`
    """
    def close(self):
        """
        Close order of the resources is not defined.
        If you want to control the close order use a `ResourceList`
        .. code-block::python
        """
        close_multiple(list(iter_owned_resources(self)))


