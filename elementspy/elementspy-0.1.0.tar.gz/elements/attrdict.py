import collections
import contextlib
import os

import numpy as np
import ruamel.yaml as yaml


class AttrDict(collections.OrderedDict):
  """Wrap a dictionary to access keys as attributes."""

  _yaml = None

  def __init__(self, *args, **kwargs):
    super().__setattr__('_unlocked', True)
    super().__init__(*args, **kwargs)
    super().__setattr__('_unlocked', not (args or kwargs))

  def __getattr__(self, name):
    try:
      return self[name]
    except KeyError:
      raise AttributeError(name)

  def __setattr__(self, name, value):
    self[name] = value

  def __setitem__(self, name, value):
    if name.startswith('_'):
      message = 'Cannot set private key {}'
      raise AttributeError(message.format(name))
    if not self._unlocked:
      message = 'Use `with obj.unlocked():` to update key {}'
      raise RuntimeError(message.format(name))
    if name in self and not isinstance(value, type(self[name])):
      if callable(value):
        pass
      else:
        try:
          value = type(self[name])(value)
        except ValueError:
          message = 'Type {} for key {} cannot be converted to {}'
          message = message.format(type(value), name, type(self[name]))
          raise TypeError(message.format())
    if isinstance(value, AttrDict):
      value = value.copy()
    super().__setitem__(name, value)

  def __repr__(self):
    items = []
    for key, value in self.items():
      items.append('{}: {}'.format(key, self._format_value(value)))
    return '{' + ', '.join(items) + '}'

  @property
  @contextlib.contextmanager
  def unlocked(self):
    self._unlock()
    yield
    self._lock()

  def update(self, mapping):
    if not self._unlocked:
      message = 'Use obj._unlock() before updating'
      raise RuntimeError(message)
    super().update(mapping)
    return self

  def copy(self):
    obj = AttrDict(super().copy())
    with obj.unlocked:
      for key, value in obj.items():
        if isinstance(value, AttrDict):
          obj[key] = value.copy()
    object.__setattr__(obj, '_unlocked', self._unlocked)
    return obj

  def save(self, filename):
    assert str(filename).endswith('.yaml')
    self._ensure_yaml_instance()
    directory = os.path.dirname(str(filename))
    os.makedirs(directory, exist_ok=True)
    with open(filename, 'w') as f:
      self._yaml.dump(collections.OrderedDict(self), f)

  @classmethod
  def load(cls, filename):
    assert str(filename).endswith('.yaml')
    cls._ensure_yaml_instance()
    with open(filename, 'r') as f:
      return AttrDict(cls._yaml.load(f))

  def summarize(self):
    items = []
    for key, value in self.items():
      items.append('{}: {}'.format(key, self._format_value(value)))
    return '\n'.join(items)

  def _lock(self):
    super().__setattr__('_unlocked', False)
    for value in self.values():
      if isinstance(value, AttrDict):
        value._lock()

  def _unlock(self):
    super().__setattr__('_unlocked', True)
    for value in self.values():
      if isinstance(value, AttrDict):
        value._unlock()

  def _format_value(self, value):
    if isinstance(value, np.ndarray):
      template = '<np.array shape={} dtype={} min={} mean={} max={}>'
      min_ = self._format_value(value.min())
      mean = self._format_value(value.mean())
      max_ = self._format_value(value.max())
      return template.format(value.shape, value.dtype, min_, mean, max_)
    if isinstance(value, float) and 1e-3 < abs(value) < 1e6:
      return '{:.3f}'.format(value)
    if isinstance(value, float):
      return '{:4.1e}'.format(value)
    if hasattr(value, '__name__'):
      return value.__name__
    return str(value)

  @classmethod
  def _ensure_yaml_instance(cls):
    if cls._yaml is not None:
      return
    cls._yaml = yaml.YAML(typ='unsafe')
    cls._yaml.default_flow_style = False
    cls._yaml.representer.add_representer(
        collections.OrderedDict,
        lambda dumper, data: dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items()))
    cls._yaml.constructor.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        lambda loader, node: collections.OrderedDict(
            loader.construct_pairs(node)))
