import os
from IPython.display import Image


class BaseIllustrationGAN:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.najwa = Image(f"{here}/assets/najwa.png", width=400)
