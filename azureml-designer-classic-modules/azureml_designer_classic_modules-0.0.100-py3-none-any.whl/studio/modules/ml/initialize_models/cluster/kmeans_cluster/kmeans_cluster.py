import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.externals.joblib.externals.loky.process_executor import TerminatedWorkerError

from azureml.studio.common.error import ModuleOutOfMemoryError, ErrorMapping
from azureml.studio.common.parameter_range import ParameterRangeSettings, Sweepable
from azureml.studio.common.types import AutoEnum
from azureml.studio.core.logger import module_logger, TimeProfile, time_profile
from azureml.studio.modulehost.attributes import UntrainedClusterOutputPort, ModeParameter, ItemInfo, IntParameter, \
    BooleanParameter, ParameterRangeParameter, ReleaseState, ModuleMeta
from azureml.studio.modulehost.module_reflector import module_entry, BaseModule
from azureml.studio.modules.ml.common.base_clustser import BaseCluster
from azureml.studio.modules.ml.common.base_learner_setting import BaseLearnerSetting
from azureml.studio.modules.ml.common.constants import ScoreColumnConstants


class CreateClusterMode(AutoEnum):
    SingleParameter: ItemInfo(name="SingleParameter", friendly_name="Single Parameter") = ()
    ParameterRange: ItemInfo(name="ParameterRange", friendly_name="Parameter Range",
                             release_state=ReleaseState.Alpha) = ()


class KMeansCentroidInit(AutoEnum):
    Random: ItemInfo(name="Random", friendly_name="Random") = ()
    KMeansPP: ItemInfo(name="K-Means++", friendly_name="K-Means++") = ()
    Default: ItemInfo(name="Default", friendly_name="First N") = ()
    # todo: init with ndarray.
    Evenly: ItemInfo(name="Evenly", friendly_name="Evenly", release_state=ReleaseState.Alpha) = ()
    UseLabelColumn: ItemInfo(name="Use label column", friendly_name="Use label column",
                             release_state=ReleaseState.Alpha) = ()
    KMeansPPFast: ItemInfo(name="K-Means++ Fast", friendly_name="K-Means++ Fast",
                           release_state=ReleaseState.Alpha) = ()


class KMeansMetric(AutoEnum):
    Euclidian: ItemInfo(name="Euclidean", friendly_name="Euclidean") = ()
    Cosine: ItemInfo(name="Cosine", friendly_name="Cosine", release_state=ReleaseState.Alpha) = ()


class KMeansAssignLabelMode(AutoEnum):
    Ignore: ItemInfo(name="Ignore label column", friendly_name="Ignore label column") = ()
    MissingValues: ItemInfo(name="Fill missing values", friendly_name="Fill missing values") = ()
    OverwriteFromClosest: ItemInfo(name="Overwrite from closest to center",
                                   friendly_name="Overwrite from closest to center") = ()


class KMeansClusteringModuleDefaultParameters:
    Mode = CreateClusterMode.SingleParameter
    Noc = 2
    PsNoc = "2; 3; 4; 5"
    Metric = KMeansMetric.Euclidian
    NormalizeFeatures = True
    Init = KMeansCentroidInit.KMeansPP
    Init1 = KMeansCentroidInit.KMeansPP
    Iter = 100
    RandomNumberSeed = None
    RandomNumberSeed1 = None
    Alm = KMeansAssignLabelMode.Ignore

    @classmethod
    def to_dict(cls):
        return {
            "mode": cls.Mode,
            "noc": cls.Noc,
            "ps_noc": cls.PsNoc,
            "metric": cls.Metric,
            "normalize_features": cls.NormalizeFeatures,
            "init": cls.Init,
            "init1": cls.Init1,
            "iter": cls.Iter,
            "random_number_seed": cls.RandomNumberSeed,
            "random_number_seed1": cls.RandomNumberSeed1,
            "alm": cls.Alm,
        }


