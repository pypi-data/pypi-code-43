class ModelClass(object):

    def __init__(self, **kwargs):
        # default
        self.num_classes = 12
        # momentum for batch normlization
        self.bn_mom = 0.9
        # memory space size(MB) used in convolution, if xpu memory is oom, then you can try smaller vale, such as --workspace 256
        self.workspace = 512
        # true means using memonger to save momory, https://github.com/dmlc/mxnet-memonger
        self.memonger = False

        for k,v in kwargs.items():
            setattr(self, k, v)
