# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['voting']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'voting',
    'version': '0.1.3',
    'description': 'Voting and election related functions.',
    'long_description': "voting\n======\n\n|travis| |rtd| |codecov| |pypi| |pyversions|\n\n\n.. |travis| image:: https://img.shields.io/travis/crflynn/voting.svg\n    :target: https://travis-ci.org/crflynn/voting\n\n.. |rtd| image:: https://img.shields.io/readthedocs/voting.svg\n    :target: http://voting.readthedocs.io/en/latest/\n\n.. |codecov| image:: https://codecov.io/gh/crflynn/voting/branch/master/graphs/badge.svg\n    :target: https://codecov.io/gh/crflynn/voting\n\n.. |pypi| image:: https://img.shields.io/pypi/v/voting.svg\n    :target: https://pypi.python.org/pypi/voting\n\n.. |pyversions| image:: https://img.shields.io/pypi/pyversions/voting.svg\n    :target: https://pypi.python.org/pypi/voting\n\n\nA pure Python module for election quotas, voting measures, and apportionment\nmethods.\n\nInstallation\n------------\n\nThe ``voting`` package works in Python 2.7, 3.5, 3.6 and 3.7. It is available on\npypi and can be installed using pip.\n\n.. code-block:: shell\n\n    pip install voting\n\nPackage structure\n-----------------\n\n* voting\n\n  * apportionment\n\n    * adams\n    * dhondt\n    * hagenbach_bischoff\n    * hamilton\n    * huntington_hill\n    * jefferson\n    * sainte_lague\n    * vinton\n    * webster\n\n  * diversity\n\n    * berger_parker\n    * general\n    * gini_simpson\n    * golosov\n    * inverse_simpson\n    * laakso_taagepera\n    * renyi\n    * shannon\n    * simpson\n\n  * proportion\n\n    * adjusted_loosemore_hanby\n    * dhondt\n    * gallagher\n    * grofman\n    * least_square\n    * lijphart\n    * loosemore_hanby\n    * rae\n    * regression\n    * rose\n    * sainte_lague\n\n  * quota\n\n    * droop\n    * hagenbach_bischoff\n    * hare\n    * imperiali\n\nExamples\n--------\n\nApportioning seats using the Huntington-Hill method.\n\n.. code-block:: python\n\n    from voting import apportionment\n\n\n    votes = [2560, 3315, 995, 5012]\n    seats = 20\n    assignments = apportionment.huntington_hill(votes, seats)\n\n\nCalculating the effective number of parties using Golosov's measure.\n\n.. code-block:: python\n\n    from voting import diversity\n\n\n    parties = [750, 150, 50, 50]\n    effective_parties = diversity.golosov(parties)\n\n\nMeasuring the disproportionality of democratic representation using the\nSainte-Lague measure.\n\n.. code-block:: python\n\n    from voting import proportion\n\n\n    votes = [750, 150, 50, 50]\n    seats = [80, 16, 2, 2]\n    disproportionality = proportion.sainte_lague(votes, seats)\n\nDetermining the Droop quota\n\n.. code-block:: python\n\n    from voting import quota\n\n\n    votes = 1000\n    seats = 20\n    election_quota = quota.droop(votes, seats)\n",
    'author': 'Christopher Flynn',
    'author_email': 'crf204@gmail.com',
    'url': 'https://github.com/crflynn/voting',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
