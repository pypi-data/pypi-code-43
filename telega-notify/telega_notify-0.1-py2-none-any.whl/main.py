#!/usr/bin/env python
# vim: set fileencoding=utf-8 tw=0:

from __future__ import print_function

import os
import re
import sys
import socks
import urllib2
import urlparse

import toml


__all__ = ['send_message']


CONFIGS = [
    '~/.config/telega-notify.toml',
    '/etc/telega-notify.toml',
]


def read_config():
    for fn in CONFIGS:
        fn = os.path.expanduser(fn)
        if os.path.exists(fn):
            with open(fn, 'rb') as f:
                return toml.loads(f.read())

    print('Config file not found, possible locations:', file=sys.stderr)
    for fn in CONFIGS:
        print('- %s' % fn, file=sys.stderr)

    exit(1)


def get_opener(config):
    proxy = config.get('proxy')
    if not proxy:
        return urllib2.build_opener()

    url = urlparse.urlparse(proxy)
    if url.scheme == 'socks5':
        m = re.match(r'^([^:]+):([^@]+)@([^:]+):(.+)$', url.netloc)
        if m is None:
            print('Proxy URL should look like this: socks5://user:password@host:port', file=sys.stderr)
            exit(2)

        user, passwd, host, port = m.groups()

        try:
            from sockshandler import SocksiPyHandler
            opener = urllib2.build_opener(SocksiPyHandler(socks.SOCKS5, host, int(port), True, user, passwd))
            return opener
        except ImportError:
            print('Install PySocks to use a socks5 proxy.', file=sys.stderr)
            exit(5)

    print('Unsupported proxy type: %s' % url.scheme, file=sys.stderr)
    exit(3)


def send_message(message):
    """Sends a message to the configured chat."""
    config = read_config()

    url = "https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s" % (config['token'], config['chat_id'], urllib2.quote(message))

    opener = get_opener(config)
    req = opener.open(url)
    res = req.read()

    code = req.getcode()
    if code == 200:
        return True
    else:
        print('Telegram API error: %s' % res, file=sys.stderr)
        return False


def main(prog, message=None, *args):
    if message is None:
        print('Reading message from stdin...', file=sys.stderr)
        message = sys.stdin.read()

    message = message.strip()
    if send_message(message):
        print('Message sent.', file=sys.stderr)
    else:
        exit(6)
