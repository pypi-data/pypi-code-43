import unittest
from functools import wraps

import numpy as np
import pandas as pd
from scipy.sparse import csc_matrix, csr_matrix

from pointannotator.annotate_samples import \
    AnnotateSamples, SCORING_EXP_RATIO, SCORING_MARKERS_SUM, SCORING_LOG_FDR, \
    SCORING_LOG_PVALUE, PFUN_HYPERGEOMETRIC


def dense_sparse(test_case):
    # type: (Callable) -> Callable
    """Run a single test case on both dense and sparse data."""
    @wraps(test_case)
    def _wrapper(self):
        # Make sure to call setUp and tearDown methods in between test runs so
        # any widget state doesn't interfere between tests
        def _setup_teardown():
            self.tearDown()
            self.setUp()

        def to_pandas_sparse(spmatrix, columns, indices):
            return pd.DataFrame.sparse.from_spmatrix(
                spmatrix, columns=columns, index=indices)

        def pandas_from_csc(df):
            return to_pandas_sparse(
                csc_matrix(df.values), columns=df.columns, indices=df.index)

        def pandas_from_csr(df):
            return to_pandas_sparse(
                csr_matrix(df.values), columns=df.columns, indices=df.index)

        test_case(self, lambda x: x)
        _setup_teardown()
        test_case(self, pandas_from_csr)
        _setup_teardown()
        test_case(self, pandas_from_csc)

    return _wrapper


