"""Generating terraform with pyterranetes is, as with kubernetes, just a
question of writing a p10s script which creates a
``terraform.Context`` object and adds terraform blocks to it:

.. code-block:: python

    from p10s import tf

    c = tf.Context()

    # Fully explicit style
    c += tf.Variable("foo", dict(
        default=0
    ))

    c += tf.Resource("type", "name", dict(
        var = 'value'
    ))

    # Helper function
    c += tf.variables(key="${data.terraform_remote_state.key}"})
    c += tf.outputs(key="${module.m.key}"})

    # HCL syntax if a large amount of code needs to be converted to
    # pyterranetes quickly
    c += tf.from_hcl(""\"
        module "m" {
          source = "../m/"
        }
    ""\")

    # property/attribute syntax for a more pythonic feeling
    c.resource.type.name = {
        'key': 'value',
    }

    c.module.name = {
        'source': './modules/my-module/',
    }

For each terraform configuration block there is a corresponding python
class. Depending on the block type and how it's used some of the
classes provid convenience methods and constructors. All of the
classes have a ``.body`` property representing the data inside the
block.

There are 3 different categories of terraform blocks:

Blocks that don't have any properties other than ``.body``:
    :py:class:`terraform <p10s.terraform.Terraform>`, and
    :py:class:`locals <p10s.terraform.Locals>`.
Blocks that also have a name property:
    :py:class:`provider <p10s.terraform.Provider>`,
    :py:class:`variable <p10s.terraform.Variable>`, and
    :py:class:`output <p10s.terraform.Output>`
Blocks that also have a type and a name property:
    :py:class:`resource <p10s.terraform.Resource>`, and
    :py:class:`data <p10s.terraform.Data>`

Sometimes it's more convenient to start with hcl code, we can use the
:py:func:`from_hcl <p10s.terraform.from_hcl>` function:

.. code-block:: python

    c += tf.from_hcl(\"""
        resource "type" "name" {
          var = "value"
          ...
        }
    \""")

Note the hcl has two, equivalent, ways to assign a nested map (dict in python):

.. code-block:: none

    key {
       v = k
    }

and

.. code-block:: none

    key = {
       v = k
    }

When parsing hcl pyterranetes will convert both of these to a single
entry with key ``key`` and value a dict with the values of the
corresponsding block. As pyterranetes only actually generates
``.tf.json`` and not ``.tf`` (hcl) files, there is also no ambiguity
in the output.

Alternatively there's another way to add blocks to a context using the
properties ``resource``, ``module`` and ``variable`` (there is
currently no equivalent auto syntax for provider, local or output
blocks).

.. code-block:: python

    from p10s import tf

    c = tf.Context()

    c.resource.random_id.project_name = {
        'byte_length': 8
    }

    c.module.mod = {
        'source': './modules/module'
    }

    c.variable.name = 'default-value'

"""

import collections.abc
from copy import deepcopy
from pprint import pformat

from p10s.config_context import JSONContext
from p10s.loads import hcl
from p10s.utils import merge_dicts


class Context(JSONContext):
    """Context for terraform files.

    As with the k8s.Context this instances of this class represent a
    single terraform file. Block of terraform can be added using the
    ``+=`` operator.

    By default adding the same terraform block multiple times to a context
    does not cause any errors, the values will be merged in as normal. If
    needed more strict verification can be added by passing `strict=True`
    to the Context constructor.

    """

    output_file_extension = ".tf.json"

    def __init__(self, *args, data=None, strict=False, **kwargs):
        if data is None:
            self.data = {}
        else:
            self.data = data

        self.strict = strict

        super().__init__(*args, **kwargs)

    def _merge_in(self, values):
        self.data = merge_dicts(self.data, values)
        return self

    def add(self, block):
        if not isinstance(block, (list, tuple)):
            block = [block]
        for b in block:
            if self.strict:
                existing = self.lookup(b._key())
                if existing is not None:
                    raise DuplicateBlockError(existing, block)
            self._merge_in(b.data)
        return self

    def lookup(self, key):
        def _rec(here, path):
            if len(path) == 0:
                return here
            if isinstance(here, collections.abc.Mapping):
                if path[0] in here:
                    first = path.pop(0)
                    return _rec(here[first], path)
            return None

        return _rec(self.data, key)

    def __iadd__(self, block):
        """Add ``block`` to the context's data, destructively modifies ``self``

        :param TerraformBlock block:
        """
        return self.add(block)

    def __add__(self, block):
        """Returns a new context containg all the data in ``self`` and ``block``

        :param TerraformBlock block:
        """
        return deepcopy(self).add(block)

    @property
    def resource(self):
        return AutoResource(self)

    @property
    def module(self):
        return AutoModule(self)

    @property
    def variable(self):
        return AutoVariable(self)


class DuplicateBlockError(ValueError):
    def __init__(self, existing, new_block):
        self.existing = existing
        self.new_block = new_block


