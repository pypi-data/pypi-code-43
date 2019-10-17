from copy import deepcopy
from logging import getLogger
from os.path import join, dirname, exists, splitext

import pandas as pd
from openscm.scmdataframe import df_append, ScmDataFrame
from pymagicc.io import (
    convert_magicc_to_openscm_regions,
    convert_magicc7_to_openscm_variables,
    MAGICCData,
)
from scipy.io import loadmat

from .distributions import Uniform, Normal
from .finder import PointEstimateFinder
from .parameterset import ScenarioParameterSet

logger = getLogger(__name__)


def _lookup_param_col(df, param, model_code):
    try:
        v = df.set_index("purpose").at[param, model_code]
    except KeyError:
        return None
    return _maybe_as_float(v)


def _maybe_as_float(v):
    try:
        return float(v)
    except ValueError:
        return v


def _handle_simcap_varnames(p, fname):
    """
    Interpret variable/region data from simcap naming convention
    """
    if p["name"] == "CARBONCYCLE":
        res = {"variable": "CARBONCYCLE_" + p["colcode"], "region": "World"}
    else:
        if p["colcode"].startswith("BOX"):
            p["colcode"] = p["colcode"][3:]
        res = {
            "variable": p["name"],
            "region": convert_magicc_to_openscm_regions(p["colcode"]),
        }

    if "_WITHIN_" in fname:
        v, fname = fname.split("_WITHIN_")
        res["file_variable"] = v
    else:
        res["file_variable"] = p["name"]
    res["file"] = fname

    return res


def get_target(tuning_data):
    weights = []
    data = []

    for sce in tuning_data:
        for t in tuning_data[sce]:
            variable = t["file_variable"]
            err_msg = "Could not find data for scenario {}, variable {} and region {} in {}".format(
                sce, variable, t["region"], t["file"]
            )

            _, file_ext = splitext(t["file"].lower())
            if file_ext == ".mat":
                logger.error(".mat files are no longer supported")
                continue
            elif file_ext == ".mag":
                df = MAGICCData(t["file"])
                if variable in df["variable"].values:
                    df = df.filter(variable=variable, region=t["region"])
                else:
                    df = df.filter(
                        variable=convert_magicc7_to_openscm_variables(variable),
                        region=t["region"],
                    )
            elif file_ext == ".csv":
                df = ScmDataFrame(
                    pd.read_csv(t["file"])
                )  # read as a normal SCM Dataframe
                if len(df["scenario"].unique()) > 1:
                    # if there are more th
                    df = df.filter(scenario=sce)
                    if not len(df):
                        logger.error(err_msg)
                        continue
                else:
                    # If only one scenario is present assume that it is correct
                    if sce not in df["scenario"].values:
                        logger.error(
                            "Scenario {} was not found in {}. Assuming data from scenario".format(
                                sce, t["file"]
                            )
                        )
                if variable in df["variable"].values:
                    df = df.filter(variable=variable, region=t["region"])
                else:
                    df = df.filter(
                        variable=convert_magicc7_to_openscm_variables(variable),
                        region=t["region"],
                    )
            else:
                raise ValueError(
                    "Unknown file extension encountered: {}".format(file_ext)
                )

            if len(df):
                df["scenario"] = sce
                if "variable" in t:
                    df["variable"] = t["variable"]
                data.append(df)

                # Copy the df and setup the weights
                w = deepcopy(df)
                w._data.loc[:, :] = t["weight"] if "weight" in t else 1.0
                weights.append(w)
            else:
                logger.error(err_msg)

    return df_append(data), df_append(weights)


