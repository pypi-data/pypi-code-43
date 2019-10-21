import lightgbm

from azureml.studio.common.parameter_range import ParameterRangeSettings, Sweepable
from azureml.studio.modulehost.attributes import ModeParameter, FloatParameter, IntParameter, \
    ParameterRangeParameter, ReleaseState, UntrainedLearnerOutputPort, ModuleMeta, BooleanParameter
from azureml.studio.modulehost.module_reflector import module_entry, BaseModule
from azureml.studio.modules.ml.common.base_learner import BaseLearner, TaskType, CreateLearnerMode, RestoreInfo
from azureml.studio.modules.ml.common.base_learner_setting import BaseLearnerSetting


class MultiClassBoostedDecisionTreeModuleDefaultParameters:
    Mode = CreateLearnerMode.SingleParameter
    NumberOfLeaves = 20
    MinimumLeafInstances = 10
    LearningRate = 0.2
    NumTrees = 100
    PsNumberOfLeaves = "2; 8; 32; 128"
    PsMinimumLeafInstances = "1; 10; 50"
    PsLearningRate = "0.025; 0.05; 0.1; 0.2; 0.4"
    PsNumTrees = "20; 100; 500"
    RandomNumberSeed = None
    AllowUnknownLevels = True

    @classmethod
    def to_dict(cls):
        return {
            "mode": cls.Mode,
            "number_of_leaves": cls.NumberOfLeaves,
            "minimum_leaf_instances": cls.MinimumLeafInstances,
            "learning_rate": cls.LearningRate,
            "num_trees": cls.NumTrees,
            "ps_number_of_leaves": cls.PsNumberOfLeaves,
            "ps_minimum_leaf_instances": cls.PsMinimumLeafInstances,
            "ps_learning_rate": cls.PsLearningRate,
            "ps_num_trees": cls.PsNumTrees,
            "random_number_seed": cls.RandomNumberSeed,
            "allow_unknown_levels": cls.AllowUnknownLevels,
        }


