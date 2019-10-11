#
# Copyright (c) 2006-2019 Balabit
# All Rights Reserved.
#
from collections import namedtuple


HttpProxySettings = namedtuple('HttpProxySettings', 'server port username password')


def extract_http_proxy_settings(response_body):
    proxy_enabled = response_body and response_body.get('enabled')
    authentication_enabled = proxy_enabled and response_body.get('authentication').get('selection') == 'password'
    return HttpProxySettings(
        server=response_body.get('server').get('value') if proxy_enabled else None,
        port=response_body.get('port') if proxy_enabled else None,
        username=response_body.get('authentication').get('username') if authentication_enabled else None,
        password=response_body.get('authentication').get('password') if authentication_enabled else None
    )
