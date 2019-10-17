from concurrent.futures import ProcessPoolExecutor, as_completed, wait
from copy import deepcopy
from datetime import datetime
from logging import getLogger

import numpy as np
import pandas as pd
from openscm.scmdataframe import ScmDataFrame
from tqdm import tqdm

from . import mat4py

logger = getLogger(__name__)


# ZN: can we get rid of most of these given the new capabilities of ScmDataFrame?
def load_iam_timeseries(fname):
    # Read in the data. It requires a bit of wrangling to get it in the IamDataFrame format
    df = pd.read_csv(fname, header=None)
    df = df.set_index(0).T
    df.pop("time")
    df = ScmDataFrame(df)
    df["time"] = [
        datetime(d.year, d.month, d.day) for d in df["time"]
    ]  # strip out any hour values
    df = df.filter(
        region=[
            "World",
            "World|Northern Hemisphere|Land",
            "World|Northern Hemisphere|Ocean",
            "World|Southern Hemisphere|Land",
            "World|Southern Hemisphere|Ocean",
        ]
    )

    # Resample to annual means
    return df.resample("AS")


def merge_iam_timeseries(*args):
    """Merges two or more timeseries in the ScmDataFrame format.

    This method assumes that all data are from the same scenario. All scenarios in the resulting dataframe will be the same as specified
    by data in the last value of ``dfs``

    Parameters
    ----------
    args : openscm.scmdataframe.ScmDataFrame or string
        2 or more items to merge. ``openscm.scmdataframe.ScmDataFrame`` objects can be passed directly otherwise, if a string is passed
        then the dataframe will be attempted to be read from file

    Returns
    -------
    openscm.scmdataframe.ScmDataFrame

    """
    dfs = args
    assert len(dfs) >= 2, "At least two input dfs are required"

    def get_df(f):
        if isinstance(f, ScmDataFrame):
            return f
        else:
            return load_iam_timeseries(f)

    # Ensure that each df is loaded
    dfs = [get_df(f) for f in dfs]
    target_scenario = dfs[-1]["scenario"].unique()[0]
    res = None
    for df in dfs:
        df_copy = deepcopy(df)

        df_copy["scenario"] = target_scenario
        if res is None:
            res = df_copy
        else:
            res = res.append(df_copy)

    return res


def create_iam_dataframe(
    ts,
    index=None,
    variable="Surface Temperature",
    scenario="unspecified",
    model="unspecified",
    region="World",
    unit="K",
):
    """Create a IamDataFrame from a timeseries

    A number of the interfaces within scmcallib expect IamDataFrames, but they are not always the easiest things to initialise. This
    function provides a helper function for converting a 1d timeseries into a IamDataFrame

    Parameters
    ----------
    ts :
        1D np array or pd.Series/pd.Dataframe.
    index :
        If None, use the index from the ts. This assumes that `ts` is a pd.Series or pd.DataFrame. (Default value = None)
    variable :
         (Default value = 'Surface Temperature')
    scenario :
         (Default value = 'unspecified')
    model :
         (Default value = 'unspecified')
    region :
         (Default value = 'World')
    unit :
         (Default value = 'K')

    Returns
    -------
    type
        openscm.scmdataframe.ScmDataFrame instance

    """
    if index is None:
        if isinstance(ts, (pd.DataFrame, pd.Series)):
            index = ts.index
        else:
            raise ValueError("No valid index")

    if isinstance(ts, (pd.DataFrame, pd.Series)):
        assert len(ts)
        ts = ts.values.squeeze()

    assert ts.ndim == 1
    return ScmDataFrame(
        pd.Series(ts, index=index),
        columns={
            "unit": [unit],
            "variable": [variable],
            "region": [region],
            "model": [model],
            "scenario": [scenario],
        },
    )


def prepare_dataframe(df, extra_cols=()):
    """Convert model output in the form of a ScmDataFrame into something more useful in this use case

    Parameters
    ----------
    df : openscm.scmdataframe.ScmDataFrame
        Timeseries data from an scm or other training data
    extra_cols : listlike of str
        Additional meta columns to include in the output DataFrame

    Returns
    -------
    pd.DataFrame
        DataFrame with a time index and MultiIndex columns for model and region

    """
    return df.timeseries(meta=["variable", "region"] + list(extra_cols)).T


def convert_tuningstruc_to_scmdf(
    filepath, variable=None, region=None, unit=None, scenario=None, model=None
):
    """Convert a matlab tuningstruc to an ScmDataFrame

    Parameters
    ----------
    filepath : str
        Filepath from which to load the data

    variable : str
        Name of the variable contained in the tuningstruc. If None,
        `convert_tuningstruc_to_scmdf` will attempt to determine it from the input
        file.

    region : str
        Region to which the data in the tuningstruc applies. If None,
        `convert_tuningstruc_to_scmdf` will attempt to determine it from the input
        file.

    unit : str
        Units of the data in the tuningstruc. If None,
        `convert_tuningstruc_to_scmdf` will attempt to determine it from the input
        file.

    scenario : str
        Scenario to which the data in the tuningstruc applies. If None,
        `convert_tuningstruc_to_scmdf` will attempt to determine it from the input
        file.

    model : str
        The (integrated assessment) model which generated the emissions scenario
        associated with the data in the tuningstruc. If None,
        `convert_tuningstruc_to_scmdf` will attempt to determine it from the input
        file and if it cannot, it will be set to "unspecified".

    Raises
    ------
    ValueError
        If a metadata variable is not supplied and it cannot be determined from the
        tuningstruc.

    Returns
    -------
    :obj: `ScmDataFrame`
        ScmDataFrame with the tuningstruc data
    """
    dataset = mat4py.loadmat(filepath)

    for m, climate_model in enumerate(dataset["tuningdata"]["modelcodes"]):
        metadata = {
            "variable": [variable],
            "region": [region],
            "unit": [unit],
            "climate_model": [climate_model],
            "scenario": [scenario],
            "model": [model],
        }
        for k, v in metadata.items():
            if v == [None]:
                try:
                    metadata[k] = [dataset["tuningdata"]["model"][m][k]]
                except KeyError:
                    if k == "model":
                        metadata[k] = ["unspecified"]
                        continue

                    error_msg = "Cannot determine {} from file: " "{}".format(
                        k, filepath
                    )
                    raise KeyError(error_msg)

        scmdf = ScmDataFrame(
            data=np.asarray(dataset["tuningdata"]["model"][m]["data"][1]),
            columns=metadata,
            index=dataset["tuningdata"]["model"][m]["data"][0],
        )
        try:
            ref_df.append(scmdf, inplace=True)
        except NameError:
            ref_df = scmdf

    return ref_df


