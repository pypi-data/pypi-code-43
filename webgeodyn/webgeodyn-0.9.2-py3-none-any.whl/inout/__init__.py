"""
This submodule contains readers/writers functions for input/output of data files.

Each module file corresponds to a format (e.g. ``zforecast.py`` implements the "zforecast" format).

A format name must be used when loading a Model :

.. code-block:: python

    models = Models()
    model = models.loadModel("/path/to/data/", "modelName", "dataFormat")

This command will use (if it exists) the ``inout/dataformat.py`` file to read the data and load it into webgeodyn.

Function template
#################

Inside the .py files, webgeodyn is looking for ``load`` and ``save`` functions.

``load`` and ``save`` should have the following behaviour :

.. code-block:: python

    def load(dataDirectory, dataModel, keepRealisations=True):
        # 1 -
        # Load the data from dataDirectory
        #
        # 2 -
        # if keepRealisations:
        #   Make a 3D data array
        #   [times, semiNormalisedSchmidt spherical harmonics coef, realisations]
        # else:
        #   Make a 2D data array
        #   [times, semiNormalisedSchmidt spherical harmonics coefs]
        #
        # 3 -
        # add measures to the dataModel object by using the following
        dataModel.addMeasure(measureName, measureType, lmax, units, measureData, times=times)

        # measureName : Any measure name
        # measureType : "MF" or "SV" or "U"
        # lmax : (int) spherical harmonics order
        # units : (string) e.g. "nT"
        # measureData : 2D (without realisations) or 3D (with realisations) array
        # times : 1D array containing time values in years


    def save(dataDirectory, dataModel, forceOverwrite=False):
        # Use dataModel to save files into dataDirectory
        # If forceOverwrite is set to True, the file should be overwritten if exists.
        # If forceOverwrite is set to False, an error should be raised if the file exists.


"""


import os

_formats = [f[:-3] for f in os.listdir(os.path.curdir) if f.endswith('.py') and not f.startswith('__')]
