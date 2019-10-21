from copy import deepcopy
from zml.semantic import *
from zml.context import RenderingContext
from zml.exceptions import IndentationException
from zml.model import Model
from zml.resource import Resource
import zml


num_spaces_per_indent = 2


def eval_context_item(res, node):
    if 'resource' in res:
        document = zml.document.Document()
        resource = node.document.resources[res['resource']]
        resource.import_resource(document)
        value = document
        if 'data_node_descriptor' in res:
            value = value.get_var(res['data_node_descriptor'])
            if isinstance(value, Model):
                value = value
        elif 'model_descriptor' in res:
            value = value.models[res['model_descriptor']].fields
    elif 'context_item' in res and 'properties' not in res:
        value = node.get_var(res['context_item'])
        if isinstance(value, Model):
            value = value
    elif 'data_node_descriptor' in res:
        value = node.get_var(res['data_node_descriptor'])
        if isinstance(value, Model):
            value = value
        if isinstance(value, Field):
            value = value
    elif 'model_descriptor' in res:
        value = node.document.models[res['model_descriptor']].fields
    if 'properties' in res:
        if not isinstance(value, dict) and not isinstance(value, Field) and not isinstance(value, Model):
            value = value.local_context
        properties = res['properties']
        value = get_combined_properties(value, properties)
    return value


def get_property(obj, property_descriptor):
    value = obj[property_descriptor]
    return value


def get_meta_data(obj, property_descriptor):
    if property_descriptor == 'descriptor':
        value = obj.descriptor
    elif property_descriptor == 'label':
        value = obj.label
    elif property_descriptor == 'type':
        value = obj.type
    return value


def get_combined_properties(value, properties):
    for property_item in properties:
        # currently we only handle dict properties. future implementations will handle
        # list item accessors with dot-number syntax (.0 for first element, .1 for second etc.)
        property_descriptor = property_item[1][0]
        if property_item[0] == 'property':
            value = get_property(value, property_descriptor)
        elif property_item[0] == 'meta_data':
            value = get_meta_data(value, property_descriptor)
    return value


def eval_model(res, node):
    if 'model_descriptor' in res:
        return node.document.models[res['model_descriptor']]


def eval_translation(res, node):
    translation_descriptor = res['translation_descriptor']
    if 'properties' in res:
        value = node.document.get_translation(translation_descriptor, node.document.language)
        for property_item in res['properties']:
            property_descriptor = property_item[1][0]
            value = value[property_descriptor]
    else:
        value = node.document.get_translation(translation_descriptor, node.document.language)
    return value


def render_translation(res, node):
    return str(eval_translation(res, node))


class NodeRenderingContext(RenderingContext):
    pass


class Path(object):

    def __init__(self, document):
        self.document = document

    def execute(self, context, *args, **kwargs):
        if 'action' in context['context']:
            action = context['context']['action']
        else:
            return ''
        if 'router' in context['context']:
            router = self.document.router[context['context']['router']]
        else:
            router = self.document.default_router
        if action in router:
            route = router[action]
            url = ''
            for item in route:
                if 'path_segment' in item:
                    url += '/' + item[1][0]

                elif 'path_variable' in item:
                    path_variable = item[1][0]
                    if path_variable in context['context']:
                        url += '/' + context['context'][path_variable]
            return url


framework_components = {
    'path': Path,
    'sin': math.sin,
    'pi': math.pi
}


