#
# Copyright (c) 2006-2019 Balabit
# All Rights Reserved.
#

from safeguard.sessions.plugin import AAPlugin


class Plugin(AAPlugin):
    def __init__(self, configuration):
        super().__init__(configuration)

    def do_authenticate(self):
        return {'verdict': 'ACCEPT'}

    def do_authorize(self):
        return {'verdict': 'ACCEPT'}
