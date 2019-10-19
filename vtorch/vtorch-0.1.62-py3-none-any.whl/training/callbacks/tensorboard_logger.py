import os
from torch.utils.tensorboard import SummaryWriter


class TfLogger:
    def __init__(self, path, experiment_name, grad_w=False):
        if not os.path.isdir(path):
            os.mkdir(path)
        self.grad_w = grad_w
        self.summary_writer = SummaryWriter(os.path.join(path, experiment_name))

    def logging(self, **kwargs):
        info = {"lr": kwargs["lr"]}
        for data_name, metrics_value in [("train", kwargs["train_metrics"]), ("val", kwargs["val_metrics"])]:
            for name, value in metrics_value.items():
                info[f"{data_name}_{name}"] = value
        for tag, value in info.items():
            self.summary_writer.add_scalar(tag, value, kwargs["epoch"])
        if self.grad_w:
            for tag, value in kwargs["named_parameters"]:
                tag = tag.replace('.', '/')
                self.summary_writer.add_histogram(tag, value.data.cpu().numpy(), kwargs["epoch"] + 1)
                self.summary_writer.add_histogram(tag + '/grad', value.grad.data.cpu().numpy(), kwargs["epoch"] + 1)

    def close(self):
        self.summary_writer.close()
