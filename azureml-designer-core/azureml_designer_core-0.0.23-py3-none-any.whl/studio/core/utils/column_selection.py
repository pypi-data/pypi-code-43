import json
import re
import pandas as pd
from pandas.core.dtypes.common import is_integer_dtype, is_float_dtype, is_bool_dtype, is_string_like_dtype
from pandas.core.dtypes.common import is_datetime64_ns_dtype, is_timedelta64_ns_dtype, is_categorical_dtype

from azureml.studio.core.io.data_frame_directory import DataFrameDirectory
from azureml.studio.core.data_frame_schema import DataFrameSchema, ColumnTypeName, ElementTypeName


class RuleType:
    COLUMN_NAMES = 'ColumnNames'
    COLUMN_INDEXES = 'ColumnIndexes'
    COLUMN_TYPES = 'ColumnTypes'
    ALL_COLUMNS = 'AllColumns'


class ColumnKind:
    FEATURE = 'Feature'
    SCORE = 'Score'
    LABEL = 'Label'
    ALL = 'All'


class ColumnType:
    STRING = 'String'
    INTEGER = 'Integer'
    DOUBLE = 'Double'
    BOOLEAN = 'Boolean'
    DATETIME = 'DateTime'
    TIME_SPAN = 'TimeSpan'
    CATEGORICAL = 'Categorical'
    NUMERIC = 'Numeric'
    ALL = 'All'


def is_string_series(series: pd.Series):
    # pandas doesn't provide a good solution for string series,
    # defaultly a string series is object dtype, which is indistinguishable with mixed type series.
    # is_string_like_dtype can handle the case the the series is np string arrays,
    # otherwise we should check whether all elements are string types.
    return is_string_like_dtype(series) or series.apply(type).eq(str).all()


def is_numeric_dtype(series: pd.Series):
    # If we use is_numeric_dtype in pandas, bool will be treated as numeric, which is not acceptable in our scenario.
    return is_integer_dtype(series) or is_float_dtype(series)


class ColumnSelectionRuleSet:
    IS_FILTER = 'isFilter'
    RULES = 'rules'

    def __init__(self, input_dict):
        self.is_filter = input_dict.get(ColumnSelectionRuleSet.IS_FILTER)
        self.rules = list()
        for rule_dict in input_dict.get(ColumnSelectionRuleSet.RULES):
            self.rules.append(ColumnSelectionRule(rule_dict))

    def is_valid(self):
        """
        Interpret the ruleset as follows to get the set of selected columns.
        Prerequisites:
            1. Each rule is either an include rule or exclude rule.
            2. Rules are processed in order.
            3. Ensure that the first rule is an include rule.
               In filter mode, the first rule must be an include rule,
               In non-filter mode, there is only one include rule.
        :return: True if the rule set is valid, otherwise return False
        """
        if not isinstance(self.is_filter, bool):
            return False

        if not isinstance(self.rules, list) or not self.rules:
            return False

        # In non-filter mode, only one include rule is allowed.
        if not self.is_filter and self.rule_count > 1:
            return False

        # See prerequisites 3
        if self.rules[0].is_exclude:
            return False
        return all((rule.is_valid() for rule in self.rules))

    def schema_required(self):
        return any((rule.schema_required() for rule in self.rules))

    @property
    def rule_count(self):
        return len(self.rules)


class ColumnSelectionRule:
    RULE_TYPE = 'ruleType'
    IS_EXCLUDE = 'exclude'
    COLUMNS = 'columns'
    COLUMN_TYPES = 'columnTypes'
    COLUMN_KINDS = 'columnKinds'

    def __init__(self, input_dict):
        self.rule_type = input_dict.get(ColumnSelectionRule.RULE_TYPE)
        self.is_exclude = input_dict.get(ColumnSelectionRule.IS_EXCLUDE)
        self.columns = input_dict.get(ColumnSelectionRule.COLUMNS)
        self.column_types = input_dict.get(ColumnSelectionRule.COLUMN_TYPES)
        self.column_kinds = input_dict.get(ColumnSelectionRule.COLUMN_KINDS)

    def is_valid(self):
        """
        Interpret the rules in order as follows:
            1. Interpret the rule's selection criteria as if it were an include rule, against
            the full set of columns in the DataFrame, to get a set of columns selected by the rule.
            2. If the rule is an include rule, then set includedIndexes to the union of includedIndexes
            and the rule's column set.
            3. If the rule is an exclude rule, then remove any columns in the rule's column set from
            includedIndexes.
            4. Once all the rules have been processed, includedIndexes contains the set of selected
            columns.
        :return: True if the rule is valid, otherwise return False
        """
        if not isinstance(self.rule_type, str) or not isinstance(self.is_exclude, bool):
            return False

        if self.rule_type in {RuleType.COLUMN_INDEXES, RuleType.COLUMN_NAMES}:
            if not isinstance(self.columns, list) or not self.columns:
                return False

        if self.rule_type == RuleType.COLUMN_TYPES:
            # A COLUMN_TYPE rule must have the same size
            if not isinstance(self.column_types, list) or not self.column_types:
                return False
            if not isinstance(self.column_kinds, list) or not self.column_kinds:
                return False
        return True

    def schema_required(self):
        return self.rule_type == RuleType.COLUMN_TYPES


