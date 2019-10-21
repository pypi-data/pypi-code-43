from zml.node import Model


class Operator(object):
    pass


class Processor(Operator):

    def __init__(self, render=False, lazy=False):
        self.lazy = lazy

    def subtree_handler_default(self, node):
        for child in node.children:
            child.process_subtree(self)
        return ''

    def process(self, node):
        node.process(lazy=self.lazy)
        self.subtree_handler_default(node)

    def subtree_handler_for_loop(self, node):
        # prepare
        # iterator_descriptor = node.tokens['iterator']
        variable_descriptor = node.tokens['variable']
        if not self.lazy:
            iterator = node.eval_context_item(node.tokens)
            if isinstance(iterator, Model):
                iterator = iterator.values()
            for item in iterator:
                node.set_var(variable_descriptor, item)
                # execute
                self.subtree_handler_default(node)
#        else:
#            self.subtree_handler_default(node)

    def subtree_handler_if_statement(self, node):
        # prepare
        condition = node.eval_context_item(node.tokens)
        if not self.lazy:
            if condition:
                # execute
                self.subtree_handler_default(node)
        else:
            self.subtree_handler_default(node)


class Renderer(Operator):

    def __init__(self, render=False, lazy=False, base_render_level=0):
        self.base_render_level = base_render_level
        self.lazy = lazy

    def subtree_handler_default(self, node):
        out = ''
        for child in node.children:
            # prevent rendering of ComponentNode
            # ComponentNodes will be rendered explicitly
            if not child.is_component:
                out += child.render_subtree(self)
        return out

    def render(self, node):
        node.render()
        out = ''
        out += node.leading
        out += self.subtree_handler_default(node)
        out += node.trailing
        return out

    def subtree_handler_for_loop(self, node):
        # prepare
        out = ''
        if not self.lazy:
            variable_descriptor = node.tokens['variable']
            iterator = node.eval_context_item(node.tokens)
            if isinstance(iterator, Model):
                iterator = iterator.fields.values()
            for item in iterator:
                node.set_var(variable_descriptor, item)
                # execute
                out += self.subtree_handler_default(node)
        else:
            out += self.subtree_handler_default(node)
        return out

    def subtree_handler_if_statement(self, node):
        # prepare
        out = ''
        if not self.lazy:
            condition = node.eval_context_item(node.tokens)
            if condition:
                # execute
                out += self.subtree_handler_default(node)
        else:
            out += self.subtree_handler_default(node)
        return out
