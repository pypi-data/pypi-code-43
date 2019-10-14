import functools
import pathlib
import pickle


class DiskCache:

  def __init__(self, filename, *args, **kwargs):
    self._filename = pathlib.Path(filename)
    assert self._filename.suffix == '.pickle'
    self._args = args
    self._kwargs = kwargs
    self._cache = kwargs.pop('cache', {})
    self._autosave = kwargs.pop('autosave', True)
    self._overwrite = kwargs.pop('overwrite', False)
    self._filename.parent.mkdir(parents=True, exist_ok=True)
    if self._filename.exists() and not self._overwrite:
      with self._filename.open('rb') as f:
        self._cache.update(pickle.load(f))

  def __call__(self, function):
    body = functools.partial(self._body, function)
    body = functools.wraps(function)(body)
    body.save = self.save
    return body

  def _body(self, function, *args, **kwargs):
    key = str((args, tuple(sorted(kwargs.items(), key=lambda x: x[0]))))
    if key in self._cache:
      return self._cache[key]
    result = function(*(self._args + args), **{**self._kwargs, **kwargs})
    self._cache[key] = result
    if self._autosave:
      self.save()
    return result

  def save(self):
    with self._filename.open('wb') as f:
      pickle.dump(dict(self._cache), f, pickle.HIGHEST_PROTOCOL)
