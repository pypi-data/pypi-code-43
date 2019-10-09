#
# Copyright (c) 2006-2019 Balabit
# All Rights Reserved.
#
"""
.. py:module:: safeguard.sessions.plugin.plugin_configuration
    :synopsis: Interface to parse plugin configuration text options.

The PluginConfiguration service implements parsing and accessing the textual configuration set for plugin instances.
The API is built on Python configparser.ConfigParser module with some additional functionality.

"""
import logging
import re

from configparser import ConfigParser

from safeguard.sessions.plugin.exceptions import PluginSDKValueError
from safeguard.sessions.plugin.plugin_configuration_exceptions import RequiredConfigurationSettingNotFound
from safeguard.sessions.plugin.credential_store import CredentialStore
from safeguard.sessions.plugin.lazy_proxy import LazyProxy


class PluginConfiguration:
    """
    The PluginConfiguration class represents the plugin configuration service.

    :param str configuration: runtime configuration
    :param str defaults: design time configuration defaults
    """
    def __init__(self, configuration, defaults=None):
        self.parser = ConfigParser()
        if defaults is not None:
            self.parser.read_string(defaults)
        self.parser.read_string(configuration)
        self._credential_store = LazyProxy(lambda: self._instantiate_credential_store())
        self.log = logging.getLogger(__name__)
        self.log.debug("Configuration initialized")

    def get(self, section, option, default=None, required=False):
        """
        The :meth:`get` method returns a configuration option as a string value.
        If the value of the option is `$` the secret identified by the section and option pair
        is retrieved from the configured credential store

        :param str section: which [section] to search
        :param str option: which option to get
        :param default: return value if section or option is not present
        :param boolean required: whether to throw an exception on missing option
        :return: the value of the option or None
        :rtype: str
        :raises: :class:`RequiredConfigurationSettingNotFound
          <safeguard.sessions.plugin.plugin_configuration_exceptions.RequiredConfigurationSettingNotFound>`
        """
        self._check_required(section, option, required)
        value = self.parser.get(section, option, fallback=default)
        if self._from_credential_store(value):
            return self._get_result_from_cred_store(self._credential_store.get_passwords, section, option)

        if self._is_literal_dollar_sign(value):
            return '$'
        return value

    def get_certificate(self, section, option, required=False):
        """
        The :meth:`get_certificate` method returns a configuration option as a dict value.
        If the value of the option is `$` the certificate identified by the section and option pair
        is retrieved from the configured credential store
        When the certificate and private key is given in the configuration it should be in PEM format
        and all the new lines must be indentet with one whitespace

        Example configuration:

        .. code-block:: ini

            [foo]
            certificate = -----BEGIN CERTIFICATE-----
             cert
             -----END CERTIFICATE-----
             -----BEGIN RSA PRIVATE KEY-----
             key
             -----END RSA PRIVATE KEY-----

        :param str section: which [section] to search
        :param str option: which option to get
        :param boolean required: whether to throw an exception on missing option
        :return: private key and certificate parsed as dict
        :rtype: dict
        :raises: :class:`RequiredConfigurationSettingNotFound
          <safeguard.sessions.plugin.plugin_configuration_exceptions.RequiredConfigurationSettingNotFound>`
        """
        value = self.parser.get(section, option)
        if self._from_credential_store(value):
            return self._get_result_from_cred_store(self._credential_store.get_certificates, section, option)
        try:
            return dict(key=self._extract_private_key(value),
                        cert=self._extract_certificate(value))
        except PluginSDKValueError as e:
            e.append_variables({'section': section, 'option': option})
            raise e

    def getboolean(self, section, option, default=None, required=False):
        """
        The :meth:`getboolean` method returns the boolean value of a configuration option. The configuration option may
        have the values \"yes\" and \"no\" or their upper case variants. In case of invalid value, a
        :class:`PluginSDKValueError` exception is raised.

        :param str section: which [section] to search
        :param str option: which option to get
        :param default: value if section or option is not present
        :param boolean required: whether to throw exception on missing option
        :return: the value of the option or None
        :rtype: boolean
        :raises: :class:`RequiredConfigurationSettingNotFound
          <safeguard.sessions.plugin.plugin_configuration_exceptions.RequiredConfigurationSettingNotFound>`
        :raises: :class:`PluginSDKValueError <safeguard.sessions.plugin.exceptions.PluginSDKValueError>`
        """
        value = self.getienum(section, option, ('yes', 'no'), default, required)
        if value == default:
            return value
        return value == 'yes'

    def getint(self, section, option, default=None, required=False):
        """
        The :meth:`getint` method returns the integer value of a configuration option. If the configuration option
        cannot be converted to an integer value, then a :class:`PluginSDKValueError` exception is raised.

        :param str section: which [section] to search
        :param str option: which option to get
        :param default: value if section or option is not present
        :param boolean required: whether to throw exception on missing option
        :return: the value of the option or None
        :rtype: int
        :raises: :class:`RequiredConfigurationSettingNotFound
          <safeguard.sessions.plugin.plugin_configuration_exceptions.RequiredConfigurationSettingNotFound>`
        :raises: :class:`PluginSDKValueError <safeguard.sessions.plugin.exceptions.PluginSDKValueError>`
        """
        value = self.get(section, option, default=default, required=required)
        if value == default:
            return value
        try:
            return int(value)
        except ValueError:
            raise PluginSDKValueError(
                'Configuration setting is not an integer',
                {'option': option, 'section': section, 'value': value}
            )

    def getfloat(self, section, option, default=None, required=False):
        """
        The :meth:`getfloat` method returns the floating point value of a configuration option. If the configuration
        option cannot be converted to a floating point value, then a :class:`PluginSDKValueError` exception is raised.

        :param str section: which [section] to search
        :param str option: which option to get
        :param default: value if section or option is not present
        :param boolean required: whether to throw exception on missing option
        :return: the value of the option or None
        :rtype: float
        :raises: :class:`RequiredConfigurationSettingNotFound
          <safeguard.sessions.plugin.plugin_configuration_exceptions.RequiredConfigurationSettingNotFound>`
        :raises: :class:`PluginSDKValueError <safeguard.sessions.plugin.exceptions.PluginSDKValueError>`
        """
        value = self.get(section, option, default=default, required=required)
        if value == default:
            return value
        try:
            return float(value)
        except ValueError:
            raise PluginSDKValueError(
                'Configuration setting is not a floating point number',
                {'option': option, 'section': section, 'value': value}
            )

    def getienum(self, section, option, value_set, default=None, required=False):
        """
        The :meth:`getienum` method returns the value of an option that may only assume certain lower case string
        values. In other words the lower case value of the configuration option is checked against a list of possible
        values. In case the configuration value is not one of the allowed values, then a :class:`PluginSDKValueError`
        exception is raised.

        .. code-block:: python

            from safeguard.sessions.plugin import PluginConfiguration

            config = PluginConfiguration(\"\"\"
                                  [foobar]
                                  color1 = LightGreen
                                  color2 = LightBlue
                                   \"\"\")

            # next line is ok, returns 'lightgreen'
            config.getienum('foobar', 'color1', ('green', 'lightgreen'))

            # next line throws PluginSDKValueError exception
            config.getienum('foobar', 'color2', ('green', 'lightgreen'))

        :param str section: which [section] to search
        :param str option: which option to get
        :param seq value_set: a container of possible lower case values (the container should implement the **in**
          operator)
        :param str default: value if section or option is not present
        :param boolean required: whether to throw exception on missing option
        :return: the value of the option or None
        :rtype: str
        :raises: :class:`RequiredConfigurationSettingNotFound
          <safeguard.sessions.plugin.plugin_configuration_exceptions.RequiredConfigurationSettingNotFound>`
        :raises: :class:`PluginSDKValueError <safeguard.sessions.plugin.exceptions.PluginSDKValueError>`
        """
        value = self.get(section, option, default, required)
        if value == default:
            return value
        value = value.lower()
        if value not in value_set:
            raise PluginSDKValueError(
                'Configuration setting is not one of {}'.format(value_set),
                {'option': option, 'section': section, 'value': value}
            )
        return value

    def _check_required(self, section, option, required):
        if required and not self._has_option(section, option):
            raise RequiredConfigurationSettingNotFound(
                "Required configuration setting missing",
                {'option': option, 'section': section}
            )

    def _has_option(self, section, option):
        return self.parser.has_option(section, option)

    @staticmethod
    def _get_result_from_cred_store(getter_function, section, option):
        result = getter_function(section, option)
        if not result:
            return None
        return result[0]

    @staticmethod
    def _from_credential_store(value):
        return value == '$'

    @staticmethod
    def _is_literal_dollar_sign(value):
        return value == '$$'

    def _extract_certificate(self, value):
        certificate_regex = r'-----BEGIN CERTIFICATE-----[\s\S]*-----END CERTIFICATE-----'
        return self._get_matches(certificate_regex, value)

    def _extract_private_key(self, value):
        private_key_regex = r'-----BEGIN [RD]SA PRIVATE KEY-----[\s\S]*-----END [RD]SA PRIVATE KEY-----'
        return self._get_matches(private_key_regex, value)

    @staticmethod
    def _get_matches(regex, value):
        matches = re.findall(regex, value, re.MULTILINE)
        if not matches:
            raise PluginSDKValueError('Invalid certificate or private key configured')
        return matches[0]

    def _instantiate_credential_store(self):
        section = 'credential_store'
        option = 'name'
        self._check_required(section, option, required=True)
        credential_store_name = self.parser.get(section, option)
        return CredentialStore.from_config(None, name=credential_store_name)
