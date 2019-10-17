from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

import numpy as np

import torch as t
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

DEVICE = t.device("cuda" if t.cuda.is_available() else "cpu")


class Accuracy:
    def __init__(self) -> None:
        self._correct_instances: List[int] = []
        self._num_instances = 0

    def accumulate(self, outputs: t.Tensor, targets: t.Tensor) -> None:
        preds = t.argmax(outputs, dim=1)
        correct = t.sum(preds == targets).item()
        self._correct_instances.append(correct)
        self._num_instances += targets.shape[0]

    def calculate(self) -> float:
        return np.sum(self._correct_instances) / self._num_instances


class Trainer(ABC):
    def __init__(
        self, trainloader: DataLoader, valloader: DataLoader, epochs: int, model: t.nn.Module
    ):
        self.trainloader = trainloader
        self.valloader = valloader
        self.epochs = epochs
        self.model = model

    def _tb_write(
        self,
        writer: SummaryWriter,
        epoch: int,
        train_loss: float,
        train_acc: float,
        val_loss: float,
        val_acc: float,
    ):
        if writer is None:
            return

        for i, param in enumerate(self.model.parameters()):
            writer.add_histogram(f"layer-{i}", param, epoch)

        writer.add_scalars("Accuracy", {"acc/train": train_acc, "acc/val": val_acc}, epoch)
        writer.add_scalars("Loss", {"loss/train": train_loss, "loss/val": val_loss}, epoch)
        writer.close()

    def _print_summary(
        self,
        to_print: bool,
        epoch,
        train_loss: float,
        train_acc: float,
        val_loss: float,
        val_acc: float,
    ):
        if not to_print:
            return

        print(f"\nEpoch {epoch} summary")
        print(f"\tTraining: Loss={train_loss:.3f}, Accuracy={train_acc*100:.2f}%")
        print(f"\tValidation: Loss={val_loss:.3f}, Accuracy={val_acc*100:.2f}%")

    def train(self, writer: Optional[SummaryWriter] = None, print_summary=False) -> None:
        self.model = self.model.to(DEVICE)
        self.model.train()

        for epoch in range(self.epochs):
            loss_per_batch: List[float] = []
            accuracy = Accuracy()

            for inputs, targets in self.trainloader:
                inputs = inputs.to(DEVICE)
                targets = targets.to(DEVICE)

                with t.enable_grad():
                    outputs, loss = self.train_batch(inputs, targets)
                    loss_per_batch.append(loss.item())
                    accuracy.accumulate(outputs, targets)

            self.end_train_epoch(epoch)

            if writer or print_summary:
                epoch_train_loss = np.mean(loss_per_batch)
                epoch_train_acc = accuracy.calculate()
                eval_results = self.evaluate()
                epoch_val_acc = eval_results["accuracy"]
                epoch_val_loss = eval_results["loss"]
                self._tb_write(
                    writer, epoch, epoch_train_loss, epoch_train_acc, epoch_val_loss, epoch_val_acc
                )
                self._print_summary(
                    print_summary,
                    epoch,
                    epoch_train_loss,
                    epoch_train_acc,
                    epoch_val_loss,
                    epoch_val_acc,
                )

    def evaluate(self) -> Dict[str, float]:
        accuracy = Accuracy()
        loss_per_batch: List[float] = []
        self.model.eval()

        for inputs, targets in self.valloader:
            inputs = inputs.to(DEVICE)
            targets = targets.to(DEVICE)

            with t.no_grad():
                outputs, loss = self.eval_batch(inputs, targets)
                loss_per_batch.append(loss.item())
                accuracy.accumulate(outputs, targets)

        acc = accuracy.calculate()
        loss = np.mean(loss_per_batch)
        return {"accuracy": acc, "loss": loss}

    @abstractmethod
    def train_batch(self, inputs: t.Tensor, targets: t.Tensor) -> Tuple[t.Tensor, t.Tensor]:
        pass

    def end_train_epoch(self, epoch) -> None:
        pass

    @abstractmethod
    def eval_batch(self, inputs: t.Tensor, targets: t.Tensor) -> Tuple[t.Tensor, t.Tensor]:
        pass
