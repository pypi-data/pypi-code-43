import functools
from functools import wraps
import inspect
import os
import sys

import boto3
import yaml


_GENERATE = False
_GENERATOR = None


class InternalNode(object):
    def __init__(self):
        self.node = {}
        self.buckets = []

    def _set_unset_keys(self):
        pass

    def dump_yaml(self):
        self._set_unset_keys()
        return yaml.safe_dump(self.__dict__)


class MissingMainBody(Exception):
    pass


class MissingBaseDefinitionError(Exception):
    pass


class BaseDefinitionOrderError(Exception):
    pass


class FabNodeGenerator(object):
    def __init__(self):
        global _GENERATE
        _GENERATE = True
        self.nodes = {}
        self.outputs = {}
        self.reverse = os.environ.get('REVERSE', 'False') == 'True'

    def append_to_output(self, output_stage, out):
        if output_stage not in self.outputs:
            self.outputs[output_stage] = []
        self.outputs[output_stage].append(out)

    def _prepare_ordered_output_for_node(self, node):
        if '_pre' in node:
            self.append_to_output('_pre', node['_pre'].dump_yaml())

        if '_main' not in node:
            raise MissingMainBody('Missing main body for %s' % node)
        self.append_to_output('_main', node['_main'].dump_yaml())

    def output(self):
        out = []
        steps = ['_pre', '_main']
        if self.reverse:
            steps.reverse()
        for fx_name, sub in self.nodes.items():
            for s in steps:
                if s in sub:
                    out.append(sub[s].__dict__)
        out = {'nodes': out}
        return yaml.safe_dump(out)

    def get_instance(self, fx_name, sub_node='_main'):
        if fx_name not in self.nodes:
            self.nodes[fx_name] = {}
        if sub_node not in self.nodes[fx_name]:
            self.nodes[fx_name][sub_node] = InternalNode()
        return self.nodes[fx_name][sub_node]

    def generate_function(self, name, fx):
        fx()
        node = self.nodes[name]
        if '_pre' in node:
            pass

        if '_main' not in node:
            raise MissingMainBody('Missing main body for %s' % name)

    def generate_all(self, module):
        cm = sys.modules[module]
        fns = {
            name: obj for name, obj in inspect.getmembers(cm)
            if inspect.isfunction(obj) and hasattr(obj, 'wrapper')
        }
        for name, f in fns.items():
            self.generate_function(name, f)
        for name, n in self.nodes.items():
            self._prepare_ordered_output_for_node(n)
        return self.output()


def generator():
    global _GENERATOR
    if not _GENERATOR:
        _GENERATOR = FabNodeGenerator()
    return _GENERATOR


def g(fx_name, subnode='_main'):
    return generator().get_instance(fx_name, subnode)


class FabNodeDecoratorBase(object):
    def __init__(self):
        self.all = os.environ.get('ALL', 'False') == 'True'

    def function_is_fabnode_decorator(self, fn):
        return hasattr(fn, 'wrapper')

    def assert_fabnode_made(self, fn):
        if self.function_is_fabnode_decorator(fn) and (
                not hasattr(fn, 'initialized')):
            raise MissingBaseDefinitionError(
                'Missing base definition. Decorators out of order?')

    def should_call_function(self, fn):
        global _GENERATE
        return self.function_is_fabnode_decorator(fn) or (
            not self.function_is_fabnode_decorator(fn) and not _GENERATE)


class BasicNode(FabNodeDecoratorBase):
    def __init__(self, function_name, name, description):
        super(BasicNode, self).__init__()
        self.name = name
        self.description = description
        self.function_name = function_name

    def __call__(self, fn, *args, **kwargs):
        if self.function_is_fabnode_decorator(fn):
            raise BaseDefinitionOrderError(
                'Decorating a fabnode decorator. Base Nodes should decorate '
                'non-fabnode functions')

        @wraps(fn)
        def _fx(*args, **kwargs):
            filename = os.path.splitext(inspect.getsourcefile(fn))[0]
            self.filename = filename
            self.fn_name = fn.__name__
            g(self.fn_name)
            g(self.fn_name).script = inspect.getsourcefile(fn)
            g(self.fn_name).stack_name = self.name
            g(self.fn_name).description = self.description
            g(self.fn_name).node.update({
                'fxname': self.function_name,
                'handler': '%s.%s' % (self.filename, self.fn_name),
                'archive': '%s.zip' % filename,
                'role_import': 'iamFilterRoleId',
            })

            if self.should_call_function(fn):
                return fn(*args, **kwargs)
        _fx.wrapper = self
        _fx.initialized = True
        return _fx


def compose2(f, g):
    return lambda *a, **kw: f(g(*a, **kw))


def compose(*fs):
    return functools.reduce(compose2, fs)