class MultiClassBoostedDecisionTreeModule(BaseModule):

    @staticmethod
    @module_entry(ModuleMeta(
        name="MultiClass Boosted Decision Tree",
        description="Creates a multiclass classifier using a boosted decision tree algorithm",
        category="Machine Learning\\Initialize Model\\Classification",
        version="2.0",
        owner="Microsoft Corporation",
        family_id="1D67B731-34D7-4ADB-BC2A-A8844CD1BD2D",
        release_state=ReleaseState.Release,
        is_deterministic=True,
    ))
    def run(
            mode: ModeParameter(
                CreateLearnerMode,
                name="Create trainer mode",
                friendly_name="Create trainer mode",
                description="Create advanced learner options",
                default_value=MultiClassBoostedDecisionTreeModuleDefaultParameters.Mode,
            ),
            number_of_leaves: IntParameter(
                name="Maximum number of leaves per tree",
                friendly_name="Maximum number of leaves per tree",
                description="Specify the maximum number of leaves allowed per tree",
                default_value=MultiClassBoostedDecisionTreeModuleDefaultParameters.NumberOfLeaves,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=1,
            ),
            minimum_leaf_instances: IntParameter(
                name="Minimum number of training instances required to form a leaf",
                friendly_name="Minimum number of samples per leaf node",
                description="Specify the minimum number of cases required to form a leaf",
                default_value=MultiClassBoostedDecisionTreeModuleDefaultParameters.MinimumLeafInstances,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=1,
            ),
            learning_rate: FloatParameter(
                name="The learning rate",
                friendly_name="Learning rate",
                description="Specify the initial learning rate",
                default_value=MultiClassBoostedDecisionTreeModuleDefaultParameters.LearningRate,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=4.94065645841247E-324,
                max_value=1,
            ),
            num_trees: IntParameter(
                name="Total number of trees constructed",
                friendly_name="Number of trees constructed",
                description="Specify the maximum number of trees that can be created during training",
                default_value=MultiClassBoostedDecisionTreeModuleDefaultParameters.NumTrees,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=1,
            ),
            ps_number_of_leaves: ParameterRangeParameter(
                name="Range for maximum number of leaves per tree",
                friendly_name="Maximum number of leaves per tree",
                description="Specify range for the maximum number of leaves allowed per tree",
                default_value=MultiClassBoostedDecisionTreeModuleDefaultParameters.PsNumberOfLeaves,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=1,
                max_limit=2147483647,
                is_int=True,
                is_log=True,
                slider_min=1,
                slider_max=1000,
            ),
            ps_minimum_leaf_instances: ParameterRangeParameter(
                name="Range for minimum number of training instances required to form a leaf",
                friendly_name="Minimum number of samples per leaf node",
                description="Specify the range for the minimum number of cases required to form a leaf",
                default_value=MultiClassBoostedDecisionTreeModuleDefaultParameters.PsMinimumLeafInstances,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=1,
                max_limit=2147483647,
                is_int=True,
                is_log=True,
                slider_min=1,
                slider_max=1000,
            ),
            ps_learning_rate: ParameterRangeParameter(
                name="Range for learning rate",
                friendly_name="Learning rate",
                description="Specify the range for the initial learning rate",
                default_value=MultiClassBoostedDecisionTreeModuleDefaultParameters.PsLearningRate,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=1.401298E-45,
                max_limit=1,
                is_int=False,
                is_log=True,
                slider_min=1E-06,
                slider_max=1,
            ),
            ps_num_trees: ParameterRangeParameter(
                name="Range for total number of trees constructed",
                friendly_name="Number of trees constructed",
                description="Specify the range for the maximum number of trees that can be created during training",
                default_value=MultiClassBoostedDecisionTreeModuleDefaultParameters.PsNumTrees,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=1,
                max_limit=2147483647,
                is_int=True,
                is_log=True,
                slider_min=1,
                slider_max=10000,
            ),
            random_number_seed: IntParameter(
                name="Random number seed",
                friendly_name="Random number seed",
                is_optional=True,
                description="Type a value to seed the random number generator used by the model. "
                            "Leave blank for default.",
            ),
            allow_unknown_levels: BooleanParameter(
                name="Allow unknown levels in categorical features",
                friendly_name="Allow unknown categorical levels",
                description="If true creates an additional level for each categorical column. "
                            "Any levels in the test dataset not available in the training dataset "
                            "are mapped to this additional level.",
                default_value=MultiClassBoostedDecisionTreeModuleDefaultParameters.AllowUnknownLevels,
                release_state=ReleaseState.Alpha
            )
    ) -> (
            UntrainedLearnerOutputPort(
                name="Untrained model",
                friendly_name="Untrained model",
                description="An untrained multiclass classification model",
            ),
    ):
        input_values = locals()
        output_values = MultiClassBoostedDecisionTreeModule.create_boosted_decision_tree_multiclassifier(**input_values)
        return output_values

    @staticmethod
    def create_boosted_decision_tree_multiclassifier(
            mode: CreateLearnerMode = MultiClassBoostedDecisionTreeModuleDefaultParameters.Mode,
            number_of_leaves: int = MultiClassBoostedDecisionTreeModuleDefaultParameters.NumberOfLeaves,
            ps_number_of_leaves: ParameterRangeSettings =
            MultiClassBoostedDecisionTreeModuleDefaultParameters.PsNumberOfLeaves,
            minimum_leaf_instances: int = MultiClassBoostedDecisionTreeModuleDefaultParameters.MinimumLeafInstances,
            ps_minimum_leaf_instances: ParameterRangeSettings =
            MultiClassBoostedDecisionTreeModuleDefaultParameters.PsMinimumLeafInstances,
            learning_rate: float = MultiClassBoostedDecisionTreeModuleDefaultParameters.LearningRate,
            ps_learning_rate: ParameterRangeSettings =
            MultiClassBoostedDecisionTreeModuleDefaultParameters.PsLearningRate,
            num_trees: int = MultiClassBoostedDecisionTreeModuleDefaultParameters.NumTrees,
            ps_num_trees: ParameterRangeSettings = MultiClassBoostedDecisionTreeModuleDefaultParameters.PsNumTrees,
            random_number_seed: int = MultiClassBoostedDecisionTreeModuleDefaultParameters.RandomNumberSeed,
            allow_unknown_levels: bool = MultiClassBoostedDecisionTreeModuleDefaultParameters.AllowUnknownLevels
    ):
        setting = BoostedDecisionTreeMultiClassifierSetting()
        if mode == CreateLearnerMode.SingleParameter:
            setting.init_single(
                number_of_leaves=number_of_leaves,
                minimum_leaf_instances=minimum_leaf_instances,
                learning_rate=learning_rate,
                num_trees=num_trees,
                random_number_seed=random_number_seed)
        else:
            setting.init_range(
                ps_number_of_leaves=ps_number_of_leaves,
                ps_minimum_leaf_instances=ps_minimum_leaf_instances,
                ps_learning_rate=ps_learning_rate,
                ps_num_trees=ps_num_trees,
                random_number_seed=random_number_seed)
        return tuple([BoostedDecisionTreeMultiClassifier(setting)])


