"""
Development Notes
    https://stackoverflow.com/questions/17913224/which-term-best-describes-elements-of-url-path
"""
import collections
from contextlib import contextmanager
import inspect
import logging
import mimetypes
import os
import re

from hippu.filter import Filters
from hippu.utils import get_name

log = logging.getLogger(__name__)


class BaseService:

    def __init__(self, name=None, context=None):
        self.name = name if name else ''
        self.filters = []
        self.context = context if context else Context()

    def __str__(self):
        return self.name

    def __call__(self, request, response, context):
        pass

    def match(self, request):
        """ Returns matching handler for the request or None.

        Returned handler must be a callable that accept 'request' and 'response'
        as argumetents.

        Returning None indicates that this service cannot serve the request.

        For example,

            def match(self, request):
                def _handler(request, response):
                    pass

                return _handler
        """
        return self.create_resolver(self)

    def create_resolver(self, handler):
        """ Creates a resolver.

        Resolver wraps request filters and context with the handler.
        """
        return Resolver(handler, self.filters, self.context)

    def update_context(self, **items):
        """ Update context with given key-value pairs.

        Usage:
            service.update_context(key=value, key2=value2)
        """
        self.context.update(items)

    def add_filter(self, filter):
        """ Add a filter to pre or post process requests.

        Filters are called subsequently before requst handler.
        """
        if inspect.isclass(filter):
           self.filters.append(filter())
        else:
            self.filters.append(filter)

    def mount(self, path):
        """ Actions to mount this service under given path. """
        pass

    def unmount(self):
        """ Actions to un-mount this service. """
        pass


