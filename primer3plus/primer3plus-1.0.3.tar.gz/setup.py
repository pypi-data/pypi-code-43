# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['primer3plus', 'primer3plus.design', 'primer3plus.params', 'primer3plus.utils']

package_data = \
{'': ['*']}

install_requires = \
['loggable-jdv>=0.1.2,<0.2.0', 'primer3-py>=0.6.0,<0.7.0']

setup_kwargs = {
    'name': 'primer3plus',
    'version': '1.0.3',
    'description': 'An easy-to-use Python API for Primer3 primer design.',
    'long_description': '# Primer3Plus\n\nPrimer3Plus is a Python DNA primer design tool based off of Primer3 and the\nPython primer3 wrapper (https://pypi.org/project/primer3-py/).\n\n```python\nimport json\n\ndesign = Design()\ntemplate = """\nTCATGTAATTAGTTATGTCACGCTTACATTCACGCCCTCCCCCCAC\nATCCGCTCTAACCGAAAAGGAAGGAGTTAGACAACCTGAAGTCTAG\nGTCCCTATTTATTTTTTTATAGTTATGTTAGTATTAAGAACGTTAT\nTTATATTTCAAATTTTTCTTTTTTTTCTGTACAGACGCGTGTACGC\nATGTAACATTATACTGAAAACCTTGCTTGAGAAGGTTTTGGGACGC\nTCGAAGGCTTTAATTTGC\n"""\ntemplate = template.replace(\'\\n\', \'\').replace(\' \', \'\')\ndesign.settings.template(template)\ndesign.settings.as_cloning_task()\ndesign.settings.primer_num_return(1)\nresults, explain = design.run()\n\nprint(json.dumps(results, indent=1))\nprint(json.dumps(explain, indent=1))\n```\n\n```json\n{\n "0": {\n  "PAIR": {\n   "PENALTY": 11.204301707622733,\n   "COMPL_ANY_TH": 0.0,\n   "COMPL_END_TH": 0.0,\n   "PRODUCT_SIZE": 248\n  },\n  "LEFT": {\n   "PENALTY": 9.027129166714644,\n   "SEQUENCE": "TCATGTAATTAGTTATGTCACGCTTAC",\n   "location": [\n    0,\n    27\n   ],\n   "TM": 57.972870833285356,\n   "GC_PERCENT": 33.333333333333336,\n   "SELF_ANY_TH": 0.0,\n   "SELF_END_TH": 0.0,\n   "HAIRPIN_TH": 0.0,\n   "END_STABILITY": 2.34\n  },\n  "RIGHT": {\n   "PENALTY": 2.1771725409080886,\n   "SEQUENCE": "GCAAATTAAAGCCTTCGAGCG",\n   "location": [\n    247,\n    21\n   ],\n   "TM": 58.82282745909191,\n   "GC_PERCENT": 47.61904761904762,\n   "SELF_ANY_TH": 0.0,\n   "SELF_END_TH": 0.0,\n   "HAIRPIN_TH": 38.006257959698985,\n   "END_STABILITY": 5.03\n  }\n }\n}\n{\n "PRIMER_LEFT_EXPLAIN": "considered 10, low tm 9, ok 1",\n "PRIMER_RIGHT_EXPLAIN": "considered 10, low tm 3, high tm 4, ok 3",\n "PRIMER_PAIR_EXPLAIN": "considered 1, ok 1",\n "PRIMER_LEFT_NUM_RETURNED": 1,\n "PRIMER_RIGHT_NUM_RETURNED": 1,\n "PRIMER_INTERNAL_NUM_RETURNED": 0,\n "PRIMER_PAIR_NUM_RETURNED": 1\n}\n```\n## Installation\n\n```\npip install primer3plus -U\n```\n\n## Requirements\n\npython >= 3.5',
    'author': 'Justin Vrana',
    'author_email': 'justin.vrana@gmail.com',
    'url': 'https://github.com/jvrana/primer3-py-plus',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
