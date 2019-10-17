from abc import abstractmethod

import numpy as np
import pandas as pd
from pandas.core.dtypes.common import is_categorical_dtype
from sklearn.metrics import (roc_auc_score, accuracy_score, precision_score, recall_score, mean_absolute_error,
                             r2_score)

import azureml.studio.modules.ml.common.metric_calculator as metric_calculator
from azureml.studio.common.datatable import data_type_conversion
from azureml.studio.modules.ml.common.constants import ScoreColumnConstants
from azureml.studio.common.error import NotExpectedLabelColumnError, ErrorMapping, NotScoredDatasetError
from azureml.studio.core.logger import module_logger, TimeProfile
from azureml.studio.modulehost.constants import ElementTypeName
from azureml.studio.modules.datatransform.common.named_encoder import NamedLabelEncoder, BinaryNamedLabelEncoder
from azureml.studio.modules.ml.common.ml_utils import TaskType, drop_illegal_label_instances
from azureml.studio.modules.ml.common.report_data import ReportData, ReportNameConstants


class BaseEvaluator:
    task_type = None
    default_predict_column = ScoreColumnConstants.ScoredProbabilitiesColumnName
    score_column_key = ScoreColumnConstants.CalibratedScoreType

    def __init__(self, to_compare=False):
        self.is_to_compare = to_compare
        self.label_column_name = None

    @abstractmethod
    def _evaluate(self, df, meta_data):
        pass

    def evaluate_data(self, scored_data, dataset_name):
        """Evaluate scored data, generate evaluation result and visualization information.

        :param scored_data: DataTable, scored dataset.
        :param dataset_name: str, scored dataset's friendly name
        :return: evaluate_result: dataframe
                 visualization information: Report Data. Only the binary-classifier will return non-None data.
        """
        self.dataset_name = dataset_name
        if scored_data is None:
            module_logger.info("Got an Empty Scored Data Instance")
            return None, None
        df = scored_data.data_frame
        self.label_column_name = scored_data.meta_data.label_column_name
        module_logger.info(f"Evaluate data set with {self.label_column_name} as Label Column.")
        self._drop_missing_label_instance(df)
        self._update_scored_label_column(meta_data=scored_data.meta_data)
        if self.scored_label_column_name not in df.columns:
            ErrorMapping.throw(NotScoredDatasetError(dataset_name=dataset_name))
        return self._evaluate(df, meta_data=scored_data.meta_data)

    def _drop_missing_label_instance(self, df):
        drop_illegal_label_instances(df, column_name=self.label_column_name, task_type=self.task_type)

    def _update_scored_label_column(self, meta_data):
        """Update scored label column name if score_column_names existing in data table

        default scored_label_column_name is set to compatible with previous version data table
        new version data table contains score column names info, so update score_column_name with new data table
        :param meta_data: DataFrameSchema
        :return: None
        self.score_label_column will be updated if score_column_names of scored data is not empty.
        """
        if self.score_column_key in meta_data.score_column_names:
            self.scored_label_column_name = meta_data.score_column_names[self.score_column_key]


