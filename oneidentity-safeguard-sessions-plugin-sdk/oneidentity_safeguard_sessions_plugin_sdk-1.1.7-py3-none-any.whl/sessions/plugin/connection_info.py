#
# Copyright (c) 2006-2019 Balabit
# All Rights Reserved.
#
"""
.. py:module:: safeguard.sessions.plugin.connection_info
    :synopsis: Read-only container for parameters passed to AAA plugins.
"""


class ConnectionInfo:
    """
    The :class:`ConnectionInfo` class gives easy access to the parameters passed to an AAA plugin. It is meant to
    represent a read-only record of the SPS sessions being processed. It is also the means to pass many parameters
    between functions if needed.
    """
    def __init__(self, session_id=None, protocol=None, connection_name=None, client_ip=None, client_port=None,
                 gateway_user=None, target_username=None, key_value_pairs=None, gateway_groups=None, target_server=None,
                 target_port=None, gateway_domain=None):
        self._session_id = session_id
        self._protocol = protocol
        self._connection_name = connection_name
        self._client_ip = client_ip
        self._client_port = client_port
        self._gateway_user = gateway_user
        self._target_username = target_username
        self._key_value_pairs = key_value_pairs
        self._gateway_groups = gateway_groups
        self._target_server = target_server
        self._target_port = target_port
        self._gateway_domain = gateway_domain

    @property
    def session_id(self):
        """
        The unique identifier of the session.
        """
        return self._session_id

    @property
    def protocol(self):
        """
        The protocol used in the connection, one of ssh, telnet, rdp.
        """
        return self._protocol

    @property
    def connection_name(self):
        """
        Name of the connection policy (<protocol> Control -> Connections).
        """
        return self._connection_name

    @property
    def client_ip(self):
        """
        A string containing the IP address of the client.
        """
        return self._client_ip

    @property
    def client_port(self):
        """
        The port number of the client.
        """
        return self._client_port

    @property
    def gateway_user(self):
        """
        Contains the gateway username of the client, if already available (for example, if the user performed inband
        gateway authentication), otherwise its value is None.
        """
        return self._gateway_user

    @property
    def target_username(self):
        """
        The user name SPS uses to authenticate on the target server.
        """
        return self._target_username

    @property
    def key_value_pairs(self):
        """
        A dictionary containing plugin-specific information, for example, it may include the username. This dictionary
        also contains any key-value pairs that the user specified. In the plugin, such fields are already parsed into
        separate key-value pairs.
        """
        return self._key_value_pairs

    @property
    def gateway_groups(self):
        """
        The gateway groups of the gateway user as calculated by SPS.
        """
        return self._gateway_groups

    @property
    def target_server(self):
        """
        A string containing the IP address of the target server.
        """
        return self._target_server

    @property
    def target_port(self):
        """
        The port number on the target server.
        """
        return self._target_port

    @property
    def gateway_domain(self):
        """
        The domain name of the gateway user if known.
        """
        return self._gateway_domain
