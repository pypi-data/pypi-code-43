from ipaddress import ip_address, ip_network, _BaseAddress
import logging
logger = logging.getLogger(__name__)


class _BaseIPDataClass:
    def __str__(self):
        return str(self.__class__) + "." + self.ID

    def __repr__(self):
        return "'" + self.__str__() + "'"

    def __hash__(self):
        return hash(self.__class__.__name__ + "." + self.ID)

    def __eq__(self, other):
        try:
            return self.__class__ == other.__class__ and self.ID == other.ID
        except:
            return False


class IP(_BaseIPDataClass):
    def __init__(self, ip):
        if not isinstance(ip, _BaseAddress):
            self._ip = ip_address(ip)
        else:
            self._ip = ip
        self.version = self._ip.version
        self.decimal = int(self._ip)
        self.compressed = self._ip.compressed
        self.exploded = self._ip.exploded
        self.ID = self.exploded

    def __int__(self):
        return self.decimal

    def __lt__(self, other):
        if not isinstance(other, IP):
            other = IP(other)
        return self._ip.__lt__(other._ip)

    def __le__(self, other):
        if not isinstance(other, IP):
            other = IP(other)
        return self == other or self._ip.__lt__(other._ip)

    def __add__(self, other):
        return IP(self.decimal + other)

    def __sub__(self, other):
        return IP(self.decimal - other)


class Pool(_BaseIPDataClass):
    @staticmethod
    def from_netrange(pool):
        pool = pool.replace(' ', '')
        lower, upper = None, None
        if '/' in pool:
            try:
                net = ip_network(pool)
                lower, upper = ip_address(int(net.network_address) + 1), ip_address(int(net.broadcast_address) - 1)
            except Exception as e:
                raise ValueError("Bad CIDR pool: " + pool) from e
        elif '-' in pool:
            try:
                lower, upper = pool.split('-')
            except Exception as e:
                raise ValueError("Bad range pool: " + pool) from e
        else:
            try:
                single_ip_pool = ip_address(pool)
                lower, upper = single_ip_pool, single_ip_pool
            except:
                raise ValueError("Bad pool: " + pool)
        return Pool(lower, upper)

    def __init__(self, lower, upper):
        if not isinstance(lower, IP):
            self.lower = IP(lower)
        else:
            self.lower = lower
        if not isinstance(upper, IP):
            self.upper = IP(upper)
        else:
            self.upper = upper
        if self.lower.version != self.upper.version:
            raise ValueError("IPs are not the same version")
        self.version = self.lower.version
        self.normalized = self.lower.exploded + ' - ' + self.upper.exploded
        self.count = (int(self.upper) - int(self.lower)) + 1
        self.ID = self.normalized

    def __contains__(self, ip):
        if not isinstance(ip, IP):
            ip = IP(ip)
        if ip.version != self.version:
            return False
        return self.lower.decimal <= ip.decimal <= self.upper.decimal

    def __str__(self):
        return self.normalized
