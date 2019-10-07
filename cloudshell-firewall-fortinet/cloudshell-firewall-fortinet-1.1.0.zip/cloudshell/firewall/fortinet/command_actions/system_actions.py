import re

from cloudshell.devices.networking_utils import UrlParser

from cloudshell.firewall.fortinet.command_actions.base import BaseCommandAction
from cloudshell.firewall.fortinet.command_templates import configuration
from cloudshell.firewall.fortinet.helpers.exceptions import FortiNetException


class SystemActions(BaseCommandAction):

    def backup_config(self, dst_path):
        params = self._prepare_params_file_path(dst_path)
        self.execute_command(configuration.BACKUP_CONF, **params)

    @staticmethod
    def _prepare_params_file_path(dst_path):
        url_dict = UrlParser.parse_url(dst_path)

        file_path = ('{}/{}'.format(
            url_dict[UrlParser.PATH], url_dict[UrlParser.FILENAME])
        ).strip('/')

        params = {
            url_dict[UrlParser.SCHEME.lower()]: '',
            'file_name': url_dict[UrlParser.FILENAME],
            'file_path': file_path,
            'host': url_dict[UrlParser.HOSTNAME],
            'port': url_dict[UrlParser.PORT],
            'user': url_dict[UrlParser.USERNAME],
            'password': url_dict[UrlParser.PASSWORD],
        }

        if 'flash' in params and not params['file_name']:
            params['file_name'] = params['host']

        return dict(filter(lambda (k, v): v is not None, params.items()))

    def _get_conf_revision_id(self, file_name):
        revisions = self.execute_command(configuration.SHOW_REVISIONS)

        match = re.search(
            r'^\s*(?P<id>\d+).+?\s{}\s*$'.format(file_name),
            revisions,
            re.MULTILINE+re.IGNORECASE)

        try:
            revision_id = match.group('id')
        except AttributeError:
            raise FortiNetException('Cannot find config file "{}" on the device'.format(file_name))

        return revision_id

    def restore_config(self, path):
        params = self._prepare_params_file_path(path)

        if 'flash' in params:
            params['revision_id'] = self._get_conf_revision_id(params['file_name'])

        self.execute_command(configuration.RESTORE_CONF, **params)

    def load_firmware(self, path):
        params = self._prepare_params_file_path(path)

        if 'flash' in params:
            params['revision_id'] = params['file_name']

        self.execute_command(configuration.LOAD_FIRMWARE, **params)
