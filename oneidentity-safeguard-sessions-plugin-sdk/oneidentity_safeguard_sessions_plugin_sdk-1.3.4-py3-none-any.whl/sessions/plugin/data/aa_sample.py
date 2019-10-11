#
# Copyright (c) 2006-2019 Balabit
# All Rights Reserved.
#
from copy import deepcopy


class GatewayAndTargetUserDiffer(RuntimeError):
    pass


scenarios = {}


def scenario(cls):
    scenarios[cls.__name__] = cls
    return cls


class Parameters(dict):
    description = ""

    def __init__(self, cookie=None, session_cookie=None, protocol=None, gateway_user=None, gateway_groups=None,
                 target_username=None, target_server=None, target_port=None, key_value_pairs=None):
        super().__init__(
            cookie=cookie if isinstance(cookie, dict) else {},
            session_cookie=session_cookie if isinstance(session_cookie, dict) else {},
            session_id='{}-example-1'.format(protocol) if protocol else 'example-1',
            connection_name='example',
            protocol=protocol,
            client_ip='1.2.3.4',
            client_port=12341,
            gateway_user=gateway_user,
            gateway_groups=gateway_groups,
            target_username=target_username,
            target_server=target_server,
            target_port=target_port,
            key_value_pairs=key_value_pairs if isinstance(key_value_pairs, dict) else {},
        )

    def __setitem__(self, key, value):
        if key in self:
            return super().__setitem__(key, value)
        else:
            raise KeyError("May not create new keys.")

    def __delitem__(self, key):
        raise NotImplementedError()

    @property
    def mfa_password(self):
        return self['key_value_pairs'].get('otp')

    @mfa_password.setter
    def mfa_password(self, value):
        self['key_value_pairs']['otp'] = value

    @property
    def otp(self):
        return self.mfa_password

    @otp.setter
    def otp(self, value):
        self.mfa_password = value

    def answer_question(self, key, value):
        self['key_value_pairs'][key] = value

    def make_copy(self):
        return deepcopy(dict(self))


@scenario
class SshWithoutGatewayAuth(Parameters):
    description = "SSH session without priory gateway authentication"

    def __init__(self, target_username, gateway_user, **kwargs):
        if target_username != gateway_user:
            raise GatewayAndTargetUserDiffer()
        super().__init__(
            target_username=target_username if target_username else "gatewayuser",
            protocol='ssh',
            target_port=22,
            target_server='5.6.7.8',
            **kwargs
        )


@scenario
class SshWithGatewayAuth(Parameters):
    description = "SSH session with gateway authentication"

    def __init__(self, target_username, gateway_user, **kwargs):
        super().__init__(
            target_username=target_username if target_username else "targetuser",
            gateway_user=gateway_user if gateway_user else "gatewayuser",
            protocol='ssh',
            target_port=22,
            target_server='5.6.7.8',
            **kwargs
        )


@scenario
class RdpWithoutGatewayAuth(Parameters):
    description = "RDP session without gateway authentication"

    def __init__(self, gateway_user, **kwargs):
        super().__init__(
            protocol='rdp',
            **kwargs,
        )
        self['key_value_pairs']['username'] = gateway_user if gateway_user else "gatewayuser"


@scenario
class RdpWithGatewayAuth(Parameters):
    description = "RDP session with gateway authentication"

    def __init__(self, gateway_user, **kwargs):
        super().__init__(
            protocol='rdp',
            gateway_user=gateway_user if gateway_user else "gatewayuser",
            **kwargs,
        )
