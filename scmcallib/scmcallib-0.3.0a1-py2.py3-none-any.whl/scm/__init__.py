"""
Provides an interface to run a number of different Simple Climate Models.

In future, this will likely be replaced with _OpenSCM as that project aims to provide a consistent interface to a wider variety of
models.

It is recommended that the scm objects are used within a context manager (see below). This helps clean up any temporary resources
used. This is particularly important for the parallel versions of MAGICC (``MAGICC6_Parallel`` and ``MAGICC7_Parallel``) which
may create a large number of instances and processes.

    .. code-block:: python

        from scmcallib.scm import MAGICC7_SCM

        with MAGICC7_SCM() as m:
            # A new magicc instance is only created on the first call to ``run``
            res = m.run({}, variables=['Surface Temperature'])
            # Reuses the same instance
            res = m.run({}, variables=['Surface Temperature'])

        # the magicc instance is automatically removed once out of the scope of the context manager.


    .. _openscm: https://github.com/openclimatedata/openscm
"""

# TODO: This module could likely be replaced with openscm once it is stable
from .base import BaseSCM  # noqa: F401
from .ar5ir import AR5IR
from .magicc import MAGICC7_SCM, MAGICC6_SCM, MAGICC6_Parallel, MAGICC7_Parallel

_models = [AR5IR, MAGICC6_SCM, MAGICC7_SCM, MAGICC6_Parallel, MAGICC7_Parallel]


def get_scm(scm_name):
    """
    Get a SCM class

    Parameters
    ----------
    scm_name: str
        SCM name (``name`` attribute on the class)

    Returns
    -------
    An SCM class which can then be initialised

    """
    for m in _models:
        if m.name == scm_name.lower():
            return m

    raise ValueError(
        "No scm named {}. Options include {}".format(
            scm_name, [m.name for m in _models]
        )
    )
