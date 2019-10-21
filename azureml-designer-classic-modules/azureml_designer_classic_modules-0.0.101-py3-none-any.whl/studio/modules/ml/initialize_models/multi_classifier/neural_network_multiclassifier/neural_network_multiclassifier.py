from sklearn.neural_network import MLPClassifier

import azureml.studio.core.utils.strutils as strutils
from azureml.studio.common.parameter_range import ParameterRangeSettings, Sweepable
from azureml.studio.common.types import AutoEnum
from azureml.studio.modulehost.attributes import ModeParameter, BooleanParameter, FloatParameter, IntParameter, \
    ParameterRangeParameter, ReleaseState, UntrainedLearnerOutputPort, ModuleMeta, StringParameter, ItemInfo
from azureml.studio.modulehost.module_reflector import module_entry, BaseModule
from azureml.studio.modules.ml.common.base_learner import BaseLearner, TaskType, CreateLearnerMode, RestoreInfo
from azureml.studio.modules.ml.common.base_learner_setting import BaseLearnerSetting


class CreateNeuralNetworkRegressionModelNeuralNetworkTopology(AutoEnum):
    DefaultHiddenLayers: ItemInfo(name="Fully-connected case", friendly_name="Fully-connected case") = ()
    # TODO:
    CustomHiddenLayers: ItemInfo(name="Custom definition script", friendly_name="Custom definition script",
                                 release_state=ReleaseState.Alpha) = ()


class CreateNeuralNetworkModelNormalizationMethod(AutoEnum):
    Binning: ItemInfo(name="Binning normalizer", friendly_name="Binning normalizer",
                      release_state=ReleaseState.Alpha) = ()
    Gaussian: ItemInfo(name="Gaussian normalizer", friendly_name="Gaussian normalizer",
                       release_state=ReleaseState.Alpha) = ()
    MinMax: ItemInfo(name="Min-Max normalizer", friendly_name="Min-Max normalizer", ) = ()
    NONE: ItemInfo(name="Do not normalize", friendly_name="Do not normalize",
                   release_state=ReleaseState.Alpha) = ()


class MulticlassNeuralNetworkModuleDefaultParameters:
    Mode = CreateLearnerMode.SingleParameter
    NeuralNetworkTopology = CreateNeuralNetworkRegressionModelNeuralNetworkTopology.DefaultHiddenLayers
    NeuralNetworkTopologyForRange = CreateNeuralNetworkRegressionModelNeuralNetworkTopology.DefaultHiddenLayers
    InitialWeightsDiameter = 0.1
    LearningRate = 0.1
    PsLearningRate = "0.1; 0.2; 0.4"
    Momentum = 0
    NormalizerType = CreateNeuralNetworkModelNormalizationMethod.MinMax
    NumHiddenNodes = "100"
    NumHiddenNodesForRange = "100"
    NumIterations = 100
    PsNumIterations = "20; 40; 80; 160"
    Shuffle = True
    RandomNumberSeed = None
    AllowUnknownLevels = True

    @classmethod
    def to_dict(cls):
        return {
            "mode": cls.Mode,
            "neural_network_topology": cls.NeuralNetworkTopology,
            "neural_network_topology_for_range": cls.NeuralNetworkTopologyForRange,
            "initial_weights_diameter": cls.InitialWeightsDiameter,
            "learning_rate": cls.LearningRate,
            "ps_learning_rate": cls.PsLearningRate,
            "momentum": cls.Momentum,
            "normalizer_type": cls.NormalizerType,
            "num_hidden_nodes": cls.NumHiddenNodes,
            "num_hidden_nodes_for_range": cls.NumHiddenNodesForRange,
            "num_iterations": cls.NumIterations,
            "ps_num_iterations": cls.PsNumIterations,
            "shuffle": cls.Shuffle,
            "random_number_seed": cls.RandomNumberSeed,
            "allow_unknown_levels": cls.AllowUnknownLevels,
        }


