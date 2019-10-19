from typing import Dict, Union, Optional
from vtorch.training.callbacks import EarlyStopping, TfLogger


class Callbacks:
    def __init__(self, tf_logging: Optional[Dict[str, Union[str, bool]]] = None,
                 early_stopping: Optional[Dict[str, Union[str, bool, int]]] = None):
        self.tf_logging = TfLogger(**tf_logging) if tf_logging is not None else None
        self.early_stopping = EarlyStopping(**early_stopping) if early_stopping is not None else None

    def write_tensorboard_logs(self, train_metrics: Dict[str, float],
                               val_metrics: Dict[str, float],
                               lr: float,
                               epoch: int) -> None:
        tf_logging_info = dict()
        tf_logging_info["train_metrics"] = train_metrics
        tf_logging_info["val_metrics"] = val_metrics
        tf_logging_info["epoch"] = epoch
        tf_logging_info["lr"] = lr
        if self.tf_logging is not None:
            self.tf_logging.logging(**tf_logging_info)

    def add_metric(self, val_metrics: Dict[str, float]):
        if self.early_stopping is not None:
            self.early_stopping.add_metric(val_metrics[self.early_stopping.metric_name])

    def should_stop_early(self):
        if self.early_stopping is not None:
            return self.early_stopping.should_stop_early()
        return False

    def is_best_so_far(self):
        if self.early_stopping is not None:
            return self.early_stopping.is_best_so_far()
        return False
