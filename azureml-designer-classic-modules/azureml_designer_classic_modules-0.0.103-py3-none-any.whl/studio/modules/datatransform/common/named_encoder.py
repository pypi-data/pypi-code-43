import numpy as np
import azureml.studio.common.datatable.data_type_conversion as data_type_conversion
from azureml.studio.modulehost.constants import ElementTypeName
from pandas.core.dtypes.common import is_categorical_dtype
from azureml.studio.common.datatable.data_table_schema import DataTableSchema
from azureml.studio.common.error import ErrorMapping, ColumnUniqueValuesExceededError
from scipy.stats import lognorm
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder, MinMaxScaler, StandardScaler

import azureml.studio.modules.ml.common.mathematic_op as math_op


# todo: fix the threshold.
# it is the instances' size of a customer's dataset
MAX_CATEGORY_COUNT = 1000
# nearly all categories are different from each other, according to the bot_detection dataset
MAX_CATEGORY_PERCENT = 0.97
_NAN_STR = '#NAN'


class NamedMinMaxEncoder:
    def __init__(self, column_name: str, constant_column_option=False):
        self.column_name = column_name
        self.encoder = MinMaxScaler()
        self.constant_column_option = constant_column_option
        self.std = None
        # unfitted flag = True means that it got invalid series when preform fitting, and it was not fitted.
        # values will be transformed to nan by unfitted encoder.
        self.unfitted = False

    def fit(self, series):
        series = math_op.inf2nan(series)
        if all(series.isna()):
            self.unfitted = True
            return
        self.std = np.nanstd(series)
        if self.std < 1e-9:
            return
        if np.issubdtype(series.dtype, np.integer):
            series = series.astype(np.float64)
        self.encoder.fit(series.values.reshape(-1, 1))

    def transform(self, series):
        series = math_op.inf2nan(series)
        values = np.array(series.values, dtype=np.float)
        if getattr(self, 'unfitted', False):
            return np.full_like(series, np.nan, dtype=float)
        if self.std < 1e-9:
            if self.constant_column_option:
                return values * 0.0
            else:
                return np.full_like(values, np.nan, dtype=float)
        return self.encoder.transform(values.reshape(-1, 1)).reshape(-1)

    def fit_transform(self, series):
        self.fit(series)
        return self.transform(series)


class NamedOneHotEncoder:
    def __init__(self, column_name: str):
        self.column_name = column_name
        self.one_hot_encoder = OneHotEncoder(sparse=True, handle_unknown='ignore')

    def fit(self, series):
        series = self.validate_series(series)
        self.one_hot_encoder.fit(np.array(series.values).reshape(-1, 1))

    def transform(self, series):
        series = self.validate_series(series)
        encoded = self.one_hot_encoder.transform(np.array(series.values).reshape(-1, 1))

        return encoded

    def fit_transform(self, series):
        self.fit(series)
        return self.transform(series)

    def inverse_transform(self, array):
        return self.one_hot_encoder.inverse_transform(array.reshape(-1, 1)).reshape(-1)

    def validate_series(self, series):
        if is_categorical_dtype(series.dtype):
            self._check_too_many_unique_values(categories_size=len(series.cat.categories),
                                               instances_size=series.count(),
                                               column_name=series.name)
            if _NAN_STR not in series.cat.categories:
                series = series.cat.add_categories(_NAN_STR)
            series.fillna(_NAN_STR, inplace=True)
            series = data_type_conversion.convert_column_by_element_type(series, ElementTypeName.STRING)
        elif DataTableSchema.get_column_element_type(series)[0] == ElementTypeName.BOOL:
            series.fillna(_NAN_STR, inplace=True)
            series = data_type_conversion.convert_column_by_element_type(series, ElementTypeName.STRING)
        else:
            categories_size = len(set(series))
            self._check_too_many_unique_values(categories_size=categories_size,
                                               instances_size=series.count(),
                                               column_name=series.name)
            series.fillna(_NAN_STR, inplace=True)
        return series

    @staticmethod
    def _check_too_many_unique_values(categories_size, instances_size, column_name):
        """Check whether a category or a string column contains too many unique values

        Some training data contains a text column or instances_id column, which are illegal features.
        For the text column, it could not be simply treated as categories. Text analytics modules should be used to
        pre-process text feature first.
        For the instances_id column, it costs a great amount of memory but is useless to train a model.
        So we should throw ColumnUniqueValuesExceededError when training data contains such columns.

        However, it is difficult to check whether the data is text or instances_id, accordingly,
        now the condition is set as:
        both the percentage and number of categories exceed the limitation.

        :param categories_size: int, number of unique categories in the column
        :param instances_size: int, number of non-nan instances in the column.
        :return: None
        """
        if (categories_size > MAX_CATEGORY_COUNT and
                categories_size > MAX_CATEGORY_PERCENT * instances_size):
            ErrorMapping.throw(ColumnUniqueValuesExceededError(column_name=column_name))


