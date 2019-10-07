import os
import math
from collections import namedtuple
import xml.etree.ElementTree as ET  # nosec (trused XML source)
import urllib.request
import re
import base64
from datetime import datetime
import logging
from bebanjo import xml_utils
from bebanjo.error import XMLPassError, InvalidResourceError

DEFAULT_PER_PAGE = 50   # default number of items per page for pagination call

logger = logging.getLogger(__name__)

# pylint: disable=bare-except


def hyphen_to_under(tag):
    return tag.replace('-', '_')


def strip_url_params(url):
    m = re.match(r'([^?]*)\?', url)
    return m.group(1) if m else url


def trailing_id(url):
    '''Returns string digits from end of url or int
    '''
    try:
        return re.search(r'\d+$', str(url)).group(0)
    except Exception:
        raise ValueError(f'URL {url} contains no trailing digits')


def overlay_url(left, right):
    '''Returns new url from left side overlayed with right side. left side must be full url
    '''
    split_left = left.split('/api')
    split_right = right.split('/api')
    if len(split_right) > 1:
        # right is full url
        return f'{split_left[0]}/api{split_right[1]}'
    # right is partial, make sure it has / prefix and append to left
    right = '/' + right if not right.startswith('/') else right
    return left + right


def name_from_resource(url):
    '''Returns the resource name from the right-most side of the url. e.g.
        "../titles/101" returns "title"
        "../title_groups returns title_groups
    '''
    return re.findall(r'([a-z_-]+)', url)[-1]


def return_object_name_from_resource(url):
    '''Returns a name for the resource that would be returned from the URL. e.g.:
        "../titles/101" returns "title"
        "../title_groups returns title_groups
    '''
    m = re.match(r'.*/api.*/([a-z_-]+)(/\d+)?$', url)
    if m is None:
        typ = 'api'
    elif m.group(2):
        typ = m.group(1)[:-1]
    else:
        typ = m.group(1)
    return hyphen_to_under(typ)


def image_dict_prepare(image_meta, name, url, fh):
    '''In-place update of image_meta. Sets encoding based on name_or_url. If fh provided, also
    prepares the the base64 encoded image file to send and related file metadata
    '''
    path = name or url
    try:
        m = re.search(r'[.](jp[e]?g|png)$', path, re.IGNORECASE)
        ext = m.group(1).lower()
        if ext in ['jpg', 'jpeg', 'png']:
            enc = 'jpeg'
        elif ext == 'png':
            enc = 'png'
        else:
            raise Exception
    except:
        raise ValueError('Unsupported image file name extension')
    else:
        if image_meta.get('encoding', None) is None:
            image_meta['encoding'] = enc
        if fh:
            mes = base64.b64encode(fh.read())
            attachment_str = f'data:image/{enc};base64,{str(mes, encoding="ascii")}'
            image_meta['attachment'] = attachment_str
            if image_meta.get('file_name', None) is None:
                image_meta['file_name'] = name


def send_body(url, method, data=b''):
    '''Makes a method call to Bebanjo with data (typically utf-8 encoded xml) and returns
    the response. Method should be put, post or delete depending on CRUD operation.
    '''
    logger.debug('%s to %s with payload: %s', method, url, data.decode())
    headers = {'Content-type': 'application/xml'}
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        http_response = urllib.request.urlopen(req)  # nosec
    except urllib.error.HTTPError as e:
        logger.error('%s %s returned status %s', method, url, e.code)
        raise
    else:
        logger.info('%s %s returned status %s', method, url, http_response.getcode())
        return http_response


def pass_scope(scope, opts):
    if not isinstance(scope, tuple) and len(scope) != 3:
        raise ValueError('scope parameter must be tuple of 3 elements')
    scope, from_to = scope[0], [scope[1], scope[2]]
    scopes = set(['going_online', 'coming_offline', 'online'])
    if scope not in scopes:
        raise ValueError('first element of scope must be: ' + '|'.join(scopes))
    opts.append(f'scope={scope}')
    for i in (0, 1):
        if isinstance(from_to[i], datetime):
            from_to[i] = from_to[i].isoformat(timespec='minutes')
        if not re.match(r'^\d{4}-\d\d-\d\dT?(\d\d:\d\d(:\d\d)?)?(Z|[+-]\d\d:\d\d)?$', from_to[i]):
            raise ValueError(f'invalid datetime value in scope: {from_to[i]}')
    opts.append(f'from={from_to[0]}')
    opts.append(f'to={from_to[1]}')


def value_from_el(el):
    el_type = el.attrib.get('type', None)
    if el_type == 'integer':
        return int(el.text)
    if el_type == 'boolean':
        return el.text.startswith('true')
    if el_type == 'array':
        return [ai.text for ai in el.findall('./')]
    # else like no type or datetime or not invented at time of writing is treated as text type
    return '' if el.text is None else el.text


