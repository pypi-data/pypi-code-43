#!/usr/bin/env python
from setuptools import setup
setup(
  name = 'cs.queues',
  description = 'some Queue subclasses and ducktypes',
  author = 'Cameron Simpson',
  author_email = 'cs@cskk.id.au',
  version = '20191007',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Development Status :: 4 - Beta', 'Intended Audience :: Developers', 'Operating System :: OS Independent', 'Topic :: Software Development :: Libraries :: Python Modules', 'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'],
  include_package_data = True,
  install_requires = ['cs.logutils', 'cs.pfx', 'cs.py3', 'cs.resources', 'cs.seq'],
  keywords = ['python2', 'python3'],
  license = 'GNU General Public License v3 or later (GPLv3+)',
  long_description = '*Latest release 20191007*:\nPushQueue: improve __str__.\nClean lint, drop cs.obj dependency.\n\nQueue-like items: iterable queues and channels.\n\n## Class `Channel`\n\nA zero-storage data passage.\nUnlike a Queue(1), put() blocks waiting for the matching get().\n\n## Function `IterablePriorityQueue(*args, capacity=0, name=None, **kw)`\n\nFactory to create an iterable PriorityQueue.\n\n## Function `IterableQueue(*args, capacity=0, name=None, **kw)`\n\nFactory to create an iterable Queue.\n\n## Class `NullQueue`\n\nMRO: `cs.resources.MultiOpenMixin`  \nA queue-like object that discards its inputs.\nCalls to .get() raise Queue_Empty.\n\n### Method `NullQueue.__init__(self, blocking=False, name=None)`\n\nInitialise the NullQueue.\n\nParameters:\n* `blocking`: if true, calls to .get() block until .shutdown().\n  Default: False.\n* `name`: a name for this NullQueue.\n\n## Class `PushQueue`\n\nMRO: `cs.resources.MultiOpenMixin`  \nA puttable object which looks like an iterable Queue.\n\nCalling .put(item) calls `func_push` supplied at initialisation\nto trigger a function on data arrival, whose processing is mediated\nqueued via a Later for delivery to the output queue.\n\n### Method `PushQueue.__init__(self, name, functor, outQ)`\n\nInitialise the PushQueue with the Later `L`, the callable `functor`\nand the output queue `outQ`.\n\nParameters:\n* `functor` is a one-to-many function which accepts a single\n  item of input and returns an iterable of outputs; it may be a\n  generator. These outputs are passed to outQ.put individually as\n  received.\n* `outQ` is a MultiOpenMixin which accepts via its .put() method.\n\n## Class `TimerQueue`\n\nClass to run a lot of "in the future" jobs without using a bazillion\nTimer threads.\n\n\n\n# Release Log\n\n*Release 20191007*:\nPushQueue: improve __str__.\nClean lint, drop cs.obj dependency.\n\n*Release 20190812*:\n_QueueIterator: do MultiOpenMixin.__init__ so that __str__ is functional.\n\n*Release 20181022*:\nBugfix Channel, drasticly simplify PushQueue, other minor changes.\n\n*Release 20160828*:\nUse "install_requires" instead of "requires" in DISTINFO.\nTimerQueue.add: support optional *a and **kw arguments for func.\nMany bugfixes and internal changes.\n\n*Release 20150115*:\nMore PyPI metadata fixups.\n\n*Release 20150111*:\nInitial PyPI release.',
  long_description_content_type = 'text/markdown',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.queues'],
)
