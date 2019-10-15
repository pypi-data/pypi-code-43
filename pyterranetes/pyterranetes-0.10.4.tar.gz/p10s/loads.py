"""It is often easier to write some terraform or yaml code directly in
the native syntax instead of having to write out the full python
object using python's literal dict/list syntax.

Note: you probably shouldn't call these functions directly, while they
document the exact syntax and haviour of the parsers, you probably
want to be using one of the specific object generators instead:
:func:`from_hcl <p10s.terraform.from_hcl>`, :func:`many_from_hcl
<p10s.terraform.many_from_hcl>`, :func:`from_yaml
<p10s.kubernetes.from_yaml>` and :func:`many_from_yaml
<p10s.kubernetes.many_from_yaml>`.

.. autofunction:: p10s.loads.yaml
.. autofunction:: p10s.loads.yaml_all
.. autofunction:: p10s.loads.hcl
.. autofunction:: p10s.loads.json

"""
import io
import json as json_lib
from pathlib import Path

import hcl as pyhcl
from ruamel.yaml import YAML

ruamel = YAML(typ="safe", pure=True)
ruamel.default_flow_style = False


def _data(object):
    if isinstance(object, (io.BufferedIOBase, io.TextIOBase, io.RawIOBase, io.IOBase)):
        return object.read()
    elif isinstance(object, Path):
        return object.open().read()
    else:
        return object


def yaml(input):
    """Parses ``input`` as a single yaml document and returns the
corresponding python data structure.

:param input: the source of the yaml
:type input: str, Path or IOBase
    """
    try:
        return ruamel.load(_data(input))
    except Exception as e:
        print("Error parsing %s" % input)
        raise (e)


def yaml_all(input):
    """Parses ``input`` as multiple yaml documents and returns a list of python objects (dicts, lists, etc.)

:param input: the source of the yaml
:type input: str, Path or IOBase
"""
    try:
        return ruamel.load_all(_data(input))
    except Exception as e:
        print("Error parsing %s" % input)
        raise (e)


def hcl(input):
    """Parses ``input`` as a hcl code and returns the corresponding python dict.

As with terraform's json syntax blocks are converted to nested dicts:

.. code-block:: text

    terraform {
      a = "b"
    }

parses to

.. code-block:: python

    {'terraform':
        {'a': 'b'}
    }

and this:

.. code-block:: terraform

    resource "type" "name" {
      a = "b"
    }

parses to

.. code-block:: python

    {'resource':
        {'type':
            {'name':
                {'a': 'b'}
            }
        }
    }

Multiple blocks are merged into a single dict as per the tf.json format:

.. code-block:: terraform

    resource "type" "first" {
      a = "b"
    }
    resource "type" "second" {
      a = "b"
    }

parses to

.. code-block:: python

    {'resource':
        {'type':
            {'first':  {'a': 'b'}},
            {'second': {'a': 'b'}},
        }
    }

:param input: the source of the hcl
:type input: str, Path or IOBase
"""
    return pyhcl.loads(_data(input))


def json(input):
    """Parses ``input`` as a single json object.

:param input: the source of the json
:type input: str, Path or IOBase
"""
    return json_lib.loads(_data(input))


def load_file(filename):
    filename = Path(filename)
    suffix = filename.suffix
    if suffix == ".yaml":
        return yaml(filename)
    elif suffix == ".hcl":
        return hcl(filename)
    elif suffix == ".json":
        return json(filename)
    else:
        raise Exception("Unknown extension {}" % filename)
