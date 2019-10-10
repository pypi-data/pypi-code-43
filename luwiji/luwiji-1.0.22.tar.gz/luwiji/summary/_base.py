import os
from IPython.display import Image


class BaseIllustrationSummary:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.machine_learning = Image(f"{here}/assets/machine_learning.png", width=900)
        self.tools = Image(f"{here}/assets/tools.png", width=900)
        self.ml_essentials = Image(f"{here}/assets/ml_essentials.png", width=900)
        self.ml_algorithms = Image(f"{here}/assets/ml_algorithms.png", width=900)
        self.metrics_evaluation = Image(f"{here}/assets/metrics_evaluation.png", width=900)
        self.review1 = Image(f"{here}/assets/review1.png", width=900)
        self.review2 = Image(f"{here}/assets/review2.png", width=900)
