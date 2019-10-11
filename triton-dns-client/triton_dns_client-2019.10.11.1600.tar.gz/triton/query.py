import re
import typing
from ipaddress import IPv6Address, IPv4Address, AddressValueError

import triton
from triton.dns import Message


class Query:
    """
    Main class for resolving domain names
    """

    def __init__(self, ip: typing.Union[IPv6Address, IPv4Address, str],
                 domain: typing.Text,
                 type=1,
                 cls=1,
                 use_cache=True,
                 custom_cache=None,
                 loop=None,
                 dnssec=True,
                 timeout=5,
                 retries=3):
        self.loop = triton.loop if not loop else loop
        self.cache = triton.cache if not custom_cache else custom_cache
        self.use_cache = use_cache
        self.dnssec = dnssec
        self.timeout = timeout
        self.retries = retries
        self.nameserver = self.str_to_ip(ip)
        self.target = domain
        self.type = type
        self.cls = cls
        self.validate()

    @staticmethod
    def str_to_ip(str_ip):
        if isinstance(str_ip, IPv4Address) or isinstance(str_ip, IPv6Address):
            return str_ip
        try:
            ip = IPv6Address(str_ip)
            return ip
        except AddressValueError:
            ip = IPv4Address(str_ip)
            return ip

    def validate(self):
        assert isinstance(self.target, str)
        assert re.match('^(?:[\*]?(?:\.)?[A-z\-0-9]+){0,10}$', self.target) or self.target == '.'
        assert self.type in [x.id for x in triton.dns.message.rdata.ResourceRecord.__subclasses__()]
        assert self.cls == 1

    @classmethod
    async def create_and_resolve(cls,
                                 ip: typing.Union[IPv6Address, IPv4Address, str],
                                 domain: typing.Text,
                                 qtype=1,
                                 qcls=1,
                                 use_cache=True,
                                 custom_cache=None,
                                 loop=None,
                                 dnssec=True,
                                 timeout=5,
                                 retries=3):
        instance = cls(ip, domain, qtype, qcls, use_cache, custom_cache, loop, dnssec, timeout, retries)
        return await instance.resolve()

    async def resolve(self):
        question_message = Message.create_question(name=self.target,
                                                   qtype=self.type,
                                                   qclass=self.cls,
                                                   dnssec=self.dnssec)
        if self.use_cache:
            result = self.cache.find(self.target, self.type, self.cls)
            if result:
                return result
            result = await triton.protocol.UdpClient.send_message(message=question_message,
                                                                  host=self.nameserver,
                                                                  timeout=self.timeout,
                                                                  retries=self.retries,
                                                                  loop=self.loop)
            if result:
                self.cache.store(result)
                return result
        else:
            return await triton.protocol.UdpClient.send_message(message=question_message,
                                                                host=self.nameserver,
                                                                timeout=self.timeout,
                                                                retries=self.retries,
                                                                loop=self.loop)

    def sync_resolve(self):
        question_message = Message.create_question(name=self.target,
                                                   qtype=self.type,
                                                   qclass=self.cls,
                                                   dnssec=self.dnssec)

        return self.loop.run_until_complete(triton.protocol.UdpClient.send_message(message=question_message,
                                                                                   host=self.nameserver,
                                                                                   timeout=self.timeout,
                                                                                   retries=self.retries))
