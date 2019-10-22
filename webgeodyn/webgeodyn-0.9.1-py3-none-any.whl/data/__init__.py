"""

The module implements `GHData`_ or `TSData`_ classes that are used to store measure data.

    - `GHData`_ contains data described by :math:`g_l^m` and :math:`h_l^m` spherical harmonics coefficients. This includes magnetic field ('MF') or secular variation ('SV').
    - `TSData`_ contains data described by a poloidal/toroidal decomposition of spherical harmonics coefficients (:math:`tc_l^m`, :math:`ts_l^m`, :math:`sc_l^m`, :math:`ss_l^m`). This includes the core flow ('U') or its horizontal divergence ('DIVHU').

`MeasureData`_ is the parent class containing common features of `GHData`_ and `TSData`_

Data creation
#############

Creation of a new measure is done by instancing `GHData`_ or `TSData`_:

.. code-block:: python

    from webgeodyn.data import GHData, TSData
    from webgeodyn.data.normPnm import semiNormalisedSchmidt

    PnmNorm = semiNormalisedSchmidt
    myData = GHData(data, lmax, units, measureType, PnmNorm, gridth=tharray, gridph=pharray):
    # data :
    #   2D array [times, harmonics coefficients]
    #   or 3D array [times, harmonics coefficients, realisations]
    # lmax : int
    # units : string
    # measureType : "MF", "SV" or "U"
    # PnmNorm : normalisation function
    # gridth (optional) : array containing list of theta points
    # gridph (optional) : array containing list of phi points


`normPnm`_ contains normalisation functions for Legendre functions :

    - `semiNormalisedSchmidt`_ returns Schmidt semi-normalised coefficients (default).
    - `noNorm`_ should be used instead when no normalisation is desired.

Operation on data
#################

Setting data
------------

To set a new data array for `GHData`_ or `TSData`_, use the ``setData`` function (overwriting directly data arrays may cause errors when computing data):

.. code-block:: python

    myData.setData(newdata)
    # newdata :
    #   2D array [times, harmonics coefficients]
    #   or 3D array [times, harmonics coefficients, realisations]

Evaluating values into real space
---------------------------------

To compute values on the globe (on given :math:`r`, :math:`\\theta`, :math:`\phi`), use the ``computeRThetaPhiData`` function:

.. code-block :: python

    globeData = myData.computeRThetaPhiData(r, thlist, phlist, components=["th","ph","norm"], usegridPnm=False, computeallrealisation=False, irealisation=-1)

    # Returns a dictionary containing for each component (r, theta, phi, norm), a 3D array [times, theta, phi]
    # (if computeallrealisation=True, the returned array is 4D [times, theta, phi, realisations])
    #
    # r : (float) radius
    # thlist : (array or list) list of theta points where the values are to be calculated
    # phlist : (array or list) list of phi points where the values are to be calculated
    #    phlist or thetalist must contain unique values [theta] or [phi]
    # components : list of components to be calculated. Can contain "r", "th", "ph", "norm" for GHData and "th", "ph", "norm", "divh" for TSData.
    # usegridPnm : Whether to use precalculated Pnm for listed th and ph values (warning, use only if thlist and phlist are equal to myData.th and myData.ph)
    # computeallrealisation: (boolean)
    #    if True, returns a 4D array [times, theta, phi, realisations]
    #    if False, returns a 3D array [times, theta, phi]
    # irealisation: (int)
    #    if irealisation<0, returns a 3D array [times, theta, phi] corresponding to the mean of realisations
    #    if irealisation>0, returns a 3D array [times, theta, phi] corresponding to the ith realisation


Conversion from array index (:math:`k`) to degree, order (:math:`l`, :math:`m`)
-------------------------------------------------------------------------------

To convert :math:`g_l^m` to/from :math:`k`, the index in the data array, use ``lm2k`` or ``k2lm``:

.. code-block :: python

    k = myData.lm2k(l, m, coef)
    # l (equivalent to n in other notations) : integer
    # m : integer
    # coef :
    #    "g" or "h" for GHData
    #    "tc", "ts", "sc", or "ss" for TSData
    #
    # returns :
    # k : integer index

    l, m, coef = myData.k2lm(k)
    # k : integer index
    #
    # returns :
    # l (equivalent to n in other notations) : integer
    # m : integer
    # coef :
    #    "g" or "h" for GHData
    #    "tc", "ts", "sc", or "ss" for TSData


.. _GHData: https://geodynamo.gricad-pages.univ-grenoble-alpes.fr/webgeodyn/webgeodyn.data.GHData.html
.. _TSData: https://geodynamo.gricad-pages.univ-grenoble-alpes.fr/webgeodyn/webgeodyn.data.TSData.html
.. _MeasureData: https://geodynamo.gricad-pages.univ-grenoble-alpes.fr/webgeodyn/webgeodyn.data.measuredata.html
.. _normPnm: https://geodynamo.gricad-pages.univ-grenoble-alpes.fr/webgeodyn/webgeodyn.data.normPnm.html
.. _semiNormalisedSchmidt: https://geodynamo.gricad-pages.univ-grenoble-alpes.fr/webgeodyn/webgeodyn.data.normPnm.html#webgeodyn.data.normPnm.semiNormalisedSchmidt
.. _noNorm: https://geodynamo.gricad-pages.univ-grenoble-alpes.fr/webgeodyn/webgeodyn.data.normPnm.html#webgeodyn.data.normPnm.noNorm

"""

from .TSData import TSData
from .GHData import GHData
