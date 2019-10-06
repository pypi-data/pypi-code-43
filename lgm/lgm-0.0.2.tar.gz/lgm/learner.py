import torch
from functools import partial
from torch import tensor
from .optimizer import adam_opt
from .utils import ALL_CBS, param_getter, listify, CancelTrainException, CancelEpochException, CancelBatchException
from .callbacks import TrainEvalCallback, ProgressCallback, Recorder, CudaCallback, AvgStatsCallback, SaveModelCallback

class Learner():
    """
    Main train-eval class that packages together a model, the data,
    the loss function and the optimizer.
    In addition, it keeps track of a learning rate and a splitter function that
    can split the model layers into mutiple groups so that they can be trained
    with different learning rates.
    Default splitter does nothing, but this is where splitter functions for
    discriminative learning rates should be passed.
    Finally, the learner is passed a list of callbacks and can be called (like
    a function) with attrs inherited from the callbacks.
    Callbacks added by default: TrainEvalCallback, ProgressCallback, Recorder,
    CudaCallback (if cuda available), AvgStatsCallback for loss_func (other
    metrics can be added).
    """
    def __init__(self, model, data, loss_func, opt_func=adam_opt(), lr=1e-2,
                 splitter=param_getter, metrics=None, cbs=None, cb_funcs=None,
                 model_name=None, path_str=None):
        self.model = model
        self.data = data
        self.loss_func = loss_func
        self.opt_func = opt_func
        self.lr = lr
        self.splitter = splitter
        self.metrics = metrics
        self.in_train = False
        self.logger = print
        self.opt = None
        self.ALL_CBS = ALL_CBS # inventory of all possible callback functions

        self.cbs = []
        self.add_cb(ProgressCallback())
        self.add_cb(TrainEvalCallback())
        self.add_cb(Recorder())
        if torch.cuda.is_available():
            self.add_cb(CudaCallback())
        self.add_cb(partial(AvgStatsCallback, listify(self.metrics))())
        if model_name and isinstance(model_name, str):
            self.add_cb(SaveModelCallback(model_name=model_name, path_str=path_str))
        self.add_cbs(cbs)
        self.add_cbs(cbf() for cbf in listify(cb_funcs))

    def add_cbs(self, cbs):
        for cb in listify(cbs): self.add_cb(cb)

    def add_cb(self, cb):
        "grab callback and set it as an attr under its name"
        cb.set_runner(self)
        setattr(self, cb.name, cb)
        self.cbs.append(cb)

    def remove_cbs(self, cbs):
        for cb in listify(cbs): self.cbs.remove(cb)

    def one_batch(self, i, xb, yb):
        try:
            self.iter = i
            self.xb, self.yb = xb, yb;                      self('begin_batch')
            self.pred = self.model(self.xb);                self('after_pred')
            self.loss = self.loss_func(self.pred, self.yb); self('after_loss')
            if not self.in_train: return
            self.loss.backward();                           self('after_backward')
            self.opt.step();                                self('after_step')
            self.opt.zero_grad()
        except CancelBatchException:                        self('after_cancel_batch')
        finally:                                            self('after_batch')

    def all_batches(self):
        self.iters = len(self.dl)
        try:
            for i, (xb, yb) in enumerate(self.dl):
                self.one_batch(i, xb, yb)
        except CancelEpochException: self('after_cancel_epoch')

    def do_begin_fit(self, epochs):
        self.epochs = epochs
        self.loss = tensor(0.)
        self('begin_fit')

    def do_begin_epoch(self, epoch):
        self.epoch = epoch
        self.dl = self.data.train_dl
        return self('begin_epoch')

    def fit(self, epochs, cbs=None, reset_opt=False):
        # pass callbacks to fit() and have them removed when done
        self.add_cbs(cbs)
        # create optimizer on fit(), optionally replacing existing
        if reset_opt or not self.opt:
            self.opt = self.opt_func(self.splitter(self.model), lr=self.lr)

        try:
            self.do_begin_fit(epochs)
            for epoch in range(epochs):
                self.do_begin_epoch(epoch)
                if not self('begin_epoch'): self.all_batches()

                with torch.no_grad():
                    self.dl = self.data.valid_dl
                    if not self('begin_validate'): self.all_batches()
                self('after_epoch')

        except CancelTrainException: self('after_cancel_train')
        finally:
            self('after_fit')
            self.remove_cbs(cbs)

    def __call__(self, cb_name):
        res = False
        assert cb_name in self.ALL_CBS
        for cb in sorted(self.cbs, key=lambda x: x._order):
            res = cb(cb_name) and res
        return res