def get_link_data(el):
    '''extract link rel and href from elememt. Includes conversion of rel to underscore
    '''
    if el.tag == 'link':
        rel = hyphen_to_under(el.attrib.get('rel'))
        link = namedtuple('Link', 'rel href')(rel, el.attrib.get('href'))
        return link
    return None


def _get_collections_members(elcol):
    '''returns dict of member objects from given etree element that is a collection
    '''
    mems = {}
    for elch in elcol:
        if elch.tag in ['total-entries', 'link']:
            continue   # ignore, already parsed in other process
        else:
            mem = objectify_element(elch)
            mems[mem.id] = mem
    return mems


def transfer_pagination_from_href(pagination, link):
    '''in place transfer of url parameters to pagination dict
    '''
    mg = re.search(r'[?&]per_page=([0-9]+)', link.href)
    if mg:
        pagination['per_page'] = int(mg.group(1))   # else leave to defaults
    if link.rel == 'next':
        mg = re.search(r'[?&]page=([0-9]+)', link.href)
        pagination['next'] = int(mg.group(1)) if mg else None


def get_metadata_attributes_pagination(el):
    meta = {}
    attributes = {}
    pagination = {}
    for node in el:
        link = get_link_data(node)
        if link:
            # special case
            if link.rel == 'self':
                attributes['self_href'] = link.href
            elif link.rel in ['next', 'prev']:
                transfer_pagination_from_href(pagination, link)
            else:     # return as Bebanjo objects
                try:
                    child = node[0]  # if link node has a child, then objectify to a fetched object
                    attributes[link.rel] = objectify_element(child, link.href)
                except IndexError:   # else a simple url fetcher object
                    attributes[link.rel] = Fetcher(url=link.href)
        else:
            node_tag = hyphen_to_under(node.tag)
            if node_tag == 'total_entries':  # special case
                pagination[node_tag] = int(node.text)
            else:
                meta[node_tag] = value_from_el(node)
    return meta, attributes, pagination


def objectify_element(el, url=None):
    '''Given an etree XML element from Movida/Sequence, return an object instance including
    any child items.

    URL must be provided in circumstances where the element does not contain
    a link node of rel='self' e.g. metadata or titles resource.  If link self is found it
    overrides the given url.
    '''
    meta, attributes, pagination = get_metadata_attributes_pagination(el)
    self_href = attributes.pop('self_href', url)
    class_name = el.tag.title().replace('_', '')
    el_type = el.attrib.get('type', '')
    if el_type == 'array':        # el represents a collection, need to build members
        members = _get_collections_members(el)
        return Collection(url=self_href, members=members, attributes=attributes,
                          pagination=pagination)
    if el_type == 'document':
        if class_name != 'Metadata':
            raise ValueError
        return Metadata(url=url, meta=meta)
    if meta:
        _ = meta.pop('id', None)  # discard, is ro and @property of self_href
        attributes['_meta1'] = meta
    return type(class_name, (Fetcher,), attributes)(url=self_href)


def objectify_response(http_response, url):
    '''Pass a http response and return an instance of Fetcher compatible class.
    '''
    body_b = http_response.read()
    logger.debug('response body: %s', body_b.decode())
    try:
        el = ET.fromstring(body_b)  # nosec (trused source)
    except ET.ParseError:
        raise XMLPassError({'msg': 'Bad response body XML', 'body': body_b.decode()})
    else:
        r = objectify_element(el, url=strip_url_params(url))
        return r


def _get(url):
    '''Do a GET call to Movida and transform the response into an instance of Fetcher
    compatible class.
    '''
    try:
        http_response = urllib.request.urlopen(url)  # nosec (url locked to http)
    except urllib.error.HTTPError as e:
        logger.error('GET %s returned status %s', url, e.code)
        raise
    else:
        logger.info('GET %s returned status %s', url, http_response.getcode())
        return objectify_response(http_response, url)


def patch_attributes(obj, attributes):
    for name, val in attributes.items():
        setattr(obj, name, val)


