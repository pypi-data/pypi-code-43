import lightgbm

from azureml.studio.common.parameter_range import ParameterRangeSettings, Sweepable
from azureml.studio.modulehost.attributes import ModeParameter, FloatParameter, IntParameter, \
    ParameterRangeParameter, ReleaseState, UntrainedLearnerOutputPort, ModuleMeta, BooleanParameter
from azureml.studio.modulehost.module_reflector import module_entry, BaseModule
from azureml.studio.modules.ml.common.base_learner import BaseLearner, TaskType, CreateLearnerMode, RestoreInfo
from azureml.studio.modules.ml.common.base_learner_setting import BaseLearnerSetting


class TwoClassBoostedDecisionTreeModuleDefaultParameters:
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


class TwoClassBoostedDecisionTreeModule(BaseModule):

    @staticmethod
    @module_entry(ModuleMeta(
        name="Two-Class Boosted Decision Tree",
        description="Creates a binary classifier using a boosted decision tree algorithm",
        category="Machine Learning\\Initialize Model\\Classification",
        version="2.0",
        owner="Microsoft Corporation",
        family_id="E3C522F8-53D9-4829-8EA4-5C6A6B75330C",
        release_state=ReleaseState.Release,
        is_deterministic=True,
    ))
    def run(
            mode: ModeParameter(
                CreateLearnerMode,
                name="Create trainer mode",
                friendly_name="Create trainer mode",
                description="Create advanced learner options",
                default_value=TwoClassBoostedDecisionTreeModuleDefaultParameters.Mode,
            ),
            number_of_leaves: IntParameter(
                name="Maximum number of leaves per tree",
                friendly_name="Maximum number of leaves per tree",
                description="Specify the maximum number of leaves allowed per tree",
                default_value=TwoClassBoostedDecisionTreeModuleDefaultParameters.NumberOfLeaves,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=1,
            ),
            minimum_leaf_instances: IntParameter(
                name="Minimum number of training instances required to form a leaf",
                friendly_name="Minimum number of samples per leaf node",
                description="Specify the minimum number of cases required to form a leaf",
                default_value=TwoClassBoostedDecisionTreeModuleDefaultParameters.MinimumLeafInstances,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=1,
            ),
            learning_rate: FloatParameter(
                name="The learning rate",
                friendly_name="Learning rate",
                description="Specify the initial learning rate",
                default_value=TwoClassBoostedDecisionTreeModuleDefaultParameters.LearningRate,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=4.94065645841247E-324,
                max_value=1,
            ),
            num_trees: IntParameter(
                name="Total number of trees constructed",
                friendly_name="Number of trees constructed",
                description="Specify the maximum number of trees that can be created during training",
                default_value=TwoClassBoostedDecisionTreeModuleDefaultParameters.NumTrees,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=1,
            ),
            ps_number_of_leaves: ParameterRangeParameter(
                name="Range for maximum number of leaves per tree",
                friendly_name="Maximum number of leaves per tree",
                description="Specify range for the maximum number of leaves allowed per tree",
                default_value=TwoClassBoostedDecisionTreeModuleDefaultParameters.PsNumberOfLeaves,
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
                default_value=TwoClassBoostedDecisionTreeModuleDefaultParameters.PsMinimumLeafInstances,
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
                default_value=TwoClassBoostedDecisionTreeModuleDefaultParameters.PsLearningRate,
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
                default_value=TwoClassBoostedDecisionTreeModuleDefaultParameters.PsNumTrees,
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
                default_value=TwoClassBoostedDecisionTreeModuleDefaultParameters.AllowUnknownLevels,
                release_state=ReleaseState.Alpha
            )
    ) -> (
            UntrainedLearnerOutputPort(
                name="Untrained model",
                friendly_name="Untrained model",
                description="An untrained binary classification model",
            ),
    ):
        input_values = locals()
        output_values = TwoClassBoostedDecisionTreeModule.create_boosted_decision_tree_biclassifier(**input_values)
        return output_values

    @staticmethod
    def create_boosted_decision_tree_biclassifier(
            mode: CreateLearnerMode = TwoClassBoostedDecisionTreeModuleDefaultParameters.Mode,
            number_of_leaves: int = TwoClassBoostedDecisionTreeModuleDefaultParameters.NumberOfLeaves,
            ps_number_of_leaves: ParameterRangeSettings =
            TwoClassBoostedDecisionTreeModuleDefaultParameters.PsNumberOfLeaves,
            minimum_leaf_instances: int = TwoClassBoostedDecisionTreeModuleDefaultParameters.MinimumLeafInstances,
            ps_minimum_leaf_instances: ParameterRangeSettings =
            TwoClassBoostedDecisionTreeModuleDefaultParameters.PsMinimumLeafInstances,
            learning_rate: float = TwoClassBoostedDecisionTreeModuleDefaultParameters.LearningRate,
            ps_learning_rate: ParameterRangeSettings =
            TwoClassBoostedDecisionTreeModuleDefaultParameters.PsLearningRate,
            num_trees: int = TwoClassBoostedDecisionTreeModuleDefaultParameters.NumTrees,
            ps_num_trees: ParameterRangeSettings = TwoClassBoostedDecisionTreeModuleDefaultParameters.PsNumTrees,
            random_number_seed: int = TwoClassBoostedDecisionTreeModuleDefaultParameters.RandomNumberSeed,
            allow_unknown_levels: bool = TwoClassBoostedDecisionTreeModuleDefaultParameters.AllowUnknownLevels,
    ):
        setting = BoostDecisionTreeBiClassifierSetting()
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
        return tuple([BoostDecisionTreeBiClassifier(setting)])


