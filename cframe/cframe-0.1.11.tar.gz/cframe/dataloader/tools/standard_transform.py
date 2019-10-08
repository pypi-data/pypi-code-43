import numpy as np
import torch
from PIL import Image


class Compose(object):
    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, img):
        for t in self.transforms:
            img = t(img)
        return img


class ReSize(object):
    def __init__(self, shape, interpolation=Image.BILINEAR):
        assert isinstance(shape, tuple)
        self.shape = shape
        self.interpolation = interpolation

    def __call__(self, img):
        if isinstance(img, np.ndarray):
            img = Image.fromarray(img)

        ratio = self.shape[0] / self.shape[1]
        w, h = img.size
        if w / h < ratio:
            t = int(h * ratio)
            w_padding = (t-w) // 2
            img = img.crop((-w_padding, 0, w+w_padding, h))
        else:
            t = int(w / ratio)
            h_padding = (t-h) // 2
            img = img.crop((0, -h_padding, w, h+h_padding))

        img = img.resize(self.shape, self.interpolation)

        return np.array(img)


class Normalize(object):
    def __init__(self, mean, std, inplace=False):
        self.mean = mean
        self.std = std
        self.inplace = inplace

    def __call__(self, tensor):
        if not self.inplace:
            tensor = tensor.clone()

        mean = torch.as_tensor(self.mean, dtype=torch.float32, device=tensor.device)
        std = torch.as_tensor(self.std, dtype=torch.float32, device=tensor.device)
        tensor.sub_(mean[:, None, None]).div_(std[:, None, None])
        return tensor


class ToTensor(object):
    def __call__(self, img):
        assert isinstance(img, np.ndarray)
        if img.ndim == 3:
            img = np.transpose(img, [2, 0, 1])
            img = img / 255.
        img = torch.from_numpy(img)
        return img.float()


class ToLabel(object):
    def __call__(self, img):
        assert isinstance(img, np.ndarray)
        img = torch.from_numpy(img)
        return img.long()


class CamVidReLabel(object):
    def __call__(self, img):
        assert isinstance(img, torch.LongTensor)
        img[img != 0] = 1
        img[img == 1] = 255
        img[img == 0] = 1
        img[img == 255] = 0
        return img
