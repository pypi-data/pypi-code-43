import pandas as pd
import numpy as np
from collections import Counter

from pandas.api.types import is_categorical_dtype

from azureml.studio.core.utils.missing_value_utils import drop_na
from azureml.studio.core.data_frame_schema import ColumnTypeName, DataFrameSchema
from azureml.studio.core.io.visualizer import JsonVisualizer
from azureml.studio.core.logger import logger

UNKNOWN_OBJECT = 'cannot be visualized'


class DataFrameVisualizer(JsonVisualizer):
    # This type is for the visualization in official modules.
    DEFAULT_TYPE = 'Visualization'
    MAX_ROW_NUMBER = 100
    # a dictionary to map statistical names in output dictionary
    # to index name in describe DataFrame of DataTable
    NUMERIC_STAT_NAMES_MAPPING = {
        'Mean': 'mean',
        'Median': '50%',
        'Min': 'min',
        'Max': 'max',
        'Standard Deviation': 'std'
    }
    MISSING_KEY = 'Missing Values'
    UNIQUE_KEY = 'Unique Values'
    # statistics for general column
    GENERIC_STAT_NAMES = [UNIQUE_KEY, MISSING_KEY]

    ALL_STAT_NAMES = list(NUMERIC_STAT_NAMES_MAPPING.keys()) + GENERIC_STAT_NAMES

    def __init__(self, data: pd.DataFrame, schema=None, file_path=None):
        if not isinstance(data, pd.DataFrame):
            raise ValueError(f"DataFrame is required, got {type(data)}")
        if schema is None:
            schema = DataFrameSchema.data_frame_to_dict(data)
        if isinstance(schema, DataFrameSchema):
            schema = schema.to_dict()
        self.column_attrs = schema.get('columnAttributes')

        self.data = data
        self.num_of_cols = len(data.columns)
        self.num_of_rows = len(data)
        if self.num_of_cols == 0 or self.num_of_rows == 0:
            self.df_statistics = pd.DataFrame()
        else:
            self.df_statistics = self.compute_statistics(data)

        try:
            json_data = {
                "visualizationType": 'default',
                "data": self._get_data_frame_visualization(),
                "statistics": self._get_statistics(),
                "layout": self._get_graph_layout(),
            }
        except BaseException as e:
            logger.exception(f"Exception occurs when computing visualization.", exc_info=e)
            json_data = {'visualizationType': 'default', 'data': None, 'statistics': None, 'layout': None}

        if file_path is None:
            file_path = '_data.visualization'
        super().__init__(self.DEFAULT_TYPE, json_data, file_path)

    def compute_statistics(self, data):
        default_stat = pd.Series({'count': self.num_of_rows})
        # Treat np.inf and -np.inf as np.nan temporarily, which will be ignored when computing statistics
        with pd.option_context('use_inf_as_na', True):
            stats = []
            for col in data.columns:
                try:
                    stats.append(data[col].describe())
                except BaseException as e:
                    logger.exception(f"Exception occurs when computing statistics in column '{col}'", exc_info=e)
                    stats.append(default_stat)
            statistics = pd.concat(stats, axis=1, keys=data.columns, sort=False)
        return statistics

    def _get_data_frame_visualization(self):
        return self.visualization_item(
            self._sample_visualization(),
            self._schema_visualization(),
            self.num_of_rows,
            self.num_of_cols,
        )

    def _sample_visualization(self):
        num_samples = min(len(self.data), self.MAX_ROW_NUMBER)
        return DataFrameEncoder.encode_as_matrix(self.data[:num_samples])

    @staticmethod
    def _attr_visualization(index, name, elm_type, col_type):
        return {
            'name': name,
            'index': index,
            'elementType': elm_type,
            'featureType': f'{col_type} Feature',
        }

    def _schema_visualization(self):
        return [
            self._attr_visualization(
                index=i, name=attr['name'], elm_type=attr['elementType']['typeName'], col_type=attr['type']
            ) for i, attr in enumerate(self.column_attrs)
        ]

    def _get_statistics(self):
        features = [
            self._attr_visualization(i, name, 'float64', 'Numeric') for i, name in enumerate(self.ALL_STAT_NAMES)
        ]
        records = [] if self.num_of_rows == 0 else [
            self._get_column_statistics(
                self.data[column], stat=self.df_statistics[column],
            ) for column in self.data.columns[:self.MAX_ROW_NUMBER]
        ]
        return self.visualization_item(records, features, self.num_of_cols, len(self.ALL_STAT_NAMES))

    def _get_column_statistics(self, column, stat):
        result = []
        nan = ElementEncoder.FLOAT_MAPPER[np.nan]
        unique_val = stat['unique'] if 'unique' in stat and not pd.isnull(stat['unique']) else column.nunique()
        for key in self.ALL_STAT_NAMES:
            if key == self.MISSING_KEY:
                result.append(int(len(column) - stat['count']))
            elif key == self.UNIQUE_KEY:
                result.append(int(unique_val))
            else:
                df_key = self.NUMERIC_STAT_NAMES_MAPPING.get(key)
                result.append(ElementEncoder.encode(stat[df_key]) if df_key in stat else nan)
        return result

    def _get_graph_layout(self):
        features = [
            self._attr_visualization(i, name, 'object', 'Object') for i, name in enumerate(['Histogram', 'Boxplot'])
        ]
        layouts = [] if self.num_of_rows == 0 else [
            self._hist_boxplot_column(
                self.data[column],
                self.column_attrs[i],
                col_stat=self.df_statistics[column],
            ) for i, column in enumerate(self.data.columns[:self.MAX_ROW_NUMBER])
        ]
        return self.visualization_item(layouts, features, self.num_of_cols, numberOfColumns=2)

    @staticmethod
    def _hist_boxplot_column(column, col_attr, col_stat):
        nrows = len(column)
        if is_categorical_dtype(column):
            # First convert column to numpy.array to drop the categorical dtype to avoid bug.
            column = pd.Series(np.asarray(column))
        # Drop NA to make sure NA values doesn't affect the columns.
        data = drop_na(column, include_inf=True)
        hist = DataFrameVisualizer._hist_column(data, nrows, col_attr)
        boxplot = DataFrameVisualizer._box_plot_column(data, col_stat) \
            if len(data) > 0 and col_attr['type'] == ColumnTypeName.NUMERIC else None
        return hist, boxplot

    @staticmethod
    def _hist_column(column, nrows, col_attr):
        try:
            if col_attr['type'] == ColumnTypeName.NUMERIC and len(column) > 0:
                return NumericHistogramLayout(column, nrows).to_json()
            return HistogramLayout(column, nrows).to_json()
        except BaseException:
            return None

    @staticmethod
    def _box_plot_column(column, col_stat):
        try:
            return BoxplotLayout(column, col_stat).to_json()
        except BaseException:
            return None

    @staticmethod
    def visualization_item(records, features, numberOfRows, numberOfColumns, name=None):
        return locals().copy()


