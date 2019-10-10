import os
from abc import ABC, abstractmethod

from mlcomp.worker.executors import Executor
from mlcomp.worker.executors.base.equation import Equation


@Executor.register
class Infer(Equation, ABC):
    def __init__(
            self,
            test: bool = False,
            layout: str = None,
            plot_count: int = 0,
            **kwargs
    ):
        super().__init__(**kwargs)

        self.test = test
        self.layout = layout
        self.plot_count = plot_count

    @abstractmethod
    def count(self):
        pass

    @abstractmethod
    def plot(self, preds):
        pass

    def key(self):
        return 'y'

    @abstractmethod
    def save(self, preds, folder: str):
        pass

    @abstractmethod
    def save_final(self, folder: str):
        pass

    @abstractmethod
    def create_base(self):
        pass

    @abstractmethod
    def adjust_part(self, part):
        pass

    def work(self):
        folder = 'data/pred'
        os.makedirs(folder, exist_ok=True)

        self.create_base()
        parts = self.generate_parts(self.count())

        for preds in self.solve(self.key(), parts):
            self.save(preds, folder)

            if self.layout:
                self.plot(preds)

        self.save_final(folder)