class TerraformBlock:
    """Abstract base class for all terrform blocks.

    Exposes the :py:meth:`.body <p10s.terrform.TerraformBlock.body>`
    property for direct manipulation of the block's data.

    """

    def __init__(self, data=None):
        if data is not None:
            self.data = data

    @property
    def body(self):
        """Returns the data contained in thie block. name, type, provider or
        other non-body values are exposed as properties on the
        corresponding object.

        """
        return self._body()

    def update(self, new_body_values):
        """Merges in ``new_body_values`` with this block's body. Does not
        change ``name`` or ``type`` or any of the block's
        properties.

        """
        merge_dicts(self.body, new_body_values)
        return self

    def _body(self):
        raise NotImplementedError()  # pragma: no cover

    def _key(self):
        raise NotImplementedError()  # pragma: no cover

    def __eq__(self, other):
        if isinstance(other, TerraformBlock):
            return self.__dict__ == other.__dict__
        else:
            return super().__eq__(other)


class NoArgsBlock(TerraformBlock):
    def __init__(self, body):
        super().__init__({self.KIND: body})

    def _body(self):
        return self.data[self.KIND]

    def _key(self):
        return [self.KIND]

    def __repr__(self):
        return "#<%s %s>" % (self.KIND, len(self.body))


class NameBlock(TerraformBlock):
    def __init__(self, name, body=None):
        self._name = name
        body = body if body is not None else {}
        super().__init__({self.KIND: {name: body}})

    def _body(self):
        return self.data[self.KIND][self.name]

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if name != self._name:
            self.data[self.KIND][name] = self.data[self.KIND][self._name]
            del self.data[self.KIND][self._name]
            self._name = name

    def _key(self):
        return [self.KIND, self.name]

    def __repr__(self):
        return "#<%s %s %s>" % (self.KIND, self.name, len(self.body))


class TypeNameBlock(TerraformBlock):
    def __init__(self, type, name, body=None):
        self._type = type
        self._name = name
        body = body if body is not None else {}
        super().__init__({self.KIND: {type: {name: body}}})

    def _body(self):
        return self.data[self.KIND][self._type][self._name]

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, name):
        self.data[self.KIND][name] = self.data[self.KIND][self._type]
        del self.data[self.KIND][self._type]
        self._type = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        type_block = self.data[self.KIND][self._type]
        type_block[name] = type_block[self._name]
        del type_block[self._name]
        self._name = name

    def _key(self):
        return [self.KIND, self.type, self.name]

    def __repr__(self):
        return "#<%s %s %s %s>" % (self.KIND, self.type, self.name, len(self.body))


class Terraform(NoArgsBlock):
    """``terraform`` block. Doesn't expose any properties beyond ``body``."""

    KIND = "terraform"


class Locals(NoArgsBlock):
    """``locals`` block. Doesn't expose any properties beyond ``body``."""

    KIND = "locals"


class Variable(NameBlock):
    """``variable`` block. Exposes `.name` as a property.

    If you're defining a variable without a type or a description (90%
    of the cases in practice), it is probably easier to use
    :func:`variables <p10s.terraform.variables>`.

    """

    KIND = "variable"

    def __repr__(self):
        return "#<%s %s %s>" % (self.KIND, self.name, self.body.get("default", None))


def variables(**kwargs):
    """Helper function for defining multiple :class:`variable
    <p10s.terraform.Variable` blocks which only specify their default
    value.

    Example:

    .. code-block:: python

      c += tf.variables(
          name='value,
          other='other value')

    is short hand for:

    .. code-block:: python

      c += tf.Variable("name", {'default': 'value'})
      c += tf.Variable("other", {'default': 'other value'})

    """
    return [
        Variable(name=name, body={"default": kwargs[name]}) for name in kwargs.keys()
    ]


class Output(NameBlock):
    """``output`` block. Exposes `.name` as a property.

    The constructor is designed to be convenient to use in p10s
    scripts. Any (single) keyword argument passed to the constructor,
    other than ``name`` and ``body``, is assumed to be the name of an
    output with the given value.

    So this call:

    .. code-block:: python

        o = Output(ip="${aws_eip.ip.public_ip})

    is equivalent to this:

    .. code-block:: python

        o = Output(name="ip", body={
            'var_name': "${aws_eip.ip.public_ip}
        })

    The convenience constructor can be used to define exactly one output,
    for similar syntax for multiple outputs see :func:`outputs
    <p10s.terraform.outputs>`

    """

    KIND = "output"

    def __init__(self, name=None, body=None, **kwargs):
        if name is None and body is None:
            keys = list(kwargs.keys())
            if len(keys) != 1:
                raise Exception(
                    "Output's dwim constructor expects exactly one arg, not %s", kwargs
                )
            name = keys[0]
            body = {"value": kwargs[name]}

        super().__init__(name=name, body=body)

    def __repr__(self):
        return "#<%s %s %s>" % (self.KIND, self.name, self.body.get("value", None))


