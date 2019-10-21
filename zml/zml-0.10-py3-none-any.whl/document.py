from zml.exceptions import (DocumentNotDefinedException, TranslationNotDefinedException)
from zml.context import RenderingContext
from zml.node import (Egg, EmptyNode, AssignmentNode, CodeNode, ComponentNode, ComponentCallNode,
                      DataNode, ModelNode, Node, MetaNode, ListItemNode, SlotNode, ResourceNode,
                      RouterNode, TranslationNode)
from zml.node import eval_context_item
from zml.backend import FileBackend, IpfsBackend
from zml.operator import Processor, Renderer
from zml.util import find_file_in_dirs, load_file
from zml.request import Request
from zml.resource import Resource
from zml.semantic import *
from zml.exceptions import NotFoundException


type_mapping = {
    '*': ComponentNode,
    '@': ResourceNode,
    '+': ModelNode,
    '~': RouterNode,
    '!': TranslationNode,
    '#': DataNode,
    '&': MetaNode,
    '%': CodeNode,
    '|': SlotNode,
    '-': ListItemNode
}


def render_address(address, path=None, get_params=None, post_params=None):
    backend = IpfsBackend()
    if address[0] == 'Q':
        code, mime_type = backend.load(address)
    out = render(code, path=path, get_params=get_params, post_params=post_params, cid=address)
    # out = Document(source=code, request=request).render()
    return out


def get_address(address):
    if address[0] == 'Q':
        backend = IpfsBackend()
        raw, mime_type = backend.load(address)
        if mime_type in ['image/jpeg', 'image/png', 'image/gif']:
            res = raw
        else: 
            res = import_source(raw, cid=address)
    elif address[0] == 'http://':
        backend = RestBackend()
        res, mime_type = backend.load(address)
    else:
        backend = FileBackend()
        raw, mime_type = backend.load(address)
        if mime_type in ['image/jpeg', 'image/png', 'image/gif']:
            res = raw
        else: 
            res = import_source(raw, cid=address)
    return res, mime_type


def get_path(path):
    res = FULL_PATH.parseString(path)
    if 'resource' in res:
        address = res['resource']
        backend = IpfsBackend()
        if address[0] == 'Q':
            source, mime_type = backend.load(address)
            document = import_source(source, cid=address)
            node = document.root
            if 'segments' in res:
                for segment in res['segments']:
                    node = node.eval_segment(segment)
                return node
    else:
        raise Exception("Content ID missing in path.")


def get_data_node(line, document, base_indent=0):
    res = LINE.parseString(line)
    if 'list_item_glyph' in res:
        return ListItemNode(line, document=document, global_context=document.global_context, base_indent=base_indent, renderer=Renderer())
    else:
        res = ASSIGNMENT.parseString(line)
        if 'descriptor' in res:
            return AssignmentNode(line, document=document, global_context=document.global_context,
                                  base_indent=base_indent, renderer=Renderer())


def get_document_node(line, document, base_indent=0):
    res = LINE.parseString(line)
    if 'descriptor' in res:
        if 'glyph' in res:
            glyph = res['glyph']
            if glyph in type_mapping:
                descriptor = res['descriptor']
                doc = type_mapping[glyph](line, document=document, is_ancestor=True, descriptor=descriptor,
                                          global_context=document.global_context, base_indent=base_indent,
                                          renderer=Renderer())
                return doc
        else:
            return Node(line, document=document, global_context=document.global_context, base_indent=base_indent,
                        renderer=Renderer())
    elif 'namespace_descriptor' in res:
        return ComponentCallNode(line, document=document, global_context=document.global_context,
                                 base_indent=base_indent, renderer=Renderer())
    else:
        return EmptyNode(line, document=document, global_context=document.global_context, base_indent=base_indent,
                         renderer=Renderer())