class TreeNode:

    def __init__(self, line='', is_root=False, is_ancestor=False, ancestor=None, base_indent=0):
        self.line = line
        self.base_indent = base_indent
        self.children = []
        self.body = None
        self.value = None
        self.link = None
        self.is_root = is_root
        self.is_ancestor = is_ancestor
        if ancestor is None:
            # explicitly state logic here to be clear that in both cases ancestor is set to self
            if self.is_ancestor:
                self.ancestor = self
            else:
                self.ancestor = self
        else:
            self.ancestor = ancestor
        indentation = len(line) - len(line.lstrip())
        if indentation % num_spaces_per_indent != 0:
            raise IndentationException
        self.level = int(indentation / num_spaces_per_indent)
        self.render_level = 0
        self.base_render_level = 0

    def __repr__(self):
        # return '{}\n{}'.format(self.line, json.dumps(self.local_context, indent=2))
        return "{}({})\n".format(self.__class__.__name__, self.line)

    def add_children(self, nodes):
        if nodes:
            childlevel = nodes[0].level
            while nodes:
                node = nodes.pop(0)
                node.ancestor = self
                if node.level == childlevel:
                    if self.is_ancestor:
                        node.ancestor = self
                        node.local_context = {}
                    # add node as a child
                    self.children.append(node)
                elif node.level > childlevel:
                    # add nodes as grandchildren of the last child
                    # if self.children[-1].is_ancestor:
                    #     node.ancestor = self.children[-1]
                    #     node.local_context = self.children[-1].local_context
                    nodes.insert(0, node)
                    self.children[-1].add_children(nodes)
                elif node.level <= self.level:
                    # this node is a sibling, no more children
                    nodes.insert(0, node)
                    return

    def is_data(self):
        if self.is_root:
            return False
        else:
            return self.parent.is_data()


class Egg(TreeNode):

    expression = EGG

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        res = self.expression.parseString(self.line)
        if 'key' in res:
            self.body = res['key']
        if 'value' in res:
            self.link = res['value']
        # print('***')
        # print(self.line)
        # print(self.value)


