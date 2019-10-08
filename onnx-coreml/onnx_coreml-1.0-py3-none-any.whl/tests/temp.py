import torch
import torch.nn as nn

m = nn.BatchNorm2d(100, affine=False)
input = torch.randn(20, 100, 35, 45)
output = m(input)

torch.onnx.export(m, input, "bn.onnx", verbose=True)