class KMeansClusteringModule(BaseModule):
    @staticmethod
    @module_entry(ModuleMeta(
        name="K-Means Clustering",
        description="Initialize K-Means clustering model",
        category="Machine Learning\\Initialize Model\\Clustering",
        version="3.0",
        owner="Microsoft Corporation",
        family_id="5049A09B-BD90-4C4E-9B46-7C87E3A36810",
        release_state=ReleaseState.Release,
        is_deterministic=True,
    ))
    def run(
            mode: ModeParameter(
                CreateClusterMode,
                name="Create trainer mode",
                friendly_name="Create trainer mode",
                description="Create advanced learner options",
                default_value=KMeansClusteringModuleDefaultParameters.Mode,
            ),
            noc: IntParameter(
                name="Number of Centroids",
                friendly_name="Number of centroids",
                description="Number of Centroids",
                default_value=KMeansClusteringModuleDefaultParameters.Noc,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateClusterMode.SingleParameter,),
                min_value=2,
            ),
            ps_noc: ParameterRangeParameter(
                name="Range for Number of Centroids",
                friendly_name="Range for Number of Centroids",
                description="Specify range for the number of centroids ",
                default_value=KMeansClusteringModuleDefaultParameters.PsNoc,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateClusterMode.ParameterRange,),
                min_limit=2,
                max_limit=2147483647,
                is_int=True,
                is_log=True,
                slider_min=2,
                slider_max=1000,
            ),
            metric: ModeParameter(
                KMeansMetric,
                name="Metric",
                friendly_name="Metric",
                description="Selected metric",
                default_value=KMeansClusteringModuleDefaultParameters.Metric,
            ),
            normalize_features: BooleanParameter(
                name="Should input instances be normalized",
                friendly_name="Normalize features",
                description="Indicate whether instances should be normalized",
                default_value=KMeansClusteringModuleDefaultParameters.NormalizeFeatures,
            ),
            init: ModeParameter(
                KMeansCentroidInit,
                name="Initialization",
                friendly_name="Initialization",
                description="Initialization algorithm",
                default_value=KMeansClusteringModuleDefaultParameters.Init,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateClusterMode.SingleParameter,),
            ),
            init1: ModeParameter(
                KMeansCentroidInit,
                name="Initialization for sweep",
                friendly_name="Initialization for sweep",
                description="Initialization algorithm when sweeping ",
                default_value=KMeansClusteringModuleDefaultParameters.Init1,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateClusterMode.ParameterRange,),
            ),
            iter: IntParameter(
                name="Iterations",
                friendly_name="Iterations",
                description="Number of iterations",
                default_value=KMeansClusteringModuleDefaultParameters.Iter,
                min_value=1,
            ),
            random_number_seed: IntParameter(
                name="Random number seed",
                friendly_name="Random number seed",
                is_optional=True,
                description="Type a value to seed the random number for centroid generator used by the training model. "
                            "Leave blank to have value randomly choosen at first train.",
                parent_parameter="Initialization",
                parent_parameter_val=(
                        KMeansCentroidInit.Random, KMeansCentroidInit.KMeansPP, KMeansCentroidInit.KMeansPPFast),
            ),
            random_number_seed1: IntParameter(
                name="Random number seed for sweep",
                friendly_name="Random number seed",
                is_optional=True,
                description="Type a value to seed the random number for centroid generator used when sweeping. "
                            "Leave blank to have value randomly choosen at first train.",
                parent_parameter="Initialization for sweep",
                parent_parameter_val=(KMeansCentroidInit.Random, KMeansCentroidInit.KMeansPP,
                                      KMeansCentroidInit.KMeansPPFast),
            ),

            alm: ModeParameter(
                KMeansAssignLabelMode,
                name="Assign Label Mode",
                friendly_name="Assign label mode",
                description="Mode of value assignment to the labeled column",
                default_value=KMeansClusteringModuleDefaultParameters.Alm,
            )
    ) -> (
            UntrainedClusterOutputPort(
                name="Untrained model",
                friendly_name="Untrained model",
                description="Untrained K-Means clustering model",
            ),
    ):
        input_values = locals()
        output_values = (KMeansClusteringModule.create_kmeans_learner(**input_values))
        return output_values

    @staticmethod
    def create_kmeans_learner(
            mode=KMeansClusteringModuleDefaultParameters.Mode,
            noc=KMeansClusteringModuleDefaultParameters.Noc,
            ps_noc=KMeansClusteringModuleDefaultParameters.PsNoc,
            metric=KMeansClusteringModuleDefaultParameters.Metric,
            normalize_features=KMeansClusteringModuleDefaultParameters.NormalizeFeatures,
            init=KMeansClusteringModuleDefaultParameters.Init,
            init1=KMeansClusteringModuleDefaultParameters.Init1,
            iter=KMeansClusteringModuleDefaultParameters.Iter,
            random_number_seed=KMeansClusteringModuleDefaultParameters.RandomNumberSeed,
            random_number_seed1=KMeansClusteringModuleDefaultParameters.RandomNumberSeed1,
            alm=KMeansClusteringModuleDefaultParameters.Alm,
    ):
        setting = KMeansClusterSetting()
        if mode == CreateClusterMode.SingleParameter:
            setting.init_single(noc=noc, kmeans_metric=metric, normalize_features=normalize_features,
                                kmeans_centroid_init=init, kmeans_iter=iter,
                                random_number_seed=random_number_seed, alm=alm)
        else:
            setting.init_range(ps_noc=ps_noc, kmeans_metric=metric, normalize_features=normalize_features,
                               kmeans_centroid_init=init1, kmeans_iter=iter,
                               random_number_seed=random_number_seed1, alm=alm)
        return KMeansCluster(setting=setting),


