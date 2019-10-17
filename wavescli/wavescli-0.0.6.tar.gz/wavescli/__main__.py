# -*- coding: utf-8 -*-

import click
from .cli import main
from .apiclient import ApiClient


class CliObject(dict):
    """Classe auxiliar criada para fazer lazy-initialization do
    client da API sem mudar muito a estrutura do CLI"""

    def __init__(self):
        self._client = None
        super(CliObject, self).__init__()

    @property
    def client(self):
        if self._client is None:
            cfg = self['config']
            url = cfg['WAVES_URL']
            self._client = ApiClient(url)
        return self._client


def run():
    default_context = CliObject()

    try:
        return main(obj=default_context)
    except Exception as exc:
        click.secho(str(exc), fg='red')


if __name__ == '__main__':
    run()
