import torch
from functools import partial
from .utils import listify, compose

def maybe_update(os, dest, f):
    "updates defaults only if not already specified"
    for o in os:
        for k,v in f(o).items():
            if k not in dest: dest[k] = v

def get_defaults(d): return getattr(d, '_defaults', {})

class Optimizer():
    """
    params is assumed to be a list of lists for discriminative learning rates.
    hypers are hyperparams for each param group (each list in the list of lists)
    """
    def __init__(self, params, steppers, **defaults):
        self.steppers = listify(steppers)
        maybe_update(self.steppers, defaults, get_defaults)

        # might be a generator
        self.param_groups = list(params)

        # ensure params is a list of lists
        if not isinstance(self.param_groups[0], list):
            self.param_groups = [self.param_groups]

        # one dict of hyperparams for each param group (clones provided **defaults)
        self.hypers = [{**defaults} for p in self.param_groups]

    def grad_params(self):
        return [(p, hyper) for pg, hyper in zip(self.param_groups, self.hypers)
                           for p in pg if p.grad is not None]

    def zero_grad(self):
        for p, hyper in self.grad_params():
            p.grad.detach_()
            p.grad.zero_()

    def step(self):
        for p, hyper in self.grad_params():
            compose(p, self.steppers, **hyper)

def sgd_step(p, lr, **kwargs):
    "example stepper for use with Optimizer"
    p.data.add_(-lr, p.grad.data)
    return p
# sgd_step._defaults = dict(lr=1e-1)

def weight_decay(p, lr, wd, **kwargs):
    "update with gradient of L2 regularizer with parameter weight decay wd"
    p.data.mul_(1 - lr*wd)
    return p
weight_decay._defaults = dict(wd=0.)

# alternatively
# def l2_reg(p, lr, wd, **kwargs):
    # p.grad.data.add_(wd, p.data)
    # return p
# l2_reg._defaults = dict(wd=0.)

# SGD optimizer with weight decay
sgd_opt = partial(Optimizer, steppers=[weight_decay, sgd_step])

# To inspect the hyperparams of the optimizer:
# opt = sgd_opt(learn.model.parameters(), lr=1e-1, wd=1e-4)
# print(opt.hypers)

class StatefulOptimizer(Optimizer):
    "optimizer with state for momentum. we assemble the relevant state with stats"
    def __init__(self, params, steppers, stats=None, **defaults):
        self.stats = listify(stats)
        maybe_update(self.stats, defaults, get_defaults)
        super().__init__(params, steppers, **defaults)
        self.state = {}

    def step(self):
        for p, hyper in self.grad_params():
            if p not in self.state:
                #Create a state for p and call all the statistics to initialize it.
                self.state[p] = {}
                maybe_update(self.stats, self.state[p], lambda o: o.init_state(p))
            state = self.state[p]
            for stat in self.stats:
                state = stat.update(p, state, **hyper)
            compose(p, self.steppers, **state, **hyper)
            self.state[p] = state

class Stat():
    "base class used to assemble state for StatefulOptimizer"
    _defaults = {}
    def init_state(self, p): raise NotImplementedError
    def update(self, p, state, **kwargs): raise NotImplementedError

class AverageGrad(Stat):
    "assembles state for momentum"
    _defaults = dict(mom=0.9)

    def __init__(self, dampening=False):
        self.dampening = dampening

    def init_state(self, p):
        return {'grad_avg': torch.zeros_like(p.grad.data)}

    def update(self, p, state, mom, **kwargs):
        state['mom_damp'] = 1-mom if self.dampening else 1.
        # the update below is just the definition of momentum
        state['grad_avg'].mul_(mom).add_(state['mom_damp'],
                                         p.grad.data)
        return state

def momentum_step(p, lr, grad_avg, **kwargs):
    p.data.add_(-lr, grad_avg)
    return p

sgd_mom_opt = partial(StatefulOptimizer,
                      steppers=[momentum_step, weight_decay],
                      stats=AverageGrad(), wd=1e-2)

class AverageSqrGrad(Stat):
    _defaults = dict(sqr_mom=0.99)

    def __init__(self, dampening=True):
        self.dampening=dampening

    def init_state(self, p):
        return {'sqr_avg': torch.zeros_like(p.grad.data)}

    def update(self, p, state, sqr_mom, **kwargs):
        state['sqr_damp'] = 1-sqr_mom if self.dampening else 1.
        state['sqr_avg'].mul_(sqr_mom).addcmul_(state['sqr_damp'],
                                                p.grad.data,
                                                p.grad.data)
        return state

class StepCount(Stat):
    def init_state(self, p):
        return {'step': 0}

    def update(self, p, state, **kwargs):
        state['step'] += 1
        return state

def debias(mom, damp, step):
    return damp * (1 - mom**step) / (1-mom)

def adam_step(p, lr, mom, mom_damp, step, sqr_mom, sqr_damp,
              grad_avg, sqr_avg, eps, **kwargs):
    debias1 = debias(mom,     mom_damp, step)
    debias2 = debias(sqr_mom, sqr_damp, step)
    p.data.addcdiv_(-lr / debias1, grad_avg, (sqr_avg/debias2).sqrt() + eps)
    return p
adam_step._defaults = dict(eps=1e-5)

def adam_opt(xtra_step=None, **kwargs):
    return partial(StatefulOptimizer,
                   steppers=[adam_step,weight_decay]+listify(xtra_step),
                   stats=[AverageGrad(dampening=True), AverageSqrGrad(), StepCount()],
                   **kwargs)

