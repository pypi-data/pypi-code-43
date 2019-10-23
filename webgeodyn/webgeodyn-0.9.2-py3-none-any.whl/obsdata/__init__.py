"""
Implements classes to read observatory data:

    - `observatory`_ contains classes to manage ObservatoryGroups (CHAMP, SWARM, Magnetic observatories) and Observatory (single observatory at (:math:`r`, :math:`\\theta`, :math:`\phi`) with MF and SV data)
    - `obsdata`_ implements the ObsData class to interface with the `server`_ module` (returning data when needed). It also reads data from .40 and .10 files.

.. _obsdata: http://geodynamo.gricad-pages.univ-grenoble-alpes.fr/webgeodyn/doc/html/webgeodyn.obsdata.obsdata.html
.. _observatory: http://geodynamo.gricad-pages.univ-grenoble-alpes.fr/webgeodyn/doc/html/webgeodyn.obsdata.observatory.html
.. _server: http://geodynamo.gricad-pages.univ-grenoble-alpes.fr/webgeodyn/doc/html/webgeodyn.server.html
"""

from .obsdata import ObsData
