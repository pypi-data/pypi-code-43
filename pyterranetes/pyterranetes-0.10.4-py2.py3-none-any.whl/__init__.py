"""The ``p10s`` module doesn't contain any actual code, is exists to
provide a convenient way to import code into a p10s script.

Example:

.. code-block:: python

    from p10s import tf, k8s

The following things are importable from this module:

``tf``
    just the ``p10s.terraform`` module
``k8s``
    the ``p10s.kubernetes`` module
``values``
    the ``p10s.values`` module
``yaml``, ``json``, ``hcl``
    parsers for syntax of the given type

"""

import p10s.config_context as cfg
import p10s.kubernetes as k8s
import p10s.terraform as tf
import p10s.values
from p10s.__version__ import __version__
from p10s.generator import register_context
from p10s.loads import hcl, json, yaml
