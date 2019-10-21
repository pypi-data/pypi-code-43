from jcopdl.optim._lookahead import Lookahead
from jcopdl.optim._radam import RAdam
from jcopdl.optim._ralamb import Ralamb


def Ranger(params, lr=1e-3, betas=(0.9, 0.999), alpha=0.5, k=6, *args, **kwargs):
    """
    RAdam + Lookahead optimizer
    """
    radam = RAdam(params, lr=lr, betas=betas, *args, **kwargs)
    return Lookahead(radam, alpha, k)


def RangerLARS(params, lr=1e-3, betas=(0.9, 0.999), alpha=0.5, k=6, *args, **kwargs):
    """
    RAdam + LARS + Lookahead optimizer
    """
    ralamb = Ralamb(params, lr=lr, betas=betas, *args, **kwargs)
    return Lookahead(ralamb, alpha, k)