class Service(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._root_node = Node('service')

    @classmethod
    def create_route(cls, method, path, handler, context=None):
        return Route(method, path, handler, context)

    def create_node(self, name):
        if '{' in name:
            match = re.search(r'{([^:]+):*(.*)}', name)
            var_name = match.group(1)
            type_name = match.group(2) if match.group(2) else 'str'

            node = Variable(var_name, type_name)
            # node.set_data_type(type_name)
        else:
            node = Node(name)

        return node

    def map(self, method, path, handler, context=None):
        node = self._root_node
        method = method.upper()

        # Verbose "Map GET /path/to/resource"
        log.debug("Map %s %s -> %s", method, path, get_name(handler))

        for segment in path.split('/')[1:]:
            if node.has_child(segment):
                #
                # Previously mapped node found. No route will be created.
                #

                node = node.get_child(segment)
                continue

            # Create child node unless segment value is ''. This denotes the current node
            # itself.

            if segment:
                #
                # No previously defined node found. New node will be created.
                #

                child = self.create_node(segment)
                node.put_child(segment, child)
                node = child

        #
        # Create a route object to match the given method and path.
        #

        route = self.create_route(method, path, handler, context)
        node.put_route(method, route)

        return route

    def match(self, request):
        path = request.path.relative
        method = request.method
        node = self._root_node

        context = Context()
        context.update(self.context)

        log.debug("Searching matching handler from '%s' service.", self)

        for segment in path.split('/')[1:]:
            if node.is_collection():
                #
                # Current (parent) node is 'collection' of resources with a dynamic
                # naming.
                #
                # For example:
                #   /api/orders/{number}
                #

                node = node.first_child()

                try:
                    # Node name must match the given type specification.
                    # context[node.name] = node.type(segment)
                    context.put(node.name, node.type(segment))
                except Exception as err:
                    log.warning(err)
                    return None

            elif segment:
                #
                # Get child node with given name.
                #

                node = node.get_child(segment)
            else:
                #
                # Segment is empty string => this will denote current node
                # like root node.
                #
                # HTTP RFC 2396 defines path separator to be single slash.
                #

                pass

            # No matching node found; Given path does not match any known
            # route.
            if not node:
                return None

        route = node.get_route(method)

        if not route:
            return None

        context.update(route.context)

        return Resolver(route.handler, self.filters, context)


class FileService(BaseService):
    """ Service to server static files from given root path. """

    def __init__(self, path='./static', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._static_dir = os.path.abspath(os.path.expanduser(path))
        self._mount_path = ''
        self._mime = mimetypes.MimeTypes()

    @property
    def static_dir(self):
        return self._static_dir

    @static_dir.setter
    def static_dir(self, path):
        self._static_dir = os.path.abspath(path)

    def mount(self, path):
        self._mount_path = path

    def unmount(self):
        pass

    def match(self, request):
        path = request.path.relative

        if self._mount_path:
            path = os.path.join(self._mount_path, path.lstrip('/'))

        path = os.path.join(self.static_dir, path.lstrip('/'))

        # Requested file path might be relative (e.g., '../') and can point
        # outside of the given root path. Thus the path is explicitly converted
        # to absolute path. Absolute path must start with root path.
        path = os.path.abspath(path)
        if not path.startswith(self._static_dir):
            return None

        if os.path.isfile(path):
            fname = path
        elif os.path.isdir(path):
            if os.path.isfile(os.path.join(path, 'index.html')):
                fname = os.path.join(path, 'index.html')
            elif os.path.isfile(os.path.join(path, 'index.htm')):
                fname = os.path.join(path, 'index.htm')
            else:
                return None
        else:
            return None

        context = Context()
        context.update(self.context)
        context.put('filename', fname)

        return Resolver(self._handler, self.filters, context)

    def _handler(self, req, res, context):
        fname = context.filename

        log.debug("Serving %s", fname)

        with open(fname, 'rb') as f:
            res.content = f.read()

        mime_type = self._get_mime_type(fname)
        res.content_type = mime_type

    def _get_mime_type(self, fname):
        """ Returns mime type of file pointed by the path. """
        return self._mime.guess_type(fname)[0]


class Context:
    def __init__(self, values=None):
        self._values = {}
        self.get = self.__getattr__

        # log.debug("New context #%s created.", id(self))

        if values:
            self.update(values)

    @classmethod
    def create(cls, values={}):
        return cls(values)

    def __getattr__(self, name):
        if name in self._values:
            return self._values[name]
        return None

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, key):
        return key in self._values

    def __iter__(self):
        return iter(self._values.items())

    def put(self, name, value):
        self._values[name] = value

    def copy(self):
        return self.create(self._values)

    def update(self, other):
        if not other:
            return

        if isinstance(other, dict):
            return self.update(other.items())

        for key, value in other:
            self.put(key, value)

    # @contextmanager
    # def value(self, name):
    #     yield self.get(name)

    def __str__(self):
        s = "Context #{}\n".format(id(self))
        for k, v in self:
            s += "  {} = {}\n".format(k, v)
        s += "\n"
        return s


class Node:
    def __init__(self, name):
        self.name = name
        self.childs = dict()
        self.routes = dict()

    def __str__(self):
        return self.name

    def first_child(self):
        return list(self.childs.values())[0]

    def is_collection(self):
        if len(self.childs) == 1:
            child = self.first_child()
            return isinstance(child, Variable)
        return False

    def has_child(self, name):
        return name in self.childs

    def add_child(self, node):
        self.childs[node.name] = node

    def put_child(self, name, node):
        self.childs[name] = node

    def get_child(self, name):
        return self.childs.get(name)

    def put_route(self, method, route):
        self.routes[method] = route

    def get_route(self, method):
        return self.routes.get(method)


class Variable(Node):
    DATA_TYPES = dict(str=str, int=int, float=float)

    def __init__(self, name, type_name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.type = self.DATA_TYPES[type_name]

    def has_child(self, name):
        return self.childs


class Route:
    """ Represents a route. """

    def __init__(self, method, path, handler, context):
        """
        Args:
            method(str): HTTP method
            path(str): Resource path.
            handler(callable): Request handler
            context(object): Request context variables (dict by default)
        """
        self.method = method.upper()
        self.path = normalize_path(path)
        self._handler = handler
        self.context = context if context else Context()

    @property
    def handler(self):
        if inspect.isclass(self._handler):
            return self._handler()
        return self._handler

    def __str__(self):
        return "Route {} {}".format(self.method, self.path)


class Resolver:
    def __init__(self, handler, filters, context):
        self._context = context if context else Context()
        self._handler = handler
        self._chain = Filters(filters, handler)

    def __call__(self, req, res):
        self._chain(req, res, self._context)


def normalize_path(path):
    if not path or path == '/':
        return '/'

    elif path[0] != '/':
        path = '/' + path

    if path[-1] == '/':
        path = path[:-1]

    return path.lower()