class Fetcher():
    '''
    Represents a generic API resource of unknown attrubutes other than its URL. Provides
    some generic capabilities that are inhereted by more specific classes of objects that
    are better known after the resource is obtained.
    '''

    def __init__(self, url):
        self._url = url

    @property
    def id(self):
        '''The objects ID if it has one else None
        '''
        m_id = re.search(r'/(\d+)/?$', self._url)
        return int(m_id.group(1)) if m_id else None

    @property
    def url(self):
        '''The objects full URL
        '''
        return self._url

    @property
    def summary_url(self):
        '''The right side of the objects URL after /api
        '''
        m = re.match(r'.*/api(/.*)$', self._url)
        return m.group(1) if m else '/'

    @property
    def resource_type(self):
        '''Provides a name for the resource object being represented by the URL
        e.g. "api", "title", "titles", "title_group"
        '''
        return return_object_name_from_resource(self.url)

    def fetch(self, _id=None, *, name=None, external_id=None, expand=None, scope=None):
        'Get a thing or things from Movida'
        opts = []
        res = ''
        if expand:
            _expand = expand if isinstance(expand, list) else [expand]
            opts.append('expand=' + ','.join(_expand))
        if _id:
            _id = str(_id)
            if not _id.isdigit():
                raise ValueError
            res += '/' + _id
        elif name:
            opts.append('name=' + str(name))
        elif external_id:
            opts.append('external_id=' + str(external_id))
        elif scope:
            pass_scope(scope, opts)
        url = self._url + res
        opts = '?' + '&'.join(opts) if opts else ''
        r = _get(url + opts)
        # if context of request was singular, return the item out of the collection
        if name or external_id:
            return list(r.members.values())[0] if r else None
        return r

    def create(self, meta=None, links=None):
        '''Attempts to create a new object in Movida/Sequence based on a given object
        '''
        el = self._generate_child_root_tag()
        return self._create_from_el(el, meta, links)

    def _create_from_el(self, el, meta=None, links=None):
        xml = xml_utils.as_xml(el, meta, links)
        response = send_body(self._url, method='POST', data=xml)
        created = objectify_response(response, self._url)
        self._safe_add_member(created)
        return created

    def update(self, meta=None, links=None):
        '''Updating a thing's 1st class metadata and relations in Bebanjo, the response back
        updates our local/self. Exception raised if unsuccessful.
        '''
        root = ET.Element(self._snake_class_name())
        new = self._do_rest_xml_then_put(root, meta, links)
        self._copy_from(new)

    def delete(self, _id=None):
        '''Delete self or a child by ID or our metadata
        '''
        url = self.url
        if _id:
            # therefore a collection deleting a child, or singular deleting metadata
            if _id == 'metadata':
                setattr(self, 'metadata', Metadata(url=self.url + '/metadata'))
            else:
                if not str(_id).isdigit():
                    raise ValueError
                _ = self.members.pop(int(_id), None)  # pylint: disable=no-member
            url += f'/{_id}'
        else:
            # when deleting in self context it's not possible to remove us from parent; user to do
            pass
        send_body(url, method='DELETE')

    def add_platforms(self, targets):
        '''Creates target platforms. Expects an iterable of platform IDs or URLs. Returns self.
        To avoid 422 error when target already exists, preload self with fetch call and they
        will be ignored.  Updates self if self is instance of Collection.
        '''
        resource_name = name_from_resource(self.url)
        if resource_name != 'target_platforms':
            raise InvalidResourceError('add_platforms called on target_platforms resource')
        if isinstance(self, Collection):
            exists = [str(x.platform.id) for x in self]
        else:
            exists = []
        for pid in targets:
            _pid = trailing_id(pid)
            if _pid not in exists:
                platform_url = overlay_url(self.url, f'/api/platforms/{_pid}')
                el = ET.Element('target-platforms')

                self._create_from_el(el, meta={}, links={'platform': platform_url})
        return self

    def add_link(self, path, name=None):
        '''Adds a property to self of type fetcher so that it may be used to fetch from Movida.
        This feature avoids calls to Movida to get a predictable collection resource. Path can
        be relative to self or a full URL. Name of the property is based on last non-ID element
        of path or name if provided. Returns the new link's Fetcher object.
        '''
        path = overlay_url(self.url, path)
        name = name or name_from_resource(path)
        new_thing = Collection(url=path)
        setattr(self, name, new_thing)
        return new_thing

    def create_image(self, fullpath, *, meta={}):
        '''Creates a new image instance in Movida based on fullpath and optional metadata (dict).
        Note: the parent collective object (self) may be a basic Fetcher class not supporting
        child members. So we don't try to update members with the newly created image.
        '''
        if name_from_resource(self.url) != 'images':
            raise InvalidResourceError('create_image called on non-images resource')
        if fullpath.startswith('http'):
            meta['file-url'] = fullpath
            image_dict_prepare(meta, name=None, url=fullpath, fh=None)
            return self.create(meta)
        # else
        _, name = os.path.split(fullpath)
        with open(fullpath, 'rb') as fh:
            image_dict_prepare(meta, name=name, url=None, fh=fh)
        image = self.create(meta)
        self._safe_add_member(image)
        return image

    def __len__(self):
        return 0

    def __getitem__(self, key):
        '''Gives the object ability to get metadata (held in _meta1) by key like a dict
        '''
        if isinstance(key, int):
            raise TypeError(f'{self.__class__.__name__} is not itterable')
        if getattr(self, '_meta1', None) is None:
            raise TypeError(f'{self.__class__.__name__} is not subscriptable')
        return self._meta1[key]  # pylint: disable=no-member

    def __repr__(self):
        ri = []
        for k in '_meta1 metadata'.split():
            v = getattr(self, k, None)
            if v is not None:
                ri.append(f'{k}: {v.__repr__()}')
        return f'{self.__class__.__name__ }({", ".join(ri)})'

    def _generate_child_root_tag(self):
        '''Prepares an etree root element based on self
        '''
        root_tag = hyphen_to_under(name_from_resource(self._url))
        if root_tag.endswith('s'):
            root_tag = root_tag[:-1]
        tag = ET.Element(root_tag)
        if root_tag == 'metadata':
            tag.set('type', 'document')
        return tag

    def _do_rest_xml_then_put(self, root, meta=None, links=None):
        xml = xml_utils.as_xml(root, meta, links)
        response = send_body(self._url, method='PUT', data=xml)
        return objectify_response(response, self._url)

    def _snake_class_name(self):
        return hyphen_to_under(type(self).__name__.lower())

    def _copy_from(self, other):
        for key in ['_meta1', '_pagination', 'metadata', 'members'] + other.child_getters():
            attr = getattr(other, key, None)
            if attr:
                setattr(self, key, attr)

    def _safe_add_member(self, child):
        '''Add an item to self.members and return item.  Only possible when self is
        a class Collection, hence safe add.  When Fetcher maps to a collection resource
        it should still be possible to create child items in Movida from it.
        '''
        try:
            self.members[child.id] = child
        except AttributeError:
            pass

    def child_getters(self):
        '''Returns list of names of our child getters.
        '''
        r = []
        for k in dir(self):
            if not k.startswith('_'):
                v = getattr(self, k)
                if isinstance(v, Fetcher):
                    r.append(k)
        return r


