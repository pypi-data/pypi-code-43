import triton
from triton.protocol.exception import TimeoutError
from . import exceptions


class ResolveStatus:
    def __init__(self):
        self.secure = True


class ChainResolver:
    def __init__(self, target_domain, target_type, target_class=1, custom_cache=None, loop=None):
        self.loop = loop if loop else triton.loop
        self.target_domain = target_domain.lower()
        self.target_type = target_type
        self.target_class = target_class
        self.cache = triton.cache if not custom_cache else custom_cache
        self.status = ResolveStatus()
        self.current_resolve_depth = 1
        self.result = None

    def cache_get(self, name):
        return self.cache.get(name)

    async def cache_set(self, name, ip, expire) -> None:
        ns = self.cache.add_nameserver(name)
        await ns.add_address(ip=ip, expire=expire)

    @property
    def current_resolve_domain(self):
        return '.'.join(
            self.target_domain.split('.')[-self.current_resolve_depth:]) if self.current_resolve_depth > 0 else '.'

    @property
    def current_resolve_domain_upper(self):
        return '.'.join(
            self.target_domain.split('.')[
            -(self.current_resolve_depth - 1):]) if self.current_resolve_depth > 1 else '.'

    async def get_zone_ns(self):
        try:
            domain = self.cache.get(self.current_resolve_domain_upper)
            for ns in domain.nameservers:
                try:
                    ns_domain = self.cache.get(ns.rdata.nsdname.label.lower())
                    for addr in ns_domain.all_rr_by_type(1, 28):
                        try:
                            await triton.Query.create_and_resolve(str(addr.rdata.address),
                                                                  self.current_resolve_domain, 2, dnssec=True,
                                                                  custom_cache=self.cache,
                                                                  loop=self.loop)
                            if self.current_resolve_domain == self.target_domain:
                                return
                            self.current_resolve_depth += 1
                            return await self.get_zone_ns()
                        except OSError:
                            continue
                        except TimeoutError:
                            continue
                        except exceptions.CannotConnectToNameserver:
                            continue
                except exceptions.DomainNotFound:
                    await self.update_nameservers(ns.rdata.nsdname.label.lower())
            else:
                return self.get_ns_for_domain()
        except exceptions.DomainNotFound:
            await self.update_nameservers(self.current_resolve_domain_upper)
            pass  # TODO return empty response?

    async def update_nameservers(self, domain):
        try:
            cached_domain = self.cache.get(domain)
            if not cached_domain.all_rr_by_type(1) and not cached_domain.all_rr_by_type(28):
                if not cached_domain.all_rr_by_type(1):
                    await ChainResolver(domain, 28, loop=self.loop, custom_cache=self.cache).go()
                if not cached_domain.all_rr_by_type(28):
                    await ChainResolver(domain, 1, loop=self.loop, custom_cache=self.cache).go()
        except exceptions.DomainNotFound:
            await ChainResolver(domain, 28, loop=self.loop, custom_cache=self.cache).go()
            await ChainResolver(domain, 1, loop=self.loop, custom_cache=self.cache).go()
        # await ChainResolver(domain, 6, loop=self.loop, custom_cache=self.cache).go()
        # await ChainResolver(domain, 48, loop=self.loop, custom_cache=self.cache).go()
        # await ChainResolver(domain, 43, loop=self.loop, custom_cache=self.cache).go()

    def get_ns_for_domain(self):
        try:
            domain = self.cache.get(self.target_domain)
            if not domain.nameservers:
                raise exceptions.DomainNotFound()
        except exceptions.DomainNotFound:
            for _ in range(self.current_resolve_depth):
                try:
                    domain = self.cache.get(self.current_resolve_domain_upper)
                    if domain.nameservers:
                        return domain.nameservers
                    raise exceptions.DomainNotFound()
                except exceptions.DomainNotFound:
                    self.current_resolve_depth -= 1
            else:
                raise exceptions.NameserversNotFound()
        return domain.nameservers

    async def go(self):
        if self.result:
            return self.result
        await self.get_zone_ns()
        nameserves = self.get_ns_for_domain()
        for ns in nameserves:
            await self.update_nameservers(ns.rdata.nsdname.label.lower())
            try:
                ns_domain = self.cache.get(ns.rdata.nsdname.label.lower())
                for a_rr in ns_domain.all_rr_by_type(1, 28):
                    try:
                        return await triton.Query.create_and_resolve(a_rr.rdata.address, self.target_domain,
                                                                     self.target_type,
                                                                     dnssec=self.status.secure,
                                                                     custom_cache=self.cache,
                                                                     loop=self.loop)

                    except OSError:
                        continue
                    except exceptions.CannotConnectToNameserver:
                        continue
            except exceptions.DomainNotFound:
                print(f'not found {ns.rdata.nsdname.label.lower()} in cache')
                continue
        else:
            return triton.dns.Message.create_question(self.target_domain, self.target_type, self.target_type)

    # async def find_target_zone_nameservers(self, parent_zone_ds=None):
    #     domain = self.cache.get(self.current_resolve_domain_upper)
    #     if not domain:
    #         return
    #     for ns in domain.all_rr_by_type(2):
    #         ns_domain = self.cache.get(ns.rdata.nsdname.label)
    #         if ns_domain:
    #             for address in ns_domain.all_rr_by_type(1, 28):
    #                 if self.current_resolve_domain not in self.cache.database:
    #                     try:
    #                         await triton.Query.create_and_resolve(str(address.rdata.address),
    #                                                               self.current_resolve_domain, 2, dnssec=True,
    #                                                               custom_cache=self.cache,
    #                                                               loop=self.loop)
    #                         await triton.Query.create_and_resolve(str(address.rdata.address),
    #                                                               self.current_resolve_domain_upper, 48, dnssec=True,
    #                                                               custom_cache=self.cache,
    #                                                               loop=self.loop)
    #                         await triton.Query.create_and_resolve(str(address.rdata.address),
    #                                                               self.current_resolve_domain, 43, dnssec=True,
    #                                                               custom_cache=self.cache,
    #                                                               loop=self.loop)
    #                     except OSError:
    #                         continue
    #                     except TimeoutError:
    #                         continue
    #                     if self.status.secure:
    #                         await self.verify_keys()
    #                     if self.current_resolve_domain != self.target_domain:
    #                         self.current_resolve_depth += 1
    #                         return await self.find_target_zone_nameservers(parent_zone_ds)
    #                     else:
    #                         return True
    #                 else:
    #                     print('already in cache')
    #                     if self.current_resolve_domain != self.target_domain:
    #                         self.current_resolve_depth += 1
    #                         return await self.find_target_zone_nameservers()
    #                     else:
    #                         return True

    async def verify_keys(self):
        # TODO
        return
        try:
            assert await zone_ds.verify_rrsig(zone_keys)
            if parent_zone_ds and self.current_resolve_depth != 1:
                assert await zone_keys.verify_keys(parent_zone_ds)
                parent_zone_ds = zone_ds
            parent_zone_ds = zone_ds
            assert await zone_keys.verify_rrsig(zone_keys)
            assert await zone_nameservers.verify_rrsig(zone_keys)
        except triton.dns.dnssec.exceptions.VerificationError:
            self.status.secure = False
