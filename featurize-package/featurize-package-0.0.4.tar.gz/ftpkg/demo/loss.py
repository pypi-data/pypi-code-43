from featurize_jupyterlab.core import loss
import torch.nn.functional as F


@loss('PyTorch cross_entropy', 'Simple wrap of the cross_entropy of PyTorch')
def cross_entropy():
    def loss(trainer, data):
        image, target = data
        output = trainer.model(image)
        return F.nll_loss(output, target)
    return loss