def convert_scmdf_to_tuningstruc(scmdf, outpath):
    """Convert an ScmDataFrame to a matlab tuningstruc

    One tuningstruc file will be created for each unique
    ["model", "scenario", "variable", "region", "unit"] combination in the input
    ScmDataFrame.

    Parameters
    ----------
    scmdf : :obj: `ScmDataFrame`
        ScmDataFrame to convert to a tuningstruc

    outpath : str
        Base path in which to save the tuningstruc. The rest of the pathname is
        generated from the metadata. `.mat` is also appended automatically.
    """
    iter = scmdf.timeseries().groupby(
        ["model", "scenario", "variable", "region", "unit"]
    )
    for (model, scenario, variable, region, unit), df in iter:
        dataset = {}
        dataset["tuningdata"] = {}
        dataset["tuningdata"]["modelcodes"] = []
        dataset["tuningdata"]["model"] = []

        for m, (climate_model, df) in enumerate(df.groupby("climate_model")):
            # impossible to make dataframe with duplicate rows so not an issue
            # this is just in case
            error_msg = (
                "Should only have a single unique timeseries for a given "
                '["climate_model", "model", "scenario", "variable", '
                '"region", "unit"] combination'
            )
            assert df.shape[0] == 1, error_msg

            dataset["tuningdata"]["modelcodes"].append(climate_model)
            dataset["tuningdata"]["model"].append({})

            dataset["tuningdata"]["model"][m]["model"] = model
            dataset["tuningdata"]["model"][m]["scenario"] = scenario
            dataset["tuningdata"]["model"][m]["variable"] = variable
            dataset["tuningdata"]["model"][m]["region"] = region
            dataset["tuningdata"]["model"][m]["unit"] = unit

            dataset["tuningdata"]["model"][m]["notes"] = (
                "{} {} {} {} ({}) tuningstruc (written with scmcallib)"
                "".format(scenario, model, region, variable, unit)
            )
            dataset["tuningdata"]["model"][m]["data"] = [
                [float(t.year) for t in df.columns],
                list(df.values.squeeze()),
            ]
            dataset["tuningdata"]["model"][m]["col_code"] = ["YEARS", variable]

        outfile = (
            "{}_{}_{}_{}_{}.mat".format(outpath, scenario, model, variable, region)
            .replace(" ", "_")
            .replace("|", "_")
        )
        # ask Jared how to add logging here
        mat4py.savemat(outfile, dataset)


def parallel_process(
    func, arr, n_jobs=10, use_kwargs=False, front_num=3, show_progress=False, pool=None
):
    """
    A parallel version of the map function with a progress bar.

    Adapted from http://danshiebler.com/2016-09-14-parallel-progress-bar/

    Parameters
    ----------
    func : function
        A python function to apply to the elements of array
    arr: listlike
        An array of configuration to iterate over
    n_jobs: int default=16
    use_kwargs : boolean, default=False
        Whether to consider the elements of array as dictionaries of keyword arguments to function
    front_num : int, default=3
        The number of iterations to run serially before kicking off the parallel job. Useful for catching bugs

    Returns
    -------
        [func(arr[0]), func(arr[1]), ...]
    """

    # We run the first few iterations serially to catch bugs
    front = []
    if front_num > 0:
        front = [func(**a) if use_kwargs else func(a) for a in arr[:front_num]]
    # If we set n_jobs to 1, just run a list comprehension. This is useful for benchmarking and debugging.
    if n_jobs == 1:
        if show_progress:
            return front + [
                func(**a) if use_kwargs else func(a) for a in tqdm(arr[front_num:])
            ]
        else:
            return front + [
                func(**a) if use_kwargs else func(a) for a in arr[front_num:]
            ]

    cleanup_pool = False
    if pool is None:
        pool = ProcessPoolExecutor(n_jobs)
        cleanup_pool = True

    try:
        # Pass the elements of array into func
        if use_kwargs:
            futures = [pool.submit(func, **a) for a in arr[front_num:]]
        else:
            futures = [pool.submit(func, a) for a in arr[front_num:]]
        kwargs = {
            "total": len(futures),
            "unit": "it",
            "unit_scale": True,
            "leave": True,
        }
        # Print out the progress as tasks complete
        if show_progress:
            for f in tqdm(as_completed(futures), **kwargs):
                pass
        else:
            wait(futures)
    finally:
        if cleanup_pool:
            pool.shutdown()

    out = []
    # Get the results from the futures.
    for i, future in enumerate(futures):
        try:
            out.append(future.result())
        except Exception as e:
            out.append(e)
    return front + out
