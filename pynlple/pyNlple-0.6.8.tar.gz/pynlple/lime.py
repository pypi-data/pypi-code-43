# -*- coding: utf-8 -*-
import logging

from pickle import PicklingError
from sklearn.externals.joblib import dump as joblib_dump
from sklearn.externals.joblib import load as joblib_load
from numpy.random import randint


logger = logging.getLogger(__name__)


def dump(explainer, filepath, *args, **kwargs):
    try:
        return joblib_dump(explainer, filepath, *args, **kwargs),
    except PicklingError as e:
        if 'Can\'t pickle <function' in str(e) and 'Explainer.__init__.<locals>.kernel' in str(e):
            logger.warning('Omitting explainer.base.kernel_fn due to: %s.\
                                            Returning the kernel_fn as the second argument' % (str(e),))
            kernel_fn = explainer.base.kernel_fn
            explainer.base.kernel_fn = None
            return joblib_dump(explainer, filepath, *args, **kwargs), kernel_fn
        else:
            raise e


def load(filepath, rollback_kernel_fn=None, rollback_kernel_width=None, *args, **kwargs):
    explainer = joblib_load(filepath, *args, **kwargs)
    if rollback_kernel_fn is not None:
        logger.warning('Applying the provided kernel_fn to the pickled explainer. %s' % (str(rollback_kernel_fn),))
        explainer.base.kernel_fn = rollback_kernel_fn
    elif explainer.base.kernel_fn is None:
        logger.warning('Applying the default kernel_fn to the pickled explainer. Kernel width: %s' % (str(rollback_kernel_width),))
        if hasattr(explainer, 'scaler'):
            stub_data = randint(0, 1, (3, explainer.scaler.mean_.shape[0]))
            if rollback_kernel_width:
                stub_explainer = explainer.__class__(stub_data, kernel_width=rollback_kernel_width)
            else:
                stub_explainer = explainer.__class__(stub_data)
        else:
            if rollback_kernel_width:
                stub_explainer = explainer.__class__(kernel_width=rollback_kernel_width)
            else:
                stub_explainer = explainer.__class__()

        explainer.base.kernel_fn = stub_explainer.base.kernel_fn
    return explainer