class Node(TreeNode, NodeRenderingContext):

    expression = ELEMENT

    def __init__(self, line, document=None, expression=None, global_context=None, local_context=None,
                 meta_data={}, descriptor=None, base_indent=0, renderer=None, *args, **kwargs):
        super().__init__(line, *args, **kwargs)
        if local_context is None:
            local_context = {}
        if global_context is None:
            global_context = {}
        self.line = line
        self.data = dict()
        self.descriptor = descriptor
        self.local_context = local_context
        self.meta_data = meta_data
        self.global_context = global_context
        self.renderer = renderer
        self.minimise = False
        self.leading = ''
        self.trailing = ''
        self.is_component = False
        self.is_code = False
        self.has_list_items = False
        self.line = line.strip()
        self.document = document
        self.out = ()
        if self.is_root:
            self.level = -1

    def get_path(self):
        node = self
        path = ''
        while node != self.document.root:
            segment = ''
            if node.glyph:
                segment += node.glyph
            segment += node.descriptor
            path = segment + path
            if node.parent:
                node = node.parent
            else:
                return path
        return path

    def eval_segment(self, segment):
        if 'data_node_descriptor' in segment[1]:
            return self.data[segment[1]['data_node_descriptor']]

    def get_address(self):
        if self.document.cid:
            return self.document.cid + self.get_path()
        else:
            return self.get_path()

    def process(self, lazy=False):
        if not lazy and self.is_root is False:
            self.expression.setParseAction(self.parse)
            res = self.expression.parseString(self.line)
            self.tokens = self.expression.parseString(self.line)
            self.render_parts(res)

    def render(self):
        self.tokens = self.expression.parseString(self.line)
        if 'inline_content' in self.tokens:
            value = self.render_inline_content(self.tokens)
            self.set_var('_value', value)
        if self.is_root is False:
            self.expression.setParseAction(self.parse)
            res = self.expression.parseString(self.line)
            self.render_parts(res)
        else:
            return ''

    def get_combined_properties(self, properties):
        return get_combined_properties(self, properties)

    def get_meta_data(self, property_descriptor):
        return get_meta_data(self, property_descriptor)

    def eval_context_item(self, res):
        return eval_context_item(res, self)

    def is_list(self):
        return self.has_list_items

    def parse(self, s, l, t):
        return t

    def render_parts(self, res):
        self.leading = self.render_leading(res)
        self.trailing = self.render_trailing(res)

    def render_indent(self):
        render_level = (self.ancestor.base_render_level + self.render_level)
        indent = ' ' * self.base_indent + ' ' * render_level * 2
        return indent

    def render_start_tag(self, res):
        descriptor = self.render_descriptor(res)
        attributes = self.render_attributes(res)
        id_classes = self.render_id_classes(res)
        out = '<{}{}{}>'.format(descriptor, id_classes, attributes)
        return out

    def render_inline_start_tag(self, res):
        descriptor = self.render_descriptor(res)
        attributes = self.render_attributes(res)
        id_classes = self.render_id_classes(res)
        value = ''
        if 'inline_content' in res:
            value = self.render_inline_content(res)
        elif 'expression' in res:
            value = self.eval_expression(res)
        out = '<{}{}{}>{}'.format(descriptor, id_classes, attributes, value)
        return out

    def render_end_tag(self, res):
        descriptor = self.render_descriptor(res)
        out = ''
        if descriptor in void_elements:
            out += ''
        else:
            if not self.minimise and descriptor not in inline_elements:
                render_level = (self.ancestor.base_render_level + self.render_level)
                out += ' ' * self.base_indent + ' ' * render_level * 2
            out += '</{}>'.format(descriptor)
            if not self.minimise:
                out += '\n'
        return out

    def render_inline_end_tag(self, res):
        descriptor = self.render_descriptor(res)
        out = '</{}>'.format(descriptor)
        return out

    def render_inline_semantics(self, res):
        out = ''
        out += self.render_inline_start_tag(res)
        out += res['inline_semantic_content_words']
        out += self.render_inline_end_tag(res)
        if 'trailing_space' in res:
            out += ' '
        return out

    def render_leading(self, res):
        descriptor = self.render_descriptor(res)
        start_tag = self.render_start_tag(res)
        value = ''
        if 'inline_content' in res:
            value = self.render_inline_content(res)
        elif 'expression' in res:
            value = self.eval_expression(res)
        leading = ''
        if not self.minimise:
            leading += self.render_indent()
        leading += start_tag + value
        if not self.minimise and descriptor not in inline_elements:
            leading += '\n'
        return leading

    def render_trailing(self, res):
        return self.render_end_tag(res)

    def render_descriptor(self, res):
        if 'descriptor' in res:
            return res['descriptor']
        else:
            return ''

    def eval_arith_expression(self, res):
        expr = ''.join(res['arith_expression'])
        del exprStack[:]
        ARITH_EXPRESSION.parseString(expr, parseAll=True)
        return evaluateStack(exprStack)

    def eval_boolean(self, res):
        if res['boolean'] == 'True':
            return True
        elif res['boolean'] == 'False':
            return False

    def render_boolean(self, res):
        return str(self.eval_boolean(res))

    def eval_literal(self, res):
        # note that this works by using addParseAction(removeQuotes) in LITERAL
        value = res['literal']
        return value

    def render_literal(self, res):
        return str(self.eval_literal(res))

    def eval_expression(self, res):
        if 'arith_expression' in res:
            return self.eval_arith_expression(res)
        elif 'boolean' in res:
            return self.eval_boolean(res)
        elif 'literal' in res:
            return self.eval_literal(res)
        elif 'framework_component' in res:
            return self.eval_framework_component(res)
        elif 'component_descriptor' in res:
            return self.eval_component(res)
        elif 'value_accessor' in res:
            # might lead to endless loop ?
            return self.eval_value_accessor(res)
        elif 'meta_data' in res or 'resource' in res or 'context_item' in res or 'context_item_with_property' in res:
            return self.eval_context_item(res)
        elif 'translation_accessor' in res:
            return eval_translation(res, self)

    def eval_attribute_value(self, attribute):
        if 'moustache' in attribute:
            attribute_value = self.render_moustache(attribute)
        elif 'quoted_string' in attribute:
            attribute_value = attribute['quoted_string']
        elif 'number' in attribute:
            attribute_value = attribute['number']
        elif 'literal' in attribute:
            attribute_value = attribute['literal']
        elif 'context_item' in attribute:
            return self.eval_context_item(attribute)
        elif 'model_descriptor' in attribute:
            return eval_model(attribute, self)
        return attribute_value

    def render_attribute(self, attribute):
        out = ' '
        out += attribute['attribute_key']
        if 'attribute_value' in attribute:
            out += '="{}"'.format(self.eval_attribute_value(attribute))
        return out

    def render_attributes(self, res):
        if 'attributes' in res:
            return ' '.join(
                [''.join(
                    [self.render_attribute(attribute) for attribute in res['attributes']]
                )]
            )
        else:
            return ''

    def render_id_classes(self, res):
        out = ''
        if 'id_classes' in res:
            if 'uid' in res:
                out += ' id="{}"'.format(res['uid'][0])
            if 'classes' in res:
                out += ' class="{}"'.format(' '.join(res['classes']))
        return out

    def render_inline_content(self, res):
        out = ''
        if 'inline_content' in res:
            inline_content_items = res['inline_content']
            for item in inline_content_items:
                itemtype = item[0]
                if itemtype == 'inline_content_words':
                    out += self.render_words(item[1][0])
                elif itemtype == 'inline_content_newlines':
                    out += ''.join(item[1])
                if itemtype == 'inline_semantics':
                    out += self.render_inline_semantics(item[1])
                if itemtype == 'moustache':
                    out += self.render_moustache(item[1])
