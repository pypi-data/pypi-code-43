from mxnet import gluon
import mxnet as mx



def trainer(params: gluon.ParameterDict, optim: str = 'sgd', learning_rate=1e-2,
            weight_decay=0):
    """
    Provide gluon trainer
    :return:
    """
    return gluon.Trainer(params, optim,
                         {'learning_rate': learning_rate,
                          'wd':            weight_decay})


def softmaxCELoss(ctx: mx.Context, from_logits=False):
    """
    Provide wrap Softmax CELoss
    :return: Initialized gluon.loss.SoftmaxCELoss layer
    """
    loss_fcn = gluon.loss.SoftmaxCELoss(from_logits)
    loss_fcn.initialize(ctx=ctx)
    return loss_fcn
