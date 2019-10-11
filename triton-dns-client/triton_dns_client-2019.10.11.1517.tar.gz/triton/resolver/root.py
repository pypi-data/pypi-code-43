import triton
from triton.protocol.exception import TimeoutError


class ResolveStatus:
    def __init__(self):
        self.secure = True


class ChainResolver:
    def __init__(self, target_domain, target_type, custom_cache=None):
        self.target_domain = target_domain.lower()
        self.target_type = target_type
        self.cache = triton.cache if not custom_cache else custom_cache
        self.status = ResolveStatus()
        self.current_resolve_depth = 1
        self.result = None

    def cache_get(self, name):
        return triton.cache.get(name)

    async def cache_set(self, name, ip, expire) -> None:
        ns = triton.cache.add_nameserver(name)
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

    async def update_nameservers(self, domain):
        await ChainResolver(domain, 28).go()
        await ChainResolver(domain, 1).go()

    def get_ns_for_domain(self):
        domain = triton.cache.get(self.target_domain)
        if not domain:
            for _ in range(self.current_resolve_depth):
                domain = triton.cache.get(self.current_resolve_domain)
                if domain:
                    return domain.nameservers
                else:
                    self.current_resolve_depth -= 1
            else:
                return []
        else:
            return domain.nameservers

    async def go(self):
        if self.result:
            return self.result
        await self.find_target_zone_nameservers()
        nameserves = self.get_ns_for_domain()
        for ns in nameserves:
            if not triton.cache.get(ns.rdata.nsdname.label):
                await self.update_nameservers(ns.rdata.nsdname.label)
            ns_domain = triton.cache.get(ns.rdata.nsdname.label.lower())
            for a_rr in ns_domain.all_rr_by_type(1, 28):
                try:
                    result = await triton.Query.create_and_resolve(a_rr.rdata.address, self.target_domain,
                                                                   self.target_type,
                                                                   dnssec=self.status.secure)
                    if result:
                        if self.status.secure:
                            try:
                                zone_keys = await triton.Query.create_and_resolve(str(a_rr.rdata.address),
                                                                                  self.target_domain, 48)
                            except triton.protocol.exception.TimeoutError:
                                continue
                            assert await result.verify_rrsig(zone_keys)
                        self.result = result
                        return result
                except OSError:
                    continue
        return {}

    async def find_target_zone_nameservers(self, parent_zone_ds=None):
        domain = triton.cache.get(self.current_resolve_domain_upper)
        for ns in domain.all_rr_by_type(2):
            ns_domain = triton.cache.get(ns.rdata.nsdname.label)
            if ns_domain:
                for address in ns_domain.all_rr_by_type(1, 28):
                    if self.current_resolve_domain not in self.cache.database:
                        try:
                            await triton.Query.create_and_resolve(str(address.rdata.address),
                                                                  self.current_resolve_domain, 2, dnssec=True)
                            await triton.Query.create_and_resolve(str(address.rdata.address),
                                                                  self.current_resolve_domain_upper, 48, dnssec=True)
                            await triton.Query.create_and_resolve(str(address.rdata.address),
                                                                  self.current_resolve_domain, 43, dnssec=True)
                        except OSError:
                            continue
                        except TimeoutError:
                            continue
                        if self.status.secure:
                            await self.verify_keys()
                        if self.current_resolve_domain != self.target_domain:
                            self.current_resolve_depth += 1
                            return await self.find_target_zone_nameservers(parent_zone_ds)
                        else:
                            return True
                    else:
                        if self.current_resolve_domain != self.target_domain:
                            self.current_resolve_depth += 1
                            return await self.find_target_zone_nameservers()
                        else:
                            return True

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