class Metadata(dict, Fetcher):
    '''dict methods take precidence e.g. __len__ comes from dict.
    '''

    def __init__(self, *, url, meta={}):
        Fetcher.__init__(self, url=url)
        dict.__init__(self, meta)

    def __repr__(self):
        return f'{self.__class__.__name__}({dict.__repr__(self)})'

    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def update(self, meta: dict):       # pylint: disable=arguments-differ
        root = ET.Element('metadata')
        root.set('type', 'document')
        new = self._do_rest_xml_then_put(root, meta)
        for k, v in new.items():
            self[k] = v


class Collection(Fetcher):

    def __init__(self, url=None, members=None, attributes=None, pagination=None):
        Fetcher.__init__(self, url=url)
        self.members = members or {}
        if attributes:
            patch_attributes(self, attributes)
        self._pagination = pagination or {}
        # self.per_page = DEFAULT_PER_PAGE
        self._item_cursor = 0

    def get_paginated(self, page=1, per_page=DEFAULT_PER_PAGE):
        '''Get selected pages of referenced collection using pagination.  Hold only the last page
        of members locally, return self. Update page num, so any itteration continues from this
        point.
        '''
        opts = [f'page={page}', 'pagination=true']
        opts += [f'per_page={per_page}']
        opts = '?' + '&'.join(opts)
        new = _get(self._url + opts)
        if new:
            self._copy_from(new)
            return self
        return None

    def get_member(self, _id):
        '''Get's child member if it exists else returns None
        '''
        return self.members.get(_id)

    @property
    def count_pages(self):
        if isinstance(self.items_available, int) and self.per_page:
            return math.ceil(self.items_available / self.per_page)
        return None

    @property
    def next_page(self):
        return self._pagination.get('next')

    @property
    def per_page(self):
        return self._pagination.get('per_page', DEFAULT_PER_PAGE)

    @property
    def items_available(self):
        return self._pagination.get('total_entries')

    @property
    def keys(self):
        return self.members.keys

    # item itteration - requires indexable items like list but also need dict attributes
    # so maitain list of keys alongside an ordered dict. Only require list when itterating.

    def _refresh_item_key_list(self):
        self._item_key_list = list(self.members.keys())  # pylint: disable=attribute-defined-outside-init

    def __iter__(self):
        self._item_cursor = 0
        self._refresh_item_key_list()
        return self

    def __next__(self):
        if self._item_cursor == len(self) and self.next_page:
            self._item_cursor = 0
            self.get_paginated(page=self.next_page, per_page=self.per_page)
            self._refresh_item_key_list()
        if self._item_cursor < len(self):
            item_key = self._item_key_list[self._item_cursor]
            item = self.members[item_key]
            self._item_cursor += 1
            return item
        raise StopIteration()

    def __getitem__(self, key):
        # Conveniently get a local member by ID e.g. title_groups[187341]
        return self.members[key]

    def __len__(self):
        return self.members.__len__()

    def __str__(self):
        return f'{type(self).__name__}  (url: {self._url}) Contains {len(self)} items.'