class KMeansClusterSetting(BaseLearnerSetting):
    def __init__(self):
        """
        TODO (linchi)
        there remains several problems.
        1. sklearn can not define custom metric like cosine, the only metric of kmeans is euclidean
        2. support init using label column.
        :param noc: int, Number of Centroids. n_clusters
        :param kmeans_metric: str, ['cosine', 'euclidean'], evaluating distance between two data point.
        :param kmeans_centroid_init: str, ['k-means++', 'random'], Initialization .init
        :param kmeans_iter: int, Iterations. max_iter
        :param random_number_seed: opt int, Random number seed. random_state
        """
        super(KMeansClusterSetting, self).__init__()
        self.noc = KMeansClusteringModuleDefaultParameters.Noc
        self.kmeans_metric = KMeansClusteringModuleDefaultParameters.Metric
        self.kmeans_centroid_init = KMeansClusteringModuleDefaultParameters.Init
        self.kmeans_iter = KMeansClusteringModuleDefaultParameters.Iter
        self.alm = KMeansClusteringModuleDefaultParameters.Alm
        self.normalize_features = KMeansClusteringModuleDefaultParameters.NormalizeFeatures
        self.parameter_range = {
            'n_clusters': Sweepable.from_prs(
                "n_clusters",
                ParameterRangeSettings.from_literal(KMeansClusteringModuleDefaultParameters.PsNoc)).attribute_value,
        }

    def init_single(self,
                    noc: int = KMeansClusteringModuleDefaultParameters.Noc,
                    kmeans_metric: KMeansMetric = KMeansClusteringModuleDefaultParameters.Metric,
                    normalize_features: bool = KMeansClusteringModuleDefaultParameters.NormalizeFeatures,
                    kmeans_centroid_init: KMeansCentroidInit = KMeansClusteringModuleDefaultParameters.Init,
                    kmeans_iter: int = KMeansClusteringModuleDefaultParameters.Iter,
                    random_number_seed: int = KMeansClusteringModuleDefaultParameters.RandomNumberSeed,
                    alm: KMeansAssignLabelMode = KMeansClusteringModuleDefaultParameters.Alm):
        self.create_learner_mode = CreateClusterMode.SingleParameter
        self.noc = noc
        self.kmeans_metric = kmeans_metric
        self.kmeans_centroid_init = kmeans_centroid_init
        self.kmeans_iter = kmeans_iter
        self.random_number_seed = random_number_seed
        self.normalize_features = normalize_features
        self.alm = alm

    def init_range(self, ps_noc=None,
                   kmeans_metric: KMeansMetric = KMeansMetric.Euclidian,
                   kmeans_centroid_init: KMeansCentroidInit = KMeansCentroidInit.KMeansPP,
                   kmeans_iter: int = 100,
                   normalize_features: bool = True,
                   random_number_seed: int = None,
                   alm: KMeansAssignLabelMode = KMeansAssignLabelMode.Ignore):
        self.create_learner_mode = CreateClusterMode.ParameterRange
        self.kmeans_metric = kmeans_metric
        self.kmeans_centroid_init = kmeans_centroid_init
        self.kmeans_iter = kmeans_iter
        self.normalize_features = normalize_features
        self.alm = alm
        self.add_sweepable(Sweepable.from_prs('n_clusters', ps_noc))


