import mysql.connector
from mysql.connector import Error
import os
import pandas as pd
import re
import numpy as np
import warnings
from typing import List, Tuple
from google.cloud import storage

months_dict = {
    "JANEIRO": "01",
    "FEVEREIRO": "02",
    "MARÇO": "03",
    "ABRIL": "04",
    "MAIO": "05",
    "JUNHO": "06",
    "JULHO": "07",
    "AGOSTO": "08",
    "SETEMBRO": "09",
    "OUTUBRO": "10",
    "NOVEMBRO": "11",
    "DEZEMBRO": "12",
}

def get_file_from_path(path):
    return re.findall(r'/([a-zA-Z0-9_-]*?\.[a-z0-9]*)', path)[0]

def connect_and_query(query: str) -> pd.DataFrame:
    """
    Opens a connection to a SQL database and returns the output the Query as a pandas DataFrame
    It is important to note that the environment variables need to be set prior to execution. 

    Args:
        query (str): The query to be fetched at the database.

    Returns:
        (:class:`pandas.Dataframe`): The output of the query in DataFrame format.
    """
    mySQLconnection = None
    # for the next part, it is important to set the environment variables
    try:
        print("Opening MySQL Connection")
        mySQLconnection = mysql.connector.connect(
            host=os.environ.get("HOST_PLM_DATABASE"),
            database=os.environ.get("PLM_DATABASE"),
            user=os.environ.get("USER_PLM_DATABASE"),
            password=os.environ.get("PASSWORD_PLM_DATABASE"),
        )
        print("Connection Opened, starting Fetch")

        output = pd.read_sql(query, con=mySQLconnection)

    except Error as e:
        print("Error while connecting to MySQL", e)
        return e

    finally:
        # closing database connection.
        if mySQLconnection:
            if mySQLconnection.is_connected():
                mySQLconnection.close()
                print("MySQL connection is closed")
                return output


def format_produto_animale(produto: str) -> str:
    """
    Formats the 'produto' column to follow a xx.xx.x+ standard, thus removing forbidden characters (letters, specials, etc).

    Args:
        produto (str): A single entry from the produto column.

    Returns:
        (str): The formatted string if it fits the pattern. If no match is found returns nothing (empty string)

    """
    m = re.match("(^[0-9]{2}\.[0-9]{2}\.[0-9]+)", produto)
    if m:
        return m.groups()[0]
    else:
        return produto


def calculate_giro(
    df: pd.DataFrame, columns: list = ["value", "grade_total", "preco", "qtty"]
) -> pd.DataFrame:
    """
    Calculates giro and disc from a dataframe

    Args:
        df (:class:`pandas.Dataframe`):: A correctly structured DataFrame
        columns (list(str)): The column names that represent:
            - value
            - grade_total
            - preco
            - qtty
    
    Returns:
        (:class:`pandas.Dataframe`):: The original DataFrame with two additional columns,
        giro and discount.
    
    Todo:
        Complete the Args documentation.
    """
    # columns[0] = value, columns[1] = grade_total, columns[2] = preco_varejo_original, columns[3] = qtty
    nan_indexes = []

    # checking if any important row has a zero (dividend row)
    for c in columns:
        if c == columns[0]:
            pass
        else:
            if df[c].eq(0).any().sum() > 0:
                column_indexes = np.where(df[columns[1]].eq(0).tolist())[0].tolist()
                nan_indexes = nan_indexes + column_indexes
                warnings.warn(
                    "{} column has at least one 0, resulting in NaN.".format(c)
                )

    warnings.warn("The NaN indexes are: {}".format(np.unique(nan_indexes)))

    # calculating giro
    df["giro"] = df[columns[0]] / (df[columns[1]] * df[columns[2]])
    # calculating discount
    df["disc"] = 1 - df[columns[0]] / (df[columns[3]] * df[columns[2]])

    return df


def clean_animale_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
        Cleans the animale sales dataset.

        It excludes infinite, zero quantities and NaN entries from the DataFrame.

        Args:
            df (:class:`pandas.Dataframe`): The animale sales dataset.

        Returns:
           :class:`pandas.Dataframe`: The cleaned dataset.
    """
    df.drop_duplicates(subset="id_produto_cor", keep=False, inplace=True)
    df["grade_total"].replace(0, np.nan, inplace=True)
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def load_provao_dataset(
    path_animale: str, path_provao: str
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
        Loads the animale sales dataset (with sales indicators) and the votes dataset.

        Args:
            path_animale (str): Path to the animale dataset in Pickle format.
            path_provao (str): Path to the provao dataset in CSV format.
        
        Returns:
            (tuple): Tuple contaning:
                - df_merged (:class:`pandas.Dataframe`): A merged dataset from animale and provao.
                - df_animale (:class:`pandas.Dataframe`): Animale sales dataset.
                - df_provao (:class:`pandas.Dataframe`): Provao dataset      
    """

    df_animale = pd.read_pickle(path_animale)
    df_provao = pd.read_csv(path_provao)

    df_provao = df_provao.rename(columns={"preco": "nota_preco"})
    df_provao.drop(columns=["id_colecao", "id_produto_estilo", "produto"], inplace=True)

    df_animale = clean_animale_dataset(df_animale)
    df_animale.rename(columns={"preco_varejo_original": "preco"}, inplace=True)

    df_merged = df_animale.merge(df_provao, on="id_produto_cor")
    return df_merged, df_animale, df_provao