#                if itemtype == 'translation_accessor':
#                    out += render_translation(item[1], self)
        return out

    def render_words(self, res):
        out = res
        return out

    def eval_value_accessor(self, res):
        return self.get_var('_value')

    def render_value_accessor(self, res):
        return self.eval_value_accessor(res)

    def _render_component(self, component_descriptor):
        namespace = self.document.namespace
        component = None
        # rendered_view_source = local_indent
        rendered_view_source = ''
        if component_descriptor in self.document.namespaces[namespace]:
            component = self.document.namespaces[namespace][component_descriptor]
        elif component_descriptor in self.inherited_document.namespaces[namespace]:
            component = self.inherited_document.namespaces[namespace][component_descriptor]
        if component:
            component_node = deepcopy(component)
            component_node.parent = self
            # component_node.ancestor = self.ancestor
            component_node.base_render_level = self.render_level
            if not self.parent.is_component and not self.parent.is_code:
                component_node.base_render_level += 1

            component_node.render_level = component_node.base_render_level
            # local_indent = ' ' * self.render_level * 2
            self.renderer.base_render_level = self.render_level
            rendered_component = component_node.render_subtree(self.renderer)
            rendered_view_source += rendered_component
        # strip last newline, as it would double with the inline content's trailing newline
        rendered_view_source = rendered_view_source.rstrip()
        return rendered_view_source

    def render_component(self, res):
        # prepend local indent on each line
        component_descriptor = res['component_descriptor']
        # prepend newline, because view will be included in inline content,
        # which is missing a leading newline
        return '\n' + self._render_component(component_descriptor)

    def eval_framework_component(self, res):
        framework_component = res['framework_component']
        if 'moustache_attributes' in res:
            params = dict()
            for attribute in res['moustache_attributes']:
                key = attribute['moustache_attribute_key']
                value = attribute['moustache_attribute_value']
                if value == '_context':
                    value = self.local_context
                params[key] = value
            return framework_components[framework_component](self.document).execute(params)

    def render_framework_component(self, res):
        return self.eval_framework_component(res)

    def render_context_item(self, res):
        return str(self.eval_context_item(res))

    def render_moustache(self, res):
        out = ''
        if 'framework_component' in res:
            out += self.render_framework_component(res)
        elif 'component_descriptor' in res:
            out += self.render_component(res)
        elif 'value_accessor' in res:
            out += self.render_value_accessor(res)
        elif 'context_item' in res:
            out += self.render_context_item(res)
        elif 'context_item_with_property' in res:
            out = self.render_context_item(res)
        elif 'translation_accessor' in res:
            out += render_translation(res, self)
        return out

    def process_subtree(self, processor=None):
        processor.process(self)

    def render_subtree(self, renderer=None):
        out = renderer.render(self)
        return out

    def get_children_type(self):
        return None


