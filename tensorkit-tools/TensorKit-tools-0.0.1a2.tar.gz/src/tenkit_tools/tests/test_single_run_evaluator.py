
import pytest

from tenkit_tools.evaluation.base_evaluator import test_defaults
from tenkit_tools.datareader import NumpyDataReader
@pytest.fixture
def num_samples():
    return 30

def random_summary(random_tensor):
    summary = {
        "dataset_path": 'path?',
        "model_type": 'CP_ALS',
        "model_rank": 3,
        "dataset_shape": random_tensor.shape,
        "experiment_completed": True, 
        "best_run": "run_011.h5", 
        "best_fit": 0.9, 
        "best_loss": 10, 
        "std_loss": 0.001, 
        "std_fit": 0.001}

@pytest.fixture
def random_tensor(num_samples):
    return np.random.randn(num_samples, 20, 40)

@pytest.fixture
def random_classes(num_samples):
    return [{}, {'class':np.random.randint(0, high=2, size=num_samples)}, {}]

@pytest.fixture
def random_datareader(random_tensor, random_classes):
    return NumpyDataReader(tensor=random_tensor, classes=random_classes)

def test_evaluator_creation(random_summary, random_datareader):
    # TODO: 
    # trenger random summary og random h5
    for Evaluator, kwargs in test_defaults.items():
        evaluator = Evaluator(random_summary, **kwargs)
        evaluator._evaluate(random_datareader, h5)