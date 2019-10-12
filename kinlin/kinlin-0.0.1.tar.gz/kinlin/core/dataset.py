# generic dataset classes
# MrcDataset
# EmDataset ?
# ImageDataset
from torch.utils.data import DataLoader

class Dataset:

    def __init__(self):
        pass

    def training_dataloader(self, batch_size: int = 1, shuffle: bool = True) -> DataLoader:
        raise NotImplementedError

    def validation_dataloader(self, batch_size: int = 1, shuffle: bool = True) -> DataLoader:
        raise NotImplementedError

    def test_dataloader(self, batch_size: int = 1, shuffle: bool = True) -> DataLoader:
        raise NotImplementedError

    def __repr__(self):
        return f'Dataset: {self.__class__.__name__}\n'\
               f'\tTraining size: {len(self.training_dataloader())}\n' \
               f'\tValidation size: {len(self.validation_dataloader())}\n' \
               f'\tTest size: {len(self.validation_dataloader())}'

    def print_summary(self) -> None:
        print(repr(self))
