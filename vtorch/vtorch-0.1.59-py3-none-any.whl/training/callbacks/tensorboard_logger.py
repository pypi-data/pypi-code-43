import os
import tensorflow as tf
import numpy as np
import scipy.misc
from io import BytesIO


class _Logger(object):
    def __init__(self, log_dir):
        """Create a summary writer logging to log_dir."""
        self.writer = tf.summary.FileWriter(log_dir)

    def scalar_summary(self, tag, value, step):
        """Log a scalar variable."""
        summary = tf.Summary(value=[tf.Summary.Value(tag=tag, simple_value=value)])
        self.writer.add_summary(summary, step)
        self.writer.flush()

    def image_summary(self, tag, images, step):
        """Log a list of images."""

        img_summaries = []
        for i, img in enumerate(images):
            s = BytesIO()
            scipy.misc.toimage(img).save(s, format="png")

            # Create an Image object
            img_sum = tf.Summary.Image(encoded_image_string=s.getvalue(),
                                       height=img.shape[0],
                                       width=img.shape[1])
            # Create a Summary value
            img_summaries.append(tf.Summary.Value(tag='%s/%d' % (tag, i), image=img_sum))

        # Create and write Summary
        summary = tf.Summary(value=img_summaries)
        self.writer.add_summary(summary, step)
        self.writer.flush()

    def histo_summary(self, tag, values, step, bins=1000):
        """Log a histogram of the tensor of values."""

        # Create a histogram using numpy
        counts, bin_edges = np.histogram(values, bins=bins)

        # Fill the fields of the histogram proto
        hist = tf.HistogramProto()
        hist.min = float(np.min(values))
        hist.max = float(np.max(values))
        hist.num = int(np.prod(values.shape))
        hist.sum = float(np.sum(values))
        hist.sum_squares = float(np.sum(values ** 2))

        # Drop the start of the first bin
        bin_edges = bin_edges[1:]

        # Add bin edges and counts
        for edge in bin_edges:
            hist.bucket_limit.append(edge)
        for c in counts:
            hist.bucket.append(c)

        # Create and write Summary
        summary = tf.Summary(value=[tf.Summary.Value(tag=tag, histo=hist)])
        self.writer.add_summary(summary, step)
        self.writer.flush()

    def close_file(self):
        self.writer.close()


class TfLogger:
    def __init__(self, path, experiment_name, grad_w=False):
        if not os.path.isdir(path):
            os.mkdir(path)
        self.grad_w = grad_w
        self.logger = _Logger(os.path.join(path, experiment_name))

    def logging(self, **kwargs):
        info = {"lr": kwargs["lr"]}
        for data_name, metrics_value in [("train", kwargs["train_metrics"]), ("val", kwargs["val_metrics"])]:
            for name, value in metrics_value.items():
                info[f"{data_name}_{name}"] = value
        for tag, value in info.items():
            self.logger.scalar_summary(tag, value, kwargs["epoch"])
        if self.grad_w:
            for tag, value in kwargs["named_parameters"]:
                tag = tag.replace('.', '/')
                self.logger.histo_summary(tag, value.data.cpu().numpy(), kwargs["epoch"] + 1)
                self.logger.histo_summary(tag + '/grad', value.grad.data.cpu().numpy(), kwargs["epoch"] + 1)

    def close(self):
        self.logger.close_file()
