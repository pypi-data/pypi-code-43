from ipaddress import IPv4Address, IPv6Address, AddressValueError
import asyncio
import datetime
import triton
from . import exceptions

root_nameservers = {
        'a.root-servers.net': [IPv4Address('198.41.0.4'), IPv6Address('2001:503:ba3e::2:30')],
        'b.root-servers.net': [IPv4Address('199.9.14.201'), IPv6Address('2001:500:200::b')],
        'c.root-servers.net': [IPv4Address('192.33.4.12'), IPv6Address('2001:500:2::c')],
        'd.root-servers.net': [IPv4Address('199.7.91.13'), IPv6Address('2001:500:2d::d')],
        'e.root-servers.net': [IPv4Address('192.203.230.10'), IPv6Address('2001:500:a8::e')],
        'f.root-servers.net': [IPv4Address('192.5.5.241'), IPv6Address('2001:500:2f::f')],
        'g.root-servers.net': [IPv4Address('192.112.36.4'), IPv6Address('2001:500:12::d0d')],
        'h.root-servers.net': [IPv4Address('198.97.190.53'), IPv6Address('2001:500:1::53')],
        'i.root-servers.net': [IPv4Address('192.36.148.17'), IPv6Address('2001:7fe::53')],
        'j.root-servers.net': [IPv4Address('192.58.128.30'), IPv6Address('2001:503:c27::2:30')],
        'k.root-servers.net': [IPv4Address('193.0.14.129'), IPv6Address('2001:7fd::1')],
        'l.root-servers.net': [IPv4Address('199.7.83.42'), IPv6Address('2001:500:9f::42')],
        'm.root-servers.net': [IPv4Address('202.12.27.33'), IPv6Address('2001:dc3::35')],
    }


class Domain:
    def __init__(self, cache, name):
        self.cache = cache
        self.name = name
        self.resource_records = []

    def remove_rr(self, instance):
        for n, addr in enumerate(self.resource_records.copy()):
            if addr is instance:
                self.resource_records.pop(n)

    async def check_remaining(self):
        if not self.resource_records:
            self.cache.remove_domain(self)

    def add_resource_record(self, rr):
        assert isinstance(rr, triton.dns.message.Answer)
        assert rr not in self.resource_records
        self.resource_records.append(rr)
        rr._expire_at = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=rr.ttl)
        setattr(rr.__class__, 'expire', rr_expire)
        setattr(rr.__class__, 'rr_auto_pop_self', rr_auto_pop_self)
        rr.domain = self
        asyncio.Task(rr.rr_auto_pop_self(), loop=self.cache.loop)
        return rr

    def all_rr_by_type(self, *types):
        return [rr for rr in self.resource_records if rr._type in types]

    @property
    def nameservers(self):
        return self.all_rr_by_type(2)

    @property
    def redirects(self):
        return True if self.all_rr_by_type(5) else False

    @property
    def redirect(self):
        for rr in self.all_rr_by_type(5):
            return rr.rdata.cname

    def __repr__(self):
        return self.name


def rr_expire(self):
    return int((self._expire_at - datetime.datetime.now(tz=datetime.timezone.utc)).total_seconds())


@asyncio.coroutine
def rr_auto_pop_self(self):
    assert isinstance(self, triton.dns.message.Answer)
    yield from asyncio.sleep(self.expire())
    self.domain.remove_rr(self)
    yield from self.domain.check_remaining()


class Cache:
    def __init__(self, loop):
        self.loop = loop
        self.database = []
        self.init_root_servers()

    def init_root_servers(self):
        root = self.add_domain('.')
        for rns, ips in root_nameservers.items():
            ns = self.add_domain(rns)
            for ip in ips:
                ns.add_resource_record(triton.dns.message.Answer.parse_dict(
                    None, {'name': rns,
                           'ttl': int('1' * 32, 2),
                           'type': 1 if isinstance(ip, IPv4Address) else 28,
                           'class': 1,
                           'rdata': {
                               'address': str(ip)
                           }}))
            root.add_resource_record(triton.dns.message.Answer.parse_dict(
                None, {'name': '.',
                       'ttl': int('1' * 32, 2),
                       'type': 2,
                       'class': 1,
                       'rdata': {
                           'nsdname': rns
                       }}))

    def get(self, name):
        if name == '':
            name = '.'
        for domain in self.database:
            if domain.name == name:
                return domain
        raise exceptions.DomainNotFound()

    def remove_domain(self, instance):
        for n, ns in enumerate(self.database.copy()):
            if ns is instance:
                self.database.pop(n)

    def add_domain(self, name):
        domain = Domain(self, name)
        if domain in self:
            return self.get(name)
        else:
            self.database.append(domain)
            return domain

    @property
    def root_servers(self):
        return list(root_nameservers.keys())

    def __contains__(self, item):
        return item.name in [x.name for x in self.database]

    def find(self, domain, type, cls):
        try:
            domain_ = self.get(domain)
            answers = domain_.all_rr_by_type(type)
            if answers:
                message = triton.dns.Message.create_question(domain, type, cls)
                for answer in answers:
                    answer._ttl = answer.expire() if answer.expire() else 1
                    message.answer.append(answer)
                return message
        except exceptions.DomainNotFound:
            return

    def store(self, message):
        for answer in message.answer:
            domain = self.add_domain(answer.name.lower())
            domain.add_resource_record(answer)
        for answer in message.authority:
            domain = self.add_domain(answer.name.lower())
            domain.add_resource_record(answer)
        for answer in message.additional:
            if not isinstance(answer.rdata, triton.dns.message.rdata.OPT):
                domain = self.add_domain(answer.name.lower())
                domain.add_resource_record(answer)

    def find_or_store(self, f):
        default = self

        async def wrapper(dns_server, domain, record_type, *args, **kwargs):
            self = kwargs.get('custom_cache', default)
            domain_ = self.get(domain)
            if domain_ and kwargs.get('use_cache', True):
                answers = domain_.all_rr_by_type(record_type)
                if answers:
                    message = await triton.dns.Message.create_question(domain, record_type)
                    for answer in answers:
                        answer._ttl = answer.expire() if answer.expire() else 1
                        message.answer.append(answer)
                    return message
            message = await f(dns_server, domain, record_type, *args, **kwargs)
            for answer in message.answer:
                domain = self.add_domain(answer.name.lower())
                domain.add_resource_record(answer)
            for answer in message.authority:
                domain = self.add_domain(answer.name.lower())
                domain.add_resource_record(answer)
            for answer in message.additional:
                if not isinstance(answer, triton.dns.message.rdata.OPT):
                    domain = self.add_domain(answer.name.lower())
                    domain.add_resource_record(answer)
            return message
        return wrapper