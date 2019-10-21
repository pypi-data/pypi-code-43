import pandas as pd
import numpy as np
from typing import List, Dict
from .internal import *
from .globals import *
from .estmode import EstMode
from pandas.api.types import is_string_dtype, is_numeric_dtype
from sklearn.preprocessing import LabelEncoder
from scipy import stats
from scipy import special

def subtract(a, b):
        return list(set(a) - set(b))

def set_concat(a, b):
        return list(set(a) | set(b))

def most_related_columns(df: pd.DataFrame, target: str, number: int) -> List[str]:
    return list(df.corr()[target].abs().sort_values(ascending=False)[:number].index.values)

def all_cols_except(df: pd.DataFrame, targets: List[str]) -> List[str]:
    return subtract(df.columns.values, targets)

def dummify(df, cols: List[str]):
        onehot = pd.get_dummies(df[cols])
        confirm_all_dropped(onehot, cols)
        df.drop(cols, axis=1, inplace=True)
        for col in onehot:
                df[col] = onehot[col]

def confirm_all_dropped(df: pd.DataFrame, cols: List[str]):
        dropped = set(cols) - set(df.columns.values)
        if len(dropped) < len(cols):
            raise ValueError("the following columns were not one-hot encoded: ", *set(cols) - dropped)


# safe downcast
def sd(col, max_loss_limit=0.001, avg_loss_limit=0.001, na_loss_limit=0, n_uniq_loss_limit=0, fillna=0):
    """
    max_loss_limit - don't allow any float to lose precision more than this value. Any values are ok for GBT algorithms as long as you don't unique values.
                     See https://en.wikipedia.org/wiki/Half-precision_floating-point_format#Precision_limitations_on_decimal_values_in_[0,_1]
    avg_loss_limit - same but calculates avg throughout the series.
    na_loss_limit - not really useful.
    n_uniq_loss_limit - very important parameter. If you have a float field with very high cardinality you can set this value to something like n_records * 0.01 in order to allow some field relaxing.
    """
    is_float = str(col.dtypes)[:5] == 'float'
    na_count = col.isna().sum()
    n_uniq = col.nunique(dropna=False)
    try_types = ['float16', 'float32']

    if na_count <= na_loss_limit:
        try_types = ['int8', 'int16', 'float16', 'int32', 'float32']

    for type in try_types:
        col_tmp = col

        # float to int conversion => try to round to minimize casting error
        if is_float and (str(type)[:3] == 'int'):
            col_tmp = col_tmp.copy().fillna(fillna).round()

        col_tmp = col_tmp.astype(type)
        max_loss = (col_tmp - col).abs().max()
        avg_loss = (col_tmp - col).abs().mean()
        na_loss = np.abs(na_count - col_tmp.isna().sum())
        n_uniq_loss = np.abs(n_uniq - col_tmp.nunique(dropna=False))

        if max_loss <= max_loss_limit and avg_loss <= avg_loss_limit and na_loss <= na_loss_limit and n_uniq_loss <= n_uniq_loss_limit:
            return col_tmp

    # field can't be converted
    return col

def downsize(df, deep=True, verbose=False, obj_to_cat=False):
    numerics = ['int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64', 'float16', 'float32', 'float64']
    start_mem = df.memory_usage(deep=deep).sum() / 1024 ** 2
    for col in df.columns:
        col_type = df[col].dtypes

        # collect stats
        na_count = df[col].isna().sum()
        n_uniq = df[col].nunique(dropna=False)
        
        # numerics
        if col_type in numerics:
            df[col] = sd(df[col])

        # strings
        if (col_type == 'object') and obj_to_cat:
            df[col] = df[col].astype('category')
        
        if verbose:
            print(f'Column {col}: {col_type} -> {df[col].dtypes}, na_count={na_count}, n_uniq={n_uniq}')
        new_na_count = df[col].isna().sum()
        if (na_count != new_na_count):
            print(f'Warning: column {col}, {col_type} -> {df[col].dtypes} lost na values. Before: {na_count}, after: {new_na_count}')
        new_n_uniq = df[col].nunique(dropna=False)
        if (n_uniq != new_n_uniq):
            print(f'Warning: column {col}, {col_type} -> {df[col].dtypes} lost unique values. Before: {n_uniq}, after: {new_n_uniq}')

    end_mem = df.memory_usage(deep=deep).sum() / 1024 ** 2
    percent = 100 * (start_mem - end_mem) / start_mem
    
    print('Mem. usage decreased from {:5.2f} Mb to {:5.2f} Mb ({:.1f}% reduction)'.format(start_mem, end_mem, percent))
    return df

