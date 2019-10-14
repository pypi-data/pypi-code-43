import argparse
import os

import trafaret as T
from trafaret_config import commandline


os.environ.setdefault(
    "SETTINGS_CONFIG",
    '/etc/aiohttp-light-utils/service.yaml'
)

CONFIG_TOPIC = os.environ['SERVICE_NAME']

SETTINGS =  T.Dict({
    'db': T.Or(
        T.Null,
        T.Dict({
            'url': T.String,
            'db_name': T.String
        }),
    ),
    'cache': T.Or(
        T.Null,
        T.Dict({
            'url': T.String,
            T.Key('db_name', optional=True, default=0): T.Int,
        }),
    ),
    T.Key('host'): T.IP,
    T.Key('port'): T.Int,
    T.Key('testing', optional=True, default=False): T.Bool,
    T.Key('debug', optional=True, default=False): T.Bool,
    T.Key(
        'raven_dsn',
        optional=True, default=None
    ): T.Or(T.String, T.Null),
})


def get_config(argv=None, extra=None):
    ap = argparse.ArgumentParser()

    settings = SETTINGS if extra is None else SETTINGS.merge(extra)

    trafaret_settings = T.Dict({
        T.Key(CONFIG_TOPIC): settings
    })

    commandline.standard_argparse_options(
        ap,
        default_config=os.environ['SETTINGS_CONFIG']
    )
    # ignore unknown options
    options, unknown = ap.parse_known_args(argv)

    config = commandline.config_from_options(options, trafaret_settings)
    return config.get(CONFIG_TOPIC)
