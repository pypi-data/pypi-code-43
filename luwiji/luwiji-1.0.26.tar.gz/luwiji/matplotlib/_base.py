import os
from IPython.display import Image


class BaseIllustrationMatplotlib:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.oil_price = Image(f"{here}/assets/oil.png", width=600)
