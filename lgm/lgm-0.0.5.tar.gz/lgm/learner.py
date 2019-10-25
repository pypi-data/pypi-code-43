import torch
from functools import partial
from torch import tensor
from .optimizer import adam_opt
from .utils import ALL_CALLBACKS, param_getter, listify, CancelTrainException, CancelEpochException, CancelBatchException
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
                 splitter=param_getter, metrics=None, callbacks=None, callback_funcs=None,
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
        self.ALL_CALLBACKS = ALL_CALLBACKS # inventory of all possible callback functions

        self.callbacks = []
        self.add_callback(ProgressCallback())
        self.add_callback(TrainEvalCallback())
        self.add_callback(Recorder())
        if torch.cuda.is_available():
            self.add_callback(CudaCallback())
        self.add_callback(partial(AvgStatsCallback, listify(self.metrics))())
        if model_name and isinstance(model_name, str):
            self.add_callback(SaveModelCallback(model_name=model_name, path_str=path_str))
        self.add_callbacks(callbacks)
        self.add_callbacks(callback_func() for callback_func in listify(callback_funcs))

    def add_callbacks(self, callbacks):
        for callback in listify(callbacks): self.add_callback(callback)

    def add_callback(self, callback):
        "grab callback and set it as an attr under its name"
        callback.set_runner(self)
        setattr(self, callback.name, callback)
        self.callbacks.append(callback)

    def remove_callbacks(self, callbacks):
        for callback in listify(callbacks): self.callbacks.remove(callback)

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

    def fit(self, epochs, callbacks=None, reset_opt=False):
        # pass callbacks to fit() and have them removed when done
        self.add_callbacks(callbacks)
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
            self.remove_callbacks(callbacks)

    def __call__(self, callback_name):
        res = False
        assert callback_name in self.ALL_CALLBACKS
        for callback in sorted(self.callbacks, key=lambda x: x._order):
            res = callback(callback_name) and res
        return res

