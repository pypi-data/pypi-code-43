#!/usr/bin/env python
from setuptools import setup
setup(
  name = 'cs.deco',
  description = 'Assorted decorator functions.',
  author = 'Cameron Simpson',
  author_email = 'cs@cskk.id.au',
  version = '20191006',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Development Status :: 4 - Beta', 'Intended Audience :: Developers', 'Operating System :: OS Independent', 'Topic :: Software Development :: Libraries :: Python Modules', 'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'],
  include_package_data = True,
  install_requires = [],
  keywords = ['python2', 'python3'],
  license = 'GNU General Public License v3 or later (GPLv3+)',
  long_description = '*Latest release 20191006*:\nRename @cached to @cachedmethod, leave compatible @cached behind which issues a warning (will be removed in a future release).\n\nAssorted decorator functions.\n\n## Function `cached(*a, **kw)`\n\nCompatibility wrapper for `@cachedmethod`, issuing a warning.\n\n## Function `cachedmethod(*da, **dkw)`\n\nDecorator to cache the result of a method and keep a revision\ncounter for changes.\n\nThe cached values are stored on the instance (`self`).\nThe revision counter supports the `@revised` decorator.\n\nThis decorator may be used in 2 modes.\nDirectly:\n\n    @cachedmethod\n    def method(self, ...)\n\nor indirectly:\n\n    @cachedmethod(poll_delay=0.25)\n    def method(self, ...)\n\nOptional keyword arguments:\n* `attr_name`: the basis name for the supporting attributes.\n  Default: the name of the method.\n* `poll_delay`: minimum time between polls; after the first\n  access, subsequent accesses before the `poll_delay` has elapsed\n  will return the cached value.\n  Default: `None`, meaning no poll delay.\n* `sig_func`: a signature function, which should be significantly\n  cheaper than the method. If the signature is unchanged, the\n  cached value will be returned. The signature function\n  expects the instance (`self`) as its first parameter.\n  Default: `None`, meaning no signature function;\n  the first computed value will be kept and never updated.\n* `unset_value`: the value to return before the method has been\n  called successfully.\n  Default: `None`.\n\nIf the method raises an exception, this will be logged and\nthe method will return the previously cached value,\nunless there is not yet a cached value\nin which case the exception will be reraised.\n\nIf the signature function raises an exception\nthen a log message is issued and the signature is considered unchanged.\n\nAn example use of this decorator might be to keep a "live"\nconfiguration data structure, parsed from a configuration\nfile which might be modified after the program starts. One\nmight provide a signature function which called `os.stat()` on\nthe file to check for changes before invoking a full read and\nparse of the file.\n\n*Note*: use of this decorator requires the `cs.pfx` module.\n\n## Function `decorator(deco)`\n\nWrapper for decorator functions to support optional arguments.\n\nThe actual decorator function ends up being called as:\n\n    mydeco(func, *da, **dkw)\n\nallowing `da` and `dkw` to affect the behaviour of the decorator `mydeco`.\n\nExamples:\n\n    @decorator\n    def mydeco(func, *da, kw=None):\n      ... decorate func subject to the values of da and kw\n\n    @mydeco\n    def func1(...):\n      ...\n\n    @mydeco(\'foo\', arg2=\'bah\')\n    def func2(...):\n      ...\n\n## Function `fmtdoc(func)`\n\nDecorator to replace a function\'s docstring with that string\nformatted against the function\'s module `__dict__`.\n\nThis supports simple formatted docstrings:\n\n    ENVVAR_NAME = \'FUNC_DEFAULT\'\n\n    @fmtdoc\n    def func():\n        """Do something with os.environ[{ENVVAR_NAME}]."""\n        print(os.environ[ENVVAR_NAME])\n\nThis gives `func` this docstring:\n\n    Do something with os.environ[FUNC_DEFAULT].\n\n*Warning*: this decorator is intended for wiring "constants"\ninto docstrings, not for dynamic values. Use for other types\nof values should be considered with trepidation.\n\n## Function `observable_class(property_names, only_unequal=False)`\n\nClass decorator to make various instance attributes observable.\n\nParameters:\n* `property_names`:\n  an interable of instance property names to set up as\n  observable properties. As a special case a single `str` can\n  be supplied if only one attribute is to be observed.\n* `only_unequal`:\n  only call the observers if the new property value is not\n  equal to the previous proerty value. This requires property\n  values to be comparable for inequality.\n  Default: `False`, meaning that all updates will be reported.\n\n## Function `strable(*da, **dkw)`\n\nDecorator for functions which may accept a `str`\ninstead of their core type.\n\nParameters:\n* `func`: the function to decorate\n* `open_func`: the "open" factory to produce the core type\n  if a string is provided;\n  the default is the builtin "open" function\n\nThe usual (and default) example is a function to process an\nopen file, designed to be handed a file object but which may\nbe called with a filename. If the first argument is a `str`\nthen that file is opened and the function called with the\nopen file.\n\nExamples:\n\n    @strable\n    def count_lines(f):\n      return len(line for line in f)\n\n    class Recording:\n      "Class representing a video recording."\n      ...\n    @strable(open_func=Recording)\n    def process_video(r):\n      ... do stuff with `r` as a Recording instance ...\n\n*Note*: use of this decorator requires the `cs.pfx` module.\n\n\n\n# Release Log\n\n*Release 20191006*:\nRename @cached to @cachedmethod, leave compatible @cached behind which issues a warning (will be removed in a future release).\n\n*Release 20191004*:\nAvoid circular import with cs.pfx by removing requirement and doing the import later if needed.\n\n*Release 20190905*:\nBugfix @deco: it turns out that you may not set the .__module__ attribute on a property object.\n\n*Release 20190830.2*:\nMake some getattr calls robust.\n\n*Release 20190830.1*:\n@decorator: set the __module__ of the wrapper.\n\n*Release 20190830*:\n@decorator: set the __module__ of the wrapper from the decorated target, aids cs.distinf.\n\n*Release 20190729*:\n@cached: sidestep uninitialised value.\n\n*Release 20190601.1*:\n@strable: fix the example in the docstring.\n\n*Release 20190601*:\nBugfix @decorator to correctly propagate the docstring of the subdecorator.\nImprove other docstrings.\n\n*Release 20190526*:\n@decorator: add support for positional arguments and rewrite - simpler and clearer.\n\n*Release 20190512*:\n@fmtdoc: add caveat against misuse of this decorator.\n\n*Release 20190404*:\nNew @fmtdoc decorator to format a function\'s doctsring against its module\'s globals.\n\n*Release 20190403*:\n@cached: bugfix: avoid using unset sig_func value on first pass.\n@observable_class: further tweaks.\n\n*Release 20190322.1*:\n@observable_class: bugfix __init__ wrapper function.\n\n*Release 20190322*:\nNew class decorator @observable_class.\nBugfix import of "warning".\n\n*Release 20190309*:\n@cached: improve the exception handling.\n\n*Release 20190307.2*:\nFix docstring typo.\n\n*Release 20190307.1*:\nBugfix @decorator: final plumbing step for decorated decorator.\n\n*Release 20190307*:\n@decorator: drop unused arguments, they get used by the returned decorator.\nRework the @cached logic.\n\n*Release 20190220*:\nBugfix @decorator decorator, do not decorate twice.\nHave a cut at inheriting the decorated function\'s docstring.\n\n*Release 20181227*:\nNew decoartor @strable for function which may accept a str instead of their primary type.\nImprovements to @cached.\n\n*Release 20171231*:\nInitial PyPI release.',
  long_description_content_type = 'text/markdown',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.deco'],
)
