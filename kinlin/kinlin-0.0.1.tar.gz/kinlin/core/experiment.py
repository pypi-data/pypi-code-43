from typing import List, Union
from .project import Project
from .utils import *

class Experiment:

    def __init__(self, project: Project, name: str = 'Untitled Experiment', notes: str = '', seed: int = None,
                 devices: Union[List[int], List[str], List[torch.device]] = None, tensorboard: bool = True):

        # general properties
        self.id: str = generate_random_id()
        self.project: Project = project
        self.name: str = name
        self.fname: str = generate_fname(name)
        self.notes: str = notes
        self.path: Path = project.path / self.fname
        self.path.mkdir(parents=True)  # TODO: this should never happen, but it can raise FileExistError

        # save git commit id at the moment of running the experiment
        # TODO bonus points: make .patch file to see what was changed since last commit!
        # TODO bonus bonus points: method to open github website at that revision?
        self.code = get_current_git_head()

        # determinism
        # cudnn_deterministic is slower, but gives almaximum possible determinism
        if seed is None:
            self.seed: int = generate_random_seed()
        else:
            self.seed: int = seed
        set_seed(self.seed, cudnn_deterministic=False)

        # devices
        if devices is None:
            self.devices = [0]
        else:
            self.devices = devices
        # during model initialization torch spills some memory to the GPU0 (not necessarily GPU that we will use)
        torch.cuda.set_device(self.devices[0])

        # tensorboard
        self.tensorboard = tensorboard
        # TODO figure out how (where) to integrate tensorboard - maybe a separate new process to run tensorboard + trainer

        # history
        self.history = []
        # TODO history saving
        # some kind of history rows, to be able to store actions and their results
        # and to store metrics history?

    def new_trainer(self, ):
        pass

    # TODO decorator for functions that should log entry and exit?
    def log(self, action: str,):
        pass
