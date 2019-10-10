def get_sequence(df, target_col, seq_len, dropna=True):
    """
    Create a shifted sequence for time series data
    The input dataframe should have date / sequence id as index and the time series as column

    == Arguments ==
    df: pd.DataFrame
        time series in dataframe format

    target_col: string
        column name of the time series

    seq_len: int
        how many shifted sequence to generate

    dropna: bool
        remove missing value using df.dropna()
    """
    df_new = df.copy()
    if dropna:
        df_new.dropna(inplace=True)
    cols = df_new.columns

    for i in range(seq_len - 1, 0, -1):
        for col in cols:
            df_new[f"{col}_t-{i}"] = df_new[col].shift(i)

    for col in cols:
        df_new[f"{col}_t+0"] = df_new[col]

    df_new["target"] = df_new[target_col].shift(-1)

    df_new.drop(columns=cols, inplace=True)
    df_new.dropna(inplace=True)
    return df_new
