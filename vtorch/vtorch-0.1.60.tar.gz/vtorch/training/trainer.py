import os
import math
import logging
from itertools import chain
from typing import Dict, Optional, List, Union, Iterable

import torch

from fastprogress import master_bar, progress_bar

from vtorch.common.utils import lazy_groups_of, set_seed
from vtorch.common.checks import ConfigurationError

from vtorch.data.instance import Instance
from vtorch.data.iterators.data_iterator import DataIterator, TensorDict

from vtorch.models.model import Model

from vtorch.nn import utils as nn_util

from vtorch.training.callbacks import Callbacks
from vtorch.training.schedulers import Scheduler
from vtorch.training import util as training_util
from vtorch.training.trainer_base import TrainerBase


logger = logging.getLogger(__name__)

try:
    from apex import amp
except ImportError:
    logger.info("Apex is not found. So you can't use fp16 training.")


@TrainerBase.register("default")
class Trainer(TrainerBase):
    def __init__(self,
                 model: Model,
                 optimizer: torch.optim.Optimizer,
                 iterator: DataIterator,
                 train_dataset: Iterable[Instance],
                 validation_dataset: Optional[Iterable[Instance]] = None,
                 patience: Optional[int] = None,
                 early_stopping_metric: str = "-loss",
                 validation_iterator: DataIterator = None,
                 shuffle: bool = True,
                 num_epochs: int = 20,
                 tb_logging_dir: str = "tb_logs",
                 serialization_dir: Optional[str] = None,
                 accumulation_steps: int = 0,
                 experiment_name: Optional[str] = None,
                 cuda_device: Union[int, List] = -1,
                 grad_norm: Optional[float] = 1.0,
                 lr_scheduler: Optional[str] = None,
                 lr_scheduler_params: Optional[Dict] = None,
                 fp16: bool = False,
                 fp16_opt_level: str = "O1",
                 gradual_unfreezing_steps: Optional[List[List[str]]] = ()) -> None:
        """
        A trainer for doing supervised learning. It just takes a labeled dataset
        and a ``DataIterator``, and uses the supplied ``Optimizer`` to learn the weights
        for your model over some fixed number of epochs. You can also pass in a validation
        dataset and enable early stopping. There are many other bells and whistles as well.

        Parameters
        ----------
        model : ``Model``, required.
            An Vtorch model to be optimized. Pytorch Modules can also be optimized if
            their ``forward`` method returns a dictionary with a "loss" key, containing a
            scalar tensor representing the loss function to be optimized.
            If you are training your model using GPUs, your model should already be
            on the correct device.
        optimizer : ``torch.nn.Optimizer``, required.
            An instance of a Pytorch Optimizer, instantiated with the parameters of the
            model to be optimized.
        iterator : ``DataIterator``, required.
            A method for iterating over a ``Dataset``, yielding padded indexed batches.
        train_dataset : ``Dataset``, required.
            A ``Dataset`` to train on. The dataset should have already been indexed.
        validation_dataset : ``Dataset``, optional, (default = None).
            A ``Dataset`` to evaluate on. The dataset should have already been indexed.
        patience : Optional[int] > 0, optional (default=None)
            Number of epochs to be patient before early stopping: the training is stopped
            after ``patience`` epochs with no improvement. If given, it must be ``> 0``.
            If None, early stopping is disabled.
        early_stopping_metric : str, optional (default=["-loss"])
            Validation metric for early stopping
        validation_iterator : ``DataIterator``, optional (default=None)
            An iterator to use for the validation set.  If ``None``, then
            use the training `iterator`.
        shuffle : ``bool``, optional (default=True)
            Whether to shuffle the instances in the iterator or not.
        num_epochs : int, optional (default = 20)
            Number of training epochs.
        tb_logging_dir : str, optional (default = "tb_logs")
            Folder where tb logs will be saved
        serialization_dir : str, optional (default=None)
            Path to directory for saving and loading model files. Models will not be saved if
            this parameter is not passed.
        accumulation_steps : int, optional (default = 0)
            Number of training steps to accumulate gradients
        cuda_device : ``Union[int, List[int]]``, optional (default = -1)
            An integer or list of integers specifying the CUDA device(s) to use. If -1, the CPU is used.
        grad_norm : ``float``, optional, (default = None).
            If provided, gradient norms will be rescaled to have a maximum of this value.
        """
        super().__init__(serialization_dir, cuda_device)

        # I am not calling move_to_gpu here, because if the model is
        # not already on the GPU then the optimizer is going to be wrong.
        self.model = model
        self._validation_metrics = ["loss"] + list(chain(*[metric.NAMES for metric in self.model.metrics.values()]))

        self.iterator = iterator
        self._validation_iterator = validation_iterator
        self.shuffle = shuffle
        self.optimizer = optimizer
        self.train_data = train_dataset
        self._validation_data = validation_dataset

        if patience is None:  # no early stopping
            if validation_dataset:
                logger.warning('You provided a validation dataset but patience was set to None, '
                               'meaning that early stopping is disabled')
        elif (not isinstance(patience, int)) or patience <= 0:
            raise ConfigurationError('{} is an invalid value for "patience": it must be a positive integer '
                                     'or None (if you want to disable early stopping)'.format(patience))

        # Get rid of + or -
        should_decrease = early_stopping_metric[0] == "-"
        early_stopping_metric = early_stopping_metric[1:]
        if early_stopping_metric not in self._validation_metrics:
            raise ConfigurationError("Your validation metric should be in model metrics list.")
        self._num_epochs = num_epochs

        self._experiment_name = experiment_name or self.model.MODEL_NAME

        # For tracking is_best_so_far and should_stop_early
        self._callbacks = Callbacks(tf_logging={"path": tb_logging_dir,
                                                "experiment_name": self._experiment_name},
                                    early_stopping={"patience": patience,
                                                    "should_decrease": should_decrease,
                                                    "metric_name": early_stopping_metric})
        self._serialization_dir = serialization_dir
        if not os.path.exists(self._serialization_dir):
            os.makedirs(self._serialization_dir)

        self._accumulation_steps = accumulation_steps
        self._grad_norm = grad_norm
        self._lr_scheduler_name: str = lr_scheduler or "constant"
        self._lr_scheduler_params: Optional[Dict] = lr_scheduler_params
        self._lr_scheduler: Optional[Scheduler] = None
        self._fp16 = fp16
        self._gradual_unfreezing_steps = gradual_unfreezing_steps
        if self._fp16:
            self.model, self.optimizer = amp.initialize(self.model, self.optimizer,
                                                        opt_level=fp16_opt_level, verbosity=0)

    def batch_loss(self, batch_group: List[TensorDict], for_training: bool) -> torch.Tensor:
        """
        Does a forward pass on the given batches and returns the ``loss`` value in the result.
        """
        if self._multiple_gpu:
            output_dict = training_util.data_parallel(batch_group, self.model, self._cuda_devices)
        else:
            assert len(batch_group) == 1
            batch = batch_group[0]
            batch = nn_util.move_to_device(batch, self._cuda_devices[0])
            output_dict = self.model(**batch)

        try:
            loss = output_dict["loss"]
        except KeyError:
            if for_training:
                raise RuntimeError("The model you are trying to optimize does not contain a"
                                   " 'loss' key in the output of model.forward(inputs).")
            loss = None

        return loss

    def _train_epoch(self, master_bar_logger: master_bar) -> Dict[str, float]:
        """
        Trains one epoch and returns metrics.
        """

        train_loss = 0.0
        # Set the model to "train" mode.
        self.model.train()
        self.model.zero_grad()
        num_gpus = len(self._cuda_devices)

        raw_train_generator = self.iterator(self.train_data,
                                            num_epochs=1,
                                            shuffle=self.shuffle)
        train_generator = lazy_groups_of(raw_train_generator, num_gpus)
        num_training_batches = math.ceil(self.iterator.get_num_batches(self.train_data) / num_gpus)

        if self._lr_scheduler is None:
            self._set_scheduler(num_training_batches)

        batches_this_epoch = 0
        global_steps = 0
        for batch_group in progress_bar(train_generator, total=num_training_batches,
                                        parent=master_bar_logger, leave=False):
            batches_this_epoch += 1

            loss = self.batch_loss(batch_group, for_training=True)
            if self._accumulation_steps > 1:
                loss = loss / self._accumulation_steps

            if torch.isnan(loss):
                raise ValueError("nan loss encountered")

            if self._fp16:
                with amp.scale_loss(loss, self.optimizer) as scaled_loss:
                    scaled_loss.backward()
                torch.nn.utils.clip_grad_norm_(amp.master_params(self.optimizer), self._grad_norm)
            else:
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self._grad_norm)

            train_loss += loss.item()
            if batches_this_epoch % self._accumulation_steps == 0:
                self.optimizer.step()
                self._lr_scheduler.step()
                self.model.zero_grad()
                global_steps += 1

                master_bar_logger.child.comment = f'loss: {round(train_loss / global_steps, 4)}'

        metrics = training_util.get_metrics(self.model, train_loss, global_steps, reset=True)
        return metrics

    def _validation_run(self, master_bar_logger) -> Dict[str, float]:
        """
        Computes the validation metrics. Returns it and the number of batches.
        """
        logger.info("Validating")

        self.model.eval()

        if self._validation_iterator is not None:
            val_iterator = self._validation_iterator
        else:
            val_iterator = self.iterator

        num_gpus = len(self._cuda_devices)

        raw_val_generator = val_iterator(self._validation_data,
                                         num_epochs=1,
                                         shuffle=False)
        val_generator = lazy_groups_of(raw_val_generator, num_gpus)
        num_training_batches = math.ceil(self.iterator.get_num_batches(self._validation_data) / num_gpus)

        batches_this_epoch = 0
        val_loss = 0
        for batch_group in progress_bar(val_generator, total=num_training_batches,
                                        parent=master_bar_logger, leave=False):
            loss = self.batch_loss(batch_group, for_training=False)
            if loss is not None:
                batches_this_epoch += 1
                val_loss += loss.detach().cpu().numpy()
        val_metrics = training_util.get_metrics(self.model, val_loss, batches_this_epoch, reset=True)
        return val_metrics

    def _set_scheduler(self, len_train_loader: int):
        t_total = len_train_loader // self._accumulation_steps * self._num_epochs
        if self._lr_scheduler_name == "constant":
            self._lr_scheduler = Scheduler.by_name(self._lr_scheduler_name)(optimizer=self.optimizer)
        else:
            self._lr_scheduler = Scheduler.by_name(self._lr_scheduler_name)(optimizer=self.optimizer,
                                                                            t_total=t_total,
                                                                            **self._lr_scheduler_params)

    def _gradual_unfreezing(self, step):
        if self._gradual_unfreezing_steps != ():
            for name, param in self.model.named_parameters():
                if any(list(chain(*[[i in name for i in group] for group in self._gradual_unfreezing_steps[:step+1]]))):
                    param.requires_grad = True
                else:
                    param.detach_()
                    param.requires_grad = False

    def train(self) -> None:
        """
        Trains the supplied model with the supplied parameters.
        """

        logger.info("Beginning training.")
        mb = master_bar(range(self._num_epochs))
        mb.first_bar.comment = f'{self.model.MODEL_NAME} training'
        mb_elements = ['epoch'] + \
                      [f"train_{metrics_name}" for metrics_name in self._validation_metrics] + \
                      [f"val_{metrics_name}" for metrics_name in self._validation_metrics]

        mb.write(mb_elements, table=True)
        set_seed(42, len(self._cuda_devices))
        for epoch in mb:
            self._gradual_unfreezing(epoch)
            train_metrics = self._train_epoch(mb)

            if self._validation_data is not None:
                with torch.no_grad():
                    val_metrics = self._validation_run(mb)
                    self._callbacks.add_metric(val_metrics)

            mb_results = [str(epoch)] + \
                         [str(round(train_metrics[metric], 4)) for metric in self._validation_metrics] + \
                         [str(round(val_metrics[metric], 4)) for metric in self._validation_metrics]

            mb.write(mb_results, table=True)

            if self._callbacks.should_stop_early():
                return None
            elif self._callbacks.is_best_so_far():
                with open(os.path.join(self._serialization_dir, "model.th"), 'wb') as f:
                    torch.save(self.model.state_dict(), f)

            self._callbacks.write_tensorboard_logs(train_metrics,
                                                   val_metrics,
                                                   self._lr_scheduler.get_lr()[0],
                                                   epoch + 1)

        return None