class BoostedDecisionTreeMultiClassifierSetting(BaseLearnerSetting):
    def __init__(self):
        super().__init__()
        self.number_of_leaves = MultiClassBoostedDecisionTreeModuleDefaultParameters.NumberOfLeaves
        self.minimum_leaf_instances = MultiClassBoostedDecisionTreeModuleDefaultParameters.MinimumLeafInstances
        self.learning_rate = MultiClassBoostedDecisionTreeModuleDefaultParameters.LearningRate
        self.num_trees = MultiClassBoostedDecisionTreeModuleDefaultParameters.NumTrees
        self.create_learner_mode = MultiClassBoostedDecisionTreeModuleDefaultParameters.Mode
        self.parameter_range = {
            'num_leaves': Sweepable.from_prs(
                "max_leaf_nodes", ParameterRangeSettings.from_literal(
                    MultiClassBoostedDecisionTreeModuleDefaultParameters.PsNumberOfLeaves)).attribute_value,
            'min_child_samples': Sweepable.from_prs(
                "min_samples_leaf", ParameterRangeSettings.from_literal(
                    MultiClassBoostedDecisionTreeModuleDefaultParameters.PsMinimumLeafInstances)).attribute_value,
            'learning_rate': Sweepable.from_prs(
                "learning_rate",
                ParameterRangeSettings.from_literal(
                    MultiClassBoostedDecisionTreeModuleDefaultParameters.PsLearningRate)).attribute_value,
            'n_estimators': Sweepable.from_prs(
                "n_estimators", ParameterRangeSettings.from_literal(
                    MultiClassBoostedDecisionTreeModuleDefaultParameters.PsNumTrees)).attribute_value,
        }

    def init_single(
            self,
            number_of_leaves: int = MultiClassBoostedDecisionTreeModuleDefaultParameters.NumberOfLeaves,
            minimum_leaf_instances: int = MultiClassBoostedDecisionTreeModuleDefaultParameters.MinimumLeafInstances,
            learning_rate: float = MultiClassBoostedDecisionTreeModuleDefaultParameters.LearningRate,
            num_trees: int = MultiClassBoostedDecisionTreeModuleDefaultParameters.NumTrees,
            random_number_seed: int = MultiClassBoostedDecisionTreeModuleDefaultParameters.RandomNumberSeed
    ):
        self.create_learner_mode = CreateLearnerMode.SingleParameter
        self.number_of_leaves = number_of_leaves
        self.minimum_leaf_instances = minimum_leaf_instances
        self.learning_rate = learning_rate
        self.num_trees = num_trees
        self.random_number_seed = random_number_seed

    def init_range(self, ps_number_of_leaves: ParameterRangeSettings = None,
                   ps_minimum_leaf_instances: ParameterRangeSettings = None,
                   ps_learning_rate: ParameterRangeSettings = None,
                   ps_num_trees: ParameterRangeSettings = None,
                   random_number_seed: int = None):
        self.create_learner_mode = CreateLearnerMode.ParameterRange
        self.random_number_seed = random_number_seed

        self.add_sweepable(Sweepable.from_prs('num_leaves', ps_number_of_leaves))
        self.add_sweepable(Sweepable.from_prs('min_child_samples', ps_minimum_leaf_instances))
        self.add_sweepable(Sweepable.from_prs('learning_rate', ps_learning_rate))
        self.add_sweepable(Sweepable.from_prs('n_estimators', ps_num_trees))


class BoostedDecisionTreeMultiClassifier(BaseLearner):
    def __init__(self, setting: BoostedDecisionTreeMultiClassifierSetting):
        super().__init__(setting=setting, task_type=TaskType.MultiClassification)

    @property
    def parameter_mapping(self):
        return {
            'num_leaves': RestoreInfo(MultiClassBoostedDecisionTreeModule._args.number_of_leaves.friendly_name),
            'min_child_samples': RestoreInfo(
                MultiClassBoostedDecisionTreeModule._args.minimum_leaf_instances.friendly_name),
            'learning_rate': RestoreInfo(MultiClassBoostedDecisionTreeModule._args.learning_rate.friendly_name),
            'n_estimators': RestoreInfo(MultiClassBoostedDecisionTreeModule._args.num_trees.friendly_name)
        }

    def init_model(self):
        self.model = lightgbm.LGBMClassifier(
            max_depth=3,
            num_leaves=self.setting.number_of_leaves,
            min_child_samples=self.setting.minimum_leaf_instances,
            n_estimators=self.setting.num_trees,
            learning_rate=self.setting.learning_rate,
            random_state=self.setting.random_number_seed,
            subsample=0.6,  # use sub sample lead to reduction of variance and an increase in bias.
            colsample_bytree=0.6,
            verbosity=1,
            n_jobs=-1,
        )