class MulticlassNeuralNetworkModule(BaseModule):

    @staticmethod
    @module_entry(ModuleMeta(
        name="Multiclass Neural Network",
        description="Creates a multiclass classification model using a neural network algorithm",
        category="Machine Learning\\Initialize Model\\Classification",
        version="2.0",
        owner="Microsoft Corporation",
        family_id="E8B401FB-230A-4B21-BD11-D1FDA0D57C1F",
        release_state=ReleaseState.Release,
        is_deterministic=True,
    ))
    def run(
            mode: ModeParameter(
                CreateLearnerMode,
                name="Create trainer mode",
                friendly_name="Create trainer mode",
                description="Create advanced learner options",
                default_value=MulticlassNeuralNetworkModuleDefaultParameters.Mode,
            ),
            neural_network_topology: ModeParameter(
                CreateNeuralNetworkRegressionModelNeuralNetworkTopology,
                name="Hidden layer specification",
                friendly_name="Hidden layer specification",
                description="Specify the architecture of the hidden layer or layers",
                default_value=MulticlassNeuralNetworkModuleDefaultParameters.NeuralNetworkTopology,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
            ),
            neural_network_topology_for_range: ModeParameter(
                CreateNeuralNetworkRegressionModelNeuralNetworkTopology,
                name="Hidden layer specification1",
                friendly_name="Hidden layer specification",
                description="Specify the architecture of the hidden layer or layers for range",
                default_value=MulticlassNeuralNetworkModuleDefaultParameters.NeuralNetworkTopologyForRange,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
            ),
            initial_weights_diameter: FloatParameter(
                name="The initial learning weights diameter",
                friendly_name="The initial learning weights diameter",
                description="Specify the node weights at the start of the learning process",
                default_value=MulticlassNeuralNetworkModuleDefaultParameters.InitialWeightsDiameter,
                min_value=4.94065645841247E-324,
                release_state=ReleaseState.Alpha
            ),
            learning_rate: FloatParameter(
                name="The learning rate",
                friendly_name="Learning rate",
                description="Specify the size of each step in the learning process",
                default_value=MulticlassNeuralNetworkModuleDefaultParameters.LearningRate,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=4.94065645841247E-324,
                max_value=2.0,
            ),
            ps_learning_rate: ParameterRangeParameter(
                name="Range for learning rate",
                friendly_name="Learning rate",
                description="Specify the range for the size of each step in the learning process",
                default_value=MulticlassNeuralNetworkModuleDefaultParameters.PsLearningRate,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=1.401298E-45,
                max_limit=2,
                is_int=False,
                is_log=True,
                slider_min=0.0001,
                slider_max=2,
            ),
            momentum: FloatParameter(
                name="The momentum",
                friendly_name="The momentum",
                description="Specify a weight to apply during learning to nodes from previous iterations",
                default_value=MulticlassNeuralNetworkModuleDefaultParameters.Momentum,
                min_value=0,
                max_value=1,
            ),
            # TODO: ADD NormalizationMethod After Normalize Data Done
            normalizer_type: ModeParameter(
                CreateNeuralNetworkModelNormalizationMethod,
                name="The type of normalizer",
                friendly_name="The type of normalizer",
                description="elect the type of normalization to apply to learning examples",
                default_value=MulticlassNeuralNetworkModuleDefaultParameters.NormalizerType,
                release_state=ReleaseState.Alpha
            ),
            num_hidden_nodes: StringParameter(
                name="Number of hidden nodes",
                friendly_name="Number of hidden nodes",
                description="Type the number of nodes in the hidden layer. For multiple hidden layers, "
                            "type a comma-separated list.",
                default_value=MulticlassNeuralNetworkModuleDefaultParameters.NumHiddenNodes,
                parent_parameter="Hidden layer specification",
                parent_parameter_val=(CreateNeuralNetworkRegressionModelNeuralNetworkTopology.DefaultHiddenLayers,),
            ),
            num_hidden_nodes_for_range: StringParameter(
                name="Number of hidden nodes1",
                friendly_name="Number of hidden nodes",
                description="Type the number of nodes in the hidden layer, or for multiple hidden layers, "
                            "type a comma-separated list.",
                default_value=MulticlassNeuralNetworkModuleDefaultParameters.NumHiddenNodesForRange,
                parent_parameter="Hidden layer specification1",
                parent_parameter_val=(CreateNeuralNetworkRegressionModelNeuralNetworkTopology.DefaultHiddenLayers,),
            ),
            num_iterations: IntParameter(
                name="Number of learning iterations",
                friendly_name="Number of learning iterations",
                description="Specify the number of iterations while learning",
                default_value=MulticlassNeuralNetworkModuleDefaultParameters.NumIterations,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=1,
            ),
            ps_num_iterations: ParameterRangeParameter(
                name="Range for number of learning iterations",
                friendly_name="Number of learning iterations",
                description="Specify the range for the number of iterations while learning",
                default_value=MulticlassNeuralNetworkModuleDefaultParameters.PsNumIterations,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=1,
                max_limit=2147483647,
                is_int=True,
                is_log=False,
                slider_min=1,
                slider_max=500,
            ),
            shuffle: BooleanParameter(
                name="Shuffle examples",
                friendly_name="Shuffle examples",
                description="Select this option to change the order of instances between learning iterations",
                default_value=MulticlassNeuralNetworkModuleDefaultParameters.Shuffle,
            ),
            random_number_seed: IntParameter(
                name="Random number seed",
                friendly_name="Random number seed",
                is_optional=True,
                description="Specify a numeric seed to use for random number generation. "
                            "Leave blank to use the default seed.",
            ),
            allow_unknown_levels: BooleanParameter(
                name="Allow unknown levels in categorical features",
                friendly_name="Allow unknown categorical levels",
                description="Indicate whether an additional level should be created for unknown categories. "
                            "If the test dataset contains categories not present in the training dataset "
                            "they are mapped to this unknown level.",
                default_value=MulticlassNeuralNetworkModuleDefaultParameters.AllowUnknownLevels,
                release_state=ReleaseState.Alpha
            )
    ) -> (
            UntrainedLearnerOutputPort(
                name="Untrained model",
                friendly_name="Untrained model",
                description="An untrained multiclass classification model",
            ),
    ):
        """Module Entry of the Neural Network Module

        SingleParameter -> neural_network_topology, num_hidden_nodes
        ParameterRange  -> neural_network_topology_for_range, num_hidden_nodes_for_range
        :return: UntrainedLearner
        """

        input_values = locals()
        output_values = MulticlassNeuralNetworkModule.create_neural_network_multiclassifier(**input_values)
        return output_values

    @staticmethod
    def create_neural_network_multiclassifier(
            mode: CreateLearnerMode = MulticlassNeuralNetworkModuleDefaultParameters.Mode,
            neural_network_topology=MulticlassNeuralNetworkModuleDefaultParameters.NeuralNetworkTopology,
            neural_network_topology_for_range: CreateNeuralNetworkRegressionModelNeuralNetworkTopology =
            MulticlassNeuralNetworkModuleDefaultParameters.NeuralNetworkTopologyForRange,
            initial_weights_diameter: float = MulticlassNeuralNetworkModuleDefaultParameters.InitialWeightsDiameter,
            momentum: float = MulticlassNeuralNetworkModuleDefaultParameters.Momentum,
            num_hidden_nodes: str = MulticlassNeuralNetworkModuleDefaultParameters.NumHiddenNodes,
            num_hidden_nodes_for_range: str = MulticlassNeuralNetworkModuleDefaultParameters.NumHiddenNodesForRange,
            learning_rate: float = MulticlassNeuralNetworkModuleDefaultParameters.LearningRate,
            ps_learning_rate: ParameterRangeSettings = MulticlassNeuralNetworkModuleDefaultParameters.PsLearningRate,
            num_iterations: int = MulticlassNeuralNetworkModuleDefaultParameters.NumIterations,
            ps_num_iterations: ParameterRangeSettings = MulticlassNeuralNetworkModuleDefaultParameters.PsNumIterations,
            shuffle: bool = MulticlassNeuralNetworkModuleDefaultParameters.Shuffle,
            random_number_seed: int = MulticlassNeuralNetworkModuleDefaultParameters.RandomNumberSeed,
            normalizer_type: CreateNeuralNetworkModelNormalizationMethod =
            MulticlassNeuralNetworkModuleDefaultParameters.NormalizerType,
            allow_unknown_levels: bool = MulticlassNeuralNetworkModuleDefaultParameters.AllowUnknownLevels,
    ):  # todo replace type by attribute
        setting = NeuralNetworkMultiClassifierSetting()
        if mode == CreateLearnerMode.SingleParameter:
            num_hidden_nodes = strutils.int_str_to_int_list(num_hidden_nodes)
            setting.init_single(
                initial_weights_diameter=initial_weights_diameter,
                learning_rate=learning_rate,
                momentum=momentum,
                num_hidden_nodes=num_hidden_nodes,
                num_iterations=num_iterations,
                shuffle=shuffle,
                random_number_seed=random_number_seed
            )
        else:
            num_hidden_nodes_for_range = strutils.int_str_to_int_list(num_hidden_nodes_for_range)
            setting.init_range(
                initial_weights_diameter=initial_weights_diameter, ps_learning_rate=ps_learning_rate,
                momentum=momentum, num_hidden_nodes=num_hidden_nodes_for_range,
                ps_num_iterations=ps_num_iterations, shuffle=shuffle,
                random_number_seed=random_number_seed)
        return tuple([NeuralNetworkMultiClassifier(setting)])