def reorganize_tags(tags: pd.DataFrame) -> pd.DataFrame:
    """
        Fixes the unorganized tags from the database, separating by 
        category.
    
        The value from the category is determined by the first uppercase
        letter.

        Args:
            tags (:class:`pandas.Dataframe`): 
        Returns:
            :class:`pandas.Dataframe`: The tags organized by category.

    """
    output = tags.copy
    output = tags.loc[:, []]
    for col in tags:
        for cat in tags[col].unique():
            if cat:
                aux = tags[tags[col] == cat][col]
                new_col = re.findall("([a-z]*)(.*)", cat)
                # Category value starts at the first uppercase letter.
                if new_col:
                    category_value = new_col[0][1]
                    new_col = new_col[0][0]
                    if new_col not in output.columns:
                        output[new_col] = None
                    output.loc[aux.index, new_col] = category_value
    return output


def label_encode_col(col):
    """
        Encodes a :class:`pandas.Series` with a label encoder that 
        accepts missing values (codified as a "None" string)

        Args:
            col (:class:`pandas.Series`): A column from a dataframe that 
            can include a missing entry codified as "None".
        Returns:
            :class:`pandas.Series`: The label-encoded column, with "None" 
            codified with label 0.
    """

    unique_values = col.unique()
    if "None" not in unique_values:
        unique_values = np.insert(unique_values, 0, "None")
    mapping_dict = {key: value for (value, key) in enumerate(unique_values)}
    reverse_dict = {key: value for (key, value) in enumerate(unique_values)}

    if "None" in mapping_dict:
        none_class = mapping_dict["None"]
        zero_key = reverse_dict[0]
        mapping_dict[zero_key], mapping_dict["None"] = (none_class, 0)

    # print(mapping_dict)
    return col.apply(lambda x: mapping_dict[x])


def insertData(table, data, try_num=0, update_set={}):
    """
    Opens a connection to a SQL database and inserts the received Dataframe or Series into the received Table
    It is important to note that the environment variables need to be set prior to execution. 

    Args:
        table (str): Table where data will be inserted.
        data (:class:`pandas.Dataframe` or :class:`pandas.Series`): Data to be inserted. Column names must match table columns.
        update_set (set): Set with columns to update with ON DUPLICATE KEY clause.
        
    Returns:
        (list): List of inaerted ids.
    """
    try:
        print("Opening MySQL Connection")
        mySQLconnection = mysql.connector.connect(
            host=os.environ.get("HOST_PLM_DATABASE"),
            database=os.environ.get("PLM_DATABASE"),
            user=os.environ.get("USER_PLM_DATABASE"),
            password=os.environ.get("PASSWORD_PLM_DATABASE"),
        )
        print("Connection Opened, starting Insert")

    except Error as e:
        print("Error while connecting to MySQL", e)
        return e

    cursor = mySQLconnection.cursor()
    if type(data) == pd.core.series.Series:
        data = data.sort_index()
        myDict = data.to_dict()
        tuples = [tuple([val for idx, val in data.iteritems()])]
    else:
        data = data.reindex(sorted(data.columns), axis=1)
        myDict = data.to_dict(orient="records")[0]
        tuples = [tuple(x) for x in data.values]

    sql = (
        "INSERT INTO "
        + table
        + " ("
        + ", ".join(sorted(myDict.keys()))
        + ") VALUES ("
        + ", ".join(["%s"] * len(myDict))
        + ")"
    )
    if len(update_set) > 0:
        upd_str = ""
        for value in update_set:
            upd_str = upd_str + value + " = VALUES(" + value + "), "
        upd_str = upd_str[:-2] + ";"
        sql = sql + " ON DUPLICATE KEY UPDATE " + upd_str
    print(sql)

    try:
        cursor.executemany(sql, tuples)
        mySQLconnection.commit()
        print(cursor.lastrowid)
        ids = [cursor.lastrowid + i for i in range(cursor.rowcount)]
        cursor.close()
        mySQLconnection.close()

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        mySQLconnection.rollback()
        if try_num > 10:
            cursor.close()
            mySQLconnection.close()
            return False
        else:
            print("Error, trying for the " + str(try_num + 1) + " time.")
            cursor.close()
            mySQLconnection.close()
            return insertData(table, data, try_num + 1)

    return ids


def get_col_dates(col_query_path: str) -> pd.DataFrame:
    """
        A function that queries the collection's debut and end dates.

        Args:
            col_query_path (str): A path to the .sql file containing
            the necessary query
        Returns:
            :class:`pandas.DataFrame`: A DataFrame with the colllections
            debut and end dates.
    """

    with open(col_query_path, "r") as f:
        query = f.read()

    return connect_and_query(query).replace(" ", "", regex=True)


