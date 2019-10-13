import asyncio
loop = asyncio.new_event_loop()
# Priority order kept

RESOLVERS = [
    # 'neptune.resolver.dictionary',
    # 'neptune_resolver_default',
    'triton.resolver'
    # 'neptune_resolver_rest',
    # 'neptune_resolver_postgres'
]

NEPTUNE_RESOLVER_DICTIONARY = {
    'dictionary': {
        'example.com': {
            'a': {'127.0.0.1', '127.0.0.2'}
        }
    }
}

CACHE = 'neptune_cache_redis'


NEPTUNE_CACHE_REDIS = {
    'host': 'localhost',
    'database': 1
}

NEPTUNE_RESOLVER_REST = {
    'base_url': '',
    'username': '',
    'password': '',
}

NEPTUNE_RESOLVER_POSTGRES = {

}

PROTOCOLS = [
    'neptune.protocols.udp',
    'neptune.protocols.tcp',
    'neptune_dnsoverhttps_protocol'
]

NEPTUNE_DNSOVERHTTPS_PROTOCOL = {
    'prefix': 'dns-request',
    'cert_path': '',
    'key_path': '',
    'host': '0.0.0.0',
    'port': '8090',
    'with_ssl': False
}

NEPTUNE_PROTOCOLS_UDP = {
    'host': '0.0.0.0',
    'port': 53
}

NEPTUNE_PROTOCOLS_TCP = {
    'host': '0.0.0.0',
    'port': 53
}

NEPTUNE_RESOLVER_DEFAULT = {
    'resolvers': ['1.1.1.1', '8.8.8.8'] # Your favorite DNS resolvers
}
