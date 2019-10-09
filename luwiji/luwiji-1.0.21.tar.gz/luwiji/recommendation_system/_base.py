import os
from IPython.display import Image


class BaseIllustrationRecommendationSystem:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.parse = Image(f"{here}/assets/parse.png", width=900)
