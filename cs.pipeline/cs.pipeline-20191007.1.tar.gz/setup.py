#!/usr/bin/env python
from setuptools import setup
setup(
  name = 'cs.pipeline',
  description = 'Function pipelines mediated by queues and a Later.',
  author = 'Cameron Simpson',
  author_email = 'cs@cskk.id.au',
  version = '20191007.1',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Development Status :: 4 - Beta', 'Intended Audience :: Developers', 'Operating System :: OS Independent', 'Topic :: Software Development :: Libraries :: Python Modules', 'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'],
  include_package_data = True,
  install_requires = ['cs.later', 'cs.logutils', 'cs.py.func', 'cs.queues', 'cs.resources', 'cs.seq', 'cs.threads'],
  keywords = ['python2', 'python3'],
  license = 'GNU General Public License v3 or later (GPLv3+)',
  long_description = "*Latest release 20191007.1*:\nPipeline functionality extracted from cs.later: asynchronous pipelines mediated with a cs.later.Later.\n\nFunction pipelines mediated by queues and a Later.\n\n## Class `Pipeline`\n\nMRO: `cs.resources.MultiOpenMixin`  \nA Pipeline encapsulates the chain of PushQueues created by\na call to Later.pipeline.\n\n### Method `Pipeline.__init__(self, name, L, actions, outQ)`\n\nInitialise the Pipeline from `name`, Later instance `L`,\nlist of filter functions `actions` and output queue `outQ`.\n\nEach action is either a 2-tuple of (sig, functor) or an\nobject with a .sig attribute and a .functor method returning\na callable.\n\n## Function `pipeline(later, actions, inputs=None, outQ=None, name=None)`\n\nConstruct a function pipeline to be mediated by this Later queue.\nReturn: `input, output`\nwhere `input`` is a closeable queue on which more data items can be put\nand `output` is an iterable from which result can be collected.\n\nParameters:\n* `actions`: an iterable of filter functions accepting\n  single items from the iterable `inputs`, returning an\n  iterable output.\n* `inputs`: the initial iterable inputs; this may be None.\n  If missing or None, it is expected that the caller will\n  be supplying input items via `input.put()`.\n* `outQ`: the optional output queue; if None, an IterableQueue() will be\n  allocated.\n* `name`: name for the PushQueue implementing this pipeline.\n\nIf `inputs` is None or `open` is true, the returned `input` requires\na call to `input.close()` when no further inputs are to be supplied.\n\nExample use with presupplied Later `L`:\n\n    input, output = L.pipeline(\n            [\n              ls,\n              filter_ls,\n              ( FUNC_MANY_TO_MANY, lambda items: sorted(list(items)) ),\n            ],\n            ('.', '..', '../..'),\n           )\n    for item in output:\n      print(item)\n\n\n\n# Release Log\n\n*Release 20191007.1*:\nPipeline functionality extracted from cs.later: asynchronous pipelines mediated with a cs.later.Later.",
  long_description_content_type = 'text/markdown',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.pipeline'],
)