def get_pcp_dates(pcp_query_path: str) -> pd.DataFrame:
    """
        Generates a DataFrame with the pcp dates.

        Args:
            pcp_query_path (str):
        Returns:
            :class:`pandas.Dataframe`: A DataFrame with each product id and its projected
            date to be at the store.
    """
    with open(pcp_query_path, "r") as f:
        query = f.read()

    return connect_and_query(query)


def fix_pcp(pcp: pd.DataFrame) -> pd.DataFrame:
    """
        Converts the pcp-DataFrame's date string to :class:`numpy.datetime64`.

        Args:
            pcp (:class:`pandas.DataFrame`): A DataFrame with the product's 
            planned day to be placed at the stores.
        Returns:
            :class:`pandas.Dataframe`: The DataFrame with :class:`numpy.datetime64` dates instead of string.
    """

    pcp.periodo_pcp.replace(months_dict, regex=True, inplace=True)
    pcp.periodo_pcp = pcp.periodo_pcp.apply(find_pcp_day)

    return pcp


def find_pcp_day(periodo_pcp: str) -> np.datetime64:
    """
        Converts a periodo_pcp date string to :class:`numpy.datetime64`.
        This string can have 2 forms: 
        - MM YYYY - 1/2
        - MM YYYY
        The '1' or '2' following the month and year represent the amount of
        fortnights (period of 14~15 days).

        Args:
            periodo_pcp (str): A date string with aforementioned format.
        Returns:
            :class:`numpy.datetime64`: The date in :class:`numpy.datetime64` format.
    """

    expression = "([0-9]{2})\s([0-9]{4})[\s-]*([0-9]*)"
    matches = re.findall(expression, periodo_pcp)[0]

    m = matches[0]
    y = matches[1]

    if matches[2]:
        q = int(matches[2])
    else:
        q = 1

    d = 15 * q - 7

    day_str = "{}-{}-{:02}".format(y, m, d)

    return np.datetime64(day_str)


def delay_colecao(df, delta_colecao, features):
    """
        #TODO Complete documentation.
    """
    if delta_colecao >= 1:
        col_list = df.sort_values("lancamento").colecao.unique()
        replace_dict = {}
        reverse_dict = {}
        for i, col in enumerate(col_list):
            if i + delta_colecao < len(col_list):
                replace_dict[col] = col_list[i + delta_colecao]
                reverse_dict[col_list[i + delta_colecao]] = col
            else:
                replace_dict[col] = None

        replaced_df = df.copy()
        replaced_df.colecao = df.colecao.replace(replace_dict)

        replaced_df = replaced_df[["colecao", "linha", "grupo"] + features]

        replaced_df["col_linha_grupo"] = (
            replaced_df["colecao"] + replaced_df["linha"] + replaced_df["grupo"]
        )
        replaced_df["col_linha"] = replaced_df["colecao"] + replaced_df["linha"]

        replaced_df.drop(columns=["colecao", "linha", "grupo"], inplace=True)

        df["col_linha_grupo"] = df["colecao"] + df["linha"] + df["grupo"]
        df["col_linha"] = df["colecao"] + df["linha"]

        replaced_df.drop_duplicates(inplace=True)

        df = df.merge(
            replaced_df.drop(columns="col_linha"),
            how="left",
            on=["col_linha_grupo"],
            suffixes=("", "_lg"),
        )

        replaced_df = replaced_df.groupby("col_linha").apply(np.mean)

        df = df.merge(replaced_df, how="inner", on=["col_linha"], suffixes=("", "_l"))

        lg_cols = [p + "_lg" for p in features]
        l_cols = [p + "_l" for p in features]
        nan_mask_lg = df[lg_cols[0]].isna()
        df[nan_mask_lg][lg_cols] = df[nan_mask_lg][l_cols]

        df[features] = df[lg_cols]

        df.drop(
            columns=l_cols + lg_cols + ["col_linha", "col_linha_grupo"], inplace=True
        )
    return df


def upload_to_bucket(bucket, local, remote):
    """
        Uploads file to a Google Cloud bucket

        Args:
            Filename (str): File to be uploaded.
            bucket (str): bucket name
    """

    storage_client = storage.Client.from_service_account_json(
        os.environ.get("CRED_JSON"), project=os.environ.get("PROJECT_NAME")
    )

    bucket = storage_client.get_bucket(bucket)
    blob = bucket.blob(remote)
    blob.upload_from_filename(local)


def download_from_bucket(bucket, local, remote):
    """
        Uploads file to a Google Cloud bucket

        Args:
            Filename (str): File to be downloaded. 
            bucket (str): bucket name
    """
    storage_client = storage.Client.from_service_account_json(
        os.environ.get("CRED_JSON"), project=os.environ.get("PROJECT_NAME")
    )

    bucket = storage_client.get_bucket(bucket)
    blob = bucket.blob(remote)
    blob.download_to_filename(local)