class EmptyNode(Node):

    def render_leading(self, res):
        descriptor = self.render_descriptor(res)
        start_tag = ''
        inline_content = self.render_inline_content(res)
        leading = ''
        if not self.minimise:
            leading += self.render_indent()
        leading += start_tag + inline_content
        if not self.minimise and descriptor not in inline_elements:
            leading += '\n'
        return leading


class ComponentNode(Node):

    expression = LINE
    glyph = '*'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_component = True
        self.caller_inline_content = None
        self.caller_children = None

    def process(self, lazy=False):
        self.expression.setParseAction(self.parse)
        self.tokens = self.expression.parseString(self.line)
        descriptor = self.tokens['descriptor']
        # self.local_context[descriptor] = self.childsource
        if self.document.namespace not in self.document.namespaces:
            self.document.namespaces[self.document.namespace] = dict()
        self.document.namespaces[self.document.namespace][descriptor] = self

    def render(self):
        pass


class ComponentCallNode(Node):

    expression = COMPONENT_CALL
    glyph = '*'

    def process(self, lazy=False):
        if not lazy:
            self.expression.setParseAction(self.parse)
            self.tokens = self.expression.parseString(self.line)

    def render(self):
        self.process()
        namespace = self.tokens['namespace']
        descriptor = self.tokens['component_descriptor']
        component_node = deepcopy(self.document.namespaces[namespace][descriptor])
        component_node.parent = self.parent
        component_node.ancestor = self.ancestor
        # the component call inherits the total render_level of parent and the parent's ancestor to the component
        component_node.base_render_level = self.parent.render_level + self.parent.ancestor.base_render_level
        if 'inline_content' in self.tokens:
            component_node.caller_inline_content = self.tokens['inline_content']
        component_node.caller_children = self.children
        self.renderer.base_render_level = self.render_level
        if not self.parent.is_component and not self.parent.is_code:
            component_node.base_render_level += 1
        if 'attributes' in self.tokens:
            for attribute in self.tokens['attributes']:
                attribute_key = attribute['attribute_key']
                attribute_value = self.eval_attribute_value(attribute)
                component_node.set_var(attribute_key, attribute_value)
        if 'inline_content' in self.tokens:
            value = self.render_inline_content(self.tokens)
            component_node.set_var('_value', value)
        children = []
        for child in self.children:
            children.append(child.render_subtree(self.renderer))
        component_node.set_var('_children', children)
        out = ''
        out += component_node.render_subtree(self.renderer)
        self.leading = out
        return out


class ListItemNode(Node):

    expression = LIST_ITEM

    def process(self, lazy=False):
        if not lazy:
            self.expression.setParseAction(self.parse)
            self.tokens = self.expression.parseString(self.line)
            self.parent.has_list_items = True
            # if self.parent.descriptor not in self.local_context:
            #    self.set_var(self.parent.descriptor, list())
            if not isinstance(self.parent.value, list):
                self.parent.value = list()
            if isinstance(self.parent, DataNode):
                # self.document.local_context[self.parent.descriptor] = self.parent.value
                self.local_context[self.parent.descriptor] = self.parent.value
            self.value = dict()
            self.parent.value.append(self.value)

    def render(self):
        self.process()


class TranslationNode(Node):

    expression = TRANSLATION
    glyph = '!'

    def process(self, lazy=False):
        self.value = dict()
        self.document.translations[self.descriptor] = self.value

    def render(self):
        self.process()

    def get_children_type(self):
        return AssignmentNode