class DocumentRenderingContext(RenderingContext):

    def __init__(self, global_context={}, local_context={}, request=Request()):
        self.local_context = local_context
        self.router = dict()
        self.default_router = None
        self.request = request
        self.global_context = dict()
        self.global_context['_resources'] = dict()
        self.global_context['_translations'] = dict()
        self.global_context['_models'] = dict()
        if global_context is not None:
            self.global_context.update(global_context)
        self.namespaces = dict()
        self.namespaces['_default'] = dict()
        self.translations = dict()
        self.dispatched_views = dict()

    def get_translation(self, variable_descriptor, language=None):
        if language is None:
            try:
                language = next(iter(self.translations))
            except Exception:
                raise TranslationNotDefinedException
        if variable_descriptor in self.translations[language]:
            return self.translations[language][variable_descriptor]
        raise TranslationNotDefinedException

    def set_translation(self, language, variable_descriptor, value):
        if language not in self.translations:
            self.translations[language] = dict()
        self.translations[language][variable_descriptor] = value

    def dispatch_routes(self, path):
        res = URL_PATH.parseString(path)
        path_variables = dict()
        matched_view = None
        if not self.router:
            # no routers defined, we cannot dispatch and return without exception
            return
        for router_name in self.router:
            for view_name in self.router[router_name]:
                stop_view_check = False
                url_path_items = res['segments']
                router_path_items = self.router[router_name][view_name]
                if len(url_path_items) != len(router_path_items):
                    # path is longer than route definition, match not possible
                    stop_view_check = True
                    continue
                for i, url_path_item in enumerate(url_path_items):
                    router_path_item = router_path_items[i]
                    if router_path_item[0] == 'path_segment':
                        # segment
                        route_segment = router_path_item[1][0]
                        if route_segment != url_path_item:
                            stop_view_check = True
                            continue
                    elif router_path_item[0] == 'path_variable':
                        # variable
                        path_variables[router_path_item[1][0]] = url_path_item
                if stop_view_check:
                    continue
                # all segments matched
                matched_view = view_name
                self.dispatched_views[router_name] = matched_view
                return matched_view
        raise NotFoundException('Not found')


