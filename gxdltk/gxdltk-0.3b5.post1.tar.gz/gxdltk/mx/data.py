from gxdltk.mx.header import *

__all__ = ['batch_provider']

def batch_provider(*data: list, batch_size: int = 1,
                      shuffle: bool = True) -> gdata.DataLoader:
    """
    provide batch data
    :param data: RAW data, list type
    :param batch_size: batch size
    :param shuffle:
    :return: gluon.dataloader
    """
    dataset = gdata.ArrayDataset(data)
    data_iter = gdata.DataLoader(dataset, batch_size, shuffle=shuffle)
    return data_iter