class DataFrameEncoder:
    @staticmethod
    def encode_as_matrix(df: pd.DataFrame):
        results = []
        for i in range(len(df)):
            row = df.iloc[i]
            if isinstance(row, pd.Series):
                results.append([ElementEncoder.encode(element) for element in row])
            else:
                # In some corner cases, e.g., df = pd.DataFrame({'col0': ['Apple]}, dtype='category'),
                # the row is only the element instead of a pandas series.
                results.append([ElementEncoder.encode(row)])
        return results

    @staticmethod
    def encode_as_dict(df: pd.DataFrame):
        return {column: DataFrameEncoder.encode_column(df[column]) for column in df.columns}

    @staticmethod
    def encode_column(column: pd.Series):
        if len(column) == 0:
            return None
        elif len(column) == 1:
            return ElementEncoder.encode(column[0])
        return [ElementEncoder.encode(obj) for obj in column]


class ElementEncoder:
    FLOAT_MAPPER = {
        np.nan: {'isNan': True},
        np.inf: 'inf',
        -np.inf: '-inf',
    }
    @staticmethod
    def encode(obj):
        """
        Convert an object, so that the conversion result can be written into json
        """
        if isinstance(obj, float):
            # nan, inf and -inf are float type, while nan is pandas null
            if pd.isnull(obj):
                return ElementEncoder.FLOAT_MAPPER.get(np.nan)
            elif np.isposinf(obj):
                return ElementEncoder.FLOAT_MAPPER.get(np.inf)
            elif np.isneginf(obj):
                return ElementEncoder.FLOAT_MAPPER.get(-np.inf)
            else:
                return obj
        elif isinstance(obj, (int, bool, str, complex)):
            return obj

        # In case obj is numpy built-in type
        # Note that np.nan, np.inf, -np.inf is not np.generic
        elif isinstance(obj, np.generic):
            return ElementEncoder.encode(obj.item())

        elif isinstance(obj, np.ndarray):
            return [ElementEncoder.encode(x) for x in obj]

        elif obj is None:
            return None

        # custom json encoder
        # pandas.Series and pandas.DataFrame types have to_json method
        elif hasattr(obj, 'to_json'):
            return obj.to_json()

        elif isinstance(obj, (pd.Timestamp, pd.Timedelta)):
            return str(obj)

        elif obj is pd.NaT:
            # pd.NaT is not float type
            return ElementEncoder.FLOAT_MAPPER.get(np.nan)

        elif isinstance(obj, list):
            return [ElementEncoder.encode(x) for x in obj]

        elif isinstance(obj, tuple):
            return tuple(ElementEncoder.encode(x) for x in obj)

        elif isinstance(obj, dict):
            return {ElementEncoder.encode(key): ElementEncoder.encode(value) for key, value in obj.items()}

        else:
            return UNKNOWN_OBJECT