class Document(DocumentRenderingContext):

    def __init__(self, filename=None, source=None, lookup=None,
                 viewhelperdir=None, base_indent=0, namespaces={},
                 inherited_document=None, request=Request(), cid=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename
        self.source = source
        self.cid = cid
        self.request = request
        self.lookup = lookup
        self.base_indent = base_indent
        self.namespace = '_default'
        self.namespaces = namespaces
        self.models = dict()
        self.resources = dict()
        self.inheriting_document = None
        self.inherited_document = inherited_document
        self.viewhelperdir = viewhelperdir
        self.localpage = dict()
        self.namespacemode = False
        self.language = None
        self.raw_mode = False

    def render(self,
               filename=None, source=None,
               local_context=None, global_context=None,
               base_indent=None):
        if local_context is None:
            local_context = {}
        if base_indent is None:
            base_indent = self.base_indent
        zmlsource = None
        if filename:
            document_path = self.get_absolute_path(filename)
            zmlsource = load_file(document_path)
        elif source:
            zmlsource = source
        elif self.filename:
            document_path = self.get_absolute_path(self.filename)
            zmlsource = load_file(document_path)
        elif self.source:
            zmlsource = self.source
        if zmlsource:
            result = self.render_source(source=zmlsource, local_context=self.local_context,
                                        request=self.request, base_indent=base_indent)
            return result
        else:
            raise DocumentNotDefinedException

    def get_source_from_file(self, filename):
        zmlsource = None
        if filename:
            document_path = self.get_absolute_path(filename)
            zmlsource = load_file(document_path)
        elif self.filename:
            document_path = self.get_absolute_path(self.filename)
            zmlsource = load_file(document_path)
        return zmlsource

    # todo: eventually rename to load, design loading concept for zml
    def import_document(self,
                        filename=None, source=None,
                        request=None, base_indent=None):
        """
        Imports a document in this document.
        """
        if base_indent is None:
            base_indent = self.base_indent
        zmlsource = self.get_source_from_file(filename)
        imported_document = Document(source=zmlsource, local_context=self.local_context,
                                     global_context=self.global_context)
        # todo: decide, if we have to decouple imported document from router setup and contexts of importing document
        # imported_document.router = self.router
        # imported_document.default_router = self.default_router
        if zmlsource:
            imported_document = self
            # todo: refactor, so no namespace switch is necessary
            # save namespace of importing document
            namespace_of_importing_document = self.namespace
            imported_document.translations = self.translations
            imported_document.import_source(zmlsource, request=request, base_indent=base_indent)
            self.namespace = namespace_of_importing_document
            self.namespaces.update(imported_document.namespaces)
            self.resources.update(imported_document.resources)
            self.models.update(imported_document.models)
        else:
            raise DocumentNotDefinedException

    def get_absolute_path(self, filename):
        if filename is None:
            raise DocumentNotDefinedException
        if self.lookup is None:
            self.lookup = DocumentLookup(['.'])
        absolute_path = self.lookup.get_absolute_path(filename)
        return absolute_path

    def create_node_from_egg(self, egg, parent):
        # set parent, so is_data can check data context
        egg.parent = parent
        # check if parent forces children type, otherwise set type by parsing line
        if parent.get_children_type():
            node = parent.get_children_type()(egg.line, document=self)
        else:
            if parent.is_data() or isinstance(parent, AssignmentNode):
                node = get_data_node(egg.line, document=self)
            else:
                node = get_document_node(egg.line, document=self)
        node.children = egg.children
        node.body = egg.body
        node.link = egg.link
        return node

    def set_relations(self, node, ancestor, render_level=-1):
        node.render_level = render_level
        if not node.line.startswith('%') and not node.line.startswith('*'):
            render_level += 1
        if node.line.startswith('*'):
            node.is_ancestor = True
            node.local_context = node.local_context = node.document.local_context
            ancestor = node
        elif node.line.startswith('#'):
            node.local_context = node.ancestor.local_context
            node.value = None
            node.document.local_context[node.descriptor] = node.value
            ancestor = node.ancestor
        else:
            ancestor = node.ancestor
            node.local_context = node.ancestor.local_context
        for i, child in enumerate(node.children):
            child_node = self.create_node_from_egg(child, node)
            node.children[i] = child_node
            if isinstance(child_node, DataNode):
                node.data[child_node.descriptor] = node.children[i]
            node.children[i].parent = node
            node.children[i].ancestor = ancestor
            node.children[i].minimise = node.minimise
            self.set_relations(node.children[i], ancestor=node, render_level=render_level)

    def source_to_tree(self, source, base_indent=0):
        root = Node('root', local_context=self.local_context, is_root=True, is_ancestor=True, base_indent=base_indent, renderer=Renderer())
        root.document = self
        children = list()
        multiline = False
        for line in source.splitlines():
            try:
                BEGIN_MULTILINE.parseString(line)
                multiline = True
                multiline_code = line
            except Exception:
                if multiline:
                    multiline_code += "\n" + line
                else:
                    children.append(Egg(line, base_indent))
            try:
                END_MULTILINE.parseString(line)
                multiline = False
                children.append(Egg(multiline_code, base_indent))
            except Exception:
                pass
        root.add_children(children)
        self.set_relations(root, ancestor=root)
        return root

    def render_source(self, source=None,
                    local_context={},
                    indent_global='',
                    source_indent_level=0,
                    local_context_item='_root',
                    global_context=None,
                    request=Request(),
                    base_indent=None):
        if base_indent is None:
            base_indent = self.base_indent
        root = self.source_to_tree(source, base_indent=base_indent)
        if self.request.path:
            self.dispatch_routes(self.request.path)
        out = root.render_subtree(Renderer())
        return out

    def import_source(self, source=None,
                    indent_global='',
                    source_indent_level=0,
                    local_context_item='_root',
                    request=Request(),
                    base_indent=None):
        """
        Imports source into document.
        """
        # if no source is given the templates source is used as fallback
        if source is None:
            source = self.source

        namespace_of_importing_document = self.namespace
        if base_indent is None:
            base_indent = self.base_indent
        root = self.source_to_tree(source, base_indent=base_indent)
        if self.request and self.request.path:
            self.dispatch_routes(self.request.path)
        root.process_subtree(Processor(lazy=True))
        self.namespace = namespace_of_importing_document
        return root

    def get_language(self, language):
        return self.language

    def set_language(self, language):
        self.language = language

    def get(self, path):
        res = COMBINED_ACCESSOR.parseString(path)
        value = eval_context_item(res, self)
        return value


class DocumentLookup(object):

    def __init__(self, directories=None,
                 module_directory=None, input_encoding=None):
        self.directories = directories

    def get_document(self, filename, local_context=None, global_context=None, request=Request()):
        if local_context is None:
            local_context = {}
        if global_context is None:
            global_context = {}
        find_file_in_dirs(filename, self.directories)
        return Document(filename=filename, lookup=self,
                        local_context=local_context, global_context=global_context, request=request)

    def get_absolute_path(self, filename):
        find_file_in_dirs(filename, self.directories)
        return filename


def render(tempsource, local_context=None, global_context=None,
           path=None, get_params={}, post_params={}, base_indent=0, cid=None):
    if local_context is None:
        local_context = {}
    if tempsource.endswith('.zml'):
        return render_document(tempsource, local_context=local_context, global_context=global_context, path=path, cid=cid)
    else:
        return render_source(tempsource, local_context, global_context=global_context, base_indent=base_indent,
                             path=path, cid=cid)


def render_document(documentfile, local_context=None, global_context=None,
                    path=None, get_params={}, post_params={}, base_indent=0, cid=None):
    if local_context is None:
        local_context = {}
    lookup = DocumentLookup(['.'])
    request = Request(path=path)
    document = lookup.get_document(documentfile, local_context=local_context, global_context=global_context,
                                   request=request, cid=cid)
    out = document.render(get_params=get_params, post_params=post_params, base_indent=base_indent)
    return out


def render_source(source,
                local_context=None,
                global_context=None,
                indent_global='',
                source_indent_level=0,
                local_context_item='_root',
                path=None,
                get_params={},
                post_params={},
                base_indent=0, cid=None):
    if local_context is None:
        local_context = {}
    request = Request(path=path, get_params=get_params, post_params=post_params)
    document = Document(source=source, local_context=local_context, global_context=global_context, request=request,
                        cid=cid)
    root = document.source_to_tree(source)
    # we have to process the subtree to retrieve the routes
    # which are required by the components using the dispatcher
    root.process_subtree(Processor(lazy=True))
    out = root.render_subtree(Renderer())
    if document.inheriting_document:
        # here we set local_context of inheriting document to local_context of inherited document
        # todo: decide how we design the scopes of contexts
        if isinstance(document.inheriting_document, Resource):
            document.inheriting_document.load()
            inheriting_document = Document(source=document.inheriting_document.code, inherited_document=document,
                                           request=request)
            inheriting_document.dispatched_views = document.dispatched_views
            out = inheriting_document.render(local_context=document.local_context,
                                             base_indent=base_indent)
        else:
            inheriting_document = Document(document.inheriting_document, inherited_document=document, request=request)
            inheriting_document.dispatched_views = document.dispatched_views
            out = inheriting_document.render(local_context=document.local_context,
                                             base_indent=base_indent)
    return out


def load(tempsource, local_context=None, path=None,
         global_context=None, get_params={}, post_params={}, base_indent=0):
    if local_context is None:
        local_context = {}
    if tempsource.endswith('.zml'):
        return import_document(tempsource, local_context=local_context, global_context=global_context, path=path)
    else:
        return import_source(tempsource, local_context, global_context=global_context, base_indent=base_indent, path=path, get_params=get_params, post_params=post_params)


def import_document(documentfile, local_context=None, path=None,
           global_context=None, get_params={}, post_params={}, base_indent=0):
    if local_context is None:
        local_context = {}
    request = Request(path=path, get_params=get_params, post_params=post_params)
    lookup = DocumentLookup(['.'])
    document = lookup.get_document(documentfile, local_context=local_context, global_context=global_context, request=request)
    document.import_document(request=request, base_indent=base_indent)
    return document


def import_file(documentfile, local_context=None, path=None,
           global_context=None, get_params={}, post_params={}, base_indent=0):
    if local_context is None:
        local_context = {}
    request = Request(path=path, get_params=get_params, post_params=post_params)
    lookup = DocumentLookup(['.'])
    document = lookup.get_document(documentfile, local_context=local_context, global_context=global_context, request=request)
    zmlsource = get_source_from_file(document.filename)
    return import_source(zmlsource)


def import_source(source,
                  local_context=None, global_context=None,
                  path=None, get_params={}, post_params={},
                  indent_global='', source_indent_level=0, local_context_item='_root',
                  base_indent=0, cid=None):
    # remoce leading and trailing whitespace, which is not syntax relevant
    source = source.strip()
    if local_context is None:
        local_context = {}
    request = Request(path=path, get_params=get_params, post_params=post_params)
    document = Document(source=source, local_context=local_context, global_context=global_context, request=request,
                        cid=cid)
    root = document.source_to_tree(source)
    root.process_subtree(Processor(lazy=True))
    if document.inheriting_document:
        # here we set local_context of inheriting document to local_context of inherited document
        # todo: decide how we design the scopes of contexts
        if isinstance(document.inheriting_document, Resource):
            document.inheriting_document.load()
            inheriting_document = Document(source=document.inheriting_document.code, inherited_document=document)
            inheriting_document.import_source()
        else:
            inheriting_document = Document(source=document.inheriting_document, inherited_document=document)
            inheriting_document.import_document()
    document.root = root
    return document


def get_source_from_file(filename):
    lookup = DocumentLookup(['.'])
    document_path = lookup.get_absolute_path(filename)
    zmlsource = load_file(document_path)
    return zmlsource
