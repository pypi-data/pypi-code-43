import os

import numpy as np
import pandas as pd

from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.modules.ml.common.constants import ScoreColumnConstants
from azureml.studio.modules.ml.evaluate.evaluate_generic_module.evaluate_generic_module import EvaluateModelModule
from azureml.studio.modules.ml.initialize_models.evaluator import ClusterEvaluator
from azureml.studio.modules.ml.tests.mltest_utils import assert_equal, assert_array_almost_equal


def script_directory():
    return os.path.dirname(os.path.abspath(__file__))


def _base_library():
    return os.path.join(script_directory(), 'input', 'evaluate_cluster_model')


def _get_data_table_from_dataframe(dataframe):
    dt = DataTable(dataframe)
    score_column_names = {
        ScoreColumnConstants.ClusterScoredLabelType: ScoreColumnConstants.ClusterAssignmentsColumnName
    }
    for column_name in dt.column_names:
        if column_name.startswith(ScoreColumnConstants.ClusterDistanceMetricsColumnNamePattern):
            score_column_names[column_name] = column_name
    dt.meta_data.score_column_names = score_column_names
    return dt


class TestEvaluateCluster:
    def test_evaluator(self):
        data_path = os.path.join(_base_library(), 'cluster_evaluation_input.csv')
        ref_path = os.path.join(_base_library(), 'cluster_evaluation_output_ref.csv')
        df = pd.read_csv(data_path)
        dt = _get_data_table_from_dataframe(df)
        evaluator = ClusterEvaluator()
        out_df, _ = evaluator.evaluate_data(scored_data=dt, dataset_name='Score Dataset')
        ref_df = pd.read_csv(ref_path)
        assert_equal(out_df.shape, ref_df.shape)
        for (_, row_ref), (_, row_out) in zip(ref_df.iterrows(), out_df.iterrows()):
            assert row_ref[0] == row_out[0]
            assert_array_almost_equal(row_ref[1:], row_out[1:])

    def test_evaluator_with_nan_data(self):
        # parts of data is nan
        df = pd.DataFrame({'feature1': [1, 2, 3, np.nan],
                           'feature2': [4, 5, np.nan, np.nan],
                           'Assignments': [0, 1, np.nan, np.nan],
                           'DistancesToClusterCenter no.0': [10, 20, np.nan, np.nan],
                           'DistancesToClusterCenter no.1': [16, 8, np.nan, np.nan]})
        ref_df = pd.DataFrame([['Evaluation For Cluster No.0', 16, 10, 1, 10],
                               ['Evaluation For Cluster No.1', 20, 8, 1, 8],
                               ['Combined Evaluation', 18, 9, 2, 10]],
                              columns=['Result Description', 'Average Distance to Other Center',
                                       'Average Distance to Cluster Center', 'Number of Points',
                                       'Maximal Distance to Cluster Center'])
        dt = _get_data_table_from_dataframe(df)
        evaluator = ClusterEvaluator()
        out_df, _ = evaluator.evaluate_data(dt, dataset_name='Scored Dataset')
        for (_, row_ref), (_, row_out) in zip(ref_df.iterrows(), out_df.iterrows()):
            assert row_ref[0] == row_out[0]
            assert_array_almost_equal(row_ref[1:], row_out[1:])

        # all data is nan
        df = pd.DataFrame({'feature1': [np.nan, 2, 3, np.nan],
                           'feature2': [4, np.nan, np.nan, np.nan],
                           'Assignments': [np.nan, np.nan, np.nan, np.nan],
                           'DistancesToClusterCenter no.0': [np.nan, np.nan, np.nan, np.nan],
                           'DistancesToClusterCenter no.1': [np.nan, np.nan, np.nan, np.nan]})
        ref_df = pd.DataFrame([['Combined Evaluation', np.nan, np.nan, 0, np.nan]],
                              columns=['Result Description', 'Average Distance to Other Center',
                                       'Average Distance to Cluster Center', 'Number of Points',
                                       'Maximal Distance to Cluster Center'])
        dt = _get_data_table_from_dataframe(df)
        evaluator = ClusterEvaluator()
        out_df, _ = evaluator.evaluate_data(dt, 'Scored Dataset')
        assert ref_df.equals(out_df)

    def test_evaluate_kmeans_module(self):
        data_path = os.path.join(_base_library(), 'cluster_evaluation_input.csv')
        ref_path = os.path.join(_base_library(), 'cluster_evaluation_output_ref.csv')
        df = pd.read_csv(data_path)
        dt = _get_data_table_from_dataframe(dataframe=df)
        out = EvaluateModelModule.run(scored_data=dt, scored_data_to_compare=None)
        assert isinstance(out, tuple)
        assert len(out) == 1
        assert isinstance(out[0], DataTable)
        evaluation_result = out[0]
        out_df = evaluation_result.data_frame

        ref_df = pd.read_csv(ref_path)
        assert_equal(out_df.shape, ref_df.shape)
        for (_, row_ref), (_, row_out) in zip(ref_df.iterrows(), out_df.iterrows()):
            assert row_ref[0] == row_out[0]
            assert_array_almost_equal(row_ref[1:], row_out[1:])
