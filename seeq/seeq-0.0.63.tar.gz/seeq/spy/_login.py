import logging
import os
import six
import urllib
import urllib3

from seeq.base import gconfig
from seeq.sdk43 import *
from seeq.sdk43.rest import ApiException

from ._common import Status

from urllib3.connectionpool import MaxRetryError

client = None  # type: ApiClient
user = None  # type: UserOutputV1

AUTOMATIC_PROXY_DETECTION = '__auto__'


def login(username=None, password=None, *, url=None, directory='Seeq', ignore_ssl_errors=False,
          proxy=AUTOMATIC_PROXY_DETECTION, credentials_file=None, auth_token=None, quiet=False,
          status=None, auth_provider=None):
    """
    Establishes a connection with Seeq Server and logs in with a set of credentials.
    :param username: Username for login purposes. See credentials_file argument for alternative.
    :type username: str
    :param password: Password for login purposes. See credentials_file argument for alternative.
    :type password: str
    :param url: Seeq Server url. You can copy this from your browser and cut off everything to the right of the port
    (if present). E.g. https://myseeqserver:34216
    :type url: str
    :param directory: The authentication directory to use. You must be able to supply a username/password, so some
    passwordless Windows Authentication (NTLM) scenarios will not work. OpenID Connect is also not supported. If you
    need to use such authentication schemes, set up a Seeq Data Lab server.
    :type directory: str
    :param ignore_ssl_errors: If True, SSL certificate validation errors are ignored. Use this if you're in a trusted
    network environment but Seeq Server's SSL certificate is not from a common root authority.
    :type ignore_ssl_errors: bool
    :param proxy: Specifies the proxy server to use for all requests. The default value is "__auto__", which examines
    the standard HTTP_PROXY and HTTPS_PROXY environment variables. If you specify None for this parameter,
    no proxy server will be used.
    :type proxy: str
    :param credentials_file: Reads username and password from the specified file. If specified,
    :type credentials_file: str
    :param auth_token: Provide an authorization token directly from a browser session of Seeq Workbench.
    :type auth_token: str
    :param quiet: If True, suppresses progress output.
    :type quiet: bool
    :param status: If supplied, this Status object will be updated as the command progresses.
    :type status: Status
    :param auth_provider: Deprecated. Use directory instead.
    """

    status = Status.validate(status, quiet)

    if auth_provider is not None:
        raise RuntimeError('"auth_provider" argument has been renamed to "directory"')

    # Annoying warnings are printed to stderr if connections fail
    logging.getLogger("requests").setLevel(logging.FATAL)
    logging.getLogger("urllib3").setLevel(logging.FATAL)
    urllib3.disable_warnings()

    if url:
        # noinspection PyUnresolvedReferences
        parsed_url = urllib.parse.urlparse(url)
        gconfig.override_global_property('seeq_server_hostname', parsed_url.hostname)
        if parsed_url.scheme == 'https':
            port = '443'
            if parsed_url.port:
                port = six.text_type(parsed_url.port)
            gconfig.override_global_property('seeq_server_port', '')
            gconfig.override_global_property('seeq_secure_port', port)
        if parsed_url.scheme == 'http':
            port = '80'
            if parsed_url.port:
                port = six.text_type(parsed_url.port)
            gconfig.override_global_property('seeq_server_port', port)
            gconfig.override_global_property('seeq_secure_port', '')

    api_client_url = gconfig.get_api_url()

    cert_file = os.path.join(gconfig.get_data_folder(), 'keys', 'seeq-cert.pem')
    if os.path.exists(cert_file):
        Configuration().cert_file = cert_file
    key_file = os.path.join(gconfig.get_data_folder(), 'keys', 'seeq-key.pem')
    if os.path.exists(key_file):
        Configuration().key_file = key_file

    Configuration().verify_ssl = not ignore_ssl_errors

    if proxy == AUTOMATIC_PROXY_DETECTION:
        if api_client_url.startswith('https') and 'HTTPS_PROXY' in os.environ:
            Configuration().proxy = os.environ['HTTPS_PROXY']
        elif 'HTTP_PROXY' in os.environ:
            Configuration().proxy = os.environ['HTTP_PROXY']
    elif proxy is not None:
        Configuration().proxy = proxy

    global client
    client = ApiClient(api_client_url)

    if auth_token:
        if username or password or credentials_file:
            raise RuntimeError('username, password and/or credentials_file cannot be provided along with auth_token')

        client.auth_token = auth_token
    else:
        auth_api = AuthApi(client)
        auth_input = AuthInputV1()

        if credentials_file:
            if username is not None or password is not None:
                raise RuntimeError('If credentials_file is specified, username and password must be None')

            try:
                with open(credentials_file) as f:
                    lines = f.readlines()
            except Exception as e:
                raise RuntimeError('Could not read credentials_file "%s": %s' % (credentials_file, e))

            if len(lines) < 2:
                raise RuntimeError('credentials_file "%s" must have two lines: username then password')

            username = lines[0].strip()
            password = lines[1].strip()

        if not username or not password:
            raise RuntimeError('Both username and password must be supplied')

        auth_input.username = username
        auth_input.password = password

        status.update('Logging in to <strong>%s</strong> as <strong>%s</strong>' % (
            api_client_url, username), Status.RUNNING)

        directories = dict()
        try:
            auth_providers_output = auth_api.get_auth_providers()  # type: AuthProvidersOutputV1
        except MaxRetryError as e:
            raise RuntimeError(
                '"%s" could not be reached. Is the server or network down?\n%s' % (api_client_url, e))

        for datasource_output in auth_providers_output.auth_providers:  # type: DatasourceOutputV1
            directories[datasource_output.name] = datasource_output

        if directory not in directories:
            raise RuntimeError('directory "%s" not recognized. Possible directory(s) for this server: %s' %
                               (directory, ', '.join(directories.keys())))

        datasource_output = directories[directory]
        auth_input.auth_provider_class = datasource_output.datasource_class
        auth_input.auth_provider_id = datasource_output.datasource_id

        try:
            auth_api.login(body=auth_input)
        except ApiException as e:
            if e.status == 401:
                raise RuntimeError(
                    '"%s" could not be logged in with supplied credentials, check username and password.' %
                    auth_input.username)
            else:
                raise
        except MaxRetryError as e:
            raise RuntimeError(
                '"%s" could not be reached. Is the server or network down?\n%s' % (api_client_url, e))
        except Exception as e:
            raise RuntimeError('Could not connect to Seeq"s API at %s with login "%s".\n%s' % (api_client_url,
                                                                                               auth_input.username, e))

    users_api = UsersApi(client)

    global user
    user = users_api.get_me()  # type: UserOutputV1

    user_string = user.username
    user_profile = ''
    if user.first_name:
        user_profile = user.first_name
    if user.last_name:
        user_profile += ' ' + user.last_name
    if user.is_admin:
        user_profile += ' [Admin]'
    if len(user_profile) > 0:
        user_string += ' (%s)' % user_profile.strip()

    status.update('Logged in to <strong>%s</strong> successfully as <strong>%s</strong>' % (
        api_client_url, user_string), Status.SUCCESS)


def logout(quiet=False, status=None):
    """
    Logs you out of your current session.
    :param quiet: If True, suppresses progress output.
    :type quiet: bool
    :param status: If supplied, this Status object will be updated as the command progresses.
    :type status: Status
    """

    status = Status.validate(status, quiet)
    global client  # type: ApiClient
    if client is None:
        status.update('No action taken because you are not currently logged in.', Status.FAILURE)

    auth_api = AuthApi(client)
    auth_api.logout()

    client.logout()

    status.update('Logged out.', Status.SUCCESS)