class HistogramLayout:
    """
    A histogram is a representation of the distribution of data.
    To construct a histogram, the first step is to 'bin' the range of values,
    that is to divide the entire range of values into a series of intervals,
    and then count how many values fall into each interval.

    Each bin of a histogram is described by a class HistogramBin with three fields x, dx and y.
    x means the minimum of the interval, dx means the range of the interval and y means the number
    of values or frequency fall into the interval
    """

    NUMBER_OF_BINS = 10

    def __init__(self, data: pd.Series, number_of_records):
        # Convert category column to a type matching its values
        # to prevent potential errors when computing graph layout
        # if dt.get_column_type(column_index) == ColumnTypeName.CATEGORICAL:
        #    column = convert_column_by_element_type(column, ElementTypeName.UNCATEGORY)
        self.number_of_records = number_of_records
        self.bins = self.compute_bins(data)

    def compute_bins(self, data: pd.Series):
        counts = Counter(data)
        bins = [HistogramBin(x=key, dx='', y=counts.get(key)) for key in counts]
        # Sort self.bins according to y value
        bins.sort(key=lambda bin_: bin_.y, reverse=True)
        bins = bins[:self.NUMBER_OF_BINS]
        return bins

    def to_json(self):
        return {
            "Bins": [bin_.to_json() for bin_ in self.bins],
            "NumberOfRecords": self.number_of_records
        }


class NumericHistogramLayout(HistogramLayout):
    def compute_bins(self, data: pd.Series):
        try:
            hist, bin_edges = np.histogram(data, bins=self.NUMBER_OF_BINS)
        except IndexError as e:
            max_val, min_val = max(data), min(data)
            if float(max_val) + 1 - min_val == 0:
                # Bug ID: 461520
                # If this happens, the IndexError is caused by precision error in numpy.
                # max(data) == min(data) > 2**52 cause max(data) + 1 == min(data) due to the float64 precision,
                # then numpy computes a wrong histogram range and throw error.
                # See details in https://github.com/numpy/numpy/issues/8627
                # To solve this problem, we compute the histogram with provided histogram range.
                delta = abs(max_val) / 1e10  # Delta should be large enough to compute the edges of histogram.
                hist_range = (min_val - delta, max_val + delta)
                hist, bin_edges = np.histogram(data, bins=self.NUMBER_OF_BINS, range=hist_range)
            else:
                raise ValueError("Error occurs while computing histogram with the data.") from e
        return [HistogramBin(
            x=bin_edges[i],
            dx=bin_edges[i+1] - bin_edges[i],
            y=hist[i],
        ) for i in range(self.NUMBER_OF_BINS)]


class HistogramBin:
    """
    Each bin of a histogram is described by a class HistogramBin with three fields x, dx and y.
    x means the minimum of the interval, dx means the range of the interval and y means the number
    of values or frequency fall into the interval
    """
    def __init__(self, x: float, dx, y: int, number_of_elements=0):
        self.x = x
        self.dx = dx
        self.y = y
        self.number_of_elements = number_of_elements

    def to_json(self):
        return {
            "x": ElementEncoder.encode(self.x),
            "dx": ElementEncoder.encode(self.dx),
            "y": ElementEncoder.encode(self.y),
            "numElements": self.number_of_elements,
        }


class BoxplotLayout:
    """
    A boxplot is a standardized way of displaying the distribution of data based on its statistics, including
    minimum, first quartile, median, third quartile, maximum and outliers.

    """
    MAX_NUMBER_OF_OUTLIERS = 25

    def to_json(self):
        return {
            "median": ElementEncoder.encode(self.median),
            "boxBottom": ElementEncoder.encode(self.box_bottom),
            "boxTop": ElementEncoder.encode(self.box_top),
            "whiskerBottom": ElementEncoder.encode(self.whisker_bottom),
            "whiskerTop": ElementEncoder.encode(self.whisker_top),
            "outliers": ElementEncoder.encode(self.outliers)
        }

    def __init__(self, data: pd.Series, df_statistics: pd.DataFrame):
        data = data.to_numpy()
        self.box_bottom = df_statistics.at['25%']
        self.median = df_statistics.at['50%']
        self.box_top = df_statistics.at['75%']

        iqr = self.box_top - self.box_bottom
        upper_whisker_bound = self.box_top + 1.5 * iqr
        lower_whisker_bound = self.box_bottom - 1.5 * iqr

        # Compute whisker_bottom which is the smallest value bigger than lower_whisker_bound
        self.whisker_bottom = data[data >= lower_whisker_bound].min()

        # Compute whisker_top which is the largest value smaller than upper_whisker_bound
        self.whisker_top = data[data <= upper_whisker_bound].max()

        # Compute outliers which is any value smaller than lower_whisker_bound or
        # larger than upper_whisker_bound
        # The maximum number of outliers on one side is max_number_of_outliers
        outliers_small = data[data < self.whisker_bottom]
        number_of_partition = min(self.MAX_NUMBER_OF_OUTLIERS, len(outliers_small))
        outliers_small = np.partition(outliers_small, number_of_partition-1)[:number_of_partition]

        outliers_big = data[data > self.whisker_top]
        number_of_partition = min(self.MAX_NUMBER_OF_OUTLIERS, len(outliers_big))
        outliers_big = np.partition(outliers_big, -number_of_partition)[-number_of_partition:]

        self.outliers = outliers_small.tolist() + outliers_big.tolist()
