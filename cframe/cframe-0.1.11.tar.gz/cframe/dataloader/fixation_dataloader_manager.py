from PIL import Image
from torch.utils.data import DataLoader

from cframe.dataloader.dataset import FixationDataset
from cframe.dataloader.tools import standard_transform


class FixationDataloaderManager(object):
    def __init__(self, configer):
        self.configer = configer

        self.img_transform = None
        self.saliency_transform = None
        self.fixation_transform = None

        self.img_trans_list = None
        self.saliency_trans_list = None
        self.fixation_trans_list = None

        self.pred_img_transfom = None
        self.pred_saliency_transform = None
        self.pred_fixation_tranform = None

        self.aug_transform = None

        self._init()

    def _init(self):
        size = self.configer['resize']
        self.img_trans_list = [standard_transform.ReSize(size, interpolation=Image.BILINEAR),
                          standard_transform.ToTensor(),
                          standard_transform.Normalize(**self.configer['normalize'])]
        self.saliency_trans_list = [standard_transform.ReSize(size, interpolation=Image.BILINEAR),
                               standard_transform.ToTensor()]
        self.fixation_trans_list = [standard_transform.ReSize(size, interpolation=Image.BILINEAR),
                               standard_transform.ToTensor()]

        self.img_transform = standard_transform.Compose(self.img_trans_list)
        self.saliency_transform = standard_transform.Compose(self.saliency_trans_list)
        self.fixation_transform = standard_transform.Compose(self.fixation_trans_list)

        self.pred_img_transform = standard_transform.Compose(self.img_trans_list[1:])
        self.pred_saliency_transform = standard_transform.Compose(self.saliency_trans_list[1:])
        self.pred_fixation_transform = standard_transform.Compose(self.fixation_trans_list[1:])

    def get_train_dl(self, phase='train'):
        train_dl_dict = self.configer[phase]

        return DataLoader(FixationDataset(self.configer, phase=phase,
                                         img_transform=self.img_transform,
                                         saliency_transform=self.saliency_transform,
                                         fixation_transform=self.fixation_transform,
                                         aug_transform=self.aug_transform),
                          shuffle=True,
                          batch_size=train_dl_dict['batch_size'],
                          num_workers=train_dl_dict['num_workers'],
                          drop_last=True)

    def view_train_dl(self, phase='train'):
        return FixationDataset(self.configer, phase=phase,
                             img_transform=self.img_trans_list[0],
                             saliency_transform=self.saliency_trans_list[0],
                             fixation_transform=self.fixation_trans_list[0],
                             aug_transform=None)

    def get_valid_dl(self, phase='valid'):
        valid_dl_dict = self.configer[phase]
        return DataLoader(FixationDataset(self.configer, phase=phase,
                                         img_transform=self.img_transform,
                                         saliency_transform=self.saliency_transform,
                                         fixation_transform=self.fixation_transform),
                          shuffle=False,
                          batch_size=valid_dl_dict['batch_size'],
                          num_workers=valid_dl_dict['num_workers']
                          )

    def get_test_dl(self, phase='test'):
        return DataLoader(FixationDataset(self.configer, phase=phase,
                                         img_transform=self.pred_img_transform,
                                         saliency_transform=self.pred_saliency_transform,
                                         fixation_transform=self.pred_fixation_transform),
                          shuffle=False,
                          batch_size=1,
                          num_workers=0

                          )
if __name__ == '__main__':
    from cframe.dataloader.data_configer import DataConfiger
    data_config = DataConfiger.get_data_config('DUT')
    dl_manager = FixationDataloaderManager(data_config)
    valid_dl = dl_manager.get_train_dl()
    for i, data in enumerate(valid_dl):
        print(data['img'].shape, data['fixation'].shape,data['saliency'].shape)
        break