class BoostDecisionTreeBiClassifierSetting(BaseLearnerSetting):
    def __init__(self):
        super().__init__()
        self.number_of_leaves = TwoClassBoostedDecisionTreeModuleDefaultParameters.NumberOfLeaves
        self.minimum_leaf_instances = TwoClassBoostedDecisionTreeModuleDefaultParameters.MinimumLeafInstances
        self.learning_rate = TwoClassBoostedDecisionTreeModuleDefaultParameters.LearningRate
        self.num_trees = TwoClassBoostedDecisionTreeModuleDefaultParameters.NumTrees
        self.parameter_range = {
            'num_leaves': Sweepable.from_prs(
                "max_leaf_nodes", ParameterRangeSettings.from_literal(
                    TwoClassBoostedDecisionTreeModuleDefaultParameters.PsNumberOfLeaves)).attribute_value,
            'min_child_samples': Sweepable.from_prs(
                "min_samples_leaf", ParameterRangeSettings.from_literal(
                    TwoClassBoostedDecisionTreeModuleDefaultParameters.PsMinimumLeafInstances)).attribute_value,
            'learning_rate': Sweepable.from_prs(
                "learning_rate",
                ParameterRangeSettings.from_literal(
                    TwoClassBoostedDecisionTreeModuleDefaultParameters.PsLearningRate)).attribute_value,
            'n_estimators': Sweepable.from_prs(
                "n_estimators", ParameterRangeSettings.from_literal(
                    TwoClassBoostedDecisionTreeModuleDefaultParameters.PsNumTrees)).attribute_value,
        }
        self.create_learner_mode = None

    def init_single(
            self,
            number_of_leaves: int = TwoClassBoostedDecisionTreeModuleDefaultParameters.NumberOfLeaves,
            minimum_leaf_instances: int = TwoClassBoostedDecisionTreeModuleDefaultParameters.MinimumLeafInstances,
            learning_rate: float = TwoClassBoostedDecisionTreeModuleDefaultParameters.LearningRate,
            num_trees: int = TwoClassBoostedDecisionTreeModuleDefaultParameters.NumTrees,
            random_number_seed: int = TwoClassBoostedDecisionTreeModuleDefaultParameters.RandomNumberSeed
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


class BoostDecisionTreeBiClassifier(BaseLearner):
    def __init__(self, setting: BoostDecisionTreeBiClassifierSetting):
        super().__init__(setting=setting, task_type=TaskType.BinaryClassification)

    @property
    def parameter_mapping(self):
        return {
            'num_leaves': RestoreInfo(TwoClassBoostedDecisionTreeModule._args.number_of_leaves.friendly_name),
            'min_child_samples': RestoreInfo(
                TwoClassBoostedDecisionTreeModule._args.minimum_leaf_instances.friendly_name),
            'learning_rate': RestoreInfo(TwoClassBoostedDecisionTreeModule._args.learning_rate.friendly_name),
            'n_estimators': RestoreInfo(TwoClassBoostedDecisionTreeModule._args.num_trees.friendly_name)
        }

    def init_model(self):
        self.model = lightgbm.LGBMClassifier(
            # Todo[linchi]:  max_depth: the best value depends on the interaction of the input variables. [10, 100]
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
