from sklearn.multiclass import OneVsOneClassifier

from azureml.studio.common.error import ErrorMapping, InvalidLearnerError
from azureml.studio.modulehost.attributes import UntrainedLearnerInputPort, UntrainedLearnerOutputPort, \
    ReleaseState, ModuleMeta
from azureml.studio.modulehost.module_reflector import module_entry, BaseModule
from azureml.studio.modules.ml.common.base_learner import BaseLearner
from azureml.studio.modules.ml.common.ml_utils import TaskType


class OneVsAllMulticlassModule(BaseModule):
    @staticmethod
    @module_entry(ModuleMeta(
        name="One-vs-All Multiclass",
        description="Creates a multiclass classification model from an ensemble of binary classification models",
        category="Machine Learning\\Initialize Model\\Classification",
        version="1.0",
        owner="Microsoft Corporation",
        family_id="7191EFAE-B4B1-4D03-A6F8-7205F87BE664",
        release_state=ReleaseState.Beta,
        is_deterministic=True,
    ))
    def run(
            learner: UntrainedLearnerInputPort(
                name="Untrained binary classification model",
                friendly_name="Untrained binary classification model",
                description="An untrained binary classification model",
            )
    ) -> (
            UntrainedLearnerOutputPort(
                name="Untrained model",
                friendly_name="Untrained model",
                description="An untrained multi-class classification",
            ),
    ):
        input_values = locals()
        output_values = OneVsAllMulticlassModule.create_one_vs_all_multiclassifier(**input_values)
        return output_values

    @classmethod
    def create_one_vs_all_multiclassifier(cls, learner: BaseLearner):
        if learner.task_type != TaskType.BinaryClassification:
            # The input learner must be a binary classifier
            ErrorMapping.throw(
                InvalidLearnerError(arg_name=cls._args.learner.friendly_name, learner_type=learner.__class__.__name__))

        one_vs_all_classifier = OneVsAllMultiClassifier(learner.setting, task_type=TaskType.MultiClassification,
                                                        sub_model=learner)
        return one_vs_all_classifier,


class OneVsAllMultiClassifier(BaseLearner):
    _PARAMETER_PREFIX = 'estimator__'

    def __init__(self, setting, task_type, sub_model):
        super().__init__(setting=setting, task_type=task_type)
        self.sub_model = sub_model

    def gen_inter_name(self, name):
        return self._PARAMETER_PREFIX + name

    @property
    def parameter_mapping(self):
        sub_mapping = self.sub_model.parameter_mapping
        return {self.gen_inter_name(key): val for key, val in sub_mapping.items()}

    @property
    def parameter_range(self):
        sub_parameter_range = self.sub_model.parameter_range
        return {self.gen_inter_name(key): val for key, val in sub_parameter_range.items()}

    def init_model(self):
        self.sub_model.init_model()
        self.model = OneVsOneClassifier(self.sub_model.model)
