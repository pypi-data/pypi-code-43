import numpy as np
import pandas as pd

from scipy.stats.mstats import rankdata
from scipy.stats import hypergeom, binom

from pointannotator.utils import FDR

SCORING_EXP_RATIO = "scoring_exp_ratio"
SCORING_MARKERS_SUM = "scoring_sum_of_expressed_markers"
SCORING_LOG_FDR = "scoring_log_fdr"
SCORING_LOG_PVALUE = "scoring_log_p_value"

PFUN_BINOMIAL = "binom"
PFUN_HYPERGEOMETRIC = "hypergeom"


class ScoringNotImplemented(Exception):
    pass


class AnnotateSamples:
    """
    AnnotateSamples is class used for the annotation of data items with the
    annotations (e.g. Cell Types). We used the Mann-Whitney U test for selecting
    important values and the Hyper-geometric for assigning the annotations.

    Example on biological data where we assign cell types to cells:

    >>> gene_expressions_df = pd.read_csv("data/DC_expMatrix_DCnMono.csv.gz",
    ...                                   compression='gzip')
    >>> marker_genes_df = pd.read_csv("data/panglao_gene_markers.csv.gz",
    ...                               compression="gzip")
    >>> # rename genes column and filter human markers
    >>> marker_genes_df = marker_genes_df[
    ...     marker_genes_df["Organism"] == "Human"]
    >>>
    >>> annotations = AnnotateSamples.annotate_samples(
    ...     gene_expressions_df, marker_genes_df, num_all_attributes=60000,
    ...     attributes_col="Cell Type", annotations_col="Name",
    ...     p_threshold=0.05)

    Example for full manual annotation. Here annotation is split in three
    phases. We assume that data are already loaded.

    >>> z = AnnotateSamples.mann_whitney_test(gene_expressions_df)
    >>> scores, p_val = AnnotateSamples.assign_annotations(
    ...     z, marker_genes_df, gene_expressions_df, num_all_attributes=60000,
    ...     attributes_col="Cell Type", annotations_col="Name")
    >>> scores = AnnotateSamples.filter_annotations(
    ...     scores, p_val, p_threshold=0.05)
    """
    @staticmethod
    def log_cpm(data):
        """
        Function normalizes data with the log CPM methods.

        Parameters
        ----------
        data : pd.DataFrame
            Non-normalized data table.

        Returns
        -------
        pd.DataFrame
            Normalized data table.
        """
        norm_data = np.log(1 + AnnotateSamples._cpm(data))
        return norm_data

    @staticmethod
    def _cpm(data):
        """
        This function normalizes data with CPM methods.

        Parameters
        ----------
        data : pd.DataFrame
            Tabular data.
        """
        return data.divide(data.sum(axis=1), axis=0) * 1e6

    @staticmethod
    def _ranks(data):
        """
        This function computes ranks for data in the table along axis=0.

        Parameters
        ----------
        data : np.ndarray
            Array of data to be ranked

        Returns
        -------
        np.ndarray
            Table of data ranks
        """
        x_len = data.shape[0]
        x_mask = data.sum(axis=0) > 0

        # create a matrix of ranges - init with average rank
        # for columns without nonzero expressions
        data_ge_ranked = np.ones(data.shape) * (1 + data.shape[0]) / 2

        # compute ranks only for nonzero columns
        for i in np.where(x_mask)[0]:
            mask = data[:, i] > 0
            col = np.ones(x_len) * (1 + (x_len - mask.sum())) / 2
            col[mask] = rankdata(data[mask, i]) + (x_len - mask.sum())
            data_ge_ranked[:, i] = col
        return data_ge_ranked

    @staticmethod
    def mann_whitney_test(data):
        """
        Compute z values with the Mann-Whitney U test.

        Parameters
        ----------
        data : pd.DataFrame
            Tabular data.

        Returns
        -------
        pd.DataFrame
            Z-value for each item.
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data argument must be pandas DataFrame")

        if len(data) <= 1:
            return None

        # rank data
        data_ge_ranked = AnnotateSamples._ranks(data.values)

        # compute U, mu, sigma
        n = data_ge_ranked.shape[0]
        n2 = n - 1
        u = data_ge_ranked - 1
        mu = n2 / 2
        sigma = np.zeros(data_ge_ranked.shape[1])

        for i in range(data_ge_ranked.shape[1]):
            _, counts = np.unique(data_ge_ranked[:, i], return_counts=True)
            sigma[i] = np.sqrt(
                1 * n2 / 12 * ((n + 1) - np.sum((counts ** 3 - counts)) /
                               (n * (n - 1))))

        # compute z
        z = (u - mu) / (sigma + 1e-16)

        # pack z values to pandas dataframe
        z_dataframe = pd.DataFrame(z, columns=data.columns, index=data.index)
        return z_dataframe

    @staticmethod
    def _reorder_matrix(matrix, attributes_order):
        """
        Function reorder the columns of the array to fit the attributes_order.

        Parameters
        ----------
        matrix : pd.DataFrame
            Tabular data that needs to be reordered
        attributes_order : list
            Desired attributes order

        Returns
        ------
        np.ndarray
            Reordered array.
        """
        current_order = np.array(matrix.columns.values)
        values = matrix.values
        attributes_order = np.array(attributes_order)

        xsorted = np.argsort(attributes_order)
        ypos = np.searchsorted(attributes_order[xsorted], current_order)
        indices = xsorted[ypos]  # index which tell where should be the column

        reordered_values = np.zeros((values.shape[0], len(attributes_order)))
        for i_curr, i_dest in enumerate(indices):
            reordered_values[:, i_dest] = values[:, i_curr]

        return reordered_values

    @staticmethod
    def _select_attributes(z, attributes_order, z_threshold=1):
        """
        The function selects "over"-expressed attributes for items based on z
        values. It also reorders the matrix columns.

        Parameters
        ----------
        z : pd.Dataframe
            Tabular data z values for each item in the table
        attributes_order : list
            Desired genes order
        z_threshold : float
            The threshold for selecting the attribute. For each item the
            attributes with z-value above this value are selected.

        Returns
        -------
        np.ndarray
            Reordered and thresholded z-values
        """
        reordered_z = AnnotateSamples._reorder_matrix(z, attributes_order)

        return reordered_z > z_threshold

    @staticmethod
    def _group_attributes_annotations(available_annotations, attributes_order,
                                      attributes_col, annotations_col):
        """
        Function transforms annotations to matrix with the size
        (attributes_order x annotations).
        """
        types = sorted(
            list(set(available_annotations.loc[:, annotations_col].values)))
        attributes_annotations = np.zeros((len(attributes_order), len(types)))

        for _, m in available_annotations.iterrows():
            g = m[attributes_col]
            m = m[annotations_col]
            if g is not None:
                attributes_annotations[
                    attributes_order.index(g), types.index(m)] = 1

        return attributes_annotations, types

    @staticmethod
    def _score(scoring_type, p_values, fdrs, data, M, x, m, attributes_order):
        if scoring_type == SCORING_MARKERS_SUM:
            return AnnotateSamples._reorder_matrix(
                data, attributes_order).dot(M)
        elif scoring_type == SCORING_EXP_RATIO:
            return x / m
        elif scoring_type == SCORING_LOG_FDR:
            return -np.log(fdrs)
        elif scoring_type == SCORING_LOG_PVALUE:
            return -np.log(p_values)
        else:
            raise ScoringNotImplemented()

    @staticmethod
    def assign_annotations(z_values, available_annotations, data,
                           num_all_attributes=None,
                           attributes_col="Attributes",
                           annotations_col="Annotations",
                           z_threshold=1,
                           p_value_fun=PFUN_BINOMIAL,
                           scoring=SCORING_EXP_RATIO):
        """
        The function gets a set of attributes (e.g. genes) for each item and
        attributes for each annotation. It returns the annotations significant
        for each item.

        Parameters
        ----------
        z_values : pd.DataFrame
            DataFrame that shows z values for each item. Rows are data items
            and columns are attributes.
        available_annotations : pd.DataFrame
            Available annotations (e.g. cell types), this data frame has
            two columns: attributes column name is set by *attributes_col*
            variable (default: Attributes) and annotations is set by
            *annotations_col* variable (default: Annotations).
        data : pd.DataFrame
            Tabular input (raw) data - we need that to compute
            scores.
        num_all_attributes : int
            The number of all attributes for a case (also those that do not
            appear in the data). In the case of genes, it is the number of all
            genes that an organism has. It is recommended to set your value,
            in cases when the value is not set the number of attributes in
            z_values table will be used.
        attributes_col : str
            The name of an attributes column in available_annotations
            (default: Attributes").
        annotations_col : str
            The name of an annotations column in available_annotations
            (default: Annotations").
        z_threshold : float
            The threshold for selecting the attribute. For each item, the
            attributes with z-value above this value are selected.
        p_value_fun : str, optional (defaults: TEST_BINOMIAL)
            A function that calculates the p-value. It can be either
            PFUN_BINOMIAL that uses binom.sf or
            PFUN_HYPERGEOMETRIC that uses hypergeom.sf.
        scoring : str, optional (default=SCORING_EXP_RATIO)
            Type of scoring

        Returns
        -------
        pd.DataFrame
            Annotation probabilities
        pd.DataFrame
            Annotation FDRS.
        """
        if not isinstance(z_values, pd.DataFrame):
            raise TypeError("z_values argument must be pandas DataFrame")
        if not isinstance(available_annotations, pd.DataFrame):
            raise TypeError("available_annotations argument must be pandas "
                            "DataFrame")
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data argument must be pandas DataFrame")
        if not available_annotations[attributes_col].dtype == object:
            raise TypeError("The type of attributes_col column must be "
                            "string/object")
        if not available_annotations[annotations_col].dtype == object:
            raise TypeError("The type of annotations_col column must be "
                            "string/object")

        # select function for p-value
        if p_value_fun == PFUN_HYPERGEOMETRIC:
            p_fun = lambda x, N, m, k: hypergeom.sf(x, N, m, k)
        else:
            p_fun = lambda x, N, m, k: binom.sf(x, k, m / N)

        # make an attributes order
        attributes = z_values.columns.values
        attributes_annotations = available_annotations[attributes_col].values
        attributes_order = list(set(attributes) | set(attributes_annotations))

        # get attributes-annotations matrix M
        M, annotations = AnnotateSamples._group_attributes_annotations(
            available_annotations, attributes_order,
            attributes_col, annotations_col)

        Z = AnnotateSamples._select_attributes(
            z_values, attributes_order, z_threshold)

        # if user do not set own num_all_attributes value it is set to number
        # of attributes in the table
        if num_all_attributes is None:
            num_all_attributes = len(z_values.columns)

        x = Z.dot(M)
        k = np.repeat(Z.sum(axis=1).reshape(-1, 1), x.shape[1], axis=1)
        m = np.repeat(M.sum(axis=0).reshape(1, -1), x.shape[0], axis=0)

        p_values = p_fun(x - 1, num_all_attributes, m, k)

        fdrs = np.zeros(p_values.shape)
        for i, row in enumerate(p_values):
            fdrs[i] = np.array(FDR(row.tolist()))

        scores = AnnotateSamples._score(
            scoring, p_values, fdrs, data, M, x, m, attributes_order)

        scores_table = pd.DataFrame(
            scores, columns=annotations, index=data.index)
        fdrs_table = pd.DataFrame(fdrs, columns=annotations, index=data.index)

        return scores_table, fdrs_table

    @staticmethod
    def filter_annotations(scores, p_values, return_nonzero_annotations=True,
                           p_threshold=0.05):
        """
        This function filters the probabilities on places that do not reach the
        threshold for p-value and filter zero columns if
        return_nonzero_annotations is True.

        Parameters
        ----------
        scores : pd.DataFrame
            Scores for each annotation for data items
        p_values : pd.DataFrame
            p-value scores for annotations for data items
        return_nonzero_annotations : bool
            The flag that enables filtering the non-zero columns.
        p_threshold : float
            A threshold for accepting the annotations. Annotations that have
            FDR value bellow this threshold are used.

        Returns
        -------
        pd.Dataframe
            Filtered scores for each annotation for data items
        """
        if not isinstance(scores, pd.DataFrame):
            raise TypeError("scores argument must be pandas DataFrame")
        if not isinstance(p_values, pd.DataFrame):
            raise TypeError("p_values argument must be pandas DataFrame")

        scores = scores.copy()  # do not want to edit values inplace
        scores[p_values > p_threshold] = np.nan

        if return_nonzero_annotations:
            col_not_empty = ~np.isnan(scores).all(axis=0)
            scores = scores.loc[:, col_not_empty]
        return scores

    @staticmethod
    def annotate_samples(data, available_annotations,
                         num_all_attributes=None,
                         attributes_col="Attributes",
                         annotations_col="Annotations",
                         return_nonzero_annotations=True, p_threshold=0.05,
                         p_value_fun=PFUN_BINOMIAL, z_threshold=1,
                         scoring=SCORING_EXP_RATIO, normalize=False):
        """
        Function marks the data with annotations that are provided. This
        function implements the complete functionality. First select
        attributes for each item with z_test, then annotate data and
        filter data.

        Parameters
        ----------
        data : pd.DataFrame
            Tabular data
        available_annotations : pd.DataFrame
            Available annotations (e.g. cell types), this data frame has
            two columns: attributes column name is set by *attributes_col*
            variable (default: Attributes) and annotations is set by
            *annotations_col* variable (default: Annotations).
        num_all_attributes : int
            The number of all attributes for a case (also those that do not
            appear in the data). In the case of genes, it is the number of all
            genes that an organism has. It is recommended to set your value,
            in cases when the value is not set the number of attributes in
            z_values table will be used.
        return_nonzero_annotations : bool, optional (default=True)
            If true return scores for only annotations present in at least one
            sample.
        attributes_col : str
            The name of an attributes column in available_annotations
            (default: Attributes").
        annotations_col : str
            The name of an annotations column in available_annotations
            (default: Annotations").
        p_threshold : float
            A threshold for accepting the annotations. Annotations that has FDR
            value bellow this threshold are used.
        p_value_fun : str, optional (defaults: TEST_BINOMIAL)
            A function that calculates p-value. It can be either
            PFUN_BINOMIAL that uses statistics.Binomial().p_value or
            PFUN_HYPERGEOMETRIC that uses hypergeom.sf.
        z_threshold : float
            The threshold for selecting the attribute. For each item the
            attributes with z-value above this value are selected.
        scoring : str, optional (default = SCORING_EXP_RATIO)
            Type of scoring
        normalize : bool, optional (default = False)
            This variable tells whether to normalize data or not.

        Returns
        -------
        pd.DataFrame
            Scores table - each line of the table has scores that tell how
            probable is that items have specific annotations.
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data argument must be pandas DataFrame")
        if not isinstance(available_annotations, pd.DataFrame):
            raise TypeError("available_annotations argument must be pandas "
                            "DataFrame")
        if len(data) <= 1:
            raise ValueError("At least two data items are required for "
                             "method to work.")

        if normalize:
            data = AnnotateSamples.log_cpm(data)

        z = AnnotateSamples.mann_whitney_test(
            data)

        annotation_probs, annotation_fdrs = AnnotateSamples.assign_annotations(
            z, available_annotations, data,
            num_all_attributes=num_all_attributes,
            attributes_col=attributes_col, annotations_col=annotations_col,
            z_threshold=z_threshold,
            p_value_fun=p_value_fun, scoring=scoring)

        annotation_probs = AnnotateSamples.filter_annotations(
            annotation_probs, annotation_fdrs, return_nonzero_annotations,
            p_threshold
        )

        return annotation_probs