class AssignmentNode(Node):

    expression = ASSIGNMENT

    def process(self, lazy=False):
        res = self.expression.parseString(self.line)
        descriptor = res['descriptor']
        value = ''
        if 'inline_content' in res:
            value = self.render_inline_content(res)
        elif 'expression' in res:
            value = self.eval_expression(res)
        # self.parent.set_var(descriptor, value)
        if isinstance(self.parent, AssignmentNode) or isinstance(self.parent, ListItemNode) or isinstance(self.parent,
                                                                                                          TranslationNode):
            if self.parent.value is None:
                self.parent.value = dict()
            if value:
                self.parent.value[descriptor] = value
            else:
                self.value = dict()
                self.parent.value[descriptor] = self.value
        elif isinstance(self.parent, DataNode):
            if self.local_context[self.parent.descriptor] in [None, '']:
                self.local_context[self.parent.descriptor] = dict()
            if value:
                self.local_context[self.parent.descriptor][descriptor] = value
            else:
                self.value = dict()
                self.local_context[self.parent.descriptor][descriptor] = self.value

    def render(self):
        self.process()


class FieldPropertyNode(Node):

    expression = ASSIGNMENT

    def process(self, lazy=True):
        res = self.expression.parseString(self.line)
        descriptor = res['descriptor']
        glyph = res['glyph']
        if 'inline_content' in res:
            value = self.render_inline_content(res)
        elif 'expression' in res:
            value = self.eval_expression(res)
        if glyph == '&':
            # define meta data
            if descriptor == 'type':
                self.parent.value.type = value
            if descriptor == 'label':
                self.parent.value.label = value

    def render(self):
        self.process()


class Field:

    def __init__(self, descriptor):
        self.descriptor = descriptor
        self.type = None
        self.label = ''


class FieldNode(Node):

    expression = FIELD

    def process(self, lazy=False):
        res = self.expression.parseString(self.line)
        descriptor = res['field_descriptor']
        self.value = Field(descriptor)
        self.parent.value.fields[descriptor] = self.value

    def render(self):
        self.process()

    def get_children_type(self):
        return FieldPropertyNode


class ModelNode(Node):

    expression = MODEL
    glyph = '+'

    def process(self, lazy=False):
        res = self.expression.parseString(self.line)
        descriptor = res['model_descriptor']
        self.value = Model(descriptor)
        self.document.models[self.descriptor] = self.value

    def render(self):
        self.process()

    def get_children_type(self):
        return FieldNode


class ResourceNode(Node):

    expression = RESOURCE
    glyph = '@'

#    def __init__(self):
#        super(ResourceNode, self).__init__()
#        if self.line:
#            res = self.expression.parseString(self.line)
#            self.address = res['source']
#            self.resource = Resource(address, lazy=True)

    def process(self, lazy=False):
        res = self.expression.parseString(self.line)
        address = res['source']
        self.resource = Resource(address)
        self.document.resources[self.descriptor] = self.resource

    def render(self):
        self.process()


class RouteNode(Node):

    expression = ROUTE

    def process(self, lazy=False):
        self.expression.setParseAction(self.parse)
        res = self.expression.parseString(self.line)
        router_descriptor = self.parent.descriptor
        route_descriptor = res['descriptor']
        # currently also nodes have a global_context and a local_context
        # todo design decision for rendering contexts (see module's render_source function)
        router = self.document.router
        if router_descriptor not in router:
            router[router_descriptor] = dict()
            router[router_descriptor][route_descriptor] = res['path_items']
            self.document.default_router = router[router_descriptor]
        else:
            router[router_descriptor][route_descriptor] = res['path_items']

    def render(self):
        self.process()


class RouterNode(Node):

    expression = LINE
    glyph = '~'

    def process(self, lazy=False):
        pass

    def get_children_type(self):
        return RouteNode

    def render(self):
        self.process()
        # we have to overwrite render to prevent rendering as Node
        pass


