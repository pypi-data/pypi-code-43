import copy

import numpy as np
import pandas as pd
from pandas.core.dtypes.common import is_bool_dtype, is_integer_dtype, is_float_dtype, is_string_like_dtype
from pandas.core.dtypes.common import is_categorical_dtype, is_datetime64_ns_dtype, is_timedelta64_ns_dtype

from azureml.studio.core.utils.missing_value_utils import drop_na, is_na
from azureml.studio.core.utils.labeled_list import LabeledList
from azureml.studio.core.utils.strutils import to_snake_case


class ColumnTypeName:
    NUMERIC = 'Numeric'
    STRING = 'String'
    BINARY = 'Binary'
    OBJECT = 'Object'
    CATEGORICAL = 'Categorical'
    DATETIME = 'DateTime'
    TIMESPAN = 'TimeSpan'
    NAN = 'NAN'


class ElementTypeName:
    INT = 'int64'
    FLOAT = 'float64'
    STRING = 'str'
    BOOL = 'bool'
    OBJECT = 'object'
    CATEGORY = 'category'
    DATETIME = 'datetime64'
    TIMESPAN = 'timedelta64'
    NAN = 'NAN'
    UNCATEGORY = 'uncategory'
    CONVERTABLE_LIST = [INT, FLOAT, STRING, BOOL, OBJECT, CATEGORY]
    NUMERIC_LIST = [INT, FLOAT, BOOL]


class SchemaConstants:
    TrueLabelType = 'True Labels'
    ERROR_ACTION_RAISE = 'raise'


