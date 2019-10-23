"""

This module implements **Filters**. These are functions that modify the content of a `Model`_, a `Measure`_, or spherical harmonics data.

Filter functions can be divided into three categories :

    - 1. Filters on `Model`_

    These filters take a `Model`_ object as input and return a `Model`_ object as output.

    .. code-block:: python

        from webgeodyn.filters import modelfilter
        @modelfilter
        def my_filter(model, other, optional, arguments):
            # model is a Model object, the filter should return a Model object.
            return modified_model

    - 2. Filters on `Measure`_

    These filters take a `Measure`_ object as input and return a `Measure`_ object as output.

    .. code-block:: python

        from webgeodyn.filters import measurefilter
        @measurefilter
        def my_filter(measure, other, optional, arguments):
            # measure is a Measure object, the filter should return a Measure object.
            return modified_measure

    - 3. Filters on spherical harmonics coefficient

    These filters take a 2D (resp. 3D) array as an input, and return 2D (resp. 3D) array.
    These filters are declared using the :code:`@coeffilter` decorator.

    .. code-block:: python

        from webgeodyn.filters import coeffilter
        @coeffilter
        def my_filter(coefs, other, optional, arguments):
            # coefs :
            #   2D array [times, schmidtSemiNormalized spher. harm. coefs]
            #   or 3D array [times, schmidtSemiNormalized spher. harm. coefs]
            # other, optional, arguments :
            #   arguments that can be defined to configure the filter.
            #
            #   if coefs is 2D (resp. 3D) modified_coefs must be 2D (resp 3D.)
            return modified_coefs


    If the filter cannot handle 3D arrays with realisations, the :code:`@coeffilter_norealisations` decorator should be used.

    .. code-block:: python

        from webgeodyn.filters import coeffilter_norealisations
        @coeffilter_norealisations
        def my_filter(coefs, other, optional, arguments):
            # coefs :
            #   2D array only [times, schmidtSemiNormalized spher. harm. coefs]
            return modified_coefs

    This decorator will allow looping on the different realisations of the Model and calling the filter for each one.


Calling filters
###############

Thanks to the decorators, all filters are called on a `Model`_ object.

.. code-block:: python

    from webgeodyn.filters.filename import my_filter
    from webgeodyn.models import Models

    models = Models()
    models.loadModel("/path/to/model/data/"),"Test Model","dataFormat")
    my_filter(models["Test Model"])


.. warning::
    The `Model`_ object is directly modified by the filter (i.e. the data is replaced) unless you specify :code:`copy=True` argument when calling the filter (see below).

Copying data before filtering
-----------------------------

The `Model`_ can be copied before applying the filter in order to avoid rewriting the data inside the `Model`_.

.. code-block:: python

    newModel = my_filter(models["Test Model"],copy=True)


Applying filter to specific measures
------------------------------------

:code:`@measurefilter` and :code:`@coeffilter` are by default applied to all measures in the Model. But it can be applied to a subset of measures by specifing :code:`measureName`:

.. code-block:: python

    my_filter(models["Test Model"],measureName=["MF","SV"])

This will apply the filter to measures named "MF" and "SV"

.. _Measure: https://geodynamo.gricad-pages.univ-grenoble-alpes.fr/webgeodyn/webgeodyn.data.html
.. _Model: https://geodynamo.gricad-pages.univ-grenoble-alpes.fr/webgeodyn/webgeodyn.models.model.html#webgeodyn.models.model.Model

Decorators
##########

"""

from webgeodyn.models import Model
import numpy as np


