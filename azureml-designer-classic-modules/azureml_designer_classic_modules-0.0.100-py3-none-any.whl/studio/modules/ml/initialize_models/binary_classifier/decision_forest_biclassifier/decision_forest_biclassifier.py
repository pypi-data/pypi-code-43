from sklearn.ensemble import RandomForestClassifier

from azureml.studio.common.parameter_range import ParameterRangeSettings, Sweepable
from azureml.studio.common.types import AutoEnum
from azureml.studio.modulehost.attributes import ModeParameter, IntParameter, \
    ParameterRangeParameter, ReleaseState, UntrainedLearnerOutputPort, ModuleMeta, ItemInfo, BooleanParameter
from azureml.studio.modulehost.module_reflector import module_entry, BaseModule
from azureml.studio.modules.ml.common.base_learner import BaseLearner, TaskType, CreateLearnerMode, RestoreInfo
from azureml.studio.modules.ml.common.base_learner_setting import BaseLearnerSetting


class ResamplingMethod(AutoEnum):
    Bagging: ItemInfo(name='Bagging Resampling', friendly_name="Bagging Resampling") = ()
    Replicate: ItemInfo(name="Replicate Resampling", friendly_name="Replicate Resampling") = ()


class TwoClassDecisionForestModuleDefaultParameters:
    Mode = CreateLearnerMode.SingleParameter
    ResamplingMethod = ResamplingMethod.Bagging
    TreeCount = 8
    MaxDepth = 32
    RandomSplitCount = 128
    MinLeafSampleCount = 1
    PsTreeCount = "1; 8; 32"
    PsMaxDepth = "1; 16; 64"
    PsRandomSplitCount = "1; 128; 1024"
    PsMinLeafSampleCount = "1; 4; 16"
    AllowUnknownLevels = True

    @classmethod
    def to_dict(cls):
        return {
            "mode": cls.Mode,
            "resampling_method": cls.ResamplingMethod,
            "tree_count": cls.TreeCount,
            "max_depth": cls.MaxDepth,
            "random_split_count": cls.RandomSplitCount,
            "min_leaf_sample_count": cls.MinLeafSampleCount,
            "ps_tree_count": cls.PsTreeCount,
            "ps_max_depth": cls.PsMaxDepth,
            "ps_random_split_count": cls.PsRandomSplitCount,
            "ps_min_leaf_sample_count": cls.PsMinLeafSampleCount,
            "allow_unknown_levels": cls.AllowUnknownLevels,
        }