class BinaryClassificationEvaluator(BaseEvaluator):
    task_type = TaskType.BinaryClassification
    scored_label_column_name = ScoreColumnConstants.ScoredLabelsColumnName
    score_column_key = ScoreColumnConstants.BinaryClassScoredLabelType

    def _calculate(self, y_true, y_prob, y_pred_label):
        """Calculate Binary Classification Task Metrics"""
        with TimeProfile("Calculating confusion matrix, AUC, Accuracy, Precision, Recall, F1"):
            # in confusion_matrix, confusion_matrix[i,j] means the number of instances whose
            # true label is category i while predicted label is category j.
            flatten_metric = metric_calculator.confusion_metric_flat(y_true, y_pred_label)
            if len(flatten_metric) == 4:
                # legal binary classification scored data: return 4 items, including tn, fp, fn, tp.
                tn, fp, fn, tp = flatten_metric
            elif len(flatten_metric) == 1:
                # if the number of category(label+predicted label) is 1, the returned matrix dimension would be 1 * 1.
                # so the length of flatten confusion matrix would be 1.
                tn, fp, fn, tp = 0, 0, 0, 0
                if self.label_encoder.positive_label is not None:
                    # positive label is existing, then the input instances are positive instances.
                    tp, = flatten_metric
                else:
                    tn, = flatten_metric
            else:
                ErrorMapping.throw(NotExpectedLabelColumnError(
                    dataset_name=self.dataset_name,
                    column_name=','.join([self.label_column_name, self.scored_label_column_name]),
                    reason=f"The number of classes in {self.label_column_name} and {self.scored_label_column_name} "
                           f"should not be greater than 2.")
                )

            label_category = np.unique(y_true)
            auc = roc_auc_score(y_true, y_prob) if len(label_category) == 2 else 0.0
            # Since the quantity has been counted, use the statistical data directly to avoid redundant computation.
            valid_instance_count = tn + fp + fn + tp
            accuracy = metric_calculator.safe_divide(tn + tp, valid_instance_count)
            precision = metric_calculator.safe_divide(tp, tp + fp)
            recall = metric_calculator.safe_divide(tp, tp + fn)
            f1 = 2 * metric_calculator.safe_divide(recall * precision, recall + precision)

            results = {
                'AUC': auc,
                'Accuracy': accuracy,
                'Precision': precision,
                'Recall': recall,
                'F1': f1,
                'True Negative': tn,
                'False Positive': fp,
                'False Negative': fn,
                'True Positive': tp,
            }
        return pd.DataFrame([results])

    def _evaluate(self, df, meta_data):
        self.prob_column_name = self._get_prob_column(meta_data)
        # encode input labels into 0,1 label
        self._encode_label_column(df)
        y_true = df[self.label_column_name]
        y_pred_label = df[self.scored_label_column_name]
        y_prob = df[self.prob_column_name]
        result_df = self._calculate(y_true, y_prob, y_pred_label)
        # build visualization json
        report_name = ReportNameConstants.ToComparedDataReportName if self.is_to_compare \
            else ReportNameConstants.ScoredDataReportName
        report_res = ReportData(df=df[[self.prob_column_name, self.label_column_name]],
                                report_name=report_name,
                                auc=result_df['AUC'][0],
                                prob_column_name=self.prob_column_name,
                                label_column_name=self.label_column_name,
                                positive_label=self.label_encoder.positive_label,
                                negative_label=self.label_encoder.negative_label)
        return result_df, report_res

    def _get_prob_column(self, meta_data):
        if ScoreColumnConstants.CalibratedScoreType in meta_data.score_column_names:
            return meta_data.score_column_names[ScoreColumnConstants.CalibratedScoreType]
        return ScoreColumnConstants.ScoredProbabilitiesColumnName

    def detect_label_mapping(self, df):
        """Detect label mapping with scored label column and scored probability column

        Here is a summary of the detection logic. For example, the input df is:
               Label  Prob
            0      0  0.01
            1      1  0.51
            2      0  0.49
            3      1  0.78

        Then, we groupby the df with label column and groupby result looks like:
            0: [0.01, 0.49]
            1: [0.51, 0.78]

        After that, we could use the min() and max() function to get the min/max probability values of each label.
        Finally, we use the min/max probability values to identify which label is positive and which is negative.
        """
        groupby_result = df.groupby(self.scored_label_column_name)
        min_prob_df = groupby_result.min().reset_index()

        threshold = 0.5  # 0.5 is the default threshold of the sigmoid function.
        label_count = len(groupby_result.groups)
        if label_count > 2:
            # since the evaluator evaluate the binary model scored data, the number of classes of the label columns
            # could not greater than 2
            ErrorMapping.throw(
                NotExpectedLabelColumnError(dataset_name=self.dataset_name, column_name=self.scored_label_column_name,
                                            reason="The number of classes in scored label is more than 2."))
        elif label_count == 1:
            label = min_prob_df[self.scored_label_column_name].iloc[0]
            min_prob = min_prob_df[self.prob_column_name].iloc[0]
            if min_prob >= threshold:
                self.label_encoder.positive_label = label
            else:
                self.label_encoder.negative_label = label
        else:
            # label_count == 2
            max_prob_df = groupby_result.max().reset_index()

            label_0 = min_prob_df[self.scored_label_column_name].iloc[0]
            label_1 = min_prob_df[self.scored_label_column_name].iloc[1]

            label_0_min_prob = min_prob_df[self.prob_column_name].iloc[0]
            label_1_min_prob = min_prob_df[self.prob_column_name].iloc[1]

            label_0_max_prob = max_prob_df[self.prob_column_name].iloc[0]
            label_1_max_prob = max_prob_df[self.prob_column_name].iloc[1]

            if label_1_max_prob <= threshold <= label_0_min_prob:
                self.label_encoder.positive_label = label_0
                self.label_encoder.negative_label = label_1
            elif label_0_max_prob <= threshold <= label_1_min_prob:
                self.label_encoder.positive_label = label_1
                self.label_encoder.negative_label = label_0
            else:
                ErrorMapping.throw(NotExpectedLabelColumnError(
                    dataset_name=self.dataset_name,
                    column_name=self.scored_label_column_name,
                    reason="There is a mismatch between probability column and label column, this dataset "
                           "was not generated by a legal binary classifier."))

    def _encode_label_column(self, df):
        self.label_encoder = BinaryNamedLabelEncoder()
        self.detect_label_mapping(df[[self.prob_column_name, self.scored_label_column_name]])
        module_logger.info(f"Infer label mapping from scored label column: "
                           f"positive label is {self.label_encoder.positive_label} "
                           f"and negative label is {self.label_encoder.negative_label}.")
        if is_categorical_dtype(df[self.label_column_name]):
            # Since the train model module uncategory the label column, the scored label will not be 'category' type
            # To compare the label column and the scored label column, label column should be uncategoired as what
            # we do during training.
            df[self.label_column_name] = data_type_conversion.convert_column_by_element_type(
                column=df[self.label_column_name],
                new_type=ElementTypeName.UNCATEGORY)
        for label_str in df[self.label_column_name]:
            if label_str in self.label_encoder.transform_dict:
                continue
            # if the label column contains element which is not in the scored label column
            # then try to fill missing label mapping
            if self.label_encoder.fill_missing_label(label_str) is None:
                # label encoder does not contain missing value, which means label column is inconsistent with
                # training label throw an error to inform user.
                ErrorMapping.throw(
                    NotExpectedLabelColumnError(dataset_name=self.dataset_name, column_name=self.label_column_name,
                                                reason="Label column is not consistent with training label column."))

        module_logger.info(f"Infer label mapping from scored label and label column: "
                           f"positive label is {self.label_encoder.positive_label} "
                           f"and negative label is {self.label_encoder.negative_label}.")
        module_logger.info('Perform transforming category label into numeric label.')
        with TimeProfile("Encoding label column"):
            df[self.label_column_name] = self.label_encoder.transform(df[self.label_column_name])
            df[self.scored_label_column_name] = self.label_encoder.transform(df[self.scored_label_column_name])


