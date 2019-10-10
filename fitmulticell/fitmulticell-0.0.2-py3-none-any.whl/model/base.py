import pandas as pd
import numpy as np
import numbers
import os
import xml.etree.ElementTree as ET
from typing import Callable, List, Any
import abc
import logging
from ..util import tsv_to_df
from ..sumstat import IdSumstatFun

logger = logging.getLogger(__name__)

try:
    from pyabc.parameters import Parameter
    from pyabc.external.base import ExternalModel
except ImportError:
    logger.error("pyabc must be installed.")


class MorpheusModel(ExternalModel):
    """
    Derived from pyabc.ExternalModel. Allows pyABC to call morpheus
    in order to do the model simulation, and then record the results
    for further processing.

    Parameters
    ----------

    model_file: str
        The XML file containing the morpheus model.
    par_map: dict
        A dictionary from str to str, the keys being the parameter ids
        to be used in pyabc, and the values xpaths in the `morpheus_file`.
    sumstat_funs: List
        List of functions to calculate summary statistics. The list entries
        are instances of fitmulticell.sumstat.SumstatFun.
    executable: str, optional
        The path to the morpheus executable. If None given,
        'morpheus' is used.
    suffix, prefix: str, optional (default: None, 'morpheus_model_')
        Suffix and prefix to use for the temporary folders created.
    dir: str, optional (default: None)
        Directory to put the temporary folders into. The default is
        the system's temporary files location. Note that these files
        are usually deleted upon system shutdown.
    show_stdout, show_stderr: bool, optional (default = False, True)
        Whether to show or hide the stdout and stderr streams.
    raise_on_error: bool, optional (default = False)
        Whether to raise on an error in the model execution, or
        just continue.
    name: str, optional (default: None)
        A name that can be used to identify the model, as it is
        saved to db. If None is passed, the model_file name is used.
    """

    def __init__(self,
                 model_file: str,
                 par_map: dict,
                 sumstat_funs: List = None,
                 executable: str = "morpheus",
                 suffix: str = None,
                 prefix: str = "morpheus_model_",
                 dir: str = None,
                 show_stdout: bool = False,
                 show_stderr: bool = True,
                 raise_on_error: bool = False,
                 name: str = None):
        if name is None:
            name = model_file
        super().__init__(
            executable=executable,
            file=model_file,
            fixed_args=None,
            create_folder=True,
            suffix=suffix, prefix=prefix, dir=dir,
            show_stdout=show_stdout,
            show_stderr=show_stderr,
            raise_on_error=raise_on_error,
            name=name)
        self.par_map = par_map
        if sumstat_funs is None:
            sumstat_funs = [IdSumstatFun()]
        self.sumstat_funs = sumstat_funs
        self._check_sumstat_funs()

    def __str__(self):
        s = f"MorpheusModel {{\n" \
            f"\tname      : {self.name}\n" \
            f"}}"
        return s

    def __repr__(self):
        return self.__str__()

    def __call__(self, pars: Parameter):
        """
        This function is used in ABCSMC (or rather the sample() function,
        which redirects here) to simulate data for given parameters `pars`.
        """
        # create target on file system
        loc = self.eh.create_loc()
        file_ = os.path.join(loc, "model.xml")

        # write new file with parameter modifications
        self.write_modified_model_file(file_, pars)

        # create command
        cmd = self.eh.create_executable(loc)
        cmd = cmd + f" -file={file_} -outdir={loc}"

        # call the model
        self.eh.run(cmd=cmd, loc=loc)

        # compute summary statistics
        sumstats = self.compute_sumstats(loc)

        return sumstats

    def write_modified_model_file(self, file_, pars):
        """
        Write a modified version of the morpheus xml file to the target
        directory.
        """
        tree = ET.parse(self.eh.file)
        root = tree.getroot()
        for key, val in pars.items():
            xpath = self.par_map[key]
            node = root.find(xpath)
            node.set('value', str(val))
        tree.write(file_)

    def compute_sumstats(self, loc):
        """
        Compute summary statistics from the simulated data according to the
        provided list of summary statistics functions.
        """
        sumstat_dict = {'loc': loc}
        for sumstat_fun in self.sumstat_funs:
            sumstat = sumstat_fun(loc)
            safe_append_sumstat(sumstat_dict, sumstat, sumstat_fun.name)
        return sumstat_dict

    def _check_sumstat_funs(self):
        """
        Check sumstat functions for validity.
        """
        names = [ssf.name for ssf in self.sumstat_funs]
        if not len(set(names)) == len(names):
            raise AssertionError(
                f"The summary statistics passed to MorpheusModel must have"
                f"unique names, but obtained {names}")


def safe_append_sumstat(sumstat_dict, sumstat, key):
    types_ = (numbers.Number, np.ndarray, pd.DataFrame)
    if isinstance(sumstat, types_):
        if key in sumstat_dict:
            raise KeyError(
                f"Key {key} for sumstat {sumstat} already in the "
                f"sumstat dict {sumstat_dict}.")
        sumstat_dict[key] = sumstat
        return
    if isinstance(sumstat, dict):
        for _key, _value in sumstat.items():
            _key = key + '__' + str(_key)
            safe_append_sumstat(sumstat_dict, _value, _key)
        return
    raise ValueError(
        f"Type {type(sumstat)} of sumstat {sumstat} "
        f"is not permitted.")
