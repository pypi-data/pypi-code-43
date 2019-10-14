import collections
import datetime
import glob
import pathlib
import re

from elements import attrdict


class Checkpoint(attrdict.AttrDict):

  def __init__(self, logdir):
    super().__init__()
    # These attributes are not saved since they are not part of the dict.
    object.__setattr__(self, '_logdir', pathlib.Path(logdir).expanduser())
    object.__setattr__(self, '_defaults', {})
    object.__setattr__(self, '_unlocked', True)
    try:
      self.load()
    except (IndexError, IOError):
      self.save()

  def __setitem__(self, name, value):
    if name not in self:
      message = 'Add new keys as obj.defaults.{} = value'
      raise AttributeError(message.format(name))
    super().__setitem__(name, value)

  @property
  def defaults(self):
    return DefaultsSetter(self)

  def copy(self):
    obj = Checkpoint(self._logdir)
    object.__setattr__(obj, '_defaults', self._defaults)
    for key, value in attrdict.AttrDict(self).copy().items():
      collections.OrderedDict.__setitem__(self, key, value)
    return obj

  def save(self):
    timestamp = re.sub(r'[^0-9]+', '-', datetime.datetime.utcnow().isoformat())
    filename = self._logdir / 'checkpoint-{}.yaml'.format(timestamp)
    super().save(filename)

  def load(self):
    filenames = glob.glob(str(self._logdir / 'checkpoint-*.yaml'))
    filename = sorted(filenames)[-1]
    for key, value in super().load(filename).items():
      collections.OrderedDict.__setitem__(self, key, value)

  def _set_default(self, name, value):
    if name in self._defaults:
      raise RuntimeError('Default was already set for key {}'.format(name))
    self._defaults[name] = value
    # Do not override existing value.
    if name not in self:
      collections.OrderedDict.__setitem__(self, name, value)


class DefaultsSetter:

  def __init__(self, reference):
    object.__setattr__(self, '_reference', reference)

  def __setattr__(self, name, value):
    self._reference._set_default(name, value)
