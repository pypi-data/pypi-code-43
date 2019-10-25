import os
import tempfile
import unittest

import azureml.dataprep as dprep
import pandas as pd
from nimbusml.preprocessing import DatasetTransformer

from azureml.automl.core.featurization.streaming import StreamingFeaturizer, StreamingFeaturizationTransformer
from azureml.automl.core.streaming_pipeline_wrapper import StreamingPipelineWrapper
from automl.client.core.runtime.nimbus_wrappers import NimbusMlOnlineGradientDescentRegressor, NimbusMlPipelineWrapper
from .utilities import dataframe_as_csv_file


class StreamingPipelineWrapperTests(unittest.TestCase):
    """StreamingPipelineWrapper tests."""

    initialized = False

    def __init__(self, *args, **kwargs):
        """Initialize the test."""
        super(StreamingPipelineWrapperTests, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        StreamingPipelineWrapperTests._initialize_data()
        StreamingPipelineWrapperTests._init_feature_transformer()
        StreamingPipelineWrapperTests._init_fitted_pipeline_with_featurization()
        StreamingPipelineWrapperTests._init_fitted_pipeline_without_featurization()

    @classmethod
    def tearDownClass(cls):
        os.remove(StreamingPipelineWrapperTests._tmp_data_file_path)

    @staticmethod
    def _initialize_data():
        col = [0 if i % 2 == 0 else 1 for i in range(100)]
        StreamingPipelineWrapperTests.df = pd.DataFrame(
            {
                '1': col,
                'label': col
            })
        StreamingPipelineWrapperTests._tmp_data_file_path = dataframe_as_csv_file(
            StreamingPipelineWrapperTests.df)
        StreamingPipelineWrapperTests.dflow = dprep.auto_read_file(
            StreamingPipelineWrapperTests._tmp_data_file_path)

    @staticmethod
    def _init_feature_transformer():
        featurizer = StreamingFeaturizer(StreamingPipelineWrapperTests.dflow, 'label')
        featurization_transformer = featurizer.learn_transformations()
        StreamingPipelineWrapperTests.featurization_transformer = featurization_transformer

    @staticmethod
    def _init_fitted_pipeline_with_featurization():
        trainer = NimbusMlOnlineGradientDescentRegressor(feature=['1'], label='label')
        pipeline = NimbusMlPipelineWrapper([
            ('datasettransformer',
                DatasetTransformer(StreamingPipelineWrapperTests.featurization_transformer.pipeline.model)),
            ('trainer', trainer)])
        pipeline.fit(StreamingPipelineWrapperTests.dflow)
        StreamingPipelineWrapperTests.fitted_pipeline_with_featurization = pipeline

    @staticmethod
    def _init_fitted_pipeline_without_featurization():
        trainer = NimbusMlOnlineGradientDescentRegressor(feature=['1'], label='label')
        pipeline = NimbusMlPipelineWrapper([("trainer", trainer)])
        pipeline.fit(StreamingPipelineWrapperTests.dflow)
        StreamingPipelineWrapperTests.fitted_pipeline_without_featurization = pipeline

    def _build_streaming_pipeline_with_featurization(self):
        return StreamingPipelineWrapper(
            StreamingPipelineWrapperTests.featurization_transformer,
            StreamingPipelineWrapperTests.fitted_pipeline_with_featurization
        )

    def _build_streaming_pipeline_without_featurization(self):
        return StreamingPipelineWrapper(
            None,
            StreamingPipelineWrapperTests.fitted_pipeline_without_featurization
        )

    def test_transform_with_featurization(self):
        streaming_pipeline = self._build_streaming_pipeline_with_featurization()
        df = streaming_pipeline.transform(StreamingPipelineWrapperTests.df.head(1))
        self.assertIn('1.0', df.columns)
        self.assertIn('1.1', df.columns)

    def test_transform_without_featurization(self):
        streaming_pipeline = self._build_streaming_pipeline_without_featurization()
        df = streaming_pipeline.transform(StreamingPipelineWrapperTests.df.head(1))
        self.assertIn('1', df.columns)

    def test_fit_transform_dataframe_with_featurization(self):
        streaming_pipeline = self._build_streaming_pipeline_with_featurization()
        df = streaming_pipeline.fit_transform(StreamingPipelineWrapperTests.df.head(1))
        self.assertIn('1.0', df.columns)
        self.assertNotIn('1.1', df.columns)

    def test_fit_transform_dataframe_without_featurization(self):
        streaming_pipeline = self._build_streaming_pipeline_without_featurization()
        df = streaming_pipeline.fit_transform(StreamingPipelineWrapperTests.df.head(1))
        self.assertIn('1', df.columns)

    def test_fit_transform_dataflow_with_featurization(self):
        streaming_pipeline = self._build_streaming_pipeline_with_featurization()
        streaming_pipeline.fit(StreamingPipelineWrapperTests.dflow.take(1))
        df = streaming_pipeline.transform(StreamingPipelineWrapperTests.dflow.head(1))
        self.assertIn('1.0', df.columns)
        self.assertNotIn('1.1', df.columns)

    def test_fit_transform_dataflow_without_featurization(self):
        streaming_pipeline = self._build_streaming_pipeline_without_featurization()
        streaming_pipeline.fit(StreamingPipelineWrapperTests.dflow.take(1))
        df = streaming_pipeline.transform(StreamingPipelineWrapperTests.dflow.head(1))
        self.assertIn('1', df.columns)

    def test_named_steps_with_featurization(self):
        streaming_pipeline = self._build_streaming_pipeline_with_featurization()
        self.assertEqual(2, len(streaming_pipeline.named_steps.items()))
        self.assertIsInstance(
            streaming_pipeline.named_steps['datatransformer'],
            StreamingFeaturizationTransformer
        )

    def test_named_steps_without_featurization(self):
        streaming_pipeline = self._build_streaming_pipeline_without_featurization()
        self.assertEqual(1, len(streaming_pipeline.named_steps.items()))
