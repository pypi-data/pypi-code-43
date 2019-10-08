from PIL import Image
from torch.utils.data import DataLoader

from cframe.dataloader.dataloader_manager import DataloaderManager
from cframe.dataloader.dataset import ClassificationDataset
from cframe.dataloader.tools import DefaultClassAug
from cframe.dataloader.tools import standard_transform


class ClassificationDataloaderManager(DataloaderManager):
    def __init__(self, configer):
        self.configer = configer

        self.img_transform = None

        self.img_trans_list = None

        self.pred_img_transfom = None

        self.aug_transform = DefaultClassAug(configer)

        self._init()

    def _init(self):
        size = self.configer['resize']
        self.img_trans_list = [standard_transform.ReSize(size, interpolation=Image.BILINEAR),
                          standard_transform.ToTensor(),
                          standard_transform.Normalize(**self.configer['normalize'])]

        self.img_transform = standard_transform.Compose(self.img_trans_list)
        self.pred_img_transform = standard_transform.Compose(self.img_trans_list[1:])

    def get_train_dl(self, phase='train'):
        train_dl_dict = self.configer[phase]
        return DataLoader(ClassificationDataset(self.configer, phase=phase,
                                         img_transform=self.img_transform,
                                         aug_transform=self.aug_transform),
                          shuffle=True,
                          batch_size=train_dl_dict['batch_size'],
                          num_workers=train_dl_dict['num_workers'],
                          drop_last=True)

    def get_valid_dl(self, phase='valid'):
        valid_dl_dict = self.configer[phase]
        return DataLoader(ClassificationDataset(self.configer, phase=phase,
                                         img_transform=self.img_transform,
                                         aug_transform=None),
                          shuffle=True,
                          batch_size=valid_dl_dict['batch_size'],
                          num_workers=valid_dl_dict['num_workers'],
                          drop_last=False)

    def view_train_dl(self, phase='train'):
        valid_dl_dict = self.configer[phase]
        return DataLoader(ClassificationDataset(self.configer, phase=phase,
                                         img_transform=self.img_trans_list[0]),
                          shuffle=False,
                          batch_size=valid_dl_dict['batch_size'],
                          num_workers=valid_dl_dict['num_workers']
                          )

    def get_dl(self, phase='valid'):
        valid_dl_dict = self.configer[phase]
        if phase == 'train':
            aug_transform = self.aug_transform
        else:
            aug_transform = None
        return DataLoader(ClassificationDataset(self.configer, phase=phase,
                                         img_transform=self.img_transform,
                                         aug_transform=aug_transform),
                          shuffle=False,
                          batch_size=valid_dl_dict['batch_size'],
                          num_workers=valid_dl_dict['num_workers']
                          )

    def get_test_dl(self, phase='test'):
        return DataLoader(ClassificationDataset(self.configer, phase=phase,
                                         img_transform=self.pred_img_transform),
                          shuffle=False,
                          batch_size=1,
                          num_workers=0
                          )


if __name__ == '__main__':
    from cframe.dataloader.data_configer import DataConfiger

    data_config = DataConfiger.get_data_config('leaf')
    dl_manager = ClassificationDataloaderManager(data_config)
    valid_dl = dl_manager.get_train_dl()
    for i, data in enumerate(valid_dl):
        print(data['img'].shape)
        break

