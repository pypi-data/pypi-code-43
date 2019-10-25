# -*- coding: utf-8 -*-
"""
Mapping Learning (also called maplearn) is an application to make use of machine learning easy
(easier, at least). Initially designed for geographical data (cartography based
on remote sensing),
Mapping Learning deals very well with classical (*ie* tabular) data. 

More information (in french) is available in maplearn's wiki_.

.. _wiki: https://bitbucket.org/thomas_a/maplearn/wiki/

Functionnalities
----------------

* **many algorithms** to make predictions (classification, clustering or
  regression)
* look for best hyper-parameters to **improve accuracy** of your results
* generalize machine learning's best practices (k-fold...)
* several preprocessing tasks available : reduction of dimensions...
* reads/writes **many file formats** (*geographic or not*)
* synthetizes results in a **standardized report**
* statiscal and more empirical **advices** will help novice users

Development
-----------

Mapping Learning is written in Python and used major Open Source libraries, 
like scikit-learn_ (Machine Learning algorithms),
numpy_ and pandas_ to manipulate scientific data and Gdal_ to
handle geographic data.

.. _scikit-learn: http://scikit-learn.org/
.. _numpy: http://www.numpy.org/
.. _pandas: https://pandas.pydata.org/
.. _Gdal: https://pypi.org/project/GDAL/

Mapping Learning is a free software, under LGPL license.

Modules
-------

Mapping Learning consists of 4 modules:

1. **ml**: machine learning stuff
2. **datahandler**: classes between a dataset usable in machine learning and
   the usable files
3. **filehandler**: classes to read/write data from/to a file
4. **app**: application modules (configuration, ...)

Alban Thomas (alban.thomas@univ-rennes2.fr)
"""
import logging
from logging.config import fileConfig
from pkg_resources import resource_filename

# load logging configuration file
fileConfig(resource_filename('maplearn', 'logging.cfg'))
logger = logging.getLogger(__name__)
__version__ = '0.3.1'
