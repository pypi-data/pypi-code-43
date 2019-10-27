from torch import nn

class MSELossFlat(nn.MSELoss):
    def forward(self, input, target):
        return super().forward(input.view(-1), target.view(-1))