class TestAnnotateSamples(unittest.TestCase):

    def setUp(self):
        self.markers = pd.DataFrame(
            [["Type 1", "111"], ["Type 1", "112"], ["Type 1", "113"],
             ["Type 1", "114"],
             ["Type 2", "211"], ["Type 2", "212"], ["Type 2", "213"],
             ["Type 2", "214"]],
            columns=["Annotations", "Attributes"])

        genes = ["111", "112", "113", "114", "211", "212", "213", "214"]
        self.data = pd.DataFrame(np.array(
            [[1, 1, 1, 1.1, 0, 0, 0, 0],
             [1, .8, .9, 1, 0, 0, 0, 0],
             [.7, 1.1, 1, 1.2, 0, 0, 0, 0],
             [.8, .7, 1.1, 1, 0, .1, 0, 0],
             [0, 0, 0, 0, 1.05, 1.05, 1.1, 1],
             [0, 0, 0, 0, 1.1, 1.0, 1.05, 1.1],
             [0, 0, 0, 0, 1.05, .9, 1.1, 1.1],
             [0, 0, 0, 0, .9, .9, 1.2, 1]
             ]),
            columns=genes
        )
        self.annotator = AnnotateSamples()

    @dense_sparse
    def test_artificial_data(self, array):
        annotations = self.annotator.annotate_samples(
            array(self.data), self.markers, num_all_attributes=15)

        self.assertEqual(type(annotations), pd.DataFrame)
        self.assertEqual(len(annotations), len(self.data))
        self.assertEqual(len(annotations.iloc[0]), 2)  # two types in the data
        self.assertGreater(np.nansum(annotations), 0)
        self.assertLessEqual(np.nanmax(annotations), 1)
        self.assertGreaterEqual(np.nanmin(annotations), 0)

    @dense_sparse
    def test_remove_empty_column(self, array):
        """
        Type 3 column must be removed here
        """
        markers = pd.DataFrame(
            [["Type 1", "111"], ["Type 1", "112"], ["Type 1", "113"],
             ["Type 1", "114"],
             ["Type 2", "211"], ["Type 2", "212"], ["Type 2", "213"],
             ["Type 2", "214"],
             ["Type 3", "311"], ["Type 3", "312"], ["Type 3", "313"]],
            columns=["Annotations", "Attributes"])

        annotations = self.annotator.annotate_samples(
            array(self.data), markers, num_all_attributes=20)

        self.assertEqual(type(annotations), pd.DataFrame)
        self.assertEqual(len(annotations), len(self.data))
        self.assertEqual(len(annotations.iloc[0]), 2)  # two types in the data
        self.assertGreater(np.nansum(annotations), 0)
        self.assertLessEqual(np.nanmax(annotations), 1)
        self.assertGreaterEqual(np.nanmin(annotations), 0)

        annotations = self.annotator.annotate_samples(
            array(self.data), markers, num_all_attributes=20,
            return_nonzero_annotations=False)
        self.assertEqual(len(annotations), len(self.data))
        self.assertEqual(len(annotations.iloc[0]), 3)  # two types in the data
        self.assertGreater(np.nansum(annotations), 0)
        self.assertLessEqual(np.nanmax(annotations), 1)
        self.assertGreaterEqual(np.nanmin(annotations), 0)

    @dense_sparse
    def test_sf(self, array):
        """
        Test annotations with hypergeom.sf
        """
        annotator = AnnotateSamples()
        annotations = annotator.annotate_samples(
            array(self.data), self.markers, num_all_attributes=15,
            p_value_fun=PFUN_HYPERGEOMETRIC)

        self.assertEqual(type(annotations), pd.DataFrame)
        self.assertEqual(len(annotations), len(self.data))
        self.assertEqual(len(annotations.iloc[0]), 2)  # two types in the data
        self.assertGreater(np.nansum(annotations), 0)
        self.assertLessEqual(np.nanmax(annotations), 1)
        self.assertGreaterEqual(np.nanmin(annotations), 0)

    @dense_sparse
    def test_two_example(self, array):
        self.data = self.data.iloc[:2]

        annotations = self.annotator.annotate_samples(
            array(self.data), self.markers, num_all_attributes=15)
        self.assertEqual(type(annotations), pd.DataFrame)
        self.assertEqual(len(annotations), len(self.data))

    @dense_sparse
    def test_select_attributes(self, array):
        z = self.annotator.mann_whitney_test(array(self.data))

        self.assertEqual(z.shape, self.data.shape)
        self.assertGreaterEqual(z.iloc[0, 0], 1)
        self.assertGreaterEqual(z.iloc[0, 1], 1)
        self.assertGreaterEqual(z.iloc[0, 3], 1)

    @dense_sparse
    def test_assign_annotations(self, array):
        z = np.array([
            [1.1, 1.1, 1.1, 1.1, 0, 0, 0, 0],
            [1.1, 1.1, 0, 0, 1.1, 0, 0, 0],
            [1.1, 0, 0, 0, 1.1, 1.1, 0, 0],
            [0, 0, 0, 0, 1.1, 1.1, 1.1, 1.1]
        ])
        z_table = pd.DataFrame(z, columns=self.data.columns)
        attrs = [{"111", "112", "113", "114"}, {"111", "112", "211"},
                 {"211", "212", "111"}, {"211", "212", "213", "214"}]
        exp_ann = np.array([
            [1, 0],
            [1/2, 1/4],
            [1/4, 1/2],
            [0, 1]])
        annotations, fdrs = self.annotator.assign_annotations(
            array(z_table), self.markers, array(self.data[:4]),
            num_all_attributes=15)

        self.assertEqual(len(attrs), len(annotations))
        self.assertEqual(len(attrs), len(fdrs))
        self.assertEqual(2, annotations.shape[1])  # only two types in markers
        self.assertEqual(2, fdrs.shape[1])
        np.testing.assert_array_almost_equal(exp_ann, annotations)

        exp_fdrs_smaller = np.array([
            [0.05, 2],
            [2, 2],
            [2, 2],
            [2, 0.05]])

        np.testing.assert_array_less(fdrs, exp_fdrs_smaller)

    @dense_sparse
    def test_scoring(self, array):
        # scoring SCORING_EXP_RATIO
        annotations = self.annotator.annotate_samples(
            array(self.data), self.markers, num_all_attributes=15,
            scoring=SCORING_EXP_RATIO)

        self.assertEqual(type(annotations), pd.DataFrame)
        self.assertEqual(len(annotations), len(self.data))
        self.assertEqual(len(annotations.iloc[0]), 2)  # two types in the data
        self.assertGreater(np.nansum(annotations), 0)
        self.assertLessEqual(np.nanmax(annotations), 1)
        self.assertGreaterEqual(np.nanmin(annotations), 0)

        # scoring SCORING_MARKERS_SUM
        annotations = self.annotator.annotate_samples(
            array(self.data), self.markers, num_all_attributes=15,
            scoring=SCORING_MARKERS_SUM)

        self.assertEqual(type(annotations), pd.DataFrame)
        self.assertEqual(len(annotations), len(self.data))
        self.assertEqual(len(annotations.iloc[0]), 2)  # two types in the data

        # based on provided data it should match
        # the third row is skipped, since it is special
        self.assertEqual(annotations.iloc[0, 0], self.data.iloc[0].sum())
        self.assertEqual(annotations.iloc[5, 1], self.data.iloc[5].sum())

        # scoring SCORING_LOG_FDR
        annotations = self.annotator.annotate_samples(
            array(self.data), self.markers, num_all_attributes=15,
            scoring=SCORING_LOG_FDR)

        self.assertEqual(type(annotations), pd.DataFrame)
        self.assertEqual(len(annotations), len(self.data))
        self.assertEqual(len(annotations.iloc[0]), 2)  # two types in the data

        # scoring SCORING_LOG_PVALUE
        annotations = self.annotator.annotate_samples(
            array(self.data), self.markers, num_all_attributes=15,
            scoring=SCORING_LOG_PVALUE)

        self.assertEqual(type(annotations), pd.DataFrame)
        self.assertEqual(len(annotations), len(self.data))
        self.assertEqual(len(annotations.iloc[0]), 2)  # two types in the data

    @dense_sparse
    def test_log_cpm(self, array):
        norm_data = self.annotator.log_cpm(array(self.data))
        self.assertTupleEqual(self.data.shape, norm_data.shape)
        # log_cpm must return array of same type
        self.assertEqual(type(array(self.data)), type(norm_data))

    @dense_sparse
    def test_markers_wrong_type(self, array):
        self.markers["Attributes"] = pd.to_numeric(self.markers["Attributes"])
        self.assertRaises(TypeError, self.annotator.annotate_samples,
                          array(self.data), self.markers, num_genes=15)

    @dense_sparse
    def test_keep_dataframe_index(self, array):
        self.data.index = np.random.randint(0, 16, len(self.data))
        data_index = self.data.index.values.tolist()
        annotations = self.annotator.annotate_samples(
            array(self.data), self.markers, num_all_attributes=15,
            scoring=SCORING_MARKERS_SUM)
        self.assertListEqual(data_index, annotations.index.values.tolist())

    @dense_sparse
    def test_no_num_all_attributes(self, array):
        annotations = self.annotator.annotate_samples(
            array(self.data), self.markers)

        self.assertEqual(type(annotations), pd.DataFrame)
