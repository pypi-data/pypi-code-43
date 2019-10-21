from sklearn.linear_model import LogisticRegression

from azureml.studio.common.parameter_range import ParameterRangeSettings, Sweepable
from azureml.studio.modulehost.attributes import ModeParameter, FloatParameter, IntParameter, BooleanParameter, \
    ParameterRangeParameter, ReleaseState, UntrainedLearnerOutputPort, ModuleMeta
from azureml.studio.modulehost.module_reflector import module_entry, BaseModule
from azureml.studio.modules.ml.common.base_learner import BaseLearner, TaskType, CreateLearnerMode, RestoreInfo
from azureml.studio.modules.ml.common.base_learner_setting import BaseLearnerSetting


class MulticlassLogisticRegressionModuleDefaultParameters:
    Mode = CreateLearnerMode.SingleParameter
    OptimizationTolerance = 1e-07
    L1Weight = 1
    L2Weight = 1
    MemorySize = 20
    PsOptimizationTolerance = "0.00001; 0.00000001"
    PsL1Weight = "0.0; 0.01; 0.1; 1.0"
    PsL2Weight = "0.01; 0.1; 1.0"
    PsMemorySize = "5; 20; 50"
    RandomNumberSeed = None
    AllowUnknownLevels = True

    @classmethod
    def to_dict(cls):
        return {
            "mode": cls.Mode,
            "optimization_tolerance": cls.OptimizationTolerance,
            "l1_weight": cls.L1Weight,
            "l2_weight": cls.L2Weight,
            "memory_size": cls.MemorySize,
            "ps_optimization_tolerance": cls.PsOptimizationTolerance,
            "ps_l1_weight": cls.PsL1Weight,
            "ps_l2_weight": cls.PsL2Weight,
            "ps_memory_size": cls.PsMemorySize,
            "random_number_seed": cls.RandomNumberSeed,
            "allow_unknown_levels": cls.AllowUnknownLevels,
        }