class NamedLabelEncoder:
    def __init__(self, column_name: str):
        self.column_name = column_name
        self.label_encoder = OrdinalEncoder()

    def fit(self, series):
        self.label_encoder.fit(series.values.reshape(-1, 1))

    def transform(self, series):
        return self.label_encoder.transform(series.values.reshape(-1, 1)).reshape(-1)

    def fit_transform(self, series):
        self.fit(series)
        return self.transform(series)

    def inverse_transform(self, array):
        return self.label_encoder.inverse_transform(array.reshape(-1, 1)).reshape(-1)

    @property
    def label_mapping(self):
        """
        only encode one column(label column).
        if label_encoder had been fitted, it will have attribute 'categories_', a list which has a single item.
        This item is the category mapping generated when fitting.
        :return:
        """
        label_mapping = getattr(self.label_encoder, 'categories_', None)
        if label_mapping:
            return self.label_encoder.categories_[0]
        raise ValueError("invalid label encoder")


class BinaryNamedLabelEncoder:
    """Label encoder for evaluating binary classifier scored dataset.

    Args:
        positive_label(any), record the label which will be mapped to 1.
        negative_label(any), record the label which will be mapped to 0.
        transform_dict(dict), mapping dict, map positive_label to 1 while map negative label to 0.
    """

    def __init__(self):
        self._positive_label = None
        self._negative_label = None

    def transform(self, series):
        """Transform label to 0/1 encoding."""
        series = series.apply(lambda x: self.transform_dict[x])
        return series

    def fill_missing_label(self, label):
        """Fill missing positive or negative label

        return filled label type('positive' or 'negative') if existing missing label.
        else return None
        """
        if self.positive_label is None:
            self.positive_label = label
            return 'positive'
        elif self.negative_label is None:
            self.negative_label = label
            return 'negative'
        return None

    @property
    def transform_dict(self):
        return {self.positive_label: 1, self.negative_label: 0}

    @property
    def positive_label(self):
        return self._positive_label

    @positive_label.setter
    def positive_label(self, value):
        if self.positive_label is not None:
            raise ValueError("Could not set an existing positive label.")
        self._positive_label = value

    @property
    def negative_label(self):
        return self._negative_label

    @negative_label.setter
    def negative_label(self, value):
        if self.negative_label is not None:
            raise ValueError("Could not set an existing negative label.")
        self._negative_label = value


class NamedLogNormalEncoder:
    def __init__(self, column_name, constant_column_option=False):
        self.std = None
        self.constant_column_option = constant_column_option
        self.dist = None
        self.invalid = True
        self.column_name = column_name

    def fit(self, series):
        # Make copy of original series in fit as NamedLogNormalEncoder can handle 'inf' in transform.
        series = math_op.inf2nan(series.copy())
        series = series[series > 0]
        self.std = np.nanstd(series)
        if self.std < 1e-9:
            return
        if series.shape[0] > 0:
            shape, loc, scale = lognorm.fit(series, floc=0)
            self.dist = lognorm(shape, loc, scale)
            self.invalid = False

    def transform(self, series):
        if self.std < 1e-9:
            if self.constant_column_option:
                return series.values * 0.0
            else:
                return series.values * np.nan
        if self.invalid:
            return [np.nan] * len(series)
        # Transform nan values will cause "Comparing nan with number warning"
        # To avoid this warning, record the indexes of values which are not NA,
        # and only perform transforming on them.
        # Then, replace the corresponding position in the input series with transformed values.
        valid_index = series[series.notna()].index
        not_nan_transformed = self.dist.cdf(series.dropna().values)
        transformed_series = series.copy()
        transformed_series.loc[valid_index] = not_nan_transformed
        return transformed_series

    def fit_transform(self, series):
        self.fit(series)
        return self.transform(series)


class NamedZScoreEncoder:
    def __init__(self, column_name: str, constant_column_option=False):
        self.column_name = column_name
        self.encoder = StandardScaler()
        self.constant_column_option = constant_column_option
        self.std = None

    def fit(self, series):
        series = math_op.inf2nan(series)
        self.std = np.nanstd(series)
        if self.std < 1e-9:
            return
        if np.issubdtype(series.dtype, np.integer):
            series = series.astype(np.float64)
        self.encoder.fit(series.values.reshape(-1, 1))

    def transform(self, series):
        if self.std < 1e-9:
            if self.constant_column_option:
                return series.values * 0.0
            else:
                return series.values * np.nan
        series = math_op.inf2nan(series)
        if np.issubdtype(series.dtype, np.integer):
            series = series.astype(np.float64)
        return self.encoder.transform(series.values.reshape(-1, 1)).reshape(-1)

    def fit_transform(self, series):
        self.fit(series)
        return self.transform(series)


class NamedLogisticEncoder:
    def __init__(self, column_name: str, constant_column_option=False):
        self.column_name = column_name

    def fit(self, series):
        pass

    def transform(self, series):
        return math_op.sigmoid(series)

    def fit_transform(self, series):
        self.fit(series)
        return self.transform(series)

    def inverse_transform(self, series):
        return math_op.reverse_sigmoid(series)


class NamedTanhEncoder:
    def __init__(self, column_name: str, constant_column_option=False):
        self.column_name = column_name

    def fit(self, series):
        pass

    def transform(self, series):
        return np.tanh(series)

    def fit_transform(self, series):
        self.fit(series)
        return self.transform(series)

    def inverse_transform(self, series):
        return np.arctan(series)
