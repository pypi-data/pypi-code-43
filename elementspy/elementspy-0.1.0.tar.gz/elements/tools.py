import datetime
import inspect
import pathlib
import shutil


def timestamp():
  return datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')


def project_directory():
  # Alternative implementation that only works with module execution.
  # import __main__
  # package = __main__.__spec__.name.split('.')[0]
  # return os.path.dirname(__import__(package).__file__)
  for frame in reversed(inspect.stack()):
    filename = frame.filename
    if not filename.endswith('.py'):
      continue
    if filename.startswith('/usr/'):
      continue
    if filename.endswith('/runpy.py'):
      continue
    break
  directory = pathlib.Path(filename).parent.resolve()
  while (directory.parent / '__init__.py').exists():
    directory = directory.parent
  return directory


def snapshot_project(filename):
  directory = project_directory()
  basename, ext = str(filename).split('.', 1)
  try:
    format_ = {'zip': 'zip', 'tar': 'tar', 'tar.gz': 'gztar'}[ext]
  except KeyError:
    raise TypeError(ext)
  shutil.make_archive(basename, format_, directory)


class Reuse:

  def __init__(self, lst):
    self._lst = lst
    self._adding = not bool(lst)
    self._index = 0

  def __call__(self, item):
    if self._adding:
      self._lst.append(item)
      return item
    other = self._lst[self._index]
    self._index += 1
    assert isinstance(other, type(item))
    return other
