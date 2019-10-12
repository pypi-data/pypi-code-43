# encoding=utf-8
from collections import OrderedDict
import logging
import six
from six import text_type
import requests
from requests.auth import HTTPBasicAuth, AuthBase
from requests_oauthlib import OAuth1

import mwklient.errors as errors
import mwklient.listing as listing
from mwklient.sleep import Sleepers
from mwklient.util import parse_timestamp, read_in_chunks
from mwklient.util import version_tuple_from_generator


try:
    import json
except ImportError:
    import simplejson as json

try:
    import gzip
except ImportError:
    gzip = None

__version__ = '0.1.0'

LOG = logging.getLogger(__name__)

USER_AGENT = 'mwklient/{} ({})'.format(__version__,
                                       'https://github.com/lrusso96/mwklient')


class Site():
    """A MediaWiki site identified by its hostname.

        >>> import mwklient
        >>> site = mwklient.Site('en.wikipedia.org')

    Do not include the leading "http://".

    mwklient assumes that the script path (where index.php and api.php are
    located) is '/w/'. If the site uses a different script path, you must
    specify this (path must end in a '/').

    Examples:

    >>> site = Site('vim.wikia.com', path='/')
    >>> site = Site('sourceforge.net', path='/apps/mediawiki/mwknt')

    """
    api_limit = 500

    def __init__(self, host, path='/w/', ext='.php', pool=None,
                 retry_timeout=30, max_retries=25,
                 wait_callback=lambda *x: None, clients_useragent=None,
                 max_lag=3, compress=True, force_login=True, do_init=True,
                 httpauth=None, reqs=None, consumer_token=None,
                 consumer_secret=None, access_token=None, access_secret=None,
                 client_certificate=None, custom_headers=None, scheme='https'):
        # Setup member variables
        self.host = host
        self.path = path
        self.ext = ext
        self.credentials = None
        self.compress = compress
        self.max_lag = text_type(max_lag)
        self.force_login = force_login
        self.logged_in = False
        self.requests = reqs or {}
        self.scheme = scheme
        if 'timeout' not in self.requests:
            self.requests['timeout'] = 30  # seconds

        if consumer_token is not None:
            auth = OAuth1(consumer_token, consumer_secret,
                          access_token, access_secret)
        elif isinstance(httpauth, (list, tuple)):
            auth = HTTPBasicAuth(*httpauth)
        elif httpauth is None or isinstance(httpauth, (AuthBase,)):
            auth = httpauth
        else:
            raise RuntimeError(
                'Authentication is not a tuple or an instance of AuthBase')

        self.sleepers = Sleepers(max_retries, retry_timeout, wait_callback)

        # Site properties
        self.blocked = False    # Whether current user is blocked
        self.hasmsg = False  # Whether current user has new messages
        self.groups = []    # Groups current user belongs to
        self.rights = []    # Rights current user has
        self.tokens = {}    # Edit tokens of the current user
        self.version = None

        self.namespaces = self.default_namespaces
        self.writeapi = False

        # Setup connection
        if pool is None:
            self.connection = requests.Session()
            self.connection.auth = auth

            if client_certificate:
                self.connection.cert = client_certificate
            # Set User-Agent header field
            if clients_useragent:
                ua = clients_useragent + ' ' + USER_AGENT
            else:
                ua = USER_AGENT
            self.connection.headers['User-Agent'] = ua

            if custom_headers:
                self.connection.headers.update(custom_headers)
        else:
            self.connection = pool

        # Page generators
        self.pages = listing.PageList(self)
        self.categories = listing.PageList(self, namespace=14)
        self.images = listing.PageList(self, namespace=6)

        # Compat page generators
        self.Pages = self.pages
        self.Categories = self.categories
        self.Images = self.images

        # Initialization status
        self.initialized = False

        # Upload chunk size in bytes
        self.chunk_size = 1048576

        if do_init:
            try:
                self.site_init()
            except errors.APIError as e:
                if e.args[0] == 'mwoauth-invalid-authorization':
                    raise errors.OAuthAuthorizationError(self, e.code, e.info)

                # Private wiki, do init after login
                if e.args[0] not in {u'unknown_action', u'readapidenied'}:
                    raise

    def site_init(self):

        if self.initialized:
            info = self.get('query', meta='userinfo', uiprop='groups|rights')
            userinfo = info['query']['userinfo']
            self.username = userinfo['name']
            self.groups = userinfo.get('groups', [])
            self.rights = userinfo.get('rights', [])
            self.tokens = {}
            return

        meta = self.get('query', meta='siteinfo|userinfo',
                        siprop='general|namespaces', uiprop='groups|rights',
                        retry_on_error=False)

        # Extract site info
        self.site = meta['query']['general']
        self.namespaces = {
            namespace['id']: namespace.get('*', '')
            for namespace in six.itervalues(meta['query']['namespaces'])
        }
        self.writeapi = 'writeapi' in self.site

        self.version = version_tuple_from_generator(
            self.site['generator'])

        # Require MediaWiki version >= 1.16
        self.require(1, 16)

        # User info
        userinfo = meta['query']['userinfo']
        self.username = userinfo['name']
        self.groups = userinfo.get('groups', [])
        self.rights = userinfo.get('rights', [])
        self.initialized = True

    default_namespaces = {
        0: u'', 1: u'Talk', 2: u'User', 3: u'User talk', 4: u'Project',
        5: u'Project talk', 6: u'Image', 7: u'Image talk', 8: u'MediaWiki',
        9: u'MediaWiki talk', 10: u'Template', 11: u'Template talk',
        12: u'Help', 13: u'Help talk', 14: u'Category', 15: u'Category talk',
        -1: u'Special', -2: u'Media'
    }

    def __repr__(self):
        return "<Site object '%s%s'>" % (self.host, self.path)

    def get(self, action, *args, **kwargs):
        """Perform a generic API call using GET.

        This is just a shorthand for calling api() with http_method='GET'.
        All arguments will be passed on.

        Returns:
            The raw response from the API call, as a dictionary.
        """
        return self.api(action, 'GET', *args, **kwargs)

    def post(self, action, *args, **kwargs):
        """Perform a generic API call using POST.

        This is just a shorthand for calling api() with http_method='POST'.
        All arguments will be passed on.

        Returns:
            The raw response from the API call, as a dictionary.
        """
        return self.api(action, 'POST', *args, **kwargs)

    def api(self, action, http_method='POST', *args, **kwargs):
        """Perform a generic API call and handle errors.

        All arguments will be passed on.

        Example:
            To get coordinates from the GeoData MediaWiki extension at English
            Wikipedia:

            >>> site = Site('en.wikipedia.org')
            >>> result = site.api('query', prop='coordinates',
            titles='Oslo|Copenhagen')
            >>> for page in result['query']['pages'].values():
            ...     if 'coordinates' in page:
            ...         print '{} {} {}'.format(page['title'],
            ...             page['coordinates'][0]['lat'],
            ...             page['coordinates'][0]['lon'])
            Oslo 59.95 10.75
            Copenhagen 55.6761 12.5683

        Returns:
            The raw response from the API call, as a dictionary.
        """
        kwargs.update(args)

        if action == 'query' and 'continue' not in kwargs:
            kwargs['continue'] = ''
        if action == 'query':
            if 'meta' in kwargs:
                kwargs['meta'] += '|userinfo'
            else:
                kwargs['meta'] = 'userinfo'
            if 'uiprop' in kwargs:
                kwargs['uiprop'] += '|blockinfo|hasmsg'
            else:
                kwargs['uiprop'] = 'blockinfo|hasmsg'

        sleeper = self.sleepers.make()

        while True:
            info = self.raw_api(action, http_method, **kwargs)
            if not info:
                info = {}
            if self.handle_api_result(info, sleeper=sleeper):
                return info

    def handle_api_result(self, info, kwargs=None, sleeper=None):
        if sleeper is None:
            sleeper = self.sleepers.make()

        try:
            userinfo = info['query']['userinfo']
        except KeyError:
            userinfo = ()
        if 'blockedby' in userinfo:
            self.blocked = (userinfo['blockedby'],
                            userinfo.get('blockreason', u''))
        else:
            self.blocked = False
        self.hasmsg = 'messages' in userinfo
        self.logged_in = 'anon' not in userinfo
        if 'warnings' in info:
            for _, warning in info['warnings'].items():
                if '*' in warning:
                    LOG.warning(warning['*'])

        if 'error' in info:
            error_code = info['error'].get('code')
            if error_code in {u'internal_api_error_DBConnectionError',
                              u'internal_api_error_DBQueryError'}:
                sleeper.sleep()
                return False

            # cope with https://phabricator.wikimedia.org/T106066
            error_code = info['error'].get('code')
            invalid_mwoauth = error_code == u'mwoauth-invalid-authorization'
            unused_nonce = 'Nonce already used'
            if invalid_mwoauth and unused_nonce in info['error'].get('info'):
                LOG.warning(
                    'retrying due to nonce error '
                    'https://phabricator.wikimedia.org/T106066')
                sleeper.sleep()
                return False

            if 'query' in info['error']:
                # Semantic Mediawiki does not follow the standard error format
                raise errors.APIError(None, info['error']['query'], kwargs)

            if '*' in info['error']:
                raise errors.APIError(info['error']['code'],
                                      info['error']['info'], info['error']['*']
                                      )
            raise errors.APIError(info['error']['code'],
                                  info['error']['info'], kwargs)
        return True

    @staticmethod
    def _query_string(*args, **kwargs):
        kwargs.update(args)
        qs1 = [(k, v) for k, v in six.iteritems(kwargs)
               if k not in {'wpEditToken', 'token'}]
        qs2 = [(k, v) for k, v in six.iteritems(
            kwargs) if k in {'wpEditToken', 'token'}]
        return OrderedDict(qs1 + qs2)

    def raw_call(self, script, data, files=None, retry_on_error=True,
                 http_method='POST'):
        """
        Perform a generic request and return the raw text.

        In the event of a network problem, or a HTTP response with status code
        5XX, we'll wait and retry the configured number of times before giving
        up if `retry_on_error` is True.

        `requests.exceptions.HTTPError` is still raised directly for
        HTTP responses with status codes in the 4XX range, and invalid
        HTTP responses.

        Args:
            script (str): Script name, usually 'api'.
            data (dict): Post data
            files (dict): Files to upload
            retry_on_error (bool): Retry on connection error
            http_method (str): The HTTP method, defaults to 'POST'

        Returns:
            The raw text response.
        """
        headers = {}
        if self.compress and gzip:
            headers['Accept-Encoding'] = 'gzip'
        sleeper = self.sleepers.make((script, data))

        scheme = self.scheme
        host = self.host
        if isinstance(host, (list, tuple)):
            msg = 'Specifying host as tuple is deprecated: use scheme arg.'
            warnings.warn(msg, DeprecationWarning)  # noqa
            scheme, host = host

        url = '{scheme}://{host}{path}{script}{ext}'.format(
            scheme=scheme, host=host, path=self.path, script=script,
            ext=self.ext)

        while True:
            try:
                args = {'files': files, 'headers': headers}
                for k, v in self.requests.items():
                    args[k] = v
                if http_method == 'GET':
                    args['params'] = data
                else:
                    args['data'] = data

                stream = self.connection.request(http_method, url, **args)

                if stream.headers.get('x-database-lag'):
                    wait_time = int(stream.headers.get('retry-after'))
                    LOG.warning(
                        'Database lag exceeds max lag. Waiting for %d seconds',
                        wait_time)
                    sleeper.sleep(wait_time)
                elif stream.status_code == 200:
                    return stream.text
                elif stream.status_code < 500 or stream.status_code > 599:
                    stream.raise_for_status()
                else:
                    if not retry_on_error:
                        stream.raise_for_status()
                    msg = 'Received %s response: %s. Retrying in a moment.'
                    LOG.warning(msg, stream.status_code, stream.text)
                    sleeper.sleep()

            except requests.exceptions.ConnectionError:
                # In the event of a network problem
                # (e.g. DNS failure, refused connection, etc),
                # Requests will raise a ConnectionError exception.
                if not retry_on_error:
                    raise
                LOG.warning('Connection error. Retrying in a moment.')
                sleeper.sleep()

    def raw_api(self, action, http_method='POST', *args, **kwargs):
        """Send a call to the API."""
        try:
            retry_on_error = kwargs.pop('retry_on_error')
        except KeyError:
            retry_on_error = True
        kwargs['action'] = action
        kwargs['format'] = 'json'
        data = self._query_string(*args, **kwargs)
        res = self.raw_call('api', data, retry_on_error=retry_on_error,
                            http_method=http_method)

        try:
            return json.loads(res, object_pairs_hook=OrderedDict)
        except ValueError:
            if res.startswith('MediaWiki API is not enabled for this site.'):
                raise errors.APIDisabledError
            raise errors.InvalidResponse(res)

    def raw_index(self, action, http_method='POST', *args, **kwargs):
        """Sends a call to index.php rather than the API."""
        kwargs['action'] = action
        kwargs['maxlag'] = self.max_lag
        data = self._query_string(*args, **kwargs)
        return self.raw_call('index', data, http_method=http_method)

    def require(self, major, minor, revision=None, raise_error=True):
        if self.version is None:
            if raise_error is None:
                return None
            raise RuntimeError(
                'Site %s has not yet been initialized' % repr(self))

        if revision is None:
            if self.version[:2] >= (major, minor):
                return True
            if raise_error:
                raise errors.MediaWikiVersionError(
                    'Requires version {required[0]}.{required[1]}, '
                    'current version is {current[0]}.{current[1]}'
                    .format(required=(major, minor),
                            current=(self.version[:2]))
                )
            return False
        raise NotImplementedError

    # Actions
    def email(self, user, text, subject, cc=False):
        """
        Send email to a specified user on the wiki.

            >>> try:
            ...     site.email('SomeUser', 'Some message', 'Some subject')
            ... except mwklient.errors.NoSpecifiedEmailError as err:
            ...     print 'The user does not accept email, or has not specified
            an email address.'

        Args:
            user (str): User name of the recipient
            text (str): Body of the email
            subject (str): Subject of the email
            cc (bool): True to send a copy of the email to yourself
            (default is False)

        Returns:
            Dictionary of the JSON response

        Raises:
            NoSpecifiedEmailError (mwklient.errors.NoSpecifiedEmailError):
            if recipient does not accept email
            EmailError (mwklient.errors.EmailError): on other errors
        """

        token = self.get_token('email')

        try:
            info = self.post('emailuser', target=user, subject=subject,
                             text=text, ccme=cc, token=token)
        except errors.APIError as err:
            if err.args[0] == u'noemail':
                raise errors.NoSpecifiedEmail(user, err.args[1])
            raise errors.EmailError(*err.args)

        return info

    def login(self, username=None, password=None, cookies=None, domain=None):
        """
        Login to the wiki using a username and password. The method returns
        nothing if the login was successful, but raises and error if it was not

        Args:
            username (str): MediaWiki username
            password (str): MediaWiki password
            cookies (dict): Custom cookies to include with the log-in request.
            domain (str): Sends domain name for authentication; used by some
                MediaWiki plug-ins like the 'LDAP Authentication' extension.

        Raises:
            LoginError (mwklient.errors.LoginError): Login failed, the reason
             can be obtained from e.code and e.info (where e is the exception
             object) and will be one of the API:Login errors. The most common
             error code is "Failed", indicating a wrong username or password.

            MaximumRetriesExceeded: API call to log in failed and was retried
            until all retries were exhausted. This will not occur if the
            credentials are merely incorrect. See MaximumRetriesExceeded for
            possible reasons.

            APIError: An API error occurred. Rare, usually indicates an
            internal server error.
        """

        if username and password:
            self.credentials = (username, password, domain)
        if cookies:
            self.connection.cookies.update(cookies)

        if self.credentials:
            sleeper = self.sleepers.make()
            kwargs = {
                'lgname': self.credentials[0],
                'lgpassword': self.credentials[1]
            }
            if self.credentials[2]:
                kwargs['lgdomain'] = self.credentials[2]

            # Try to login using the scheme for MW 1.27+. If the wiki is read
            # protected, it is not possible to get the wiki version upfront
            # using the API, so we just have to try.
            # If the attempt fails, we try the old method.
            try:
                kwargs['lgtoken'] = self.get_token('login')
            except (errors.APIError, KeyError):
                LOG.debug(
                    'Failed to get login token, MediaWiki is older than 1.27.')

            while True:
                login = self.post('login', **kwargs)

                if login['login']['result'] == 'Success':
                    break
                elif login['login']['result'] == 'NeedToken':
                    kwargs['lgtoken'] = login['login']['token']
                elif login['login']['result'] == 'Throttled':
                    sleeper.sleep(int(login['login'].get('wait', 5)))
                else:
                    raise errors.LoginError(self, login['login']['result'],
                                            login['login']['reason'])

        self.site_init()

    def get_token(self, type_t, force=False, title=None):

        if self.version is None or self.version[:2] >= (1, 24):
            # The 'csrf' (cross-site request forgery) token introduced in 1.24
            # replaces the majority of older tokens, like edittoken and
            # movetoken.
            if type_t not in {'watch', 'patrol', 'rollback', 'userrights',
                              'login'}:
                type_t = 'csrf'

        if type_t not in self.tokens:
            self.tokens[type_t] = '0'

        if self.tokens.get(type_t, '0') == '0' or force:

            if self.version is None or self.version[:2] >= (1, 24):
                # We use raw_api() rather than api() because api() is adding
                # "userinfo" to the query and this raises a readapideniederror
                # if the wiki is read protected and we're trying to fetch a
                # login token.
                # fix v0.0.2: type parameter must passed, with value type_t
                info = self.raw_api(
                    'query', 'GET', meta='tokens', type=type_t)

                self.handle_api_result(info)

                # Note that for read protected wikis, we don't know the version
                # when fetching the login token. If it's < 1.27, the request
                # below will raise a KeyError that we should catch.
                self.tokens[type_t] = info['query']['tokens']['%stoken' %
                                                              type_t]

            else:
                if title is None:
                    # Some dummy title was needed to get a token prior to 1.24
                    title = 'Test'
                info = self.post('query', titles=title,
                                 prop='info', intoken=type_t)
                for i in six.itervalues(info['query']['pages']):
                    if i['title'] == title:
                        self.tokens[type_t] = i['%stoken' % type_t]

        return self.tokens[type_t]

    def upload(self, file=None, filename=None, description='', ignore=False,
               url=None, filekey=None, comment=None):
        """Upload a file to the site.

        Note that one of `file`, `filekey` and `url` must be specified, but not
        more than one. For normal uploads, you specify `file`.

        Args:
            file (str): File object or stream to upload.
            filename (str): Destination filename, don't include namespace
                            prefix like 'File:'
            description (str): Wikitext for the file description page.
            ignore (bool): True to upload despite any warnings.
            url (str): URL to fetch the file from.
            filekey (str): Key that identifies a previous upload that was
                           stashed temporarily.
            comment (str): Upload comment. Also used as the initial page text
                           for new files if `description` is not specified.

        Example:

            >>> client.upload(open('somefile', 'rb'), filename='somefile.jpg',
                              description='Some description')

        Returns:
            JSON result from the API.

        Raises:
            errors.InsufficientPermission
            requests.exceptions.HTTPError
        """

        if not filename:
            raise TypeError('filename must be specified')

        if len([x for x in [file, filekey, url] if x is not None]) != 1:
            raise TypeError(
                "exactly one of 'file', 'filekey' and 'url' must be specified")

        image = self.Images[filename]
        if not image.can('upload'):
            raise errors.InsufficientPermission(filename)

        if not comment:
            comment = description
            text = None
        else:
            comment = comment
            text = description

        if file:
            if not hasattr(file, 'read'):
                file = open(file, 'rb')

            content_size = file.seek(0, 2)
            file.seek(0)

            if self.version[:2] >= (1, 20) and content_size > self.chunk_size:
                return self.chunk_upload(file, filename, ignore, comment, text)

        predata = {
            'action': 'upload',
            'format': 'json',
            'filename': filename,
            'comment': comment,
            'text': text,
            'token': image.__get_token__('edit'),
        }

        if ignore:
            predata['ignorewarnings'] = 'true'
        if url:
            predata['url'] = url

        # sessionkey was renamed to filekey in MediaWiki 1.18
        # https://phabricator.wikimedia.org/
        # rMW5f13517e36b45342f228f3de4298bb0fe186995d
        if self.version[:2] < (1, 18):
            predata['sessionkey'] = filekey
        else:
            predata['filekey'] = filekey

        postdata = predata
        files = None
        if file:

            # Workaround for https://github.com/mwclient/mwclient/issues/65
            # ----------------------------------------------------------------
            # Since the filename in Content-Disposition is not interpreted,
            # we can send some ascii-only dummy name rather than the real
            # filename, which might contain non-ascii.
            files = {'file': ('fake-filename', file)}

        sleeper = self.sleepers.make()
        while True:
            data = self.raw_call('api', postdata, files)
            info = json.loads(data)
            if not info:
                info = {}
            if self.handle_api_result(info, kwargs=predata, sleeper=sleeper):
                response = info.get('upload', {})
                break
        if file:
            file.close()
        return response

    def chunk_upload(self, file, filename, ignorewarnings, comment, text):
        """Upload a file to the site in chunks.

        This method is called by `Site.upload` if you are connecting to a newer
        MediaWiki installation, so it's normally not necessary to call this
        method directly.

        Args:
            file (file-like object): File object or stream to upload.
            params (dict): Dict containing upload parameters.
        """
        image = self.Images[filename]

        content_size = file.seek(0, 2)
        file.seek(0)

        params = {
            'action': 'upload',
            'format': 'json',
            'stash': 1,
            'offset': 0,
            'filename': filename,
            'filesize': content_size,
            'token': image.get_token('edit'),
        }
        if ignorewarnings:
            params['ignorewarnings'] = 'true'

        sleeper = self.sleepers.make()
        offset = 0
        for chunk in read_in_chunks(file, self.chunk_size):
            while True:
                data = self.raw_call('api', params, files={'chunk': chunk})
                info = json.loads(data)
                if self.handle_api_result(info, kwargs=params,
                                          sleeper=sleeper):
                    response = info.get('upload', {})
                    break

            offset += chunk.tell()
            chunk.close()
            LOG.debug('%s: Uploaded %d of %d bytes',
                      filename, offset, content_size)
            params['filekey'] = response['filekey']
            if response['result'] == 'Continue':
                params['offset'] = response['offset']
            elif response['result'] == 'Success':
                file.close()
                break
            else:
                # Some kind or error or warning occured. In any case, we do not
                # get the parameters we need to continue, so we should return
                # the response now.
                file.close()
                return response
        par = {}
        for k in params:
            if k not in ['action', 'stash', 'offset']:
                par[k] = params[k]
        par['comment'] = comment
        par['text'] = text
        return self.post('upload', **par)

    def parse(self, text=None, title=None, page=None, prop=None,
              redirects=False, mobileformat=False):
        kwargs = {}
        if text is not None:
            kwargs['text'] = text
        if title is not None:
            kwargs['title'] = title
        if page is not None:
            kwargs['page'] = page
        if prop is not None:
            kwargs['prop'] = prop
        if redirects:
            kwargs['redirects'] = '1'
        if mobileformat:
            kwargs['mobileformat'] = '1'
        result = self.post('parse', **kwargs)
        return result['parse']

    # def block(self): TODO?
    # def unblock: TODO?
    # def patrol: TODO?
    # def import: TODO?

    # Lists
    def allpages(self, start=None, prefix=None, namespace='0',
                 filterredir='all', minsize=None, maxsize=None, prtype=None,
                 prlevel=None, limit=None, direc='ascending',
                 filterlanglinks='all', generator=True, end=None):
        """Retrieve all pages on the wiki as a generator."""

        pfx = listing.List.get_prefix('ap', generator)
        kwargs = dict(listing.List.generate_kwargs(
            pfx, ('from', start), ('to', end), prefix=prefix,
            minsize=minsize, maxsize=maxsize, prtype=prtype, prlevel=prlevel,
            namespace=namespace, filterredir=filterredir, direc=direc,
            filterlanglinks=filterlanglinks,
        ))
        return listing.List.get_list(generator)(self, 'allpages', 'ap',
                                                limit=limit,
                                                return_values='title',
                                                **kwargs)

    def allimages(self, start=None, prefix=None, minsize=None, maxsize=None,
                  limit=None, direc='ascending', sha1=None, sha1base36=None,
                  generator=True, end=None):
        """Retrieve all images on the wiki as a generator."""

        pfx = listing.List.get_prefix('ai', generator)
        kwargs = dict(listing.List.generate_kwargs(
            pfx, ('from', start), ('to', end), prefix=prefix,
            minsize=minsize, maxsize=maxsize,
            direc=direc, sha1=sha1, sha1base36=sha1base36,
        ))
        return listing.List.get_list(generator)(self, 'allimages', 'ai',
                                                limit=limit,
                                                return_values='timestamp|url',
                                                **kwargs)

    def alllinks(self, start=None, prefix=None, unique=False, prop='title',
                 namespace='0', limit=None, generator=True, end=None):
        """Retrieve a list of all links on the wiki as a generator."""

        pfx = listing.List.get_prefix('al', generator)
        kwargs = dict(listing.List.generate_kwargs(pfx, ('from', start),
                                                   ('to', end),
                                                   prefix=prefix,
                                                   prop=prop,
                                                   namespace=namespace))
        if unique:
            kwargs[pfx + 'unique'] = '1'
        return listing.List.get_list(generator)(self, 'alllinks', 'al',
                                                limit=limit,
                                                return_values='title',
                                                **kwargs)

    def allcategories(self, start=None, prefix=None, direc='ascending',
                      limit=None, generator=True, end=None):
        """Retrieve all categories on the wiki as a generator."""

        pfx = listing.List.get_prefix('ac', generator)
        kwargs = dict(listing.List.generate_kwargs(pfx, ('from', start),
                                                   ('to', end),
                                                   prefix=prefix, direc=direc))
        return listing.List.get_list(generator)(self, 'allcategories', 'ac',
                                                limit=limit, **kwargs)

    def allusers(self, start=None, prefix=None, group=None, prop=None,
                 limit=None, witheditsonly=False, activeusers=False,
                 rights=None, end=None):
        """Retrieve all users on the wiki as a generator."""

        kwargs = dict(listing.List.generate_kwargs('au', ('from', start),
                                                   ('to', end), prefix=prefix,
                                                   group=group, prop=prop,
                                                   rights=rights,
                                                   witheditsonly=witheditsonly,
                                                   activeusers=activeusers))
        return listing.List(self, 'allusers', 'au', limit=limit, **kwargs)

    def blocks(self, start=None, end=None, direc='older', ids=None, users=None,
               limit=None, prop='id|user|by|timestamp|expiry|reason|flags'):
        """Retrieve blocks as a generator.

        Returns:
            mwklient.listings.List: Generator yielding dicts,
            each dict containing:
                - user: The username or IP address of the user
                - id: The ID of the block
                - timestamp: When the block was added
                - expiry: When the block runs out (infinity for indefinite
                blocks)
                - reason: The reason they are blocked
                - allowusertalk: Key is present (empty string) if the user
                is allowed to edit their user talk page
                - by: the administrator who blocked the user
                - nocreate: key is present (empty string) if the user's ability
                to create accounts has been disabled.
        """

        # TODO: Fix. Fix what?
        kwargs = dict(listing.List.generate_kwargs('bk', start=start, end=end,
                                                   direc=direc, ids=ids,
                                                   users=users, prop=prop))
        return listing.List(self, 'blocks', 'bk', limit=limit, **kwargs)

    def deletedrevisions(self, start=None, end=None, direc='older',
                         namespace=None, limit=None, prop='user|comment'):
        # TODO: Fix

        kwargs = dict(listing.List.generate_kwargs('dr', start=start, end=end,
                                                   direc=direc,
                                                   namespace=namespace,
                                                   prop=prop))
        return listing.List(self, 'deletedrevs', 'dr', limit=limit, **kwargs)

    def exturlusage(self, query, prop=None, protocol='http', namespace=None,
                    limit=None):
        r"""Retrieve the list of pages that link to a particular domain or URL,
        as a generator.

        This API call mirrors the Special:LinkSearch function on-wiki.

        Query can be a domain like 'bbc.co.uk'.
        Wildcards can be used, e.g. '\*.bbc.co.uk'.
        Alternatively, a query can contain a full domain name and some or all
        of a URL:
        e.g. '\*.wikipedia.org/wiki/\*'

        See <https://meta.wikimedia.org/wiki/Help:Linksearch> for details.

        Returns:
            mwklient.listings.List: Generator yielding dicts,
            each dict containing:
                - url: The URL linked to.
                - ns: Namespace of the wiki page
                - pageid: The ID of the wiki page
                - title: The page title.

        """

        kwargs = dict(listing.List.generate_kwargs('eu', query=query,
                                                   prop=prop,
                                                   protocol=protocol,
                                                   namespace=namespace))
        return listing.List(self, 'exturlusage', 'eu', limit=limit, **kwargs)

    def logevents(self, type_t=None, prop=None, start=None, end=None,
                  direc='older', user=None, title=None, limit=None,
                  action=None):
        """Retrieve logevents as a generator."""
        kwargs = dict(listing.List.generate_kwargs('le', prop=prop,
                                                   type_t=type_t, start=start,
                                                   end=end, direc=direc,
                                                   user=user,
                                                   title=title, action=action))
        return listing.List(self, 'logevents', 'le', limit=limit, **kwargs)

    def checkuserlog(self, user=None, target=None, limit=10, direc='older',
                     start=None, end=None):
        """Retrieve checkuserlog items as a generator."""

        kwargs = dict(listing.List.generate_kwargs('cul', target=target,
                                                   start=start, end=end,
                                                   direc=direc, user=user))
        return listing.NestedList('entries', self, 'checkuserlog', 'cul',
                                  limit=limit, **kwargs)

    # def protectedtitles requires 1.15
    def random(self, namespace, limit=20):
        """Retrieve a generator of random pages from a particular namespace.

        limit specifies the number of random articles retrieved.
        namespace is a namespace identifier integer.

        Generator contains dictionary with namespace, page ID and title.

        """

        kwargs = dict(listing.List.generate_kwargs('rn', namespace=namespace))
        return listing.List(self, 'random', 'rn', limit=limit, **kwargs)

    def recentchanges(self, start=None, end=None, direc='older',
                      namespace=None, prop=None, show=None, limit=None,
                      type_t=None, toponly=None):
        """List recent changes to the wiki, à la Special:Recentchanges.
        """
        kwargs = dict(listing.List.generate_kwargs('rc', start=start, end=end,
                                                   direc=direc,
                                                   namespace=namespace,
                                                   prop=prop, show=show,
                                                   type_t=type_t,
                                                   toponly='1' if toponly else
                                                   None))
        return listing.List(self, 'recentchanges', 'rc', limit=limit, **kwargs)

    def revisions(self, revids, prop='ids|timestamp|flags|comment|user'):
        """Get data about a list of revisions.

        See also the `Page.revisions()` method.

        API doc: https://www.mediawiki.org/wiki/API:Revisions

        Example: Get revision text for two revisions:

            >>> for revision in site.revisions([689697696, 689816909],
            prop='content'):
            ...     print revision['*']

        Args:
            revids (list): A list of (max 50) revisions.
            prop (str): Which properties to get for each revision.

        Returns:
            A list of revisions
        """
        kwargs = {
            'prop': 'revisions',
            'rvprop': prop,
            'revids': '|'.join(map(text_type, revids))
        }

        revisions = []
        pages = self.get('query', **kwargs).get('query',
                                                {}).get('pages', {}).values()
        for page in pages:
            for revision in page.get('revisions', ()):
                revision['pageid'] = page.get('pageid')
                revision['pagetitle'] = page.get('title')
                revision['timestamp'] = parse_timestamp(revision['timestamp'])
                revisions.append(revision)
        return revisions

    def search(self, search, namespace='0', what=None, redirects=False,
               limit=None):
        """Perform a full text search.

        API doc: https://www.mediawiki.org/wiki/API:Search

        Example:
            >>> for result in site.search('prefix:Template:Citation/'):
            ...     print(result.get('title'))

        Args:
            search (str): The query string
            namespace (int): The namespace to search (default: 0)
            what (str): Search scope: 'text' for fulltext, or 'title' for
            titles only.
                        Depending on the search backend,
                        both options may not be available.
                        For instance
                        `CirrusSearch
                        <https://www.mediawiki.org/wiki/Help:CirrusSearch>`_
                        doesn't support 'title', but instead provides an
                        "intitle:" query string filter.
            redirects (bool): Include redirect pages in the search
                              (option removed in MediaWiki 1.23).

        Returns:
            mwklient.listings.List: Search results iterator
        """
        kwargs = dict(listing.List.generate_kwargs('sr', search=search,
                                                   namespace=namespace,
                                                   what=what))
        if redirects:
            kwargs['srredirects'] = '1'
        return listing.List(self, 'search', 'sr', limit=limit, **kwargs)

    def usercontributions(self, user, start=None, end=None, direc='older',
                          namespace=None, prop=None, show=None, limit=None,
                          uselang=None):
        """
        List the contributions made by a given user to the wiki

        API doc: https://www.mediawiki.org/wiki/API:Usercontribs
        """
        kwargs = dict(listing.List.generate_kwargs('uc', user=user,
                                                   start=start, end=end,
                                                   direc=direc,
                                                   namespace=namespace,
                                                   prop=prop, show=show))
        return listing.List(self, 'usercontribs', 'uc', limit=limit,
                            uselang=uselang, **kwargs)

    def users(self, users, prop='blockinfo|groups|editcount'):
        """
        Get information about a list of users.

        API doc: https://www.mediawiki.org/wiki/API:Users
        """

        return listing.List(self, 'users', 'us', ususers='|'.join(users),
                            usprop=prop)

    def watchlist(self, allrev=False, start=None, end=None, namespace=None,
                  direc='older', prop=None, show=None, limit=None):
        """
        List the pages on the current user's watchlist.

        API doc: https://www.mediawiki.org/wiki/API:Watchlist
        """

        kwargs = dict(listing.List.generate_kwargs('wl', start=start, end=end,
                                                   namespace=namespace,
                                                   direc=direc, prop=prop,
                                                   show=show))
        if allrev:
            kwargs['wlallrev'] = '1'
        return listing.List(self, 'watchlist', 'wl', limit=limit, **kwargs)

    def expandtemplates(self, text, title=None, generatexml=False):
        """
        Takes wikitext (text) and expands templates.

        API doc: https://www.mediawiki.org/wiki/API:Expandtemplates
        """

        kwargs = {}
        if title is None:
            kwargs['title'] = title
        if generatexml:
            kwargs['generatexml'] = '1'

        result = self.get('expandtemplates', text=text, **kwargs)

        if generatexml:
            return result['expandtemplates']['*'], result['parsetree']['*']
        return result['expandtemplates']['*']

    def ask(self, query, title=None):
        """
        Ask a query against Semantic MediaWiki.

        API doc: https://semantic-mediawiki.org/wiki/Ask_API

        Returns:
            Generator for retrieving all search results, with each answer as a
            dictionary.
            If the query is invalid, an APIError is raised. A valid query with
            zero results will not raise any error.

        Examples:

            >>> query = "[[Category:mycat]]|[[Has name::a name]]|?Has property"
            >>> for answer in site.ask(query):
            >>>     for title, data in answer.items()
            >>>         print(title)
            >>>         print(data)
        """
        kwargs = {}
        if title is None:
            kwargs['title'] = title

        offset = 0
        while offset is not None:
            results = self.raw_api('ask',
                                   query=u'{query}|offset={offset}'.format(
                                       query=query, offset=offset),
                                   http_method='GET', **kwargs)
            self.handle_api_result(results)  # raises APIError on error
            offset = results.get('query-continue-offset')
            answers = results['query'].get('results', [])

            if isinstance(answers, dict):
                # In older versions of Semantic MediaWiki, at least until 2.3.0
                # a list was returned. In newer versions an object is returned
                # with the page title as key.
                answers = [answer for answer in answers.values()]

            for answer in answers:
                yield answer
