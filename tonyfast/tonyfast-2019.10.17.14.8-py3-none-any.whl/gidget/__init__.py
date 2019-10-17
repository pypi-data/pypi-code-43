__all__ = 'gidget',
with __import__('importnb').Notebook(lazy=True):
  from .await_gidgethub import get as gidget 