class ColumnSelectionError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class ColumnSelectionInvalidRuleSetError(ColumnSelectionError):
    def __init__(self):
        super().__init__("ColumnSelection is initialized with invalid rule set.")


class ColumnSelectionColumnNotFoundError(ColumnSelectionError):
    def __init__(self, column_index):
        self.column_index = column_index
        super().__init__(f'Column with name or index "{column_index}" not found.')


class ColumnSelectionIndexParsingError(ColumnSelectionError):
    def __init__(self, column_index_or_range):
        self.column_index_or_range = column_index_or_range
        super().__init__(f'Column index or range "{column_index_or_range}" could not be parsed.')


class ColumnSelectionIndexRangeError(ColumnSelectionError):
    def __init__(self, column_range):
        self.column_range = column_range
        super().__init__(f'Column range "{column_range}" is invalid or out of range.')


class ColumnSelection:
    _column_type_to_check_methods = {
        ColumnType.NUMERIC: is_numeric_dtype,
        ColumnType.INTEGER: is_integer_dtype,
        ColumnType.DOUBLE: is_float_dtype,
        ColumnType.STRING: is_string_series,
        ColumnType.DATETIME: is_datetime64_ns_dtype,
        ColumnType.TIME_SPAN: is_timedelta64_ns_dtype,
        ColumnType.BOOLEAN: is_bool_dtype,
        ColumnType.CATEGORICAL: is_categorical_dtype,
    }
    _element_type_to_column_type = {
        ElementTypeName.INT: ColumnType.INTEGER,
        ElementTypeName.FLOAT: ColumnType.DOUBLE,
        ElementTypeName.STRING: ColumnType.STRING,
        ElementTypeName.BOOL: ColumnType.BOOLEAN,
        ElementTypeName.CATEGORY: ColumnType.CATEGORICAL,
        ElementTypeName.DATETIME: ColumnType.DATETIME,
        ElementTypeName.TIMESPAN: ColumnType.TIME_SPAN
    }

    def __init__(self, json_query=None, dict_rule_set=None):
        if dict_rule_set is not None:
            self.rule_set = ColumnSelectionRuleSet(dict_rule_set)
        else:
            input_dict = json.loads(json_query)
            self.rule_set = ColumnSelectionRuleSet(input_dict)

        if not self.rule_set.is_valid():
            raise ColumnSelectionInvalidRuleSetError()

    def select_without_schema(self, df: pd.DataFrame, clone=True):
        included_column_indexes = self.select_column_indexes(df)
        new_df = self.select_by_indexes(df, included_column_indexes, clone)
        return new_df

    def select(self, df: pd.DataFrame, schema, clone=True):
        if isinstance(schema, dict):
            schema = DataFrameSchema.from_dict(schema)
        included_column_indexes = self.select_column_indexes(df, schema)
        new_df = self.select_by_indexes(df, included_column_indexes, clone)
        new_schema = schema.select_columns(included_column_indexes).to_dict()
        return new_df, new_schema

    def select_dataframe_directory(self, directory: DataFrameDirectory):
        if not isinstance(directory, DataFrameDirectory):
            raise TypeError("Expected type: DataFrameDirectory.")
        if directory.schema_data is None:
            return DataFrameDirectory.create(self.select_without_schema(df=directory.data))
        else:
            df, schema = self.select(df=directory.data, schema=directory.schema_data)
            return DataFrameDirectory.create(data=df, schema=schema)

    @staticmethod
    def select_by_indexes(df: pd.DataFrame, indexes, clone=True):
        return df.iloc[:, indexes].copy(deep=clone)

    def select_column_indexes(self, df: pd.DataFrame, schema=None):
        if self.rule_set.is_filter:
            # If is_filter, the index list will be ascending order.
            selected_column_index_set = set()
            for rule in self.rule_set.rules:
                rule_columns = self._get_rule_columns(df, rule, schema)
                if rule.is_exclude:
                    selected_column_index_set = selected_column_index_set.difference(set(rule_columns))
                else:
                    selected_column_index_set = selected_column_index_set.union(set(rule_columns))
            included_column_indexes = list(selected_column_index_set)
            included_column_indexes.sort()
        else:
            # If not is_filter, the rule_set is only permitted to have one rule.
            # A rule returns a list with a specific order performed by the rule.
            # The list will be directly returned as the result.
            included_column_indexes = self._get_rule_columns(df, self.rule_set.rules[0], schema)

        return included_column_indexes

    def _get_rule_columns(self, df, rule, schema=None):
        if rule.rule_type == RuleType.COLUMN_NAMES:
            return self._handle_column_names_rule(df, rule)
        if rule.rule_type == RuleType.COLUMN_INDEXES:
            return self._handle_column_indexes_rule(df, rule)
        if rule.rule_type == RuleType.COLUMN_TYPES:
            return self._handle_column_types_rule(df, rule, schema)
        if rule.rule_type == RuleType.ALL_COLUMNS:
            return list(range(len(df.columns)))

    @staticmethod
    def _handle_column_names_rule(df: pd.DataFrame, rule):
        """
        Handles a ColumnNames rule
        :param df: The DataFrame the rule will be applied to.
        :param rule: The rule
        :return: The 0-based column indexes of the columns which match the rule criteria.
        """
        # Currently, changing it to set will make UTs in join_data fail.
        column_indexes = list()
        columns = df.columns
        for col_name in rule.columns:
            if col_name not in df:
                raise ColumnSelectionColumnNotFoundError(column_index=col_name)
            else:
                column_indexes.append(columns.get_loc(col_name))
        return column_indexes

    @staticmethod
    def _handle_column_indexes_rule(df, rule):
        """
        Handle a ColumnIndexes rule.
        :param df: The DataFrame the rule will be applied to.
        :param rule: The input rule contain column indexes to choose.
        :return: The 0-based column indexes of the columns specified by the rule.
        """
        index_pattern = re.compile(r'^\s*(?P<index>\d+)\s*$')
        index_range_pattern = re.compile(r'^\s*(?P<start>\d+)\s*\-\s*(?P<end>\d+)\s*$')
        selected_column_indexes = []
        selected_set = set()
        num_of_columns = len(df.columns)

        for column in rule.columns:
            match_index = index_pattern.match(column)
            match_range = index_range_pattern.match(column)
            if match_index:
                column_index = int(match_index.group('index')) - 1
                if 0 <= column_index < num_of_columns:
                    if column_index not in selected_set:
                        selected_set.add(column_index)
                        selected_column_indexes.append(column_index)
                else:
                    raise ColumnSelectionColumnNotFoundError(column_index)
            elif match_range:
                start_index = int(match_range.group('start')) - 1
                end_index = int(match_range.group('end')) - 1
                if end_index < start_index or start_index < 0 or end_index >= num_of_columns:
                    raise ColumnSelectionIndexRangeError(column_range=column)
                for i in range(start_index, end_index+1):
                    # Using a set instead of directly 'in selected_column_indexes' here,
                    # because `in` operator cost O(1) in set while it cost O(n) in list.
                    # Since n may be large due to the query like 1-1000000,
                    # directly 'in selected_column_indexes' may cause performance problems,
                    if i not in selected_set:
                        selected_set.add(i)
                        selected_column_indexes.append(i)
            else:
                raise ColumnSelectionIndexParsingError(column_index_or_range=column)
        return selected_column_indexes

    @staticmethod
    def _handle_column_types_rule(df, rule, schema):
        if schema is None:
            return ColumnSelection._handle_column_types_rule_without_schema(df, rule)
        return ColumnSelection._handle_column_types_rule_with_schema(rule, schema)

    @staticmethod
    def _handle_column_types_rule_without_schema(df, rule):
        if not {ColumnKind.ALL, ColumnKind.FEATURE}.intersection(rule.column_kinds):
            return []
        num_of_columns = len(df.columns)
        if ColumnType.ALL in rule.column_types:
            return list(range(num_of_columns))
        return [i for i, col in enumerate(df.columns) if ColumnSelection._in_column_types(df[col], rule.column_types)]

    @staticmethod
    def _in_column_types(column, column_types):
        for column_type in column_types:
            check_method = ColumnSelection._column_type_to_check_methods.get(column_type)
            if not check_method:
                raise ValueError(f"ColumnType {column_type} does not have a valid check method.")
            if check_method(column):
                return True
        return False

    @staticmethod
    def _handle_column_types_rule_with_schema(rule, schema):
        if isinstance(schema, dict):
            schema = DataFrameSchema.from_dict(schema)

        include_categorical = False
        include_all_types = False
        for col_type in rule.column_types:
            if col_type == ColumnType.ALL:
                include_all_types = True
            elif col_type == ColumnType.CATEGORICAL:
                include_categorical = True

        selected_column_indexes = set()
        number_of_columns = len(schema.column_attributes)
        for i in range(number_of_columns):
            element_type = schema.column_attributes[i].element_type
            column_attribute = schema.column_attributes[i]
            should_include = (include_all_types
                              or include_categorical and column_attribute.column_type is ColumnTypeName.CATEGORICAL
                              or ColumnSelection._element_type_in_column_types(element_type, rule.column_types))
            if should_include:
                for col_kind in rule.column_kinds:
                    if (col_kind == ColumnKind.FEATURE and column_attribute.is_feature) \
                            or (col_kind == ColumnKind.SCORE
                                and column_attribute.name in schema.score_column_names.values()) \
                            or (col_kind == ColumnKind.LABEL
                                and column_attribute.name == schema.label_column_name) \
                            or col_kind == ColumnKind.ALL:
                        selected_column_indexes.add(i)
        return sorted(list(selected_column_indexes))

    @staticmethod
    def _element_type_in_column_types(element_type, column_types):
        # Find the column type associated with the schema's element type
        mapping_column_type = ColumnSelection._element_type_to_column_type.get(element_type, None)
        if mapping_column_type in column_types:
            return True
        # Both ColumnType.INTEGER and ColumnType.DOUBLE belong to ColumnType.NUMERIC
        elif mapping_column_type in [ColumnType.INTEGER, ColumnType.DOUBLE] and ColumnType.NUMERIC in column_types:
            return True
        return False