# set_true_na replaces all the na values in the given columns with 
# an anomolous integer value if the column is ordinal, or "unknown" 
# if the column is an object.
# The idea is that NA values for these values means that any value
# would be nonsensical. Passing in the names of categorical columns
# will cause errors to be thrown.
def set_true_na(df: pd.DataFrame, cols: List[str]):
        for col in cols:
                assert df[col].dtype.name != "category", f"column {col} was categorical, cannot set true NA values on it"
                if is_string_dtype(df[col]):
                        assert UNKNOWN_STR_VAL not in df[col].unique(), f"column {col} already contains value {UNKNOWN_STR_VAL}."
                        df[col].fillna(UNKNOWN_STR_VAL, inplace=True)
                else:
                        df[col].fillna(UNKNOWN_NUM_VAL, inplace=True)

def convert_to_cat_codes(df: pd.DataFrame, cols: List[str]):
        for col in cols:
                df[col] = df[col].astype('category').cat.codes

def fill_ordinal_na(df: pd.DataFrame, cols: List[str]):
        for col in cols:
                assert ORDINAL_BAD_VALUE not in df[col].unique(), f"column {col} already contains {ORDINAL_BAD_VALUE}" 
                df[col].fillna(ORDINAL_BAD_VALUE, inplace=True)

def encode_to_int(df: pd.DataFrame, encoding: Dict[str, Dict[str, int]]):
        df.replace(encoding, inplace=True)
        for col in encoding.keys():
                df[col].fillna(-1, inplace=True)
                df[col] = df[col].astype("int8")

def cls_impute(est, df: pd.DataFrame, cols: List[str], ignore: List[str]=[]):
        est_impute(est, df, cols, EstMode.classify, ignore=ignore)

def reg_impute(est, df: pd.DataFrame, cols: List[str], ignore: List[str]=[]):
        est_impute(est, df, cols, EstMode.regress, ignore=ignore)



# est_impute replaces all bad values with the given 
# classifier's predictions. It is assmed that the bad values
# have already been replaced with certain integers.
def est_impute(est, df: pd.DataFrame, cols: List[str], mode: EstMode, ignore: List[str]=[]):
        if mode == EstMode.classify:
                bad_val = CATEGORICAL_BAD_VALUE
        else:
                bad_val = ORDINAL_BAD_VALUE

        for col in cols:
                features = all_cols_except(df, [col] + ignore)

                # when training the model we remove rows where the
                # target column has a bad value (since these are 
                # the row's we're trying to predict for). 
                clean_frame =  df.loc[df[col] != bad_val, :]
                est.fit(
                        clean_frame[features], 
                        clean_frame[col]
                )
                preds = est.predict(df[features])
                df.loc[df[col] == bad_val, col] = np.extract((df[col] == bad_val).values, preds)

def str_cols(df: pd.DataFrame) -> List[str]:
        return df.select_dtypes(["category", "object"]).columns.values

def int_cols(df: pd.DataFrame) -> List[str]:
        return all_cols_except(df, str_cols(df))

# used for viewing the results of a Sklearn CV searcher
# more easily.
def best_n_params(results, number):
    params = []
    scores = []
    all_ranks = list(results["rank_test_score"])
    all_params = results["params"]
    all_scores = results["mean_test_score"]
    
    for i in range(number):
        if i+1 in all_ranks:
                indices = [index for index, rank in enumerate(all_ranks) if rank == i+1]
                for index in indices:
                        params.append(all_params[index])
                        scores.append(all_scores[index])
    return (params, scores)

def skew(df: pd.DataFrame, cols: List[str]):
        for col in cols:
                if np.abs(stats.skew(df[col])) > 0.75:
                        df[col] = special.boxcox1p(
                                df[col], 
                                stats.boxcox_normmax(df[col] + 1)
                        )

def split_at_proportion(df: pd.DataFrame, prop: float):
    a = int(len(df) * prop)
    
    return df.head(a), df.tail(len(df) - a)


# returns the given series as cat-codes where the codes
# are numerically ordered according to mean target encoding
# value.
def ordered_cat_codes(df, target_df, col, target):
    le = LabelEncoder()
    le.classes_ = sort_by_target(target_df, col, target)
    return le.transform(df[col])

