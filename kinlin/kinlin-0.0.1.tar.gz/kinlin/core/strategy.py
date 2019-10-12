import torch
import torch.nn as nn
import numpy as np

from enum import Enum
from typing import List, Callable, Any
from tqdm import tqdm

from .model import Model
from .dataset import Dataset
from .experiment import Experiment
from .callback import Callback

class TrainingEvents(Enum):
    START = 'on_start'
    FINISH = 'on_finish'
    TRAINING_EPOCH_START = 'on_training_epoch_start'
    TRAINING_EPOCH_FINISH = 'on_training_epoch_finish'
    TRAINING_BATCH_START = 'on_training_batch_start'
    TRAINING_BATCH_FINISH = 'on_training_batch_finish'
    VALIDATION_EPOCH_START = 'on_validation_epoch_start'
    VALIDATION_EPOCH_FINISH = 'on_validation_epoch_finish'
    VALIDATION_BATCH_START = 'on_validation_batch_start'
    VALIDATION_BATCH_FINISH = 'on_validation_batch_finish'
    TESTING_START = 'on_testing_start'
    TESTING_FINISH = 'on_testing_finish'
    TESTING_BATCH_START = 'on_testing_batch_start'
    TESTING_BATCH_FINISH = 'on_testing_batch_finish'

class TrainingStrategy:
    def __init__(self, model: Model, dataset: Dataset, optimizer: torch.optim.Optimizer, experiment: Experiment = None,
                 callbacks: List[Callback] = None):

        # properties
        self.model: Model = model
        self.dataset: Dataset = dataset
        self.optimizer: torch.optim.Optimizer = optimizer
        #self.experiment: Experiment = experiment
        self.callbacks: List[Callback] = callbacks

        # parallelize network depending on experiment settings
        # if len(self.experiment.devices) > 1:
        #     self.network = nn.DataParallel(self.model.network, device_ids=self.experiment.devices)
        # else:
        self.network = self.model.network

        # event handler
        self.handlers = {k: [] for k in TrainingEvents}

        # register events
        for event in TrainingEvents:
            # model events
            self.on_event(event, getattr(self.model, event.value))

            # callback events
            for c in self.callbacks:
                self.on_event(event, getattr(c, event.value))

    def on_event(self, event: TrainingEvents, handler: Callable):
        self.handlers[event].append(handler)

    def emit(self, event: TrainingEvents, *args, **kwargs):
        for handler in self.handlers[event]:
            handler(*args, **kwargs)

    def training_epoch(self, epoch: int) -> None:
        raise NotImplementedError

    def validation_epoch(self, epoch: int) -> None:
        raise NotImplementedError

    def test(self) -> None:
        raise NotImplementedError

    def __call__(self, n_epochs: int = 1, validation: bool = True, verbose: bool = True):
        if verbose:
            print(f'Training{" and validating" if validation else ""}'
                  f' for {n_epochs} {"epochs" if n_epochs > 1 else "epoch"}')
            self.model.print_summary()
            self.dataset.print_summary()
            print(f'Optimizer: {self.optimizer.__class__.__name__}\n'
                  f'\tLearning rate: {self.optimizer.param_groups[0]["lr"]}')
            print(f'Callbacks: {", ".join(c.__class__.__name__ for c in self.callbacks)}')

        for epoch in range(n_epochs):
            print(f'\nEpoch {epoch}:')
            self.training_epoch(epoch)

            if validation:
                self.validation_epoch(epoch)


class SupervisedTraining(TrainingStrategy):

    def training_epoch(self, epoch: int) -> None:
        self.model.network.train()
        self.emit(TrainingEvents.TRAINING_EPOCH_START, epoch, self.model)

        with tqdm(self.dataset.training_dataloader(), desc='Training', unit='batch') as t:
            for batch_id, batch in enumerate(t):
                self.emit(TrainingEvents.TRAINING_BATCH_START, batch, batch_id, epoch)
                loss, y_pred, y_true = self.model.training_fn(batch, batch_id, epoch)
                self.model.backprop_fn(loss, self.optimizer)
                self.emit(TrainingEvents.TRAINING_BATCH_FINISH, batch, batch_id, epoch,
                          loss.detach(), y_pred.detach(), y_true)

                # update progress bar
                t.set_postfix(self.model.progressbar_metrics())

        self.emit(TrainingEvents.TRAINING_EPOCH_FINISH, epoch, self.model)

    def validation_epoch(self, epoch: int) -> None:
        self.model.network.eval()
        self.model.network.train(False)
        with torch.no_grad():
            self.emit(TrainingEvents.VALIDATION_EPOCH_START, epoch, self.model)

            with tqdm(self.dataset.validation_dataloader(), desc='Validation', unit='batch') as t:
                for batch_id, batch in enumerate(t):
                    self.emit(TrainingEvents.VALIDATION_BATCH_START, batch, batch_id, epoch)
                    loss, y_pred, y_true = self.model.validation_fn(batch, batch_id, epoch)
                    self.emit(TrainingEvents.VALIDATION_BATCH_FINISH, batch, batch_id, epoch,
                              loss.detach(), y_pred.detach(), y_true)

                    # update progress bar
                    t.set_postfix(self.model.progressbar_metrics())

            self.emit(TrainingEvents.VALIDATION_EPOCH_FINISH, epoch, self.model)

    def test(self) -> None:
        self.model.network.eval()
        self.model.network.train(False)
        with torch.no_grad():
            self.emit(TrainingEvents.TESTING_START)

            with tqdm(self.dataset.validation_dataloader(), desc='Testing', unit='batch') as t:
                for batch_id, batch in enumerate(t):
                    self.emit(TrainingEvents.TESTING_BATCH_START, batch, batch_id)
                    loss, y_pred, y_true = self.model.validation_fn(batch, batch_id, -1)
                    self.emit(TrainingEvents.TESTING_BATCH_FINISH, batch, batch_id,
                              loss.detach(), y_pred.detach(), y_true)

                    # update progress bar
                    t.set_postfix(self.model.progressbar_metrics())

            self.emit(TrainingEvents.TESTING_FINISH)
