from featurize_jupyterlab.core import loss
import torch.nn.functional as F


@loss('BCE Loss', 'Simple wrap of the binary cross entropy of PyTorch')
def bce_loss():
    def loss(trainer, data):
        image, target = data
        output = trainer.model(image)
        return F.binary_cross_entropy_with_logits(output, target)
    return loss