class ColumnSelectionBuilder:
    _ALL_KIND = [ColumnKind.ALL]
    _ALL_TYPE = [ColumnType.ALL]

    def __init__(self):
        self._obj = {
            ColumnSelectionRuleSet.IS_FILTER: True,
            ColumnSelectionRuleSet.RULES: []
        }

    def include_all(self):
        self._append_rule(RuleType.ALL_COLUMNS, is_exclude=False)
        return self

    def include_col_indices(self, *col_indices):
        columns = [str(idx) if isinstance(idx, int) else idx for idx in col_indices]
        self._append_rule(RuleType.COLUMN_INDEXES, is_exclude=False, columns=columns)
        return self

    def exclude_col_indices(self, *col_indices):
        columns = [str(idx) if isinstance(idx, int) else idx for idx in col_indices]
        self._append_rule(RuleType.COLUMN_INDEXES, is_exclude=True, columns=columns)
        return self

    def include_col_names(self, *col_names):
        self._append_rule(RuleType.COLUMN_NAMES, is_exclude=False, columns=list(col_names))
        return self

    def exclude_col_names(self, *col_names):
        self._append_rule(RuleType.COLUMN_NAMES, is_exclude=True, columns=list(col_names))
        return self

    def include_col_types(self, *col_types):
        self._append_rule(RuleType.COLUMN_TYPES, is_exclude=False, column_types=list(col_types),
                          column_kinds=self._ALL_KIND)
        return self

    def exclude_col_types(self, *col_types):
        self._append_rule(RuleType.COLUMN_TYPES, is_exclude=True, column_types=list(col_types),
                          column_kinds=self._ALL_KIND)
        return self

    def include_col_kinds(self, *col_kinds):
        self._append_rule(RuleType.COLUMN_TYPES, is_exclude=False, column_types=self._ALL_TYPE,
                          column_kinds=list(col_kinds))
        return self

    def exclude_col_kinds(self, *col_kinds):
        self._append_rule(RuleType.COLUMN_TYPES, is_exclude=True, column_types=self._ALL_TYPE,
                          column_kinds=list(col_kinds))
        return self

    def keep_order_and_duplicates(self, value):
        self._set_is_filter(not value)
        return self

    def build(self):
        return ColumnSelection(dict_rule_set=self._obj)

    def _append_rule(self, rule_type, is_exclude, columns=None, column_types=None, column_kinds=None):
        rule = {
            ColumnSelectionRule.RULE_TYPE: rule_type,
            ColumnSelectionRule.IS_EXCLUDE: is_exclude
        }
        if columns is not None:
            rule[ColumnSelectionRule.COLUMNS] = columns
        if column_types is not None:
            rule[ColumnSelectionRule.COLUMN_TYPES] = column_types
        if column_kinds is not None:
            rule[ColumnSelectionRule.COLUMN_KINDS] = column_kinds
        self._obj[ColumnSelectionRuleSet.RULES].append(rule)

    def _set_is_filter(self, is_filter):
        self._obj[ColumnSelectionRuleSet.IS_FILTER] = is_filter
