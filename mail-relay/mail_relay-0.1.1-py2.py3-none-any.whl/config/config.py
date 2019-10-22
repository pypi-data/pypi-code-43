class SMTPConfig(object):
    def __init__(self, host, port, username, password, send_to_user, use_tls=False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.send_to_user = send_to_user

    def to_json(self):
        return {
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'password': self.password,
            'use_tls': self.use_tls,
            'send_to_user': self.send_to_user
        }


class IMAPConfig(object):
    def __init__(self, host, port, username, password, use_tls=False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def to_json(self):
        return {
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'password': self.password,
            'use_tls': self.use_tls
        }


class CSConfig(object):
    def __init__(self, host, port, use_tls=False):
        self.host = host
        self.port = port
        self.use_tls = use_tls

    @property
    def http(self):
        return u'{}://{}{}'.format(
            'https' if self.use_tls else 'http',
            self.host,
            '' if self.port == 80 else ':{}'.format(self.port))

    @property
    def ws(self):
        return u'{}://{}{}'.format(
            'wss' if self.use_tls else 'ws',
            self.host,
            '' if self.port == 80 else ':{}'.format(self.port))

    def to_json(self):
        return {
            'host': self.host,
            'port': self.port,
            'use_tls': self.use_tls
        }


class Config(object):
    def __init__(self, smtp, imap, cs):
        self.smtp = smtp
        self.imap = imap
        self.cs = cs
        # more to add

    @classmethod
    def from_yaml(cls, yaml_file):
        from pvHelpers.utils import read_yaml_config

        y = read_yaml_config(yaml_file)
        return cls.from_json(y)

    @classmethod
    def from_json(cls, j):
        s, i, cs = j['smtp'], j['imap'], j['cs']
        return cls(
            SMTPConfig(s['host'], s['port'], s['username'], s['password'], s['send_to_user'], s['use_tls']),
            IMAPConfig(i['host'], i['port'], i['username'], i['password'], i['use_tls']),
            CSConfig(cs['host'], cs['port'], cs['use_tls']))

    def __repr__(self):
        return str(self.to_json())

    def to_json(self):
        return {
            'smtp': self.smtp.to_json(),
            'imap': self.imap.to_json(),
            'cs': self.cs.to_json()
        }