def read_csv_tuningcore(
    fname, data_dir=None, xtrascen_fname="XTRASCENS.mat", scensets_fname="SCENSETS.mat"
):
    """
    Read in a tuning core file
    Parameters
    ----------
    fname: str
        Name of the file to read
    data_dir: str
        The directory which contains the supplementary files which are referenced in the tuning core file. If nothing
        is specified, data_dir defaults to the same directory as the tuning core file.
    xtrascen_fname: str
        Filename of the xtrascen file
    scensets_fname: str
        Filename of the scensets file

    Returns
    -------
    A dict containing the information parsed from the tuning file
    """
    if data_dir is None:
        data_dir = dirname(fname)

    df = pd.read_csv(fname, sep=";", skiprows=4, header=None)
    res = {"runs": []}

    # We are referencing specific col/row numbers as that is how simcap also does it

    model_info = df.iloc[5:, 1:5]
    model_info.columns = pd.Index(["code", "name", "descr", "do_tuning"])

    parameters = df.iloc[:, 5:].T

    # Not needed, but helps with my sanity
    cols = ["name", "scenario", "colcode", "purpose", "description"] + [
        str(v) for v in model_info["code"]
    ]
    parameters.columns = pd.Index(cols)

    scenarios = parameters["scenario"].dropna().unique()

    if xtrascen_fname is not None and exists(join(data_dir, xtrascen_fname)):
        xtrascen = loadmat(
            join(data_dir, xtrascen_fname), struct_as_record=False, squeeze_me=True
        )["XTRASCENS"]
        xtrascen_keys = xtrascen._fieldnames
    else:
        xtrascen = None
        xtrascen_keys = []
        logger.warning("Not using xtrascen file")

    if scensets_fname is not None and exists(join(data_dir, scensets_fname)):
        scensets = loadmat(
            join(data_dir, scensets_fname), struct_as_record=False, squeeze_me=True
        )["SCENSETS"]
        scensets_keys = scensets._fieldnames
    else:
        scensets = None
        scensets_keys = []
        logger.warning("Not using scensets data")

    for _, m in model_info.iterrows():
        # Header info
        model = {
            "code": m["code"],
            "name": m["name"],
            "description": m["descr"],
            "do_tuning": True if m["do_tuning"] == "1" else False,
            "fixed_parameters": [],
            "free_parameters": [],
            "scenarios": [],
        }
        model_code = m["code"]
        scenario_info = {s: {"tuning_data": [], "parameters": []} for s in scenarios}

        for _, p in parameters.iterrows():
            if p["purpose"] == "FIXEDVALUE":
                # Fixed parameter
                model["fixed_parameters"].append(
                    {"name": p["name"], "value": _maybe_as_float(p[model_code])}
                )
            elif p["purpose"] == "STARTVALUE":
                # Free parameter
                parameter_cols = parameters[parameters["name"] == p["name"]]

                val = _maybe_as_float(p[model_code])
                if not isinstance(val, float):
                    raise ValueError("value for {} is not a float".format(p["name"]))

                parameter = {"name": p["name"], "value": val}

                v = _lookup_param_col(parameter_cols, "MIN", model_code)
                if v is not None:
                    parameter["min"] = v

                v = _lookup_param_col(parameter_cols, "MAX", model_code)
                if v is not None:
                    parameter["max"] = v

                v = _lookup_param_col(parameter_cols, "DISTRIBUTION", model_code)
                if v is not None:
                    parameter["distribution"] = v
                else:
                    parameter["distribution"] = "uniform"

                model["free_parameters"].append(parameter)
            elif p["purpose"] == "DATSOURCE":
                # Figure out the different file format which simcap specifies
                # Namely, interpret a variable and region from name and colcode
                d = _handle_simcap_varnames(p, p[model_code])
                d["file"] = join(data_dir, d["file"])
                parameter_cols = parameters[
                    (parameters["name"] == p["name"])
                    & (parameters["scenario"] == p["scenario"])
                    & (parameters["colcode"] == p["colcode"])
                ]
                weight = _lookup_param_col(parameter_cols, "WEIGHT", model_code)
                if weight is not None:
                    d["weight"] = weight
                scenario_info[p["scenario"]]["tuning_data"].append(d)
            elif p["purpose"] == "XTRASCENSETTING":
                sce_params = {}

                if scensets is not None:
                    scenset_sce_name = "SCENSET_" + p["scenario"]
                    if scenset_sce_name in scensets_keys:
                        xtrascen_struct = getattr(scensets, scenset_sce_name)
                        params = {
                            f: getattr(xtrascen_struct, f)
                            for f in xtrascen_struct._fieldnames
                        }
                        sce_params = {**sce_params, **params}
                    else:
                        logger.error(
                            "Could not find scenset values for {}".format(p["value"])
                        )
                # Amend/overwrite with data from xtrascen
                if xtrascen is not None:
                    if p[model_code] in xtrascen_keys:
                        xtrascen_struct = getattr(xtrascen, p[model_code])
                        params = {
                            f: getattr(xtrascen_struct, f)
                            for f in xtrascen_struct._fieldnames
                        }
                        sce_params = {**sce_params, **params}
                    else:
                        logger.error(
                            "Could not find xtrascen values for {}".format(p["value"])
                        )
                scenario_info[p["scenario"]]["parameters"] = sce_params

        # Flatten the scenarios object
        model["scenarios"] = [
            {
                "name": s,
                "tuning_data": scenario_info[s]["tuning_data"],
                "parameters": scenario_info[s]["parameters"],
            }
            for s in scenario_info
        ]
        res["runs"].append(model)

    return res


def create_point_model(model, **kwargs):
    """

    Create a new model point estimate model instance from a configuration dict

    Note that a tuning core file may specify multiple calibration models. This function expects a single dict

    Parameters
    ----------
    model : dict
        Required keys (fixed_parameters, free_parameters)

        scenario: List of scenario definitions
            name : Name of the scenario
            parameters: List of fixed parameters for a given scenario
            tuning_data: List of scenario specific tuning_data
    Returns
    -------
    An instance of a PointEstimateFinder which has its parameter's and target's set

    """

    assert isinstance(model, dict)

    required_keys = ["fixed_parameters", "free_parameters"]
    for k in required_keys:
        if k not in model:
            raise ValueError('The model dict didnt contain a "{}" key'.format(k))
    scenarios = model.get("scenarios", [])

    params = ScenarioParameterSet([s["name"] for s in scenarios])

    for p in model["fixed_parameters"]:
        params.set_config(p["name"], p["value"])

    for p in model["free_parameters"]:
        if p["distribution"] == "uniform":
            dist = Uniform(lower=p["min"], upper=p["max"])
        elif p["distribution"] == "normal":
            dist = Normal(mu=p["mean"], sd=p["sd"])
        else:
            raise ValueError("Unknown distribution {}".format(p["distribution"]))
        params.set_tune(p["name"], dist, x0=p.get("value", None))

    # Find all the scenario parameters used
    sce_param_names = set()
    for sce in scenarios:
        for p in sce["parameters"]:
            sce_param_names.add(p)

    for p in sce_param_names:
        items = {sce["name"]: sce["parameters"].get(p, None) for sce in scenarios}
        params.set_config(p, items)

    m = PointEstimateFinder(params, **kwargs)

    # Load the data
    data, weights = get_target({sce["name"]: sce["tuning_data"] for sce in scenarios})
    m.set_target(data, iter_over="scenario", weights=weights)

    return m