class NeuralNetworkMultiClassifierSetting(BaseLearnerSetting):
    def __init__(self):
        """
        there remains some problem:
        1. initial_weights_diameter was not supported by sklearn
        2. momentum only used when optimizer = 'sgd', so which optimizer is used by tlc?
        3. learning rate can be {'constant', 'invscaling','adaptive'} in sklearn
        4. did not support parameter range
        5. did not support custom define script [ imp by StreamReader nnScript in v1]

        """
        super().__init__()
        self.initial_weights_diameter = MulticlassNeuralNetworkModuleDefaultParameters.InitialWeightsDiameter
        self.learning_rate = MulticlassNeuralNetworkModuleDefaultParameters.LearningRate
        self.momentum = MulticlassNeuralNetworkModuleDefaultParameters.Momentum
        self.num_hidden_nodes = strutils.int_str_to_int_list(
            MulticlassNeuralNetworkModuleDefaultParameters.NumHiddenNodes)
        self.num_iterations = MulticlassNeuralNetworkModuleDefaultParameters.NumIterations
        self.shuffle = MulticlassNeuralNetworkModuleDefaultParameters.Shuffle
        self.create_learner_mode = MulticlassNeuralNetworkModuleDefaultParameters.Mode
        self.parameter_range = {
            'learning_rate_init': Sweepable.from_prs(
                "learning_rate_init", ParameterRangeSettings.from_literal(
                    MulticlassNeuralNetworkModuleDefaultParameters.PsLearningRate)).attribute_value,
            'max_iter': Sweepable.from_prs(
                "max_iter", ParameterRangeSettings.from_literal(
                    MulticlassNeuralNetworkModuleDefaultParameters.PsNumIterations)).attribute_value,
        }

    def init_single(
            self,
            initial_weights_diameter: float = MulticlassNeuralNetworkModuleDefaultParameters.InitialWeightsDiameter,
            learning_rate: float = MulticlassNeuralNetworkModuleDefaultParameters.LearningRate,
            momentum: float = MulticlassNeuralNetworkModuleDefaultParameters.Momentum,
            num_hidden_nodes: list = strutils.int_str_to_int_list(
                MulticlassNeuralNetworkModuleDefaultParameters.NumHiddenNodes),
            num_iterations: int = MulticlassNeuralNetworkModuleDefaultParameters.NumIterations,
            shuffle: bool = MulticlassNeuralNetworkModuleDefaultParameters.Shuffle,
            random_number_seed: int = MulticlassNeuralNetworkModuleDefaultParameters.RandomNumberSeed
    ):
        """
        :param initial_weights_diameter: float, The initial learning weights diameter, None
        :param learning_rate: float, The learning rate, learning_rate_init
        :param momentum: float, The momentum, momentum
        :param num_hidden_nodes: list(int), Number of hidden nodes, hidden_layer_sizes
        :param num_iterations: int, Number of learning iterations, max_iter
        :param shuffle: bool, Shuffle examples, shuffle
        :param random_number_seed: int, Random number seed, random_state
        :return: None
        """
        self.create_learner_mode = CreateLearnerMode.SingleParameter
        self.initial_weights_diameter = initial_weights_diameter  # TODO : Sklearn had not supported it yet
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.num_hidden_nodes = num_hidden_nodes if num_hidden_nodes is not None else [100]
        self.num_iterations = num_iterations
        self.shuffle = shuffle
        self.random_number_seed = random_number_seed

    def init_range(self, initial_weights_diameter: float = 0.1, ps_learning_rate: ParameterRangeSettings = None,
                   momentum: float = 1, num_hidden_nodes: list = None, ps_num_iterations: ParameterRangeSettings = None,
                   shuffle: bool = True, random_number_seed: int = None):
        self.create_learner_mode = CreateLearnerMode.ParameterRange
        self.initial_weights_diameter = initial_weights_diameter
        self.momentum = momentum
        self.num_hidden_nodes = num_hidden_nodes if num_hidden_nodes is not None else [100]
        self.random_number_seed = random_number_seed
        self.shuffle = shuffle

        self.add_sweepable(Sweepable.from_prs('learning_rate_init', ps_learning_rate))
        self.add_sweepable(Sweepable.from_prs('max_iter', ps_num_iterations))


class NeuralNetworkMultiClassifier(BaseLearner):
    def __init__(self, setting: NeuralNetworkMultiClassifierSetting):
        super().__init__(setting=setting, task_type=TaskType.MultiClassification)

    @property
    def parameter_mapping(self):
        return {
            'learning_rate_init': RestoreInfo(MulticlassNeuralNetworkModule._args.learning_rate.friendly_name),
            'max_iter': RestoreInfo(MulticlassNeuralNetworkModule._args.num_iterations.friendly_name)
        }

    def init_model(self):
        self.model = MLPClassifier(
            hidden_layer_sizes=self.setting.num_hidden_nodes,
            solver='sgd',
            learning_rate_init=self.setting.learning_rate,
            learning_rate='adaptive',
            max_iter=self.setting.num_iterations,
            shuffle=self.setting.shuffle,
            random_state=self.setting.random_number_seed,
            momentum=self.setting.momentum,
            # todo, other parameter in tlc
        )
