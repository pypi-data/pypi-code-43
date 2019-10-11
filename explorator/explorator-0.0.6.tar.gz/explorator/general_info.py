from pyspark.sql import DataFrame as pysparkDataFrame
import pyspark.sql.functions as f
import pandas as pd
import numpy as np
import datetime


################################################################################################
# --------------------------------------PANDAS FUNCTIONS-------------------------------------- #
################################################################################################


def get_df_general_info(dfc):
    df_info = pd.DataFrame()

    # total_rows
    dfc_count = dfc.reset_index().count()['index']

    # general info
    df_info['type'] = dfc.dtypes
    df_info['count'] = dfc.count()
    df_info['null_count'] = dfc_count - df_info['count']
    df_info['pc_count'] = df_info['count'] / dfc_count
    df_info['uniq'] = dfc.nunique()
    df_info['pc_uniq'] = df_info['uniq'] / dfc_count
    df_info = pd.concat([df_info], axis=1, keys=['general info'])
    return df_info


def get_df_examples(dfc):
    # examples
    df_examples = dfc.head(5).transpose()
    if df_examples.shape[1] < 5:
        for i in range(5 - df_examples.shape[1] - 1, 5):
            df_examples[i] = np.NaN

    df_examples = pd.concat([df_examples], axis=1, keys=['examples'])
    return df_examples


def get_df_top_column_values(dfc):
    outside = 5 * ['value'] + 5 * ['count']
    inside = list(range(5)) + list(range(5))
    hier_index = list(zip(outside, inside))
    hier_index = pd.MultiIndex.from_tuples(hier_index)

    top_values = pd.DataFrame(index=hier_index).transpose()

    for col in dfc.columns:
        dfc_top = dfc[col].value_counts().head(5).reset_index()
        dfc_top.columns = ['value', 'count']
        if dfc_top.shape[0] == 0:
            dfc_top = dfc_top.append([np.nan, np.nan])
        top_values = pd.concat([top_values, dfc_top[['value', 'count']].unstack(1).to_frame().transpose()])
    top_values.set_index(dfc.columns, inplace=True)
    return top_values[['value', 'count']]


def get_df_description(dfc):
    arr = []
    for col in dfc.columns:
        series = pd.Series(name=col, dtype=np.number)
        if np.issubdtype(dfc[col].dtype, np.number):
            print('{} std: {}'.format(col, dfc[col].std()))
            series['avg'] = dfc[col].mean()
            series['std'] = dfc[col].std()
            series['25%'] = dfc[col].quantile(.25)
            series['50%'] = dfc[col].quantile(.50)
            series['75%'] = dfc[col].quantile(.75)
            series['min'] = dfc[col].dropna().min()
            series['max'] = dfc[col].dropna().max()
        else:
            series['avg'] = np.nan
            series['std'] = np.nan
            series['25%'] = np.nan
            series['50%'] = np.nan
            series['75%'] = np.nan

            if dfc[col].dtype == np.dtype('<M8[ns]'):
                series['min'] = dfc[col].dropna().min().strftime('%Y-%m-%d')
                series['max'] = dfc[col].dropna().max().strftime('%Y-%m-%d')
            else:
                str_dfc_col = dfc[col].dropna().apply(lambda x: str(x))
                series['min'] = str_dfc_col.min()
                series['max'] = str_dfc_col.max()

        arr.append(series)

    descr = pd.concat(arr, axis=1, sort=False).T
    descr = descr[['min', 'max', 'avg', 'std', '25%', '50%', '75%']]
    descr = pd.concat([descr], axis=1, keys=['describe'])
    return descr


###############################################################################################
# --------------------------------------SPARK FUNCTIONS-------------------------------------- #
###############################################################################################

def get_spark_df_general_info(df, spark):
    df_types = df.dtypes
    df_res = spark.createDataFrame(df_types, schema=['field_id', 'type'])
    rows_qty = df.count()
    df_res = df_res.withColumn('qty', f.lit(rows_qty))

    pd_df_res = df_res.toPandas().set_index('field_id')
    pd_df_cols = pd.DataFrame()

    # cycle
    for col_dt in df_types:
        col_type = col_dt[1]
        col_name = col_dt[0]
        # main info
        pd_df_col = df.groupby().agg(f.lit(col_name).alias('field_id'),
                                     f.count(col_name).alias('count'), f.countDistinct(col_name).alias('uniq')
                                     ).toPandas()

        pd_df_cols = pd.concat([pd_df_cols, pd_df_col])

    pd_df_res = pd.concat([pd_df_res, pd_df_cols.set_index('field_id')], axis=1)

    pd_df_res['null_count'] = pd_df_res['qty'] - pd_df_res['count']
    pd_df_res['pc_count'] = pd_df_res['count'] / pd_df_res['qty']
    pd_df_res['pc_uniq'] = pd_df_res['uniq'] / pd_df_res['qty']

    # pd_df_res = pd_df_res[['type','qty','count', 'null_count', 'pc_count', 'uniq', 'pc_uniq']]
    pd_df_res = pd_df_res[['type', 'count', 'null_count', 'pc_count', 'uniq', 'pc_uniq']]
    pd_df_res = pd.concat([pd_df_res], axis=1, keys=['general info'])

    return pd_df_res


