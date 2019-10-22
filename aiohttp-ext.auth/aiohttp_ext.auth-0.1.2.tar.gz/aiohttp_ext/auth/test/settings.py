settings = {

    'gino': {
        'driver': 'asyncpg',
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': None,
        'database': 'auth_test'
    },

    'auth': {
        'user_model': None,
        'auth_backends': [
            'aiohttp_ext.auth.auth_backends.BasicAuthorizationBackend',
            'aiohttp_ext.auth.auth_backends.BearerAuthorizationBackend'
        ]
    },

    'jwt': {
        'pub_key': './id_rsa.pub',
        'algorithm': 'RS512',
    }
}
