import subprocess
import os
from typing import List
import pandas as pd
from io import StringIO
import numpy as np


def bwtool(*args: List) -> pd.DataFrame:
    """Return DataFRame from bwtool with the given args."""
    return pd.read_csv(StringIO(subprocess.run([
        "bwtool", *[str(arg) for arg in args], "/dev/stdout"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8")), header=None, sep="\t")


def _extract(bed_path: str, bigwig_path: str) -> pd.DataFrame:
    """Return DataFrame with extracted data from given big wig files for regions specified in given.

    Parameters
    ----------------------------------------
    bed_path: str, the bed file from which to extract the regions.
    bigwig_path: str, the bigwig file from which to extract the data for the regions

    Raises
    -----------------------------------------
    ValueError:
        When one of the given file path does not exist.

    Returns
    ------------------------------------------
    Dataframe with extracted data.
    """

    for file_path in (bed_path, bigwig_path):
        if not os.path.exists(file_path):
            raise ValueError("Given bed file path {file_path} does not exist.".format(
                file_path=file_path
            ))
    return bwtool("extract", "bed", bed_path, bigwig_path)


def extract(bed_path: str, bigwig_path: str) -> pd.DataFrame:
    """Return DataFrame with extracted data from given big wig files for regions specified in given.

    Parameters
    ----------------------------------------
    bed_path: str, the bed file from which to extract the regions.
    bigwig_path: str, the bigwig file from which to extract the data for the regions

    Raises
    -----------------------------------------
    ValueError:
        When one of the given file path does not exist.

    Returns
    ------------------------------------------
    Dataframe with extracted data.
    """

    df = _extract(bed_path, bigwig_path)
    new_data = df[df.columns[-1]
                  ].str.split(",", expand=True).replace("NA", np.nan).astype(float)
    new_data.columns = [
        "score_{i}".format(i=i)
        for i in new_data.columns
    ]
    df = df.drop(columns=df.columns[-1])
    return pd.concat([df, new_data], axis=1)


def extract_mean(bed_path: str, bigwig_path: str) -> pd.DataFrame:
    """Return DataFrame with mean of extracted data from given big wig files for regions specified in given.

    Parameters
    ----------------------------------------
    bed_path: str, the bed file from which to extract the regions.
    bigwig_path: str, the bigwig file from which to extract the data for the regions

    Raises
    -----------------------------------------
    ValueError:
        When one of the given file path does not exist.

    Returns
    ------------------------------------------
    Dataframe with extracted mean data.
    """

    df = _extract(bed_path, bigwig_path)
    new_data = df[df.columns[-1]
                  ].str.split(",", expand=True).replace("NA", np.nan).astype(float).mean()
    new_data.name = "mean_score"
    df = df.drop(columns=df.columns[-1])
    return pd.concat([df, new_data], axis=1)
