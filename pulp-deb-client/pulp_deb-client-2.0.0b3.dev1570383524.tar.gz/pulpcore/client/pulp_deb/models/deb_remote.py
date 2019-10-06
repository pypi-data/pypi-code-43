# coding: utf-8

"""
    Pulp 3 API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: v3
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six


class DebRemote(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'href': 'str',
        'created': 'datetime',
        'type': 'str',
        'name': 'str',
        'url': 'str',
        'ssl_ca_certificate': 'str',
        'ssl_client_certificate': 'str',
        'ssl_client_key': 'str',
        'ssl_validation': 'bool',
        'proxy_url': 'str',
        'username': 'str',
        'password': 'str',
        'last_updated': 'datetime',
        'download_concurrency': 'int',
        'policy': 'str',
        'distributions': 'str',
        'components': 'str',
        'architectures': 'str',
        'sync_sources': 'bool',
        'sync_udebs': 'bool',
        'sync_installer': 'bool'
    }

    attribute_map = {
        'href': '_href',
        'created': '_created',
        'type': '_type',
        'name': 'name',
        'url': 'url',
        'ssl_ca_certificate': 'ssl_ca_certificate',
        'ssl_client_certificate': 'ssl_client_certificate',
        'ssl_client_key': 'ssl_client_key',
        'ssl_validation': 'ssl_validation',
        'proxy_url': 'proxy_url',
        'username': 'username',
        'password': 'password',
        'last_updated': '_last_updated',
        'download_concurrency': 'download_concurrency',
        'policy': 'policy',
        'distributions': 'distributions',
        'components': 'components',
        'architectures': 'architectures',
        'sync_sources': 'sync_sources',
        'sync_udebs': 'sync_udebs',
        'sync_installer': 'sync_installer'
    }

    def __init__(self, href=None, created=None, type=None, name=None, url=None, ssl_ca_certificate=None, ssl_client_certificate=None, ssl_client_key=None, ssl_validation=None, proxy_url=None, username=None, password=None, last_updated=None, download_concurrency=None, policy='immediate', distributions=None, components=None, architectures=None, sync_sources=None, sync_udebs=None, sync_installer=None):  # noqa: E501
        """DebRemote - a model defined in OpenAPI"""  # noqa: E501

        self._href = None
        self._created = None
        self._type = None
        self._name = None
        self._url = None
        self._ssl_ca_certificate = None
        self._ssl_client_certificate = None
        self._ssl_client_key = None
        self._ssl_validation = None
        self._proxy_url = None
        self._username = None
        self._password = None
        self._last_updated = None
        self._download_concurrency = None
        self._policy = None
        self._distributions = None
        self._components = None
        self._architectures = None
        self._sync_sources = None
        self._sync_udebs = None
        self._sync_installer = None
        self.discriminator = None

        if href is not None:
            self.href = href
        if created is not None:
            self.created = created
        if type is not None:
            self.type = type
        self.name = name
        self.url = url
        self.ssl_ca_certificate = ssl_ca_certificate
        self.ssl_client_certificate = ssl_client_certificate
        self.ssl_client_key = ssl_client_key
        if ssl_validation is not None:
            self.ssl_validation = ssl_validation
        self.proxy_url = proxy_url
        self.username = username
        self.password = password
        if last_updated is not None:
            self.last_updated = last_updated
        if download_concurrency is not None:
            self.download_concurrency = download_concurrency
        if policy is not None:
            self.policy = policy
        self.distributions = distributions
        if components is not None:
            self.components = components
        if architectures is not None:
            self.architectures = architectures
        if sync_sources is not None:
            self.sync_sources = sync_sources
        if sync_udebs is not None:
            self.sync_udebs = sync_udebs
        if sync_installer is not None:
            self.sync_installer = sync_installer

    @property
    def href(self):
        """Gets the href of this DebRemote.  # noqa: E501


        :return: The href of this DebRemote.  # noqa: E501
        :rtype: str
        """
        return self._href

    @href.setter
    def href(self, href):
        """Sets the href of this DebRemote.


        :param href: The href of this DebRemote.  # noqa: E501
        :type: str
        """

        self._href = href

    @property
    def created(self):
        """Gets the created of this DebRemote.  # noqa: E501

        Timestamp of creation.  # noqa: E501

        :return: The created of this DebRemote.  # noqa: E501
        :rtype: datetime
        """
        return self._created

    @created.setter
    def created(self, created):
        """Sets the created of this DebRemote.

        Timestamp of creation.  # noqa: E501

        :param created: The created of this DebRemote.  # noqa: E501
        :type: datetime
        """

        self._created = created

    @property
    def type(self):
        """Gets the type of this DebRemote.  # noqa: E501


        :return: The type of this DebRemote.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this DebRemote.


        :param type: The type of this DebRemote.  # noqa: E501
        :type: str
        """
        if type is not None and len(type) < 1:
            raise ValueError("Invalid value for `type`, length must be greater than or equal to `1`")  # noqa: E501

        self._type = type

    @property
    def name(self):
        """Gets the name of this DebRemote.  # noqa: E501

        A unique name for this remote.  # noqa: E501

        :return: The name of this DebRemote.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this DebRemote.

        A unique name for this remote.  # noqa: E501

        :param name: The name of this DebRemote.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501
        if name is not None and len(name) < 1:
            raise ValueError("Invalid value for `name`, length must be greater than or equal to `1`")  # noqa: E501

        self._name = name

    @property
    def url(self):
        """Gets the url of this DebRemote.  # noqa: E501

        The URL of an external content source.  # noqa: E501

        :return: The url of this DebRemote.  # noqa: E501
        :rtype: str
        """
        return self._url

    @url.setter
    def url(self, url):
        """Sets the url of this DebRemote.

        The URL of an external content source.  # noqa: E501

        :param url: The url of this DebRemote.  # noqa: E501
        :type: str
        """
        if url is None:
            raise ValueError("Invalid value for `url`, must not be `None`")  # noqa: E501
        if url is not None and len(url) < 1:
            raise ValueError("Invalid value for `url`, length must be greater than or equal to `1`")  # noqa: E501

        self._url = url

    @property
    def ssl_ca_certificate(self):
        """Gets the ssl_ca_certificate of this DebRemote.  # noqa: E501

        A string containing the PEM encoded CA certificate used to validate the server certificate presented by the remote server. All new line characters must be escaped. Returns SHA256 sum on GET.  # noqa: E501

        :return: The ssl_ca_certificate of this DebRemote.  # noqa: E501
        :rtype: str
        """
        return self._ssl_ca_certificate

    @ssl_ca_certificate.setter
    def ssl_ca_certificate(self, ssl_ca_certificate):
        """Sets the ssl_ca_certificate of this DebRemote.

        A string containing the PEM encoded CA certificate used to validate the server certificate presented by the remote server. All new line characters must be escaped. Returns SHA256 sum on GET.  # noqa: E501

        :param ssl_ca_certificate: The ssl_ca_certificate of this DebRemote.  # noqa: E501
        :type: str
        """
        if ssl_ca_certificate is not None and len(ssl_ca_certificate) < 1:
            raise ValueError("Invalid value for `ssl_ca_certificate`, length must be greater than or equal to `1`")  # noqa: E501

        self._ssl_ca_certificate = ssl_ca_certificate

    @property
    def ssl_client_certificate(self):
        """Gets the ssl_client_certificate of this DebRemote.  # noqa: E501

        A string containing the PEM encoded client certificate used for authentication. All new line characters must be escaped. Returns SHA256 sum on GET.  # noqa: E501

        :return: The ssl_client_certificate of this DebRemote.  # noqa: E501
        :rtype: str
        """
        return self._ssl_client_certificate

    @ssl_client_certificate.setter
    def ssl_client_certificate(self, ssl_client_certificate):
        """Sets the ssl_client_certificate of this DebRemote.

        A string containing the PEM encoded client certificate used for authentication. All new line characters must be escaped. Returns SHA256 sum on GET.  # noqa: E501

        :param ssl_client_certificate: The ssl_client_certificate of this DebRemote.  # noqa: E501
        :type: str
        """
        if ssl_client_certificate is not None and len(ssl_client_certificate) < 1:
            raise ValueError("Invalid value for `ssl_client_certificate`, length must be greater than or equal to `1`")  # noqa: E501

        self._ssl_client_certificate = ssl_client_certificate

    @property
    def ssl_client_key(self):
        """Gets the ssl_client_key of this DebRemote.  # noqa: E501

        A PEM encoded private key used for authentication. Returns SHA256 sum on GET.  # noqa: E501

        :return: The ssl_client_key of this DebRemote.  # noqa: E501
        :rtype: str
        """
        return self._ssl_client_key

    @ssl_client_key.setter
    def ssl_client_key(self, ssl_client_key):
        """Sets the ssl_client_key of this DebRemote.

        A PEM encoded private key used for authentication. Returns SHA256 sum on GET.  # noqa: E501

        :param ssl_client_key: The ssl_client_key of this DebRemote.  # noqa: E501
        :type: str
        """
        if ssl_client_key is not None and len(ssl_client_key) < 1:
            raise ValueError("Invalid value for `ssl_client_key`, length must be greater than or equal to `1`")  # noqa: E501

        self._ssl_client_key = ssl_client_key

    @property
    def ssl_validation(self):
        """Gets the ssl_validation of this DebRemote.  # noqa: E501

        If True, SSL peer validation must be performed.  # noqa: E501

        :return: The ssl_validation of this DebRemote.  # noqa: E501
        :rtype: bool
        """
        return self._ssl_validation

    @ssl_validation.setter
    def ssl_validation(self, ssl_validation):
        """Sets the ssl_validation of this DebRemote.

        If True, SSL peer validation must be performed.  # noqa: E501

        :param ssl_validation: The ssl_validation of this DebRemote.  # noqa: E501
        :type: bool
        """

        self._ssl_validation = ssl_validation

    @property
    def proxy_url(self):
        """Gets the proxy_url of this DebRemote.  # noqa: E501

        The proxy URL. Format: scheme://user:password@host:port  # noqa: E501

        :return: The proxy_url of this DebRemote.  # noqa: E501
        :rtype: str
        """
        return self._proxy_url

    @proxy_url.setter
    def proxy_url(self, proxy_url):
        """Sets the proxy_url of this DebRemote.

        The proxy URL. Format: scheme://user:password@host:port  # noqa: E501

        :param proxy_url: The proxy_url of this DebRemote.  # noqa: E501
        :type: str
        """
        if proxy_url is not None and len(proxy_url) < 1:
            raise ValueError("Invalid value for `proxy_url`, length must be greater than or equal to `1`")  # noqa: E501

        self._proxy_url = proxy_url

    @property
    def username(self):
        """Gets the username of this DebRemote.  # noqa: E501

        The username to be used for authentication when syncing.  # noqa: E501

        :return: The username of this DebRemote.  # noqa: E501
        :rtype: str
        """
        return self._username

    @username.setter
    def username(self, username):
        """Sets the username of this DebRemote.

        The username to be used for authentication when syncing.  # noqa: E501

        :param username: The username of this DebRemote.  # noqa: E501
        :type: str
        """
        if username is not None and len(username) < 1:
            raise ValueError("Invalid value for `username`, length must be greater than or equal to `1`")  # noqa: E501

        self._username = username

    @property
    def password(self):
        """Gets the password of this DebRemote.  # noqa: E501

        The password to be used for authentication when syncing.  # noqa: E501

        :return: The password of this DebRemote.  # noqa: E501
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """Sets the password of this DebRemote.

        The password to be used for authentication when syncing.  # noqa: E501

        :param password: The password of this DebRemote.  # noqa: E501
        :type: str
        """
        if password is not None and len(password) < 1:
            raise ValueError("Invalid value for `password`, length must be greater than or equal to `1`")  # noqa: E501

        self._password = password

    @property
    def last_updated(self):
        """Gets the last_updated of this DebRemote.  # noqa: E501

        Timestamp of the most recent update of the remote.  # noqa: E501

        :return: The last_updated of this DebRemote.  # noqa: E501
        :rtype: datetime
        """
        return self._last_updated

    @last_updated.setter
    def last_updated(self, last_updated):
        """Sets the last_updated of this DebRemote.

        Timestamp of the most recent update of the remote.  # noqa: E501

        :param last_updated: The last_updated of this DebRemote.  # noqa: E501
        :type: datetime
        """

        self._last_updated = last_updated

    @property
    def download_concurrency(self):
        """Gets the download_concurrency of this DebRemote.  # noqa: E501

        Total number of simultaneous connections.  # noqa: E501

        :return: The download_concurrency of this DebRemote.  # noqa: E501
        :rtype: int
        """
        return self._download_concurrency

    @download_concurrency.setter
    def download_concurrency(self, download_concurrency):
        """Sets the download_concurrency of this DebRemote.

        Total number of simultaneous connections.  # noqa: E501

        :param download_concurrency: The download_concurrency of this DebRemote.  # noqa: E501
        :type: int
        """
        if download_concurrency is not None and download_concurrency < 1:  # noqa: E501
            raise ValueError("Invalid value for `download_concurrency`, must be a value greater than or equal to `1`")  # noqa: E501

        self._download_concurrency = download_concurrency

    @property
    def policy(self):
        """Gets the policy of this DebRemote.  # noqa: E501

        The policy to use when downloading content. The possible values include: 'immediate', 'on_demand', and 'streamed'. 'immediate' is the default.  # noqa: E501

        :return: The policy of this DebRemote.  # noqa: E501
        :rtype: str
        """
        return self._policy

    @policy.setter
    def policy(self, policy):
        """Sets the policy of this DebRemote.

        The policy to use when downloading content. The possible values include: 'immediate', 'on_demand', and 'streamed'. 'immediate' is the default.  # noqa: E501

        :param policy: The policy of this DebRemote.  # noqa: E501
        :type: str
        """
        allowed_values = ["immediate", "on_demand", "streamed"]  # noqa: E501
        if policy not in allowed_values:
            raise ValueError(
                "Invalid value for `policy` ({0}), must be one of {1}"  # noqa: E501
                .format(policy, allowed_values)
            )

        self._policy = policy

    @property
    def distributions(self):
        """Gets the distributions of this DebRemote.  # noqa: E501

        Whitespace separated list of distributions to sync  # noqa: E501

        :return: The distributions of this DebRemote.  # noqa: E501
        :rtype: str
        """
        return self._distributions

    @distributions.setter
    def distributions(self, distributions):
        """Sets the distributions of this DebRemote.

        Whitespace separated list of distributions to sync  # noqa: E501

        :param distributions: The distributions of this DebRemote.  # noqa: E501
        :type: str
        """
        if distributions is None:
            raise ValueError("Invalid value for `distributions`, must not be `None`")  # noqa: E501
        if distributions is not None and len(distributions) < 1:
            raise ValueError("Invalid value for `distributions`, length must be greater than or equal to `1`")  # noqa: E501

        self._distributions = distributions

    @property
    def components(self):
        """Gets the components of this DebRemote.  # noqa: E501

        Whitespace separatet list of components to sync  # noqa: E501

        :return: The components of this DebRemote.  # noqa: E501
        :rtype: str
        """
        return self._components

    @components.setter
    def components(self, components):
        """Sets the components of this DebRemote.

        Whitespace separatet list of components to sync  # noqa: E501

        :param components: The components of this DebRemote.  # noqa: E501
        :type: str
        """
        if components is not None and len(components) < 1:
            raise ValueError("Invalid value for `components`, length must be greater than or equal to `1`")  # noqa: E501

        self._components = components

    @property
    def architectures(self):
        """Gets the architectures of this DebRemote.  # noqa: E501

        Whitespace separated list of architectures to sync  # noqa: E501

        :return: The architectures of this DebRemote.  # noqa: E501
        :rtype: str
        """
        return self._architectures

    @architectures.setter
    def architectures(self, architectures):
        """Sets the architectures of this DebRemote.

        Whitespace separated list of architectures to sync  # noqa: E501

        :param architectures: The architectures of this DebRemote.  # noqa: E501
        :type: str
        """
        if architectures is not None and len(architectures) < 1:
            raise ValueError("Invalid value for `architectures`, length must be greater than or equal to `1`")  # noqa: E501

        self._architectures = architectures

    @property
    def sync_sources(self):
        """Gets the sync_sources of this DebRemote.  # noqa: E501

        Sync source packages  # noqa: E501

        :return: The sync_sources of this DebRemote.  # noqa: E501
        :rtype: bool
        """
        return self._sync_sources

    @sync_sources.setter
    def sync_sources(self, sync_sources):
        """Sets the sync_sources of this DebRemote.

        Sync source packages  # noqa: E501

        :param sync_sources: The sync_sources of this DebRemote.  # noqa: E501
        :type: bool
        """

        self._sync_sources = sync_sources

    @property
    def sync_udebs(self):
        """Gets the sync_udebs of this DebRemote.  # noqa: E501

        Sync installer packages  # noqa: E501

        :return: The sync_udebs of this DebRemote.  # noqa: E501
        :rtype: bool
        """
        return self._sync_udebs

    @sync_udebs.setter
    def sync_udebs(self, sync_udebs):
        """Sets the sync_udebs of this DebRemote.

        Sync installer packages  # noqa: E501

        :param sync_udebs: The sync_udebs of this DebRemote.  # noqa: E501
        :type: bool
        """

        self._sync_udebs = sync_udebs

    @property
    def sync_installer(self):
        """Gets the sync_installer of this DebRemote.  # noqa: E501

        Sync installer files  # noqa: E501

        :return: The sync_installer of this DebRemote.  # noqa: E501
        :rtype: bool
        """
        return self._sync_installer

    @sync_installer.setter
    def sync_installer(self, sync_installer):
        """Sets the sync_installer of this DebRemote.

        Sync installer files  # noqa: E501

        :param sync_installer: The sync_installer of this DebRemote.  # noqa: E501
        :type: bool
        """

        self._sync_installer = sync_installer

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, DebRemote):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