def get_spark_df_examples(df):
    pd_df_examples = df.limit(5).toPandas().T
    pd_df_examples = pd.concat([pd_df_examples], axis=1, keys=['examples'])
    return pd_df_examples


def get_spark_df_top_column_values(df, spark):
    df = df.drop('origin_file_name', 'partition_date')
    df_types = df.dtypes
    df_res = spark.createDataFrame(df_types, schema=['field_id', 'type'])

    # for most freq
    outside = 5 * ['value'] + 5 * ['count']
    inside = list(range(5)) + list(range(5))
    hier_index = list(zip(outside, inside))
    hier_index = pd.MultiIndex.from_tuples(hier_index)
    pd.MultiIndex.from_tuples(hier_index)

    top_values = pd.DataFrame(index=hier_index).transpose()

    # most frequent values
    # cycle
    for col_dt in df_types:
        col_type = col_dt[1]
        col_name = col_dt[0]

        pd_df_freq = df.groupby(col_name).count().orderBy(f.desc('count')).limit(5).toPandas()
        pd_df_freq.columns = ['value', 'count']
        top_values = pd.concat([top_values, pd_df_freq[['value', 'count']].unstack(1).to_frame().transpose()])

    # most frequent
    top_values.set_index(df_res.toPandas().set_index('field_id').index, inplace=True)

    return top_values[['value', 'count']]


def get_spark_df_description(df, spark):
    df = df.drop('origin_file_name', 'partition_date')
    df_types = df.dtypes
    df_res = spark.createDataFrame(df_types, schema=['field_id', 'type'])
    rows_qty = df.count()
    df_res = df_res.withColumn('qty', f.lit(rows_qty))

    pd_df_res = df_res.toPandas().set_index('field_id')
    pd_df_cols = pd.DataFrame()
    pd_df_cols_min_max = pd.DataFrame()

    arr = []
    # cycle
    for col_dt in df_types:
        col_type = col_dt[1]
        col_name = col_dt[0]
        # main info and statistics
        pd_df_col_min_max = df.groupby().agg(f.min(col_name).alias('min'), f.max(col_name).alias('max')).toPandas()

        if col_type in ('timestamp', 'date'):
            arr_ts_unix = df.withColumn(col_name, f.unix_timestamp(col_name, '')). \
                approxQuantile(col_name, [0.25, 0.5, 0.75], 0.01)
            arr.append([datetime.datetime.utcfromtimestamp(i).strftime('%Y-%m-%d %H:%M:%S') for i in arr_ts_unix])

            pd_df_col = df.withColumn(col_name, f.unix_timestamp(col_name, '')). \
                groupby().agg(f.avg(col_name).alias('avg'), f.stddev(col_name).alias('std')).toPandas()
            pd_df_col = pd.DataFrame(pd.to_datetime(pd_df_col.T[0], unit='s')).T
        elif col_type == 'string':
            arr.append([np.NaN, np.NaN, np.NaN])
            pd_df_col = df.groupby().agg(f.lit('').alias('avg'), f.lit('').alias('std')).toPandas()
        else:
            arr.append(df.approxQuantile(col_name, [0.25, 0.5, 0.75], 0.01))
            pd_df_col = df.groupby().agg(f.avg(col_name).alias('avg'), f.stddev(col_name).alias('std')).toPandas()

        pd_df_cols = pd.concat([pd_df_cols, pd_df_col])
        pd_df_cols_min_max = pd.concat([pd_df_cols_min_max, pd_df_col_min_max])

    pd_df_res = pd.concat([pd_df_cols_min_max.set_index(pd_df_res.index), pd_df_cols.set_index(pd_df_res.index),
                           pd.DataFrame(arr, columns=['q25', 'q50', 'q75']).set_index(pd_df_res.index)], axis=1)

    pd_df_res = pd.concat([pd_df_res], axis=1, keys=['describe'])

    return pd_df_res


#############################################################################################
# --------------------------------------MAIN FUNCTION-------------------------------------- #
#############################################################################################


def get_total(df, info=['general', 'value', 'counts', 'examples', 'description'], spark=None):
    """
    Функция, которая создает обзорный отчет по данному датафрейму
    params:
        - dfc (pd.DataFrame or pyspark.sql.DataFrame) : DataFrame to analyze
        - info (list) : paragraphs of analysis report
    returns:
        - df_total_info (pd.DataFrame) : DataFrame with analysis
    """

    tools_pandas = {'general': get_df_general_info,
                    'values': get_df_top_column_values,
                    'examples': get_df_examples,
                    'description': get_df_description}
    tools_spark = {'general': lambda x: get_spark_df_general_info(x, spark),
                   'values': lambda x: get_spark_df_top_column_values(x, spark),
                   'examples': get_spark_df_examples,
                   'description': lambda x: get_spark_df_description(x, spark)}

    if isinstance(df, pd.DataFrame):
        tools = tools_pandas
    elif isinstance(df, pysparkDataFrame):
        tools = tools_spark
        if spark is None:
            tools = dict()
            raise Exception('Spark session needs to be passed as an argument, when the input of function \
                            is Spark DataFrame')
    else:
        tools = dict()
    df_total_info = tools[info[0]](df)
    for page in info[1:]:
        df_total_info = df_total_info.join(tools[page](df))

    return df_total_info