class TwoClassDecisionForestModule(BaseModule):

    @staticmethod
    @module_entry(ModuleMeta(
        name="Two-Class Decision Forest",
        description="Creates a two-class classification model using the decision forest algorithm",
        category="Machine Learning\\Initialize Model\\Classification",
        version="2.0",
        owner="Microsoft Corporation",
        family_id="5A7D5466-9928-40C8-A19C-D5DE4882C77E",
        release_state=ReleaseState.Release,
        is_deterministic=True,
    ))
    def run(
            mode: ModeParameter(
                CreateLearnerMode,
                name="Create trainer mode",
                friendly_name="Create trainer mode",
                description="Create advanced learner options",
                default_value=TwoClassDecisionForestModuleDefaultParameters.Mode,
            ),
            resampling_method: ModeParameter(
                ResamplingMethod,
                name="Resampling method",
                friendly_name="Resampling method",
                description="Choose a resampling method",
                default_value=TwoClassDecisionForestModuleDefaultParameters.ResamplingMethod,
            ),
            tree_count: IntParameter(
                name="Number of decision trees",
                friendly_name="Number of decision trees",
                description="Specify the number of decision trees to create in the ensemble",
                default_value=TwoClassDecisionForestModuleDefaultParameters.TreeCount,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=1,
            ),
            max_depth: IntParameter(
                name="Maximum depth of the decision trees",
                friendly_name="Maximum depth of the decision trees",
                description="Specify the maximum depth of any decision tree that can be created in the ensemble",
                default_value=TwoClassDecisionForestModuleDefaultParameters.MaxDepth,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=1,
            ),
            random_split_count: IntParameter(
                name="Number of random splits per node",
                friendly_name="Number of random splits per node",
                description="Specify the number of splits generated per node, from which the optimal split is selected",
                default_value=TwoClassDecisionForestModuleDefaultParameters.RandomSplitCount,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=1,
                release_state=ReleaseState.Alpha
            ),
            min_leaf_sample_count: IntParameter(
                name="Minimum number of samples per leaf node",
                friendly_name="Minimum number of samples per leaf node",
                description="Specify the minimum number of training samples required to generate a leaf node",
                default_value=TwoClassDecisionForestModuleDefaultParameters.MinLeafSampleCount,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=1,
            ),
            ps_tree_count: ParameterRangeParameter(
                name="Range for number of decision trees",
                friendly_name="Number of decision trees",
                description="Specify range for the number of decision trees to create in the ensemble",
                default_value=TwoClassDecisionForestModuleDefaultParameters.PsTreeCount,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=1,
                max_limit=2147483647,
                is_int=True,
                is_log=True,
                slider_min=1,
                slider_max=1024,
            ),
            ps_max_depth: ParameterRangeParameter(
                name="Range for the maximum depth of the decision trees",
                friendly_name="Maximum depth of the decision trees",
                description="Specify range for the maximum depth of the decision trees",
                default_value=TwoClassDecisionForestModuleDefaultParameters.PsMaxDepth,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=1,
                max_limit=2147483647,
                is_int=True,
                is_log=True,
                slider_min=1,
                slider_max=1024,
            ),
            ps_random_split_count: ParameterRangeParameter(
                name="Range for the number of random splits per node",
                friendly_name="Number of random splits per node",
                description="Specify range for the number of random splits per node",
                default_value=TwoClassDecisionForestModuleDefaultParameters.PsRandomSplitCount,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=1,
                max_limit=2147483647,
                is_int=True,
                is_log=True,
                slider_min=1,
                slider_max=8196,
                release_state=ReleaseState.Alpha
            ),
            ps_min_leaf_sample_count: ParameterRangeParameter(
                name="Range for the minimum number of samples per leaf node",
                friendly_name="Minimum number of samples per leaf node",
                description="Specify range for the minimum number of samples per leaf node",
                default_value=TwoClassDecisionForestModuleDefaultParameters.PsMinLeafSampleCount,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=1,
                max_limit=2147483647,
                is_int=True,
                is_log=True,
                slider_min=1,
                slider_max=64,
            ),
            allow_unknown_levels: BooleanParameter(
                name="Allow unknown values for categorical features",
                friendly_name="Allow unknown values for categorical features",
                description="Indicate whether unknown values of existing categorical features "
                            "can be mapped to a new, additional feature",
                default_value=TwoClassDecisionForestModuleDefaultParameters.AllowUnknownLevels,
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
        output_values = TwoClassDecisionForestModule.create_decision_forest_biclassifier(**input_values)
        return output_values

    @staticmethod
    def create_decision_forest_biclassifier(
            mode: CreateLearnerMode = TwoClassDecisionForestModuleDefaultParameters.Mode,
            resampling_method: ResamplingMethod = TwoClassDecisionForestModuleDefaultParameters.ResamplingMethod,
            tree_count: int = TwoClassDecisionForestModuleDefaultParameters.TreeCount,
            ps_tree_count: ParameterRangeSettings = TwoClassDecisionForestModuleDefaultParameters.PsTreeCount,
            max_depth: int = TwoClassDecisionForestModuleDefaultParameters.MaxDepth,
            ps_max_depth: ParameterRangeSettings = TwoClassDecisionForestModuleDefaultParameters.PsMaxDepth,
            random_split_count: int = TwoClassDecisionForestModuleDefaultParameters.RandomSplitCount,
            ps_random_split_count: ParameterRangeSettings =
            TwoClassDecisionForestModuleDefaultParameters.PsRandomSplitCount,
            min_leaf_sample_count: int = TwoClassDecisionForestModuleDefaultParameters.MinLeafSampleCount,
            ps_min_leaf_sample_count: ParameterRangeSettings =
            TwoClassDecisionForestModuleDefaultParameters.PsMinLeafSampleCount,
            allow_unknown_levels: bool = TwoClassDecisionForestModuleDefaultParameters.AllowUnknownLevels,
    ):
        setting = DecisionForestBiClassifierSetting()
        if mode == CreateLearnerMode.SingleParameter:
            setting.init_single(
                resampling_method=resampling_method,
                tree_count=tree_count,
                max_depth=max_depth,
                random_split_count=random_split_count,
                min_leaf_sample_count=min_leaf_sample_count
            )
        else:
            setting.init_range(
                resampling_method=resampling_method,
                ps_tree_count=ps_tree_count, ps_max_depth=ps_max_depth,
                ps_random_split_count=ps_random_split_count,
                ps_min_leaf_sample_count=ps_min_leaf_sample_count)
        return tuple([DecisionForestBiClassifier(setting)])


class DecisionForestBiClassifierSetting(BaseLearnerSetting):
    def __init__(self):
        """
        there remains some problem:
        1. Decision Forest is a gemini model, not TLC model, only be used in inter-microsoft.
           There, we use Random Forest Algorithm instead.
            And may use nimbusML.decision forest in the future.
        2. max_features should be in (0, n_features)
        """
        super().__init__()
        self.resampling_method = TwoClassDecisionForestModuleDefaultParameters.ResamplingMethod
        self.tree_count = TwoClassDecisionForestModuleDefaultParameters.TreeCount
        self.max_depth = TwoClassDecisionForestModuleDefaultParameters.MaxDepth
        self.random_split_count = TwoClassDecisionForestModuleDefaultParameters.RandomSplitCount
        self.min_leaf_sample_count = TwoClassDecisionForestModuleDefaultParameters.MinLeafSampleCount
        self.create_learner_mode = TwoClassDecisionForestModuleDefaultParameters.Mode
        self.parameter_range = {
            'n_estimators': Sweepable.from_prs(
                "n_estimators", ParameterRangeSettings.from_literal(
                    TwoClassDecisionForestModuleDefaultParameters.PsTreeCount)).attribute_value,
            'max_depth': Sweepable.from_prs(
                "max_depth", ParameterRangeSettings.from_literal(
                    TwoClassDecisionForestModuleDefaultParameters.PsMaxDepth)).attribute_value,
            # 'max_features': Sweepable.from_prs(
            #    "max_features", ParameterRangeSettings.from_literal(
            #        TwoClassDecisionForestModuleDefaultParameters.PsRandomSplitCount)).attribute_value,
            'min_samples_leaf': Sweepable.from_prs(
                "min_samples_leaf", ParameterRangeSettings.from_literal(
                    TwoClassDecisionForestModuleDefaultParameters.PsMinLeafSampleCount)).attribute_value,
        }

    def init_single(
            self,
            resampling_method: ResamplingMethod = TwoClassDecisionForestModuleDefaultParameters.ResamplingMethod,
            tree_count: int = TwoClassDecisionForestModuleDefaultParameters.TreeCount,
            max_depth: int = TwoClassDecisionForestModuleDefaultParameters.MaxDepth,
            random_split_count: int = TwoClassDecisionForestModuleDefaultParameters.RandomSplitCount,
            min_leaf_sample_count: int = TwoClassDecisionForestModuleDefaultParameters.MinLeafSampleCount):
        """
        :param resampling_method: ResamplingMethod.  bootstrap: bagging is mapped to True, and replicate to False.
        :param tree_count: int, number of decision tree. n_estimators
        :param max_depth: int, Maximum depth of the decision trees. max_depth
        :param random_split_count: int, Number of random splits per node and splits mean feature.
        :param min_leaf_sample_count: int, Minimum number of samples per leaf node. min_samples_leaf
        """
        self.create_learner_mode = CreateLearnerMode.SingleParameter
        self.resampling_method = resampling_method
        self.tree_count = tree_count
        self.max_depth = max_depth
        self.random_split_count = random_split_count
        self.min_leaf_sample_count = min_leaf_sample_count

    def init_range(self, resampling_method: ResamplingMethod = ResamplingMethod.Bagging,
                   ps_tree_count: ParameterRangeSettings = None,
                   ps_max_depth: ParameterRangeSettings = None, ps_random_split_count: ParameterRangeSettings = None,
                   ps_min_leaf_sample_count: ParameterRangeSettings = 1):
        self.create_learner_mode = CreateLearnerMode.ParameterRange
        self.resampling_method = resampling_method

        self.add_sweepable(Sweepable.from_prs('n_estimators', ps_tree_count))
        self.add_sweepable(Sweepable.from_prs('max_depth', ps_max_depth))
        # self.add_sweepable(Sweepable.from_prs('max_features', ps_random_split_count))
        self.add_sweepable(Sweepable.from_prs('min_samples_leaf', ps_min_leaf_sample_count))


class DecisionForestBiClassifier(BaseLearner):
    def __init__(self, setting: DecisionForestBiClassifierSetting):
        super().__init__(setting=setting, task_type=TaskType.BinaryClassification)

    @property
    def parameter_mapping(self):
        return {
            'n_estimators': RestoreInfo(TwoClassDecisionForestModule._args.tree_count.friendly_name),
            'max_depth': RestoreInfo(TwoClassDecisionForestModule._args.max_depth.friendly_name),
            'min_samples_leaf': RestoreInfo(TwoClassDecisionForestModule._args.min_leaf_sample_count.friendly_name)
        }

    def init_model(self):
        self.model = RandomForestClassifier(
            bootstrap=(self.setting.resampling_method == ResamplingMethod.Bagging),
            n_estimators=self.setting.tree_count,
            max_depth=self.setting.max_depth,
            # max_features=setting.random_split_count,
            min_samples_leaf=self.setting.min_leaf_sample_count,
            random_state=self.setting.random_number_seed,
            n_jobs=-1,
            verbose=51
        )
