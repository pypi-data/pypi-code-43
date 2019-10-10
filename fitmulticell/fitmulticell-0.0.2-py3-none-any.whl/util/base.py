import os
import pandas as pd


def tsv_to_df(loc: str, file_: str = "logger.csv"):
    """
    Read in the morpheus logging file `file_`, which should be in
    tab-separated tsv format and defaults to "logger.csv", inside
    directory `loc`.
    
    Parameters
    ----------
    
    loc: str
        The simulations results folder.
    file_: str, optional (default="logger.csv")
        The logger file containing the results in tsv format.
    
    Returns
    -------
    
    data_frame: pandas.DataFrame
        A dataframe of the file contents.
    """
    data_file = os.path.join(loc, file_)
    data_frame = pd.read_csv(data_file, sep="\t")
    return data_frame