class MulticlassLogisticRegressionModule(BaseModule):

    @staticmethod
    @module_entry(ModuleMeta(
        name="Multiclass Logistic Regression",
        description="Creates a multiclass logistic regression classification model",
        category="Machine Learning\\Initialize Model\\Classification",
        version="2.0",
        owner="Microsoft Corporation",
        family_id="1D195FE5-98CD-4E1A-A1C8-076AAA3E02C3",
        release_state=ReleaseState.Release,
        is_deterministic=True,
    ))
    def run(
            mode: ModeParameter(
                CreateLearnerMode,
                name="Create trainer mode",
                friendly_name="Create trainer mode",
                description="Create advanced learner options",
                default_value=MulticlassLogisticRegressionModuleDefaultParameters.Mode,
            ),
            optimization_tolerance: FloatParameter(
                name="Optimization Tolerance",
                friendly_name="Optimization tolerance",
                description="Specify a tolerance value for the L-BFGS optimizer",
                default_value=MulticlassLogisticRegressionModuleDefaultParameters.OptimizationTolerance,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=4.94065645841247E-324,
            ),
            l1_weight: FloatParameter(
                name="L1 Regularization weight",
                friendly_name="L1 regularization weight",
                description="Specify the L1 regularization weight. Use a non-zero value to avoid overfitting.",
                default_value=MulticlassLogisticRegressionModuleDefaultParameters.L1Weight,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=0,
                release_state=ReleaseState.Alpha
            ),
            l2_weight: FloatParameter(
                name="L2 Regularizaton weight",
                friendly_name="L2 regularization weight",
                description="Specify the L2 regularization weight. Use a non-zero value to avoid overfitting.",
                default_value=MulticlassLogisticRegressionModuleDefaultParameters.L2Weight,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=0,
            ),
            memory_size: IntParameter(
                name="Memory Size",
                friendly_name="Memory size for L-BFGS",
                description="Specify the amount of memory (in MB) to use for the L-BFGS optimizer. "
                            "When less memory is used, Training is faster but less accurate.",
                default_value=MulticlassLogisticRegressionModuleDefaultParameters.MemorySize,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=1,
                release_state=ReleaseState.Alpha
            ),
            ps_optimization_tolerance: ParameterRangeParameter(
                name="Range for optimization tolerance",
                friendly_name="Optimization tolerance",
                description="Specify a range for the tolerance value for the L-BFGS optimizer",
                default_value=MulticlassLogisticRegressionModuleDefaultParameters.PsOptimizationTolerance,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=1.401298E-45,
                max_limit=3.40282347E+38,
                is_int=False,
                is_log=True,
                slider_min=1E-08,
                slider_max=0.001,
            ),
            ps_l1_weight: ParameterRangeParameter(
                name="Range for L1 regularization weight",
                friendly_name="L1 regularization weight",
                description="Specify the range for the L1 regularization weight. "
                            "Use a non-zero value to avoid overfitting.",
                default_value=MulticlassLogisticRegressionModuleDefaultParameters.PsL1Weight,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=0,
                max_limit=3.40282347E+38,
                is_int=False,
                is_log=True,
                slider_min=0.0001,
                slider_max=1,
                release_state=ReleaseState.Alpha
            ),
            ps_l2_weight: ParameterRangeParameter(
                name="Range for L2 regularization weight",
                friendly_name="L2 regularization weight",
                description="Specify the range for the L2 regularization weight. "
                            "Use a non-zero value to avoid overfitting.",
                default_value=MulticlassLogisticRegressionModuleDefaultParameters.PsL2Weight,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=0,
                max_limit=3.40282347E+38,
                is_int=False,
                is_log=True,
                slider_min=0.0001,
                slider_max=1,
            ),
            ps_memory_size: ParameterRangeParameter(
                name="Range for memory size for L-BFGS the lower the value the faster and less accurate the training",
                friendly_name="Memory size for L-BFGS",
                description="Specify the range for the amount of memory (in MB) to use for the L-BFGS optimizer. "
                            "The lower the value, the faster and less accurate the training.",
                default_value=MulticlassLogisticRegressionModuleDefaultParameters.PsMemorySize,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=1,
                max_limit=2147483647,
                is_int=True,
                is_log=False,
                slider_min=1,
                slider_max=100,
                release_state=ReleaseState.Alpha
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
                description="Indicate whether an additional level should be created for each categorical column. "
                            "Any levels in the test dataset not available in the training dataset "
                            "are mapped to this additional level.",
                default_value=MulticlassLogisticRegressionModuleDefaultParameters.AllowUnknownLevels,
                release_state=ReleaseState.Alpha
            )
    ) -> (
            UntrainedLearnerOutputPort(
                name="Untrained model",
                friendly_name="Untrained model",
                description="An untrained classificaiton model",
            ),
    ):
        input_values = locals()
        output_values = MulticlassLogisticRegressionModule.create_logistic_regression_multiclassifier(**input_values)
        return output_values

    @staticmethod
    def create_logistic_regression_multiclassifier(
            mode: CreateLearnerMode = MulticlassLogisticRegressionModuleDefaultParameters.Mode,
            optimization_tolerance: float = MulticlassLogisticRegressionModuleDefaultParameters.OptimizationTolerance,
            ps_optimization_tolerance: ParameterRangeSettings =
            MulticlassLogisticRegressionModuleDefaultParameters.PsOptimizationTolerance,
            l1_weight: float = MulticlassLogisticRegressionModuleDefaultParameters.L1Weight,
            ps_l1_weight: ParameterRangeSettings = MulticlassLogisticRegressionModuleDefaultParameters.PsL1Weight,
            l2_weight: float = MulticlassLogisticRegressionModuleDefaultParameters.L2Weight,
            ps_l2_weight: ParameterRangeSettings = MulticlassLogisticRegressionModuleDefaultParameters.PsL2Weight,
            memory_size: int = MulticlassLogisticRegressionModuleDefaultParameters.MemorySize,
            ps_memory_size: ParameterRangeSettings = MulticlassLogisticRegressionModuleDefaultParameters.PsMemorySize,
            random_number_seed: int = MulticlassLogisticRegressionModuleDefaultParameters.RandomNumberSeed,
            allow_unknown_levels: bool = MulticlassLogisticRegressionModuleDefaultParameters.AllowUnknownLevels,
    ):
        setting = LogisticRegressionMultiClassifierSetting()
        if mode == CreateLearnerMode.SingleParameter:
            setting.init_single(
                optimization_tolerance=optimization_tolerance,
                l2_weight=l2_weight,
                memory_size=memory_size,
                random_number_seed=random_number_seed)
        else:
            setting.init_range(
                ps_optimization_tolerance=ps_optimization_tolerance,
                ps_l2_weight=ps_l2_weight,
                ps_memory_size=ps_memory_size,
                random_number_seed=random_number_seed
            )
        return tuple([LogisticRegressionMultiClassifier(setting)])


