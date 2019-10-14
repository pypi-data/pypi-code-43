import contextlib
import importlib
import os
import pathlib
import re

from elements import attrdict
from elements import tools


NAME_SUBSTITUTIONS = {
    r'^np\.': 'numpy.',
    r'^tf\.': 'tensorflow.',
    r'^tfp\.': 'tensorflow_probability.',
    r'^tfd\.': 'tensorflow_probability.distributions.',
}


class Config(attrdict.AttrDict):

  def __init__(self, *args, **kwargs):
    flags = kwargs.pop('flags', {})
    # Parse override flags into a mapping from key to list of values.
    if isinstance(flags, (list, tuple)):
      assert not flags or flags[0].startswith('--'), flags
      parsed = []
      for flag in flags:
        if flag.startswith('--'):
          parsed.append((flag[2:].replace('-', '_'), []))
        else:
          parsed[-1][1].append(flag)
      flags = {key: values for key, values in parsed}
    elif isinstance(flags, dict):
      for key, value in flags.items():
        assert isinstance(value, (list, tuple)), type(value)
    else:
      message = 'Flags must be list of strings or parsed dictionary.'
      raise TypeError(message)
    assert isinstance(flags, dict), type(flags)
    object.__setattr__(self, '_flags', flags)
    object.__setattr__(self, '_resolved', set())
    object.__setattr__(self, '_finalized', False)
    object.__setattr__(self, '_parent', None)  # Needed to resolve references.
    super().__init__(*args, **kwargs)
    object.__setattr__(self, '_unlocked', True)

  def __setitem__(self, name, value):
    # Skip assignment if we already resolved an override for this name.
    if name in self._resolved:
      return
    super().__setitem__(name, value)
    self._resolve_overrides()
    value = self[name]
    if isinstance(value, Config):
      # Hand relevant flags to the sub config and ask it to resolve them.
      flags = {}
      prefix = name + '.'
      for key, values in list(self._flags.items()):
        if key.startswith(prefix):
          flags[key[len(prefix):]] = self._flags.pop(key)
          self._resolved.add(key)
      object.__setattr__(value, '_parent', self)
      value._flags.update(flags)
      value._resolve_overrides()

  def copy(self):
    obj = Config(super().copy())
    object.__setattr__(obj, '_flags', self._flags)
    # TODO: Copying this makes a test case fail.
    # object.__setattr__(obj, '_resolved', self._resolved)
    object.__setattr__(obj, '_finalized', self._finalized)
    object.__setattr__(obj, '_parent', self._parent)
    return obj

  def finalize(self):
    object.__setattr__(self, '_finalized', True)
    if self._flags:
      message = 'Names {} targeted by override flags do not exist'
      names = ', '.join(list(self._flags.keys()))
      raise KeyError(message.format(names))
    for child in self.values():
      if isinstance(child, Config):
        child.finalize()
    self._lock()
    return attrdict.AttrDict(self)

  @property
  @contextlib.contextmanager
  def unlocked(self):
    # We forbid modification after finalization because it could be surprising
    # to the user that modifications are ignored in the presence of any
    # overrides.
    if self._finalized:
      message = 'Config is immutable after being finalized.'
      raise RuntimeError(message)
    with super().unlocked:
      yield

  def _resolve_overrides(self):
    for name, values in list(self._flags.items()):
      # Overrides for which we haven't seen the default cannot be resolved yet.
      if name not in self:
        continue
      values = self._flags.pop(name)
      try:
        ctor = self._find_parser(self[name], values)
        value = ctor(*values)
        self[name] = value
        self._resolved.add(name)
      except Exception as e:
        message = 'Failed to parse override for name {}'.format(name)
        raise ValueError(message) from e

  def _find_parser(self, default, values):
    if default is None:
      return lambda x: x
    if isinstance(values[0], str) and values[0].startswith('&'):
      return self._parse_reference
    if isinstance(default, bool):
      return lambda x: bool(['False', 'True'].index(x))
    if isinstance(default, int):
      # Parse ints as floats first to allow scientific notation.
      return lambda x: int(float(x))
    if isinstance(default, (list, tuple)):
      elem_example = default[0] if default else None
      return lambda *xs: type(default)(
          self._find_parser(elem_example, [x])(x) for x in xs)
    if isinstance(default, pathlib.Path):
      return lambda x: pathlib.Path(x).expanduser()
    if callable(default):
      return self._parse_symbol
    return type(default)

  def _parse_reference(self, value):
    if not value.startswith('&'):
      message = 'Override sub configs with references as in --foo.baz &foo.bar'
      raise ValueError(message)
    parts = value[1:].split('.')
    target = self
    while target._parent:
      target = target._parent
    for part in parts:
      if part not in target:
        raise KeyError('Referenced key {} does not exist'.format(value[1:]))
      target = target[part]
    return target

  def _parse_symbol(self, value):
    for pattern, replacement in NAME_SUBSTITUTIONS.items():
      value = re.sub(pattern, replacement, value)
    parts = value.split('.')
    try:
      for index in range(1, len(parts)):
        try:
          module = '.'.join(parts[:index])
          locals()[module] = importlib.import_module(module)
        except ImportError:
          pass
      symbol = eval(value)
    except NameError:  # Try to prepend project value.
      project = os.path.basename(tools.project_directory())
      if not value.startswith(project):
        return self._parse_symbol('{}.{}'.format(project, value))
      else:
        raise
    assert callable(symbol)
    return symbol