class MultiClassificationEvaluator(BaseEvaluator):
    task_type = TaskType.MultiClassification
    scored_label_column_name = ScoreColumnConstants.ScoredLabelsColumnName
    score_column_key = ScoreColumnConstants.MultiClassScoredLabelType

    def _calculate(self, y_true, y_pred):
        if len(y_pred.shape) != 1 and y_pred.shape[-1] != 1:
            y_pred = np.argmax(y_pred, axis=1)
        with TimeProfile("Calculating Overall_Accuracy, Micro_Precision, Macro_Precision, Micro_Recall, Macro_Recall"):
            results = {
                'Overall_Accuracy': accuracy_score(y_true, y_pred),
                'Micro_Precision': precision_score(y_true, y_pred, average='micro'),
                'Macro_Precision': precision_score(y_true, y_pred, average='macro'),
                'Micro_Recall': recall_score(y_true, y_pred, average='micro'),
                'Macro_Recall': recall_score(y_true, y_pred, average='macro'),
                # 'Confusion_Matrix': confusion_matrix(y_true, y_pred)
            }
        return pd.DataFrame([results])

    def _evaluate(self, df, meta_data):
        # Up till now, the visualization information of the multi-class classifier scored data is None.
        self._encode_label_column(df)
        y_true = df[self.label_column_name]
        y_pred_label = df[self.scored_label_column_name]
        result_df = self._calculate(y_true, y_pred_label)
        return result_df, None

    def _encode_label_column(self, df):
        self.label_encoder = NamedLabelEncoder('label_column')
        with TimeProfile("Encoding label column"):
            if is_categorical_dtype(df[self.label_column_name]):
                df[self.label_column_name] = data_type_conversion.convert_column_by_element_type(
                    column=df[self.label_column_name],
                    new_type=ElementTypeName.UNCATEGORY)

            all_labels = pd.concat(
                [df[self.label_column_name], df[self.scored_label_column_name]],
                axis=0
            )
            self.label_encoder.fit(all_labels)
            df[self.label_column_name] = self.label_encoder.transform(df[self.label_column_name])
            df[self.scored_label_column_name] = self.label_encoder.transform(df[self.scored_label_column_name])


