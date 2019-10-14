import shutil
from concurrent.futures import ProcessPoolExecutor
from logging import getLogger
from multiprocessing import current_process, Manager
from os.path import exists, join
from subprocess import CalledProcessError
from tempfile import mkdtemp

import pandas as pd
from openscm.scmdataframe import df_append
from openscm.scmdataframe.base import ScmDataFrameBase
from pymagicc import MAGICC6, MAGICC7
from pymagicc.io import MAGICCData

from scmcallib.utils import parallel_process
from .base import BaseSCM

logger = getLogger(__name__)

# Set the EMIS and Tuning configuration as pymagicc2.0 expects
config_defaults = {
    "file_emisscen_2": "NONE",
    "file_emisscen_3": "NONE",
    "file_emisscen_4": "NONE",
    "file_emisscen_5": "NONE",
    "file_emisscen_6": "NONE",
    "file_emisscen_7": "NONE",
    "file_emisscen_8": "NONE",
    "file_tuningmodel_1": "PYMAGICC",
    "file_tuningmodel_2": "USER",
    "file_tuningmodel_3": "USER",
    "file_tuningmodel_4": "USER",
    "file_tuningmodel_5": "USER",
    "file_tuningmodel_6": "USER",
    "file_tuningmodel_7": "USER",
    "file_tuningmodel_8": "USER",
    "file_tuningmodel_9": "USER",
    "file_tuningmodel_10": "USER",
}


def _generate_magicc_root(root_dir):
    return mkdtemp(prefix="pymagicc-", dir=root_dir)


_instances = {}


def get_magicc_inst(magicc_version=7, root_dir=None, init_callback=None):
    """Gets a MAGICC object which is ready to run

    This caches the magicc instance used to minimise overhead from copying files. Each process gets a unique copy of MAGICC
    to ensure that each chain has exclusive access to the magicc instance.

    Returns
    -------
    pymagicc.MAGICC7
        MAGICC7 object with a valid configuration
    """

    key = (magicc_version, current_process().name)
    try:
        return _instances[key]
    except KeyError:
        kwargs = {}
        if root_dir:
            kwargs["root_dir"] = _generate_magicc_root(root_dir)

        if magicc_version == 6:
            magicc = MAGICC6(**kwargs)
        else:
            magicc = MAGICC7(strict=False, **kwargs)
        magicc.create_copy()
        logger.info("Creating new magicc instance: {} - ".format(key, magicc.root_dir))
        # magicc.set_output_variables(write_binary=True, write_ascii=False)
        if magicc_version == 7:
            magicc.update_config("MAGCFG_USER.CFG", **config_defaults)
        _instances[key] = magicc
        if init_callback is not None:
            init_callback(magicc)
        else:
            magicc.set_output_variables(write_binary=True, write_ascii=False)
        return magicc


def _get_output_config(variables):
    res = {}
    var = []
    for v in variables:
        if v.startswith("CARBONCYCLE_"):
            res["out_carboncycle"] = 1
            res[
                "out_ascii_binary"
            ] = "ASCII"  # TODO: temporary until we can read carboncycle files
        elif v.startswith("DAT_"):
            var.append(v)

    # TODO: remove after pymagicc#264 is merged
    if not len(var):
        var = ["DAT_SURFACE_TEMP"]

    res["out_dynamic_vars"] = var
    return res


def read_carboncycle(fname):
    d = pd.read_csv(fname, skiprows=20, engine="python", sep=r"\s+", index_col="YEARS")
    cols = {
        "scenario": "unspecified",
        "model": "magicc",
        "region": "World",
        "unit": "unspecified",
        "variable": ["CARBONCYCLE_" + c for c in d.columns],
    }

    return MAGICCData(d, columns=cols)


def _merge_config(*ds):
    # Merge many configuration dicts case insensitively
    res = {}
    for d in ds:
        res.update({k.lower(): d[k] for k in d})
    return res