class ConfigurationNode(BasicNode):
    def __init__(self, file_or_str):
        self.filename = file_or_str if os.path.isfile(file_or_str) else None
        self.yamlstr = None if self.filename is not None else file_or_str
        if self.filename:
            with open(self.filename, 'r') as f:
                self.conf = yaml.load(f, Loader=yaml.FullLoader)
        else:
            self.conf = yaml.load(self.yamlstr, Loader=yaml.FullLoader)
        self.conf = self.conf['regions']['default']
        super(ConfigurationNode, self).__init__(
            self.conf['LambdaName'],
            self.conf['StackName'],
            self.conf['Description'])

    def make_node(self, node_type, conf):
        if node_type == 'Inputs':
            return Inputs(conf)
        if node_type == 'Outputs':
            return Outputs(conf)
        if node_type == 'S3Access':
            return S3Access(conf['bucket'], conf['role'])
        if node_type == 'S3Distribution':
            return S3Distribution(conf['bucket'])
        return None

    def __call__(self, fn, *args, **kwargs):
        skip_keys = ['LambdaName', 'StackName', 'Description']
        decorators = []
        for k, v in self.conf.items():
            if k in skip_keys:
                continue
            n = self.make_node(k, v)
            if n is not None:
                decorators.append(n)
        f = compose(*decorators)
        return f(super(ConfigurationNode, self).__call__(fn, *args, **kwargs))


class S3Distribution(FabNodeDecoratorBase):
    def __init__(self, bucket_name, archive_name=None):
        super(S3Distribution, self).__init__()
        self.bucket_name = bucket_name
        self.archive_name = archive_name

    def _check_if_bucket_exists(self, bucket_name):
        if self.all:
            return False

        profile = os.environ.get('PROFILE')
        if profile is None:
            raise Exception('profile needs to be set')
        session = boto3.Session(profile_name=profile)
        s3 = session.resource('s3')
        bucket = s3.Bucket(bucket_name)
        bucket.load()
        return False if bucket.creation_date is None else True

    def _create_prestep_stack(self):
        parent_fn_stack = g(self.fn_name).stack_name
        n = g(self.fn_name, '_pre')
        n.stack_name = '%s%s' % (parent_fn_stack, 'AutoBucket')
        n.bucket_name = self.bucket_name
        n.bucket_description = (
            'An automatically generated bucket for node %s' % parent_fn_stack)
        n.bucket_versioning = 'Suspended'
        n.template_file = 'code_bucket.rb.j2'

    def __call__(self, fn, *args, **kwargs):
        @wraps(fn)
        def _fx(*args, **kwargs):
            self.fn_name = fn.__name__
            self.assert_fabnode_made(fn)
            ret = fn(*args, **kwargs)
            if not self._check_if_bucket_exists(self.bucket_name):
                self._create_prestep_stack()
            if self.bucket_name is not None:
                g(self.fn_name).node['bucket_name'] = self.bucket_name
            if self.archive_name is not None:
                g(self.fn_name).node['archive'] = self.archive_name
            return ret
        _fx.wrapper = self
        return _fx


class Distribution(FabNodeDecoratorBase):
    def __init__(self, bucket_name, archive_name=None):
        super(Distribution, self).__init__()
        self.bucket_name = bucket_name
        self.archive_name = archive_name

    def __call__(self, fn, *args, **kwargs):

        @wraps(fn)
        def _fx(*args, **kwargs):
            self.fn_name = fn.__name__
            ret = fn(*args, **kwargs)
            g(self.fn_name).node['bucket_name'] = self.bucket_name
            g(self.fn_name).node['archive'] = self.archive_name
            self.assert_fabnode_made(fn)
            return ret
        _fx.wrapper = self
        return _fx


class Inputs(FabNodeDecoratorBase):
    def __init__(self, inputs):
        super(Inputs, self).__init__()
        self.inputs = inputs

    def __call__(self, fn, *args, **kwargs):
        @wraps(fn)
        def _fx(*args, **kwargs):
            self.fn_name = fn.__name__
            ret = fn(*args, **kwargs)
            g(self.fn_name).inputs = self.inputs
            self.assert_fabnode_made(fn)
            return ret
        _fx.wrapper = self
        return _fx


class Outputs(FabNodeDecoratorBase):
    def __init__(self, outputs):
        super(Outputs, self).__init__()
        self.outputs = outputs

    def __call__(self, fn, *args, **kwargs):
        @wraps(fn)
        def _fx(*args, **kwargs):
            self.fn_name = fn.__name__
            ret = fn(*args, **kwargs)
            g(self.fn_name).outputs = self.outputs
            self.assert_fabnode_made(fn)
            return ret
        _fx.wrapper = self
        return _fx


class S3Access(FabNodeDecoratorBase):
    def __init__(self, bucket_name, role=None):
        super(S3Access, self).__init__()
        self.bucket_name = bucket_name
        self.role = role

    def __call__(self, fn, *args, **kwargs):
        @wraps(fn)
        def _fx(*args, **kwargs):
            self.fn_name = fn.__name__
            ret = fn(*args, **kwargs)
            g(self.fn_name).buckets.append({
                'bucket_name': self.bucket_name,
                'role': self.role
            })
            self.assert_fabnode_made(fn)
            return ret
        _fx.wrapper = self
        return _fx
