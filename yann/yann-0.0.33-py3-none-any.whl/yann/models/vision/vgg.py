from torch import nn
from ...modules import Stack, Flatten
from .base import RecognitionModel


class VGG(RecognitionModel):
  Conv = nn.Conv2d
  Norm = nn.BatchNorm2d
  Downsample = nn.MaxPool2d
  Activation = nn.ReLU

  Reduce = nn.AvgPool2d

  in_channels = 3

  channels = [
    (64,),
    (128,),
    (256,),
    (512,),
    (512,)
  ]

  def __init__(self, num_classes):
    super(VGG, self).__init__()
    self.num_classes = num_classes
    self.backbone = self.build_backbone()

    self.embeddings = Stack(
      pool=self.Reduce(kernel_size=1, stride=1),
      flatten=Flatten()
    )

    self.classifier = nn.Linear(self.channels[-1][-1], self.num_classes)

  def forward(self, inputs):
    features = self.backbone(inputs)
    embeddings = self.embeddings(features)
    logits = self.classifier(embeddings)
    return logits

  def build_backbone(self):
    layers = []

    prev_channels = self.in_channels
    for channels in self.channels:
      for c in channels:
        layers.append(
          Stack(
            conv=self.Conv(prev_channels, c, kernel_size=3, padding=1),
            norm=self.Norm(c),
            activation=self.Activation(inplace=True)
          )
        )
        prev_channels = c
      layers.append(self.Downsample(kernel_size=2, stride=2))
    return Stack(*layers)


class VGG11(VGG):
  channels = [
    (64,),
    (128,),
    (256,) * 2,
    (512,) * 2,
    (512,) * 2,
  ]


class VGG13(VGG):
  channels = [
    (64,) * 2,
    (128,) * 2,
    (256,) * 2,
    (512,) * 2,
    (512,) * 2,
  ]


class VGG16(VGG):
  channels = [
    (64,) * 2,
    (128,) * 2,
    (256,) * 3,
    (512,) * 3,
    (512,) * 3,
  ]


class VGG19(VGG):
  channels = [
    (64,) * 2,
    (128,) * 2,
    (256,) * 4,
    (512,) * 4,
    (512,) * 4,
  ]
