from featurize_jupyterlab.core import dataset, option, metadata
from torchvision import datasets, transforms


@dataset('MNIST Train', 'This is a simple wrap for torchvision.datasets.MNIST(train=True)')
@option('fold', help='Absolute fold path to the dataset', required=True, default="~/.minetorch_dataset/torchvision_mnist")
@metadata('banner', 'https://upload.wikimedia.org/wikipedia/commons/2/27/MnistExamples.png')
def mnist_train(fold):
    return datasets.MNIST(fold, download=True, train=True, transform=transforms.ToTensor())


@dataset('MNIST Test', 'This is a simple wrap for torchvision.datasets.MNIST(Train=False)')
@option('fold', help='Absolute fold path to the dataset', required=True, default="~/.minetorch_dataset/torchvision_mnist")
@metadata('banner', 'https://upload.wikimedia.org/wikipedia/commons/2/27/MnistExamples.png')
def mnist(fold):
    return datasets.MNIST(fold, download=True, train=False)


@dataset('Wider Face', 'Wider Face Dataset')
@metadata('banner', 'http://shuoyang1213.me/WIDERFACE/support/intro.jpg')
def wider_face():
    return True

@dataset('Microsoft COCO', 'Microsoft COCO dataset')
@metadata('banner', 'http://cocodataset.org/images/coco-logo.png')
def coco():
    return True

@dataset('Image Net', 'Image Net Dataset')
@metadata('banner', 'https://miro.medium.com/max/750/1*IlzW43-NtJrwqtt5Xy3ISA.jpeg')
def image_net():
    return True

@dataset('Kaggle TGS Dataset', 'Kaggle TGS Dataset')
@metadata('banner', 'https://storage.googleapis.com/kaggle-competitions/kaggle/10151/logos/header.png')
def kaggle_tgs():
    return True

@dataset('Kaggle SSDD', 'Kaggle SSDD Dataset')
@metadata('banner', 'https://storage.googleapis.com/kaggle-competitions/kaggle/14241/logos/header.png')
def kaggle_ssdd():
    return True
