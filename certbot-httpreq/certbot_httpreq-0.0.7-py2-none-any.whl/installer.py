# -*- coding: utf-8 -*-
# Copyright 2019 Adrien Delle Cave
# SPDX-License-Identifier: GPL-3.0-or-later
"""HTTP Requests Let's Encrypt installer plugin."""

from __future__ import print_function

import os
import logging
import requests

from sonicprobe import helpers
from sonicprobe.libs import urisup

import zope.interface

from certbot import interfaces
from certbot.plugins import common

LOG = logging.getLogger("certbot-httpreq")


@zope.interface.implementer(interfaces.IInstaller)
@zope.interface.provider(interfaces.IPluginFactory)
class Installer(common.Plugin):
    description = "HTTP Requests Installer"

    @classmethod
    def add_parser_arguments(cls, add):
        add("certbot-httpreq-config",
            default = os.getenv('CBT_HTTPREQ_CONFIG') or '/etc/letsencrypt/certbot-httpreq.yml',
            help    = "Path to certbot-httpreq configuration file")

    def __init__(self, *args, **kwargs):
        super(Installer, self).__init__(*args, **kwargs)
        self._config = {}
        self._uri    = None

    def _build_uri(self):   # pylint: disable=missing-docstring
        return urisup.uri_help_unsplit(self._uri)

    @staticmethod
    def _set_option(conf, xtype, name, default = None):
        if not conf.get(name):
            conf[name] = os.getenv("CBT_HTTPREQ_%s_%s" % (xtype.upper(), name.upper())) or default

    def prepare(self):  # pylint: disable=missing-docstring,no-self-use
        self._config = helpers.load_conf_yaml_file(self.conf('certbot-httpreq-config'))

        if not self._config.get('deploy'):
            self._config['deploy'] = {}

        confdeploy = self._config['deploy']

        self._set_option(confdeploy, 'deploy', 'uri', 'http://localhost')
        self._set_option(confdeploy, 'deploy', 'path') or '/'
        self._set_option(confdeploy, 'deploy', 'method', 'PUT')
        self._set_option(confdeploy, 'deploy', 'format', 'json')
        self._set_option(confdeploy, 'deploy', 'param_challenge')
        self._set_option(confdeploy, 'deploy', 'timeout')
        self._set_option(confdeploy, 'deploy', 'verify')

        self._uri    = list(urisup.uri_help_split(confdeploy['uri']))
        self._uri[2] = confdeploy['path']

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return ""

    def get_all_names(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def deploy_cert(self, domain, cert_path, key_path, chain_path, fullchain_path):  # pylint: disable=unused-argument
        """
        PUT or POST or PATCH Certificate
        """
        method  = self._config['deploy']['method'].lower()

        if method not in ('put', 'post', 'patch'):
            LOG.error("invalid HTTP method for deploy: %r", method)
            return None

        headers = {}
        data    = {'domain': domain,
                   'cert':   open(cert_path, 'r').read(),
                   'key':    open(key_path, 'r').read(),
                   'chain':  open(chain_path, 'r').read()}
        json    = None

        if isinstance(self._config['deploy'].get('headers'), dict):
            headers = self._config['deploy']['headers']

        if self._config['deploy']['format'] == 'json':
            headers['Content-Type'] = 'application/json'
            json = data
            data = None

        req = getattr(requests, method)(self._build_uri(),
                                        headers = headers,
                                        data    = data,
                                        json    = json,
                                        timeout = self._config['deploy']['timeout'],
                                        verify  = self._config['deploy']['verify'])
        req.raise_for_status()
        return None

    def enhance(self, domain, enhancement, options=None):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def supported_enhancements(self):  # pylint: disable=missing-docstring,no-self-use
        return []  # pragma: no cover

    def get_all_certs_keys(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def save(self, title=None, temporary=False):  # pylint: disable=no-self-use
        pass  # pragma: no cover

    def rollback_checkpoints(self, rollback=1):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def recovery_routine(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def view_config_changes(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def config_test(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def restart(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def renew_deploy(self, lineage, *args, **kwargs): # pylint: disable=missing-docstring,no-self-use,unused-argument
        """
        Renew certificates when calling `certbot renew`
        """
        self.deploy_cert(lineage.names()[0], lineage.cert_path, lineage.key_path, lineage.chain_path, lineage.fullchain_path)


interfaces.RenewDeployer.register(Installer)
