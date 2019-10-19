from copy import copy, deepcopy
import logging
log = logging.getLogger()


class dotdict(dict):
    """ dot.notation access to dictionary attributes """

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    __getattr__= dict.get

    def copy(self):
        """ dict version returns dict """
        return copy(self)

    def __getstate__(self):
        """ dict version undefined. required for pickle. note __dict__ is not used. """
        pass

    def __setstate__(self, d):
        """ dict version undefined. required for pickle. note __dict__ is not used. """
        pass

class autodict(dotdict):
    """ dotdict that automatically creates missing_params hierarchy of autodicts

    .. warning::
        This is convenient but can hide bugs so use sparingly

    .. note::
        "hasattr will create the attribute and return true. to test if key exists use "in" operator.
    """
    def __getattr__(self, k):
        """ automatically create nested dotdict if item does not exist """
        # calling super methods avoids recursion errors
        try:
            return super().__getitem__(k)
        except KeyError:
            # ipython uses this to check if methods exist. reraise as we don't want to add it as a key.
            if k == "_ipython_canary_method_should_not_exist_":
                raise
            log.warning(f"missing_params key added automatically {k}")
            super().__setitem__(k, type(self)())
            return super().__getitem__(k)

    # for obj[index] automatically create nested autodict if item does not exist
    __getitem__ = __getattr__

    def __deepcopy__(self, x):
        """ dict version undefined so causes recursion. Not sure how to implement but don't need it """
        raise NotImplementedError(self)