class RegressionEvaluator(BaseEvaluator):
    task_type = TaskType.Regression
    scored_label_column_name = ScoreColumnConstants.ScoredLabelsColumnName
    score_column_key = ScoreColumnConstants.RegressionScoredLabelType

    def _calculate(self, y_true, y_pred):
        with TimeProfile(
                "Calculating Mean_Absolute_Error, Root_Mean_Squared_Error, Relative_Squared_Error,"
                " Relative_Absolute_Error, Coefficient_of_Determination"):
            results = {
                'Mean_Absolute_Error': mean_absolute_error(y_true, y_pred),
                'Root_Mean_Squared_Error': metric_calculator.root_mean_squared_error(y_true, y_pred),
                'Relative_Squared_Error': metric_calculator.relative_squared_error(y_true, y_pred),
                'Relative_Absolute_Error': metric_calculator.relative_absolute_error(y_true, y_pred),
                'Coefficient_of_Determination': r2_score(y_true, y_pred),
            }
        return pd.DataFrame([results])

    def _evaluate(self, df, meta_data):
        # Up till now, the visualization information of the regression scored data is None.
        y_true = df[self.label_column_name]
        y_pred = df[self.scored_label_column_name]
        return self._calculate(y_true, y_pred), None


class ClusterEvaluator(BaseEvaluator):
    task_type = TaskType.Cluster
    scored_label_column_name = ScoreColumnConstants.ClusterAssignmentsColumnName
    score_column_key = ScoreColumnConstants.ClusterScoredLabelType

    @staticmethod
    def _rebuild_result_df(df):
        df.index.name = "Result Description"
        df.rename(index=lambda x: 'Evaluation For Cluster No.' + str(x), inplace=True)
        df.reset_index(inplace=True)

    def _get_all_scored_column(self, all_column, meta_data):
        if meta_data.score_column_names:
            # score_column_names is not empty, means that the scored data is generated after using score_column_names to
            # pass scored meta info.
            scored_column = [x for x in all_column if x in meta_data.score_column_names.values()]
        else:
            # compatible with the old version.
            scored_column = [x for x in all_column if
                             x == ScoreColumnConstants.ClusterAssignmentsColumnName or x.startswith(
                                 ScoreColumnConstants.ClusterDistanceMetricsColumnNamePattern)]
        return scored_column

    def _evaluate(self, data_frame, meta_data):
        DISTANCE_TO_ASSIGNED_CLUSTER_NAME = 'Distance to Cluster Center'
        DISTANCE_TO_OTHER_CLUSTER_NAME = 'Distance to Other Center'

        def _get_assigned_cluster_distance(x):
            """
            return distance to cluster i , i = assignment in this row.
            :param x: pandas.Series in row, [assignments, dis 0, dis 1, dis 2 ...]
            :return: cluster index, distance to assigned cluster center, distance to the second closest
            """

            min_cluster = int(x[0])
            min_dis = x[min_cluster + 1]
            x[min_cluster + 1] = np.inf
            x[0] = np.inf
            return min_cluster, min_dis, x.min()

        all_column = data_frame.columns.tolist()
        scored_column = self._get_all_scored_column(all_column, meta_data)
        # drop nan rows
        nd = data_frame[scored_column].dropna(axis=0).values

        # the shape of new_nd should be (N, 3) that 3 columns corresponds to the
        # cluster index, distance to assigned cluster center, distance to the second
        # closest respectively.
        if nd.shape[0] > 0:
            new_nd = np.apply_along_axis(_get_assigned_cluster_distance, 1, nd)
        else:
            # if all samples contain nan values, just init an empty array. We assign the column number
            # to 3 explicitly to assure that the shape is consistent with results of np.apply_along_axis.
            new_nd = np.empty(shape=(0, 3))

        # calculate distance to assigned cluster and other cluster by assigned index.
        data_frame = pd.DataFrame(data=new_nd,
                                  columns=[self.scored_label_column_name,
                                           DISTANCE_TO_ASSIGNED_CLUSTER_NAME,
                                           DISTANCE_TO_OTHER_CLUSTER_NAME])
        data_frame[self.scored_label_column_name] = data_frame[self.scored_label_column_name].astype(int)

        total_average_df = data_frame.agg({DISTANCE_TO_OTHER_CLUSTER_NAME: 'mean',
                                           DISTANCE_TO_ASSIGNED_CLUSTER_NAME: 'mean'})

        # aggregate by cluster
        res_df = data_frame.groupby(self.scored_label_column_name).agg(
            {DISTANCE_TO_OTHER_CLUSTER_NAME: 'mean', DISTANCE_TO_ASSIGNED_CLUSTER_NAME: ['mean', 'count', 'max']})
        res_df.columns = ['Average ' + DISTANCE_TO_OTHER_CLUSTER_NAME, 'Average ' + DISTANCE_TO_ASSIGNED_CLUSTER_NAME,
                          'Number of Points', 'Maximal ' + DISTANCE_TO_ASSIGNED_CLUSTER_NAME]

        ClusterEvaluator._rebuild_result_df(res_df)
        # add combined evaluation
        combined_evaluation = {
            'Result Description': 'Combined Evaluation',
            'Average ' + DISTANCE_TO_ASSIGNED_CLUSTER_NAME: total_average_df[DISTANCE_TO_ASSIGNED_CLUSTER_NAME],
            'Average ' + DISTANCE_TO_OTHER_CLUSTER_NAME: total_average_df[DISTANCE_TO_OTHER_CLUSTER_NAME],
            'Number of Points': res_df['Number of Points'].sum(),
            'Maximal ' + DISTANCE_TO_ASSIGNED_CLUSTER_NAME: res_df['Maximal ' + DISTANCE_TO_ASSIGNED_CLUSTER_NAME].max()
        }
        res_df = res_df.append(combined_evaluation, ignore_index=True)
        # Up till now, the visualization information of the cluster scored data is None.
        return res_df, None
