from torch import nn
# from torch.nn import init
from functools import partial
from .data_block import ListContainer

def children(m): return list(m.children())

def find_modules(m, cond):
    if cond(m): return [m]
    return sum([find_modules(o,cond) for o in m.children()], [])

def is_lin_layer(l):
    lin_layers = (nn.Conv1d, nn.Conv2d, nn.Conv3d, nn.Linear)
    return isinstance(l, lin_layers)

def get_batch(dl, learn):
    learn.xb, learn.yb = next(iter(dl))
    learn.do_begin_fit(0)
    learn('begin_batch')
    learn('after_fit')
    return learn.xb, learn.yb

def model_summary(learn, data, find_all=False, print_mod=True):
    xb, yb = get_batch(data.valid_dl, learn)
    mods = find_modules(learn.model, is_lin_layer) if find_all else learn.model.children()
    f = lambda hook,mod,inp,out: print(f"====\n{mod}\n" if print_mod else "", out.shape)
    with Hooks(mods, f) as hooks:
        learn.model(xb)

def append_stat(hook, mod, inp, outp):
    d = outp.data
    hook.mean,hook.std = d.mean().item(),d.std().item()

def lsuv_module(m, xb):
    """ Usage:
    mods = find_modules(learn.model, is_lin_layer)
    for m in mods: print(lsuv_module(m, xb))"""
    h = Hook(m, append_stat)
    if getattr(m, 'bias', None) is not None:
        while mdl(xb) is not None and abs(h.mean) > 1e-3:
            m.bias.data -= h.mean
    while mdl(xb) is not None and abs(h.std-1) > 1e-3:
        m.weight.data /= h.std
    h.remove()
    return h.mean, h.std


class Hook():
    def __init__(self, m, f): self.hook = m.register_forward_hook(partial(f, self))
    def remove(self): self.hook.remove()
    def __del__(self): self.remove()

def append_stats(hook, mod, inp, outp):
    if not hasattr(hook,'stats'): hook.stats = ([],[])
    means,stds = hook.stats
    if mod.training:
        means.append(outp.data.mean())
        stds .append(outp.data.std())

class Hooks(ListContainer):
    def __init__(self, ms, f):
        super().__init__([Hook(m, f) for m in ms])

    def __enter__(self, *args):
        return self

    def __exit__ (self, *args):
        self.remove()

    def __del__(self):
        self.remove()

    def __delitem__(self, i):
        self[i].remove()
        super().__delitem__(i)

    def remove(self):
        for h in self:
            h.remove()