def coeffilter(coeffilter_function):
    """ Decorator for filters only applied to the coefficients of spherical harmonics.

    The functions decorated by this decorator take coefs as the first parameter and return filtered coefs.
    """
    def applyfilter(model, *args, **kwargs):
        if "copy" in kwargs and kwargs["copy"]:
            returnedModel = model.copy()
        else:
            returnedModel = model

        if "measureName" not in kwargs or kwargs["measureName"] is None:
            # Filter is called on the whole model, applying the filter to all measures
            measurelist = model.measures.keys()
        elif type(kwargs["measureName"]) == list:
            measurelist = kwargs["measureName"]
        else:
            measurelist = [kwargs["measureName"],]

        if "copy" in kwargs:
            del kwargs["copy"]
        if "measureName" in kwargs:
            del kwargs["measureName"]

        for measureName in measurelist:
            if measureName not in model.measures:
                raise ValueError(measureName + " is not inside given model measures.")

            new_coefs = coeffilter_function(returnedModel.measures[measureName].data, *args, **kwargs)
            returnedModel.measures[measureName].setData(new_coefs)

        returnedModel.clearCache()
        return returnedModel
    return applyfilter


def coeffilter_norealisations(coeffilter_function):
    """ Decorator for coeffilters that do not handle realisations.

        The functions decorated by this decorator take coefs as the first parameter and return filtered coefs.
    """
    def applyfilter(model, *args, **kwargs):
        if "copy" in kwargs and kwargs["copy"]:
            returnedModel = model.copy()
        else:
            returnedModel = model

        if "measureName" not in kwargs or kwargs["measureName"] is None:
            # Filter is called on the whole model, applying the filter to all measures
            measurelist = model.measures.keys()
        elif type(kwargs["measureName"]) == list:
            measurelist = kwargs["measureName"]
        else:
            measurelist = [kwargs["measureName"],]

        if "copy" in kwargs:
            del kwargs["copy"]
        if "measureName" in kwargs:
            del kwargs["measureName"]

        for measureName in measurelist:
            if measureName not in model.measures:
                raise ValueError(measureName + " is not inside given model measures.")

            if returnedModel.measures[measureName].has_realisations:
                new_coefs = None
                nreal = returnedModel.measures[measureName].data.shape[2]
                for ireal in range(nreal):
                    new_realisation = coeffilter_function(returnedModel.measures[measureName].data[:,:,ireal],*args)
                    if new_coefs is None:
                        new_coefs = np.zeros((new_realisation.shape[0],new_realisation.shape[1],nreal))
                    new_coefs[:,:,ireal] = new_realisation
            else:
                new_coefs = coeffilter_function(returnedModel.measures[measureName].data,*args, **kwargs)
            returnedModel.measures[measureName].setData(new_coefs)

        returnedModel.clearCache()
        return returnedModel
    return applyfilter


def measurefilter(measurefilter_function):
    """ Decorator for filters only applied to measures.

        The functions decorated by this decorator take measures as the first parameter and return the filtered measures.
    """
    def applyfilter(model, *args, **kwargs):
        if "copy" in kwargs and kwargs["copy"]:
            returnedModel = model.copy()
        else:
            returnedModel = model

        if "measureName" not in kwargs or kwargs["measureName"] is None:
            # Filter is called on the whole model, applying the filter to all measures
            measurelist = model.measures.keys()
        elif type(kwargs["measureName"]) == list:
            measurelist = kwargs["measureName"]
        else:
            measurelist = [kwargs["measureName"],]

        if "copy" in kwargs:
            del kwargs["copy"]
        if "measureName" in kwargs:
            del kwargs["measureName"]

        for measureName in measurelist:
            if measureName not in model.measures:
                raise ValueError(measureName + " is not inside given model measures.")

            new_measure = measurefilter_function(returnedModel.measures[measureName],*args, **kwargs)
            returnedModel.measures[measureName] = new_measure

        returnedModel.clearCache()
        return returnedModel
    return applyfilter


def modelfilter(modelfilter_function):
    """ Decorator for filters directly applied to the model.

        The functions decorated by this decorator take the model as first parameter and return the filtered model.
    """
    def applyfilter(model, *args, **kwargs):
        if "copy" in kwargs and kwargs["copy"]:
            returnedModel = model.copy()
        else:
            returnedModel = model

        if "copy" in kwargs:
            del kwargs["copy"]

        returnedModel = modelfilter_function(returnedModel, *args, **kwargs)

        returnedModel.clearCache()
        return returnedModel
    return applyfilter
