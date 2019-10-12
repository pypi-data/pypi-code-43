from typing import List
from .utils import *
# from .experiment import Experiment

class Project:
    def __init__(self, name: str = 'Untitled Project', notes: str = '', path: Union[Path, str] = None):

        # general properties
        self.id: str = generate_random_id()
        self.name: str = name
        self.fname: str = generate_fname(name)
        self.notes: str = notes
        if isinstance(path, str):
            path = Path(path)
        self.path: Path = path / self.fname
        self.path.mkdir(parents=True)  # TODO: this should never happen, but it can raise FileExistError

        # experiments
        # self.experiments: List[Experiment] = []

    def new_experiment(self, name: str):

        # new_exp = Experiment(project=self)
        # setup experiment?
        # self.experiments += new_exp
        pass

    def continue_experiment(self):
        pass

    def open_experiment_folder(self):
        open_folder(self.path)

