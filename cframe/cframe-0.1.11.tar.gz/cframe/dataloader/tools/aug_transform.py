import imgaug as iaa
import imgaug.augmenters as iaa
from imgaug.augmentables.segmaps import SegmentationMapOnImage


class DefaultSegAug(object):
	def __init__(self, configer):
		self.configer = configer
		self.aug = iaa.Sequential([
			iaa.Crop(percent=(0, 0.1))
						# iaa.Dropout([0.05, 0.1]),      # drop 5% or 20% of all pixels
						# iaa.Sharpen((0.0, 1.0)),       # sharpen the image
						# iaa.Affine(rotate=(-10, 10)),  # rotate by -45 to 45 degrees (affects segmaps)
						# iaa.ElasticTransformation(alpha=50, sigma=5)  # apply water effect (affects segmaps)
					])

	def __call__(self, img, label):
		# print(img.shape)
		label = SegmentationMapOnImage(label, shape=img.shape, nb_classes=self.configer['data_info']['n_classes'])
		img_aug, label_aug = self.aug(image=img, segmentation_maps=label)
		label_aug = label_aug.get_arr_int()
		# print(np.unique(label_aug))
		# print(label_aug.shape, '--')
		return img_aug, label_aug


class DefaultClassAug(object):
	def __init__(self, configer):
		self.configer = configer
		self.aug = iaa.Sequential([
			iaa.Crop(percent=(0, 0.1))
						# iaa.Dropout([0.05, 0.1]),      # drop 5% or 20% of all pixels
						# iaa.Sharpen((0.0, 1.0)),       # sharpen the image
						# iaa.Affine(rotate=(-10, 10)),  # rotate by -45 to 45 degrees (affects segmaps)
						# iaa.ElasticTransformation(alpha=50, sigma=5)  # apply water effect (affects segmaps)
					])

	def __call__(self, img):
		img_aug = self.aug(image=img)
		return img_aug