def outputs(**kwargs):
    """Helper function for defining multiple :class:`output <p10s.terraform.Output>`  blocks.

    Example:

    .. code-block:: python

      c += tf.outputs(
          name='${module.foo.id},
          other='${module.foo.key}')

    is short hand for:

    .. code-block:: python

      c += tf.Output("name", {'value': '${module.foo.id}'})
      c += tf.Output("other", {'value': '${module.foo.key}'})


    """
    return [Output(name=name, body={"value": kwargs[name]}) for name in kwargs.keys()]


class Module(NameBlock):
    """``module`` block. Exposes `.name` as a property."""

    KIND = "module"


class Provider(NameBlock):
    """``provider`` block. Exposes `.name` as a property."""

    KIND = "provider"


class Resource(TypeNameBlock):
    """``resource`` block. Exposes `.name` and `.type` as properties."""

    KIND = "resource"


class Data(TypeNameBlock):
    """``data`` block. Exposes `.name` and `.type` as properties."""

    KIND = "data"


class HCLParseError(Exception):
    def __init__(self, data, error=None):
        self.data = data
        self.error = error

    def __str__(self):
        return "Unable to parse HCL text %s: %s" % (pformat(self.data), self.error)


class HCLUnknownBlockError(HCLParseError):
    def __init__(self, kind):
        self.kind = kind

    def __str__(self):
        return "Unknown terraform block type %s" % self.kind


def many_from_hcl(hcl_string):
    """Build TerraformBlock objects from hcl text. Always returns a list of blocks.

    See :func:`p10s.terraform.from_hcl` for examples and
    :func:`p10s.loads.hcl` for details on the unerlying hcl parser.

    """

    try:
        data = hcl(hcl_string)
    except Exception as e:
        raise HCLParseError(data=hcl_string, error=e) from e

    blocks = []

    for kind in data.keys():
        if kind == "terraform":
            blocks.append(Terraform(body=data[kind]))
        elif kind == "locals":
            blocks.append(Locals(body=data[kind]))
        elif kind in ("variable", "output", "locals", "module", "provider"):
            for name in data[kind].keys():
                if kind == "variable":
                    cls = Variable
                if kind == "output":
                    cls = Output
                if kind == "module":
                    cls = Module
                if kind == "provider":
                    cls = Provider
                blocks.append(cls(name=name, body=data[kind][name]))
        elif kind in ("resource", "data"):
            for type in data[kind].keys():
                for name in data[kind][type]:
                    if kind == "resource":
                        cls = Resource
                    if kind == "data":
                        cls = Data
                    blocks.append(
                        cls(type=type, name=name, body=data[kind][type][name])
                    )
        else:
            raise HCLUnknownBlockError(kind=kind)

    return sorted(blocks, key=lambda b: repr(b))


def from_hcl(hcl_string):
    """Build a TerraformBlock from hcl text.

    :param hcl_string: hcl text to parse
    :type hcl_string: a string, a pathlib.Path, or an io.Base object

    .. code-block:: python

        c += tf.from_hcl(\"\"\"
          foo { }
        "\"\")

    Note that the return value is an instance of tf.TerraformBlock, and
    has all the corresponding methods:

    .. code-block:: python

        resource = tf.from_hcl('''
          resource "type" "name" {
            key = 'value'
          }
        ''')

        resource.body['key'] = 'other value'

    It can be convenient to keep most of the terraform code in a seperate
    file and only use pyterranetes for certain operations. In this case
    it's often best to leave the terraform code seperate and just read it
    into the p10s script:

    .. code-block:: python

        for name in (name1, name2, ...):
            resource = tf.from_hcl(Path('./base.tf'))
            resource.name = name
            c += resource

    See :func:`p10s.loads.hcl` for details on the unerlying hcl parser.
    """
    blocks = many_from_hcl(hcl_string)

    if len(blocks) == 1:
        return blocks[0]
    else:
        raise Exception(
            "Expected exactly one block when using `from_hcl` but got %s blocks from %s"
            % (len(blocks), hcl_string)
        )


class AutoResource:
    def __init__(self, context):
        self._context_ = context
        self._type_ = None

    def __getattr__(self, name):
        if name in ["_type_", "_context_"]:
            super().__getattribute__(name)
        else:
            self._type_ = name
            return self

    def __setattr__(self, name, body):
        if name in ["_type_", "_context_"]:
            super().__setattr__(name, body)
        else:
            if self._type_ is None:
                raise Exception("Can't set name before _type_ is set.")
            self._context_ += Resource(self._type_, name, body)


class AutoModule:
    def __init__(self, context):
        self._context_ = context

    def __setattr__(self, name, body):
        if name in ["_context_"]:
            super().__setattr__(name, body)
        else:
            self._context_ += Module(name, body)

    def __setitem__(self, name, body):
        self._context_ += Module(name, body)


class AutoVariable:
    def __init__(self, context):
        self._context_ = context

    def __setattr__(self, key, value):
        if key in ["_context_"]:
            super().__setattr__(key, value)
        else:
            self._context_ += Variable(key, {"default": value})

    def __setitem__(self, name, value):
        self.__setattr__(name, value)
