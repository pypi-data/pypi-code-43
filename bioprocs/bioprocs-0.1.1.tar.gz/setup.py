# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['bioprocs',
 'bioprocs.console',
 'bioprocs.console.pipeline',
 'bioprocs.scripts',
 'bioprocs.sets',
 'bioprocs.utils']

package_data = \
{'': ['*'],
 'bioprocs': ['reports/bcftools/*',
              'reports/gsea/*',
              'reports/imtherapy/*',
              'reports/mlearn/*',
              'reports/plot/*',
              'reports/stats/*',
              'reports/tcgamaf/*',
              'reports/tumhet/*'],
 'bioprocs.scripts': ['algorithm/*',
                      'bcftools/*',
                      'bed/*',
                      'bedtools/*',
                      'chipseq/*',
                      'cluster/*',
                      'cnvkit/*',
                      'common/*',
                      'docx/*',
                      'eqtl/*',
                      'fastx/*',
                      'gene/*',
                      'genomeplot/*',
                      'gsea/*',
                      'hic/*',
                      'imtherapy/*',
                      'marray/*',
                      'misc/*',
                      'mlearn/*',
                      'network/*',
                      'picard/*',
                      'plink/*',
                      'plot/*',
                      'power/*',
                      'rank/*',
                      'resource/*',
                      'rnaseq/*',
                      'sambam/*',
                      'seq/*',
                      'snp/*',
                      'snparray/*',
                      'sql/*',
                      'stats/*',
                      'tabix/*',
                      'tcga/*',
                      'tcgamaf/*',
                      'tfbs/*',
                      'tsv/*',
                      'tumhet/*',
                      'vcf/*',
                      'web/*',
                      'xlsx/*']}

install_requires = \
['PyPPL', 'completions', 'pyparam', 'python-box87']

entry_points = \
{'console_scripts': ['bioprocs = bioprocs.console:main']}

setup_kwargs = {
    'name': 'bioprocs',
    'version': '0.1.1',
    'description': 'A set of PyPPL processes for bioinformatics.',
    'long_description': None,
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
