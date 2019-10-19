from featurize_jupyterlab.core import Loss
import torch.nn.functional as F


class BCELoss(Loss):
    """Simple wrap of the binary cross entropy of PyTorch
    """
    def __call__(self, trainer, data):
        image, target = data[0].cuda(), data[1].cuda()
        output = trainer.model(image)
        return F.binary_cross_entropy_with_logits(output, target)
