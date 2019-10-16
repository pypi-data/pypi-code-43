# flake8: noqa

from .model import Model
from .labelmodel import LabelModel
from .simulator import _Simulate
from .simulator import _LabelSimulate
from . import mca


def Simulator(model, integrator="assimulo", verbosity=50):
    """Chooses the simulator class according to the model type.
    If a simulator different than assimulo is required, it can be chosen
    by the integrator argument.

    Parameters
    ----------
    model : modelbase.model
        The model instance

    Returns
    -------
    Simulate : object
        A simulate object according to the model type
    """
    if isinstance(model, LabelModel):
        return _LabelSimulate(model, integrator, verbosity)
    elif isinstance(model, Model):
        return _Simulate(model, integrator, verbosity)
    else:
        raise NotImplementedError
