"""
This module implements `Models`_ and `Model`_ objects.

Models
######

`Models`_ is a simple dictionary object, listing `Model`_ objects.

.. code-block:: python

    models = Models()
    models.loadModel("/path/to/data/", "my model", "dataFormat")
    # Model is now loaded and accessible using:
    models["my model"]

Model
#####

A `Model`_ object contains different `Measure`_ data (e.g. magnetic field, secular variation, streamfunctions ...)

.. code-block:: python

    model = Model("/path/to/data/", "dataFormat")
    # model.measures contains a dictionary of measures
    # Measures are either GHData or TSData
    # It is possible to access all their properties :
    #   model.measures["MF"].lmax
    #   model.measures["MF"].data
    #   model.measures["MF"].computeRThetaPhiData(r, thlist, phlist)
    #   ...


All measures share the same time array that is given in :code:`model.times`.


To have information on how to construct a Model from data files, please see the `InOut module documentation`_.


.. _InOut module documentation: https://geodynamo.gricad-pages.univ-grenoble-alpes.fr/webgeodyn/webgeodyn.inout.html
.. _Measure: https://geodynamo.gricad-pages.univ-grenoble-alpes.fr/webgeodyn/webgeodyn.data.html
.. _Model: https://geodynamo.gricad-pages.univ-grenoble-alpes.fr/webgeodyn/webgeodyn.models.model.html#webgeodyn.models.model.Model
.. _Models: https://geodynamo.gricad-pages.univ-grenoble-alpes.fr/webgeodyn/webgeodyn.models.models.html

"""

from .models import Models
from .model import Model