class LogisticRegressionMultiClassifierSetting(BaseLearnerSetting):
    def __init__(self):
        """
        there remains some problem:
        1. v1 supports both l1 and l2 penalty meanwhile, but sklearn only supports l1 or l2. now only use l2_weight
        2. Memory size for L-BFGS was not supported.
        """
        super().__init__()
        self.penalty = 'l2'
        self.optimization_tolerance = MulticlassLogisticRegressionModuleDefaultParameters.OptimizationTolerance
        self.l2_weight = MulticlassLogisticRegressionModuleDefaultParameters.L2Weight
        self.memory_size = MulticlassLogisticRegressionModuleDefaultParameters.MemorySize
        self.create_learner_mode = MulticlassLogisticRegressionModuleDefaultParameters.Mode
        s_l2_weight = Sweepable.from_prs(
            "l2_weight", ParameterRangeSettings.from_literal(
                MulticlassLogisticRegressionModuleDefaultParameters.PsL2Weight)).attribute_value
        self.parameter_range = {
            'tol': Sweepable.from_prs("tol", ParameterRangeSettings.from_literal(
                MulticlassLogisticRegressionModuleDefaultParameters.PsOptimizationTolerance)).attribute_value,
            'C': [1 / l2 for l2 in s_l2_weight]
        }

    def init_single(
            self,
            optimization_tolerance: float = MulticlassLogisticRegressionModuleDefaultParameters.OptimizationTolerance,
            l2_weight: float = MulticlassLogisticRegressionModuleDefaultParameters.L2Weight,
            memory_size: int = MulticlassLogisticRegressionModuleDefaultParameters.MemorySize,
            random_number_seed: int = MulticlassLogisticRegressionModuleDefaultParameters.RandomNumberSeed
    ):
        """
        :param optimization_tolerance: float, Optimization tolerance, tol
        :param l2_weight: float, l2 penalty term, C
        :param memory_size: int, Memory size for L-BFGS, not supported yet
        :param random_number_seed: int, Random number seed, random_state
        """
        self.create_learner_mode = CreateLearnerMode.SingleParameter
        self.optimization_tolerance = optimization_tolerance
        self.l2_weight = l2_weight
        self.memory_size = memory_size
        self.random_number_seed = random_number_seed

    def init_range(self,
                   ps_optimization_tolerance: ParameterRangeSettings = None,
                   ps_l2_weight: ParameterRangeSettings = None,
                   ps_memory_size: ParameterRangeSettings = None,
                   random_number_seed: int = None):
        self.create_learner_mode = CreateLearnerMode.ParameterRange
        self.random_number_seed = random_number_seed
        self.add_sweepable(Sweepable.from_prs('tol', ps_optimization_tolerance))
        s_l2_weight = Sweepable.from_prs("l2_weight", ps_l2_weight).attribute_value
        self.add_list('C', [1 / l2 if l2 > 1e-9 else 1e22 for l2 in s_l2_weight])


class LogisticRegressionMultiClassifier(BaseLearner):
    def __init__(self, setting: LogisticRegressionMultiClassifierSetting):
        super().__init__(setting=setting, task_type=TaskType.MultiClassification)

    @property
    def parameter_mapping(self):
        return {
            'tol': RestoreInfo(MulticlassLogisticRegressionModule._args.optimization_tolerance.friendly_name),
            'C': RestoreInfo(MulticlassLogisticRegressionModule._args.l2_weight.friendly_name,
                             lambda x: 0 if x > 9e21 else 1 / x)
        }

    def init_model(self):
        # TODO: how to handle l2_weight == 0 ?
        if self.setting.l2_weight < 1e-9:
            param_c = 1e22
        else:
            param_c = 1 / self.setting.l2_weight
        self.model = LogisticRegression(
            penalty='l2',
            tol=self.setting.optimization_tolerance,
            C=param_c,
            random_state=self.setting.random_number_seed,
            solver='lbfgs',
            multi_class='multinomial',
            verbose=False
        )