class DataNode(Node):

    expression = DATA_NODE
    glyph = '#'

    def is_data(self):
        return True

    def process(self, lazy=False):
        res = self.expression.parseString(self.line)
        descriptor = res['data_descriptor']
        value = ''
        if 'inline_content' in res:
            value = self.render_inline_content(res)
        elif 'expression' in res:
            value = self.eval_expression(res)
        descriptor = res['data_descriptor']
        self.local_context[descriptor] = value

    def render(self):
        self.process()

    # def get(self, path):
    #    res = COMBINED_ACCESSOR.parseString(path)
    #    return res


class MetaNode(Node):

    expression = LINE
    glyph = '&'

    def is_meta(self):
        return True

    def process(self, lazy=False):
        res = self.expression.parseString(self.line)
        descriptor = res['descriptor']
        self.meta_data[descriptor] = self.value

    def render(self):
        self.process()


class SlotNode(Node):

    expression = SLOT_NODE
    glyph = '|'

    def __init__(self, *args, **kwargs):
        self.descriptor = kwargs['descriptor']
        super().__init__(*args, **kwargs)

    def render(self):
        if self.descriptor in self.document.dispatched_views:
            view_name = self.document.dispatched_views[self.descriptor]
            namespace = self.document.namespaces[self.document.namespace]
            if view_name in namespace:
                rendered_component = self._render_component(view_name)
                self.leading = rendered_component + '\n'
                return ''  # rendered_component
        else:
            return ''


class CodeNode(Node):

    expression = CODE
    glyph = '%'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_code = True

    def is_instruction(self):
        if self.descriptor in ['inherit', 'import', 'include', 'namespace']:
            return True
        else:
            return False

    def process_subtree(self, processor):
        self.expression.setParseAction(self.parse)
        self.tokens = self.expression.parseString(self.line)
        if 'for_loop' in self.tokens:
            processor.subtree_handler_for_loop(self)
        elif 'if_statement' in self.tokens:
            processor.subtree_handler_if_statement(self)
        if self.is_instruction():
            processor.process(self)

    def render_subtree(self, renderer):
        self.expression.setParseAction(self.parse)
        self.tokens = self.expression.parseString(self.line)
        out = ''
        if 'for_loop' in self.tokens:
            out += renderer.subtree_handler_for_loop(self)
        elif 'if_statement' in self.tokens:
            out += renderer.subtree_handler_if_statement(self)
        if self.is_instruction():
            out += renderer.render(self)
        return out

    def process_inherit(self, res):
        if 'documentfile' in res:
            documentfile = res['documentfile']
            if not documentfile.endswith('.zml'):
                documentfile += '.zml'
            self.document.inheriting_document = documentfile
        elif 'resource' in res:
            resource_name = res['resource']
            if resource_name in self.document.resources:
                self.document.inheriting_document = self.document.resources[resource_name]

    def process_import(self, res):
        if 'documentfile' in res:
            documentfile = res['documentfile']
            if not documentfile.endswith('.zml'):
                documentfile += '.zml'
            self.document.import_document(documentfile)
        elif 'resource' in res:
            resource_descriptor = res['resource']
            self.document.resources[resource_descriptor].import_resource(self.document)
        # return root

    def process_include(self, res):
        out = render(filename,
                     local_context=self.document.local_context,
                     base_indent=base_indent)
        return out

    def process_namespace(self, res):
        namespace = res['namespace']
        self.document.namespace = namespace

    def process(self, lazy=False):
        self.expression.setParseAction(self.parse)
        res = self.expression.parseString(self.line)
        if 'instruction' in res:
            instruction = res['instruction']
            if instruction == 'inherit':
                self.process_inherit(res)
            elif instruction == 'import':
                self.process_import(res)
            elif instruction == 'include':
                self.process_include(res)
            elif instruction == 'namespace':
                self.process_namespace(res)

    def render(self, lazy=False):
        self.process(lazy)
        return ''
