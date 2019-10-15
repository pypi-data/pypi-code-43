import torch


def accuracy_binary(model, X, y):
    """
    Function to calculate binary classification accuracy.
    Note: Sigmoid is the final activation

    == Arguments ==
    model: torch.nn.Module
        A deep learning architecture using PyTorch nn.Module

    X: torch.Tensor
        input data

    y: torch.Tensor
        target data
    """
    with torch.no_grad():
        model.eval()
        output = model(X)

    pred = output.round().squeeze()
    acc = (y == pred).to(torch.float32).mean()
    return acc.item()


def accuracy_multiclass(model, X, y):
    """
    Function to calculate multiclass classification accuracy.
    Note: Softmax or LogSoftmax is the final activation

    == Arguments ==
    model: torch.nn.Module
        A deep learning architecture using PyTorch nn.Module

    X: torch.Tensor
        input data

    y: torch.Tensor
        target data
    """
    with torch.no_grad():
        model.eval()
        output = model(X)

    pred = output.argmax(1)
    acc = (y == pred).to(torch.float32).mean()
    return acc.item()
