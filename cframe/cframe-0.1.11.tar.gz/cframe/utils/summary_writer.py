import matplotlib
import matplotlib.pyplot as plt

# set up matplotlib
is_ipython = 'inline' in matplotlib.get_backend()
if is_ipython:
    from IPython import display

plt.ion()

class SummaryWriter(object):
    def __init__(self, *keys):
        self.logs = dict()
        for key in keys:
            self.logs[key] = []
    def append(self, **items):
        for k, v in items.items():
            self.logs[k].append(v)
    def reset(self):
        for k, v in self.logs.items():
            self.logs = []
    def save(self, path=None):
        pass
    def get(self, name):
        return self.logs[name]


if __name__ == '__main__':
    writer = SummaryWriter(*['train_loss', 'valid_loss'])
    writer.append(**dict(
        train_loss=91,
        valid_loss=100
    ))