class _MAGICC_SCM(BaseSCM):
    """
    By default, all flags which control which output variables (out_*) are written to disk have been turned off. Therefore,
    explicit config variables should be set to enable the output required for training. Additionally, binary output data are
    written by default to increase the execution speed.

    One instance per process will be created. This enables the use of multiple instances of magicc to be run simultaneously.

    Parameters
    ----------
    root_dir :
        The root directory in which the magicc instances will be created. The actual instances will be
        created as subdirectories within this directory. If None, then the default directory
        in pymagicc will be used (/tmp)
    only : listlike of str or str or None
        A list of variables to extract from the magicc output. Any additional variables not in ``only`` will not be read
    kwargs :
        Additional kwargs which are passed to the pymagicc instance

    """

    def __init__(self, root_dir=None, **kwargs):
        super(_MAGICC_SCM, self).__init__(**kwargs)
        self.root_dir = root_dir

    @property
    def version(self):
        return self.magicc_cls.version

    def cleanup(self):
        vals = list(_instances.keys())
        for k in vals:
            logger.info(
                "Cleaning up magicc instance at {}".format(_instances[k].root_dir)
            )
            shutil.rmtree(_instances[k].root_dir)
            _instances.pop(k)

    def instance(self):
        return get_magicc_inst(root_dir=self.root_dir, magicc_version=self.version)

    def _run_single(self, parameters, variables=None):
        magicc = self.instance()
        if variables is None:
            variables = []
        config = _merge_config(
            self.config_parameters, parameters, _get_output_config(variables)
        )

        try:
            results = magicc.run(**config)
        except (CalledProcessError, IndexError) as e:
            logger.exception(e.stderr)
            raise ValueError(str(e)) from e

        if exists(join(magicc.out_dir, "CARBONCYCLE.OUT")):
            results = df_append(
                [results, read_carboncycle(join(magicc.out_dir, "CARBONCYCLE.OUT"))]
            )
        return results

    def _merge_config(self, *ds):
        # Merge many configuration dicts case insensitively
        res = {}
        for d in ds:
            res.update({k.lower(): d[k] for k in d})
        return res


class MAGICC6_SCM(_MAGICC_SCM):
    __doc__ = (
        """Runner for the MAGICC6 simple climate model
    """
        + _MAGICC_SCM.__doc__
    )
    magicc_cls = MAGICC6
    name = "magicc6"


class MAGICC7_SCM(_MAGICC_SCM):
    __doc__ = (
        """Runner for the MAGICC7 simple climate model
    """
        + _MAGICC_SCM.__doc__
    )
    magicc_cls = MAGICC7
    name = "magicc7"


def _parallel_func(args):
    cls, cls_kwargs, params, iter_over, variables = args
    scm = cls(**cls_kwargs)
    return scm.run(params, variables=variables, iter_over_value=iter_over)


def _init_func(instances):
    # Assigned the shared dict to _instances
    global _instances
    _instances = instances


class ParallelMagicc(_MAGICC_SCM):
    def __init__(self, n_workers=4, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pool = None
        self.n_workers = n_workers
        self.kwargs = kwargs
        self._shared_manager = None

    def start(self):
        logger.info("Starting process pool for magicc")
        global _instances
        self._shared_manager = Manager()
        _instances = self._shared_manager.dict()

        self._pool = ProcessPoolExecutor(
            max_workers=self.n_workers, initializer=_init_func, initargs=(_instances,)
        )

    def cleanup(self):
        logger.info("Cleaning up parallel magicc instance")

        global _instances
        _instances = dict(_instances)
        if self._shared_manager is not None:
            self._shared_manager.shutdown()

        super().cleanup()

        if self._pool is not None:
            logger.info("stopping pool")
            self._pool.shutdown()

    def run_multiple(self, runs, variables=None):
        if self._pool is None:
            raise ValueError("run_multiple called outside of a context manager")
        cls = MAGICC6_SCM if self.version == 6 else MAGICC7_SCM
        runs_mp = [(cls, self.kwargs, r, i, variables) for r, i in runs]
        results = parallel_process(
            _parallel_func, runs_mp, front_num=0, pool=self._pool
        )
        for r in results:
            if not isinstance(r, ScmDataFrameBase):
                raise ValueError("Run failed: {}".format(r))

        return df_append(results)


class MAGICC6_Parallel(ParallelMagicc):
    """
    Parallel multi-process version of ``MAGICC6_SCM``

    Each instance is run on a worker process which allows for greater parallelisation.
    """
    magicc_cls = MAGICC6
    name = "magicc6-parallel"


class MAGICC7_Parallel(ParallelMagicc):
    """
    Parallel multi-process version of ``MAGICC7_SCM``

    Each instance is run on a worker process which allows for greater parallelisation.
    """
    magicc_cls = MAGICC7
    name = "magicc7-parallel"
