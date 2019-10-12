import torch

class Callback:
    def __init__(self):
        pass

### Events
    def on_start(self) -> None:
        pass

    def on_finish(self) -> None:
        pass

    def on_epoch_start(self, epoch: int, model: 'Model') -> None:
        pass

    def on_epoch_finish(self, epoch: int, model: 'Model') -> None:
        pass

    def on_batch_start(self, batch, batch_id: int, epoch: int) -> None:
        pass

    def on_batch_finish(self, batch, batch_id: int, epoch: int,
                        loss: torch.Tensor, y_pred: torch.Tensor, y_true: torch.Tensor) -> None:
        pass

    def on_training_epoch_start(self, epoch: int, model: 'Model') -> None:
        pass

    def on_training_epoch_finish(self, epoch: int, model: 'Model') -> None:
        pass

    def on_validation_epoch_start(self, epoch: int, model: 'Model') -> None:
        pass

    def on_validation_epoch_finish(self, epoch: int, model: 'Model') -> None:
        pass

    def on_testing_start(self) -> None:
        pass

    def on_testing_finish(self) -> None:
        pass

    def on_training_batch_start(self, batch, batch_id: int, epoch: int) -> None:
        pass

    def on_training_batch_finish(self, batch, batch_id: int, epoch: int,
                                 loss: torch.Tensor, y_pred: torch.Tensor, y_true: torch.Tensor) -> None:
        pass

    def on_validation_batch_start(self, batch, batch_id: int, epoch: int) -> None:
        pass

    def on_validation_batch_finish(self, batch, batch_id: int, epoch: int,
                                   loss: torch.Tensor, y_pred: torch.Tensor, y_true: torch.Tensor) -> None:
        pass

    def on_testing_batch_start(self, batch, batch_id: int) -> None:
        pass

    def on_testing_batch_finish(self, batch, batch_id: int,
                                loss: torch.Tensor, y_pred: torch.Tensor, y_true: torch.Tensor) -> None:
        pass