def sort_by_target(df, col, target):
    return list(df.groupby(col).mean().sort_values(target).index)

# returns the series but with certain levels merged.
def reclassified(df, col, mp):
    allvals = list(df[col].value_counts().index)
    mapping = mapping_from(allvals, mp)
    return df[col].map(mapping)

# creates mappings from certain categorical values to
# broader value groups based on whether the values 
# contain certain substrings.
def mapping_from(allVals, mp):
    res = {}
    for val in allVals:
        classified = False
        for key in mp.keys():
            if key in val:
                classified = True
                res[val] = mp[key]
                break
        if not classified:
            res[val] = "unclassified"
    
    return res

def multi_concat_feat(df, cols):
        assert len(cols) > 1
        
        new_df = pd.DataFrame().reindex_like(df)
        new_df["placeholder"] = df[cols[0]].astype(str)
        for col in cols[1:]:
            new_df["placeholder"] = new_df["placeholder"] + "|" + df[col].astype(str)
        return new_df["placeholder"]

def cat_concat_feat(df, a, b):
        return concat_feat(df, a, b).astype("category").cat.codes

def add_concat_feat(df, a, b):
        df[f"{a}--{b}"] = concat_feat(df, a, b).astype("category").cat.codes

def count_of(df, col):
      return df[col].map(df[col].value_counts(dropna=False))

def merge_big_categories(df, cols, upper_bound, value=""):
    for col in cols:
        cnt = df[col].value_counts()
        cnt_series = df[col].map(cnt.to_dict())
        max_value = cnt_series.max()
        max_level = cnt.idxmax()
        
        replacement = value
        
        if not replacement:
                replacement = max_level
        
        if max_value > upper_bound:
                df.at[cnt_series > upper_bound, col] = replacement
                
def merge_small_categories(df, cols, lower_bound, value=""):
        # 0.001 is a good lower bound
        for col in cols:
                cnt = df[col].value_counts()
                cnt_series = df[col].map(cnt.to_dict())
                min_value = cnt_series.min()
                min_level = cnt.idxmin()

                replacement = value

                if not replacement:
                        replacement = min_level

                if min_value < lower_bound:
                        df.at[cnt_series < lower_bound, col] = replacement

def map_from(df: pd.DataFrame,  a: str, b: str):
        vals1 = list(df[a].values)
        vals2 = list(df[b].values)
        mapping = {}

        for index in range(len(vals1)):
                mapping[vals1[index]] = vals2[index]
        
        return mapping

def add_grouped_feats(
        df: pd.DataFrame, 
        group_cols: List[str],
        target: str, 
        aggs: List[str] = ["mean"],
) -> List[str]:
        return add_grouped_feats_from(
                df, 
                df, 
                group_cols,
                target,
                aggs,
        )

def add_grouped_feats_from(
        df: pd.DataFrame,
        stat_df: pd.DataFrame, 
        group_cols: List[str],
        target: str, 
        aggs: List[str],
) -> List[str]:
        grouped = pd.merge(
                df, 
                stat_df.groupby(group_cols).agg({target: aggs}),
                on=group_cols,
                how="left"
        )

        group_name = "".join(group_cols)

        all_names = []

        for agg in aggs:
                agg_name = f"{group_name}-{target}{agg}"
                assert not contains(df, agg_name), f"duplicate column: {agg_name}" 
                df[agg_name] = grouped[(target, agg)]
                all_names.append(agg_name)
        
        return all_names


def add_multi_groups_from(
        df: pd.DataFrame,
        stat_df: pd.DataFrame, 
        group_cols: List[str],
        targets: Dict[str, List[str]], 
) -> List[str]:
        grouped = pd.merge(
                df, 
                stat_df.groupby(group_cols).agg(targets),
                on=group_cols,
                how="left"
        )

        group_name = "".join(group_cols)

        all_names = []

        for key, aggs in targets.items():
                for agg in aggs:
                        agg_name = f"{group_name}-{key}{agg}"
                        assert not contains(df, agg_name), f"duplicate column: {agg_name}" 
                        df[agg_name] = grouped[(key, agg)]
                        all_names.append(agg_name)
                
        return all_names

def add_multi_groups(
        df: pd.DataFrame,
        group_cols: List[str],
        targets: Dict[str, List[str]], 
) -> List[str]:
        return add_multi_groups_from(df, df, group_cols, targets)