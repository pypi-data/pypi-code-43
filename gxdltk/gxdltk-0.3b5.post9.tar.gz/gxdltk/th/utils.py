from gxdltk.th.header import *

__all__ = ['batch_provider','batch_idx_provider']


def batch_provider(*data: list,
                   batch_size: int = 1,
                   shuffle: bool = True) -> tdata.DataLoader:
    """

    Args:
        *data: data, multi list
        batch_size:
        shuffle:

    Returns:

    """
    dtensors = tuple(map(tensor, data))  # tensor tuple
    dataset = tdata.TensorDataset(*dtensors)
    loader = tdata.DataLoader(dataset=dataset, batch_size=batch_size,
                              shuffle=shuffle)
    return loader


def batch_idx_provider(idx_data: list,
                       batch_size: int = 1,
                       shuffle: bool = True) -> tdata.DataLoader:
   dtensors = th.LongTensor(idx_data)
   dataset = tdata.TensorDataset(dtensors)
   loader = tdata.DataLoader(dataset=dataset, batch_size=batch_size,
                             shuffle=shuffle)
   return loader