class KMeansCluster(BaseCluster):
    def __init__(self, setting: KMeansClusterSetting):
        super().__init__(setting=setting)

    def set_init_method(self, data_set=None):
        if self.setting.kmeans_centroid_init == KMeansCentroidInit.Random:
            self.model.set_params(init='random')
        elif self.setting.kmeans_centroid_init == KMeansCentroidInit.KMeansPP:
            self.model.set_params(init='k-means++')
            # When KMeansCentroidInit.KMeansPP is set,
            # run one time only is good enough since multiple times runs would show similar results.
            # See details in the following URL:
            # https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_stability_low_dim_dense.html
            self.model.set_params(n_init=1, n_jobs=1)
        elif self.setting.kmeans_centroid_init == KMeansCentroidInit.Default:
            init_center = data_set[:self.setting.noc, :]
            self.model.set_params(init=init_center)
            # When KMeansCentroidInit.Default is set and initial centroids are given by users,
            # run one time only is enough since multiple times runs are the same.
            self.model.set_params(n_init=1, n_jobs=1)
        else:
            raise NotImplementedError()

    def init_model(self):
        self.model = KMeans(
            n_clusters=self.setting.noc,
            max_iter=self.setting.kmeans_iter,
            random_state=self.setting.random_number_seed,
            verbose=1,
            n_jobs=-1,
        )

    @time_profile
    def train(self, df, label_column_name):
        """
        apply normalizing and training
        :param df: pandas.DataFrame, training data
        :param label_column_name: label column
        :return: None
        """
        # initial model
        with TimeProfile("Initializing model"):
            self.init_model()
            if self.setting.enable_log:
                module_logger.info("Enable Training Log.")
        module_logger.info(
            f"validated training data has {df.shape[0]} Row(s) and {df.shape[1]} Columns.")

        # record label column name and names of feature columns
        self.label_column_name = label_column_name
        self.init_feature_columns_names = df.columns.tolist()
        if label_column_name in self.init_feature_columns_names:
            self.init_feature_columns_names.remove(label_column_name)
        with TimeProfile("Normalizing Data"):
            self._fit_normalize(df)
            train_x, _ = self._apply_normalize(df, self.init_feature_columns_names)
        self.set_init_method(train_x)
        try:
            self._train(train_x)
        except TerminatedWorkerError as e:
            details = "KMeans workers terminated, which might be due to the high memory usage in subprocesses."
            ErrorMapping.rethrow(e, ModuleOutOfMemoryError(details=details))

    def build_cluster_label(self, label_column, distance_df):
        """

        This function is used to find the label of every cluster according to the existing label and labeled instance's
        distance to the every cluster center.
        For every cluster, we try to find the nearest labeled instance, and its label will be used as cluster's label
        :param label_column: labeled column
        :param distance_df: the distance df calculated after predicting.
        :return: None
        self.cluster_label will be set.
        """
        invalid_valid_row = label_column.isna().values
        # if all input label is None or nan, there is no valid label, return without setting cluster label.
        if all(invalid_valid_row):
            return
        cluster_number = distance_df.shape[1]
        self.cluster_label = []
        for col_index in range(cluster_number):
            distance_array = distance_df.values[:, col_index]
            if all(np.isnan(distance_array)):
                self.cluster_label.append(None)
                continue
            # mask distance in invalid row when label is nan.
            distance_array = np.ma.array(distance_df.values[:, col_index], mask=invalid_valid_row)
            min_idx = np.argmin(distance_array)
            self.cluster_label.append(label_column[min_idx])

    def reassign_label(self, previous_label_column, assignments_column):
        assert previous_label_column.shape[0] == assignments_column.shape[0]
        if self.setting.alm == KMeansAssignLabelMode.Ignore:
            return previous_label_column

        label_column = assignments_column.apply(lambda x: self.cluster_label[int(x)])
        if self.setting.alm == KMeansAssignLabelMode.MissingValues:
            # only rewrite missing value, so, use previous not-None label
            # pd.where() replaces values where the condition is False.
            label_column = label_column.where(previous_label_column.isna(), previous_label_column)
        return label_column

    @time_profile
    def predict(self, df):
        test_x = df[self.init_feature_columns_names]
        with TimeProfile("Normalizing Data"):
            test_x, _ = self._apply_normalize(test_x, test_x.columns.tolist())
        with TimeProfile("Assigning data points to cluster"):
            assignments = self.model.predict(test_x)

        with TimeProfile("Calculating distance to each cluster center"):
            distances = self.model.transform(test_x)
            distance_df = pd.DataFrame(distances,
                                       columns=[ScoreColumnConstants.ClusterDistanceMetricsColumnNamePattern + str(x)
                                                for x in range(distances.shape[1])])
        return pd.Series(assignments, name=ScoreColumnConstants.ClusterAssignmentsColumnName,
                         dtype='category'), distance_df