class DataFrameSchema:

    def __init__(
            self,
            column_attributes: LabeledList,
            score_column_names: dict = {},
            label_column_name: dict = {},
            feature_channels: dict = None,
            extended_properties: dict = None,
    ):
        """

        :param column_attributes:  a LabeledList
        :param score_column_names: dict {<Score Column Type>: <Column Name>}
        :param label_column_name: column name or dict {<Label Column Type>: <Column Name>}
        :param feature_channels: dict {<Feature Name>: <FeatureChannel>}
        :param extended_properties: an extensible property set
        """
        self._column_attributes = column_attributes

        # both self._score_columns and self._label_columns save column_index as the value rather than a column name
        self._score_columns = {}
        self._label_columns = {}

        if score_column_names:
            # Use score_column_name.setter to initialize self._score_column_names
            self.score_column_names = score_column_names

        if label_column_name:
            # Use label_column_name.setter to initialize self._label_column_name
            self.label_column_name = label_column_name

        #  feature channel represents a group of DataTable
        #  columns which can be operated on as a group.
        self._feature_channels = feature_channels if feature_channels else {}

        # share some information between modules.
        # like, indicating data table's type[ data set, scored data set, result report]
        self._extended_properties = extended_properties if extended_properties else {}

    @property
    def column_attributes(self):
        return self._column_attributes

    @property
    def score_column_names(self):
        """
        Property method to get all Score column names
        :return: Score column names
        """
        if not self._score_columns:
            return dict()
        return {col_type: self._get_column_name_by_key(col_index)
                for col_type, col_index in self._score_columns.items()}

    @score_column_names.setter
    def score_column_names(self, type_key_dict):
        """
        Setter method to initialize _score_columns from a dict {<Score Column Type>: <Column Name>}
        :param type_key_dict: dict of Score column types to column name
        :return:
        """
        if not isinstance(type_key_dict, dict):
            raise TypeError(f'Argument "type_key_dict": Score column must be set by a dictionary.')

        for col_type, col_key in type_key_dict.items():
            col_index = self._get_column_index_by_key(col_key)
            self._remove_from_label_score_feature(col_index)
            self._score_columns.update({col_type: col_index})

    @score_column_names.deleter
    def score_column_names(self):
        self._score_columns.clear()

    @property
    def label_column_name(self):
        if not self._label_columns:
            return None
        return self._get_column_name_by_key(list(self._label_columns.values())[0])

    @label_column_name.setter
    def label_column_name(self, col_key_or_type_key_dict):
        """
        Setter method to initialize _label_column_name from column name/index or a dict
        {<Label Column Type>: <Column Name>} When input is dict, only the first item will be applied
        :param col_key_or_type_key_dict: column name/index or a dict of Label column types to column name
        :return:
        """
        if isinstance(col_key_or_type_key_dict, dict):
            if col_key_or_type_key_dict:
                col_type, col_key = list(col_key_or_type_key_dict.items())[0]
            else:
                return
        elif isinstance(col_key_or_type_key_dict, int) or isinstance(col_key_or_type_key_dict, str):
            col_type = SchemaConstants.TrueLabelType
            col_key = col_key_or_type_key_dict
        else:
            raise TypeError(f'Argument "col_key_or_type_key_dict": Label column must be set by a dictionary or'
                            f' by column name or index.')

        col_index = self._get_column_index_by_key(col_key)
        self._remove_from_label_score_feature(col_index)
        self._label_columns[col_type] = col_index

    @label_column_name.deleter
    def label_column_name(self):
        self._label_columns.clear()

    # Might need to be changed in the future
    @property
    def feature_channels(self):
        return self._feature_channels

    @feature_channels.setter
    def feature_channels(self, value):
        self._feature_channels.update(value)

    @property
    def extended_properties(self):
        return self._extended_properties

    def to_dict(self):
        return {
            'columnAttributes': self.column_attributes.to_list(),
            'featureChannels': [val.to_dict() for val in self.feature_channels.values()],
            'labelColumns': {col_type: self.column_attributes.names[col_index]
                             for col_type, col_index in self._label_columns.items()},
            'scoreColumns': self.score_column_names,
        }

    @classmethod
    def generate_column_attributes(cls, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError('Argument "df": Not Dataframe.')

        return LabeledList.from_items(
            (cls.generate_column_attribute(df.iloc[:, idx], col) for idx, col in enumerate(df.columns))
        )

    @classmethod
    def generate_column_attribute(cls, column, col_name, is_feature=True):
        (element_type, column_type) = cls.get_column_element_type(column)
        return ColumnAttribute(
            name=col_name,
            column_type=column_type,
            element_type=element_type,
            is_feature=is_feature
        )

    @classmethod
    def get_column_element_type(cls, column, col_name=None):
        # Note that integer column with missing values, eg. [1, 3, np.nan], will give ElementTypeName.FLOAT
        if not isinstance(column, pd.Series):
            raise TypeError(f'Column "{col_name}": Column type is not Pandas.Series.')

        if column.empty:
            return ElementTypeName.NAN, ColumnTypeName.NAN
        if is_na(column):
            return ElementTypeName.NAN, ColumnTypeName.NAN

        if is_categorical_dtype(column):
            return ElementTypeName.CATEGORY, ColumnTypeName.CATEGORICAL
        if is_datetime64_ns_dtype(column):
            return ElementTypeName.DATETIME, ColumnTypeName.DATETIME
        if is_timedelta64_ns_dtype(column):
            return ElementTypeName.TIMESPAN, ColumnTypeName.TIMESPAN
        if is_bool_dtype(column):
            return ElementTypeName.BOOL, ColumnTypeName.BINARY
        if is_integer_dtype(column):
            return ElementTypeName.INT, ColumnTypeName.NUMERIC
        if is_float_dtype(column):
            return ElementTypeName.FLOAT, ColumnTypeName.NUMERIC
        if is_string_like_dtype(column):
            return ElementTypeName.STRING, ColumnTypeName.STRING

        return cls._dynamic_detect_element_type(column)

    @classmethod
    def _dynamic_detect_element_type(cls, column):
        # Drop np.nan, None or pd.NaT, so that
        # they will not interfere with column type detection.
        column_new = drop_na(column)

        # TODO: improve this part
        # Currently, use the simple function to get better performance since it will be implemented by C
        is_bool = 40
        is_int = 30
        is_float = 20
        is_str = 10
        is_object = 0

        def detect(x):
            if isinstance(x, bool):
                return is_bool
            # np.int64 and np.int32 is not int type
            elif isinstance(x, (int, np.int64, np.int32)):
                return is_int
            elif isinstance(x, float):
                return is_float
            elif isinstance(x, str):
                return is_str
            else:
                return is_object

        detected_type = min(detect(x) for x in column_new)

        if detected_type is is_bool:
            return ElementTypeName.BOOL, ColumnTypeName.BINARY
        elif detected_type is is_int:
            return ElementTypeName.INT, ColumnTypeName.NUMERIC
        elif detected_type is is_float:
            return ElementTypeName.FLOAT, ColumnTypeName.NUMERIC
        elif detected_type is is_str:
            return ElementTypeName.STRING, ColumnTypeName.STRING
        else:
            return ElementTypeName.OBJECT, ColumnTypeName.OBJECT

    def set_extended_property(self, name, value):
        self._extended_properties[name] = value

    def validate(self, df):
        is_valid = False
        # For zero-row df, validate the df's column names are the same as column attributes
        if df.shape[0] == 0:
            is_valid = df.columns.tolist() == self.column_attributes.names

        column_attributes_by_df = self.generate_column_attributes(df)
        if len(column_attributes_by_df) == len(self.column_attributes):
            def is_matched(column_index):
                return column_attributes_by_df[column_index].element_type is ColumnTypeName.NAN or \
                       column_attributes_by_df[column_index] == self.column_attributes[column_index]

            is_valid = all(is_matched(column_index) for column_index in range(len(column_attributes_by_df)))

        if not is_valid:
            raise ValueError(f'Attributes "meta_data" do not match with Dataframe "df".')

    def set_column_attribute(self, col_key, column):
        col_name = self._get_column_name_by_key(col_key)
        DataFrameSchema._validate_column_type(column, col_name)

        self.column_attributes[col_key] = self.generate_column_attribute(
            column=column,
            col_name=col_name,
            # Keep is_feature attribute
            is_feature=self.column_attributes[col_key].is_feature
        )

    def get_column_attribute(self, col_key):
        return self.column_attributes[col_key]

    def add_column_attribute(self, col_attribute):
        self.column_attributes.validate_name(col_attribute.name)
        self.column_attributes.append(col_attribute.name, col_attribute)

    def set_column_name(self, col_key, new_col_name):
        col_name = self._get_column_name_by_key(col_key)
        self.column_attributes[col_key].name = new_col_name
        self.column_attributes.set_name(col_name, new_col_name)
        self._set_column_name_in_feature_channels(col_name, new_col_name)

    def copy(self, if_clone=False):
        if if_clone:
            return copy.deepcopy(self)
        return self

    def set_column_as_feature(self, col_key):
        col_name = self._get_column_name_by_key(col_key)

        self._remove_from_label_score_feature(col_name)
        self.get_column_attribute(col_name).is_feature = True

    def select_columns(self, col_keys):
        column_attributes = LabeledList.from_items((self.column_attributes[i] for i in col_keys))

        col_indexes = [self._get_column_index_by_key(x) for x in col_keys]
        score_column_names = {score_type: self._get_column_name_by_key(col_index)
                              for score_type, col_index in self._score_columns.items()
                              if col_index in col_indexes}

        label_column_name = {label_type: self._get_column_name_by_key(col_index)
                             for label_type, col_index in self._label_columns.items()
                             if col_index in col_indexes}

        feature_channels = {}
        col_names_set = set(col_indexes)
        for feature_type, channel in self._feature_channels.items():
            selected_col_names = col_names_set.intersection(channel.feature_column_names)
            if selected_col_names:
                feature_channels[feature_type] = FeatureChannel(
                    channel.name, channel.is_normalized, selected_col_names)

        return DataFrameSchema(
            column_attributes=column_attributes,
            score_column_names=score_column_names,
            label_column_name=label_column_name,
            feature_channels=feature_channels,
        )

    def _get_column_name_by_key(self, col_key):
        if isinstance(col_key, int):
            return self.column_attributes.get_name(col_key)
        return col_key

    def _get_column_index_by_key(self, col_key):
        if isinstance(col_key, int):
            return col_key
        return self.column_attributes.get_index(col_key)

    def _remove_from_label_score_feature(self, col_index):
        for k, v in self._label_columns.items():
            if v == col_index:
                del self._label_columns[k]
                return

        for k, v in self._score_columns.items():
            if v == col_index:
                del self._score_columns[k]
                return

        self.get_column_attribute(col_index).is_feature = False

    def _set_column_name_in_feature_channels(self, col_name, new_col_name):
        for key, value in self._feature_channels.items():
            if col_name in value.feature_column_names:
                loc = value.feature_column_names.index(col_name)
                value.feature_column_names[loc] = new_col_name
                return

    @staticmethod
    def from_dict(schema_data):
        return DataFrameSchema(
            column_attributes=LabeledList.from_list(schema_data['columnAttributes'], ColumnAttribute),
            feature_channels={
                val['name']: FeatureChannel.from_dict(val) for val in schema_data['featureChannels']
            },
            label_column_name=schema_data['labelColumns'],
            score_column_names=schema_data['scoreColumns'],
        )

    @staticmethod
    def from_data_frame(df: pd.DataFrame):
        return DataFrameSchema(DataFrameSchema.generate_column_attributes(df=df))

    @staticmethod
    def data_frame_to_dict(df: pd.DataFrame):
        return DataFrameSchema.from_data_frame(df).to_dict()

    @staticmethod
    def _validate_column_type(column, col_name):
        if not isinstance(column, pd.Series):
            raise TypeError(f'Column "{col_name}": Column type is not Pandas.Series.')


class ColumnAttribute():
    def __init__(self, name=None, column_type=None, element_type=None, is_feature=True):
        self._name = name
        self._column_type = column_type
        self._is_feature = is_feature  # Need to be changed in the future
        self._element_type = element_type

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def column_type(self):
        return self._column_type

    @property
    def is_feature(self):
        return self._is_feature

    @is_feature.setter
    def is_feature(self, value):
        self._is_feature = value

    @property
    def element_type(self):
        return self._element_type

    def __eq__(self, other):
        if not isinstance(other, ColumnAttribute):
            raise TypeError('Argument "other": Not column attribute.')

        return self.name == other.name and \
            self.column_type == other.column_type and \
            self.element_type == other.element_type

    def to_dict(self):
        result = {
            'name': self.name,
            'type': self.column_type,
            'isFeature': self.is_feature,
            'elementType': {'typeName': self.element_type, "isNullable": False}
        }

        return result

    @classmethod
    def from_dict(cls, kvs):
        kvs = kvs.copy()
        kvs['elementType'] = kvs['elementType']['typeName']
        kvs['columnType'] = kvs.pop('type')
        return cls(**{to_snake_case(key): val for key, val in kvs.items()})


class FeatureChannel():
    def __init__(self, name=None, is_normalized=None, feature_column_names=None):
        self._name = name
        self._is_normalized = is_normalized
        self._feature_column_names = feature_column_names

    def __eq__(self, other):
        if not isinstance(other, FeatureChannel):
            raise TypeError('Argument "other": Not feature channel.')

        return self.name == other.name and \
            self.is_normalized == other.is_normalized and \
            self.feature_column_names == other.feature_column_names

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def is_normalized(self):
        return self._is_normalized

    @property
    def feature_column_names(self):
        return self._feature_column_names

    def to_dict(self):
        result = {
            'name': self.name,
            'isNormalized': self.is_normalized,
            'featureColumns': self.feature_column_names
        }

        return result

    @classmethod
    def from_dict(cls, kvs):
        kvs = kvs.copy()
        kvs['featureColumnNames'] = kvs.pop('featureColumns')
        return cls(**{to_snake_case(key): val for key, val in kvs.items()})
