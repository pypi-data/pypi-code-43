from gxdltk.th.header import *

__all__ = ['batch_provider']

def batch_provider(*data: list, batch_size: int = 1, shuffle: bool = True) \
        -> \
                tdata.DataLoader:
    """
    convert list type data to a dataloader
    :param data: your data, tensor
    :return: data loader
    """
    dtensors = tuple(map(tensor, data))  # tensor tuple
    dataset = tdata.TensorDataset(*dtensors)
    loader = tdata.DataLoader(dataset=dataset, batch_size=batch_size,
                              shuffle=shuffle)
    return loader
