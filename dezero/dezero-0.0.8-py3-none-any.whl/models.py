from dezero import Model
import dezero.functions as F
import dezero.layers as L


class Sequential(Model):
    def __init__(self, *layers):
        self.layers = []
        for layer in layers:
            self.layers.append(layer)

    def __call__(self, x):
        for layer in self.layers:
            x = layer(x)
        return x


class MLP(Model):
    def __init__(self, in_size, hidden_size, out_size, activation=F.sigmoid):
        super().__init__()
        self.f = activation
        self.l1 = L.Linear(in_size, hidden_size)
        self.l2 = L.Linear(hidden_size, out_size)

    def __call__(self, x):
        y = self.f(self.l1(x))
        y = self.l2(y)
        return y


class VGG(Model):
    pass