"""Core module of the dbis pipline."""

import collections
import importlib.util
import pickle
import platform
import traceback
import tempfile
import time

import git

from . import store
from .base import Loader
from .evaluators import Evaluator
from .output_handlers import OutputHandler
from .output_handlers import PickleBackupHandler
from .output_handlers import PostGresOutputHandler
from .utils import LOGGER
from .utils import notify_error, notify_success


class Core:
    """Represents the core functionality of the DBIS pipeline."""

    def __init__(self,
                 pipeline_config,
                 path_prefix=None,
                 dryrun=False,
                 mail=None):
        """
        Intitializes the pipeline.

        Args:
            pipeline_config: either a string to a module or a module that
            configures the pipleine.
        """
        store['path_prefix'] = path_prefix
        self.dryrun = dryrun
        self.mail = mail
        self.config_path = None
        self.git_info = self._get_git_info()

        if type(pipeline_config) == str:
            with open(pipeline_config, 'r') as config_file:
                self.config_file = config_file.read()
            self.config_path = pipeline_config
            pipeline_config = load_config(pipeline_config)

        store['config_path'] = self.config_path
        self.dataloader = pipeline_config.dataloader
        self.pipeline = pipeline_config.pipeline
        self.evaluator = pipeline_config.evaluator
        if (self.dataloader is None and self.pipeline is None
                and self.evaluator is None):
            raise ValueError('Pipeline config is empty.')

        self.output_handlers = pipeline_config.output_handlers
        if not dryrun:
            self.output_handlers.insert(0, PickleBackupHandler())
            self.output_handlers.append(PostGresOutputHandler())
        if "result_handlers" in dir(pipeline_config):
            self.result_handlers = pipeline_config.result_handlers
        else:
            self.result_handlers = []
        self.times = {}

    def run(self):
        """Runs the evaulation specified by the pipeline."""
        self.times['start'] = time.perf_counter()

        try:
            data = self.dataloader.load()
            loader_configs = self.dataloader.configuration
        except Exception as e:
            LOGGER.error(f'Error during data loading: {e}')
            traceback.print_tb(e.__traceback__)
            if self.mail:
                notify_error(
                    self.config_path,
                    'loading',
                    e,
                )
            # this is not recoverable.
            return

        if not self.dataloader.is_multiloader:
            data = [data]
            loader_configs = [loader_configs]
        for i, (run_data, loader_config) in enumerate(
                zip(data, loader_configs)):
            if hasattr(data, '__len__'):
                LOGGER.debug(f'calulating run {i+1} of {len(data)}')
            else:
                LOGGER.debug(f'calulating run {i+1}')
            self.times[f'run_start'] = time.perf_counter()
            try:
                result = self.evaluator.evaluate(self.pipeline, run_data)
            except Exception as e:
                LOGGER.error(f'Error during evaluation: {e}')
                traceback.print_tb(e.__traceback__)
                if self.mail:
                    notify_error(
                        self.config_path,
                        'evaluation',
                        e,
                        run=i,
                        loader_config=loader_config)
                # this is not recoverable.
                return
            self.times['eval'] = time.perf_counter()
            diff = self.times['eval'] - self.times['start']
            LOGGER.debug(f"evaluation: {diff:.2f} seconds")
            self._backup_result(result)

            for handler in self.result_handlers:
                try:
                    if callable(handler):
                        handler(result)
                    else:
                        function, kwargs = handler
                        function(result, **kwargs)
                except Exception as e:
                    if hasattr(handler, '__name__'):
                        LOGGER.error(
                            f'Result handler {handler.__name__} failed: {e}'
                        )  # noqa E501
                    else:
                        LOGGER.error(f'Result handler {handler} failed: {e}')
                    if self.mail:
                        notify_error(
                            self.config_path,
                            'result handling',
                            e,
                            run=i,
                            loader_config=loader_config)
                    continue
            self.times['result'] = time.perf_counter()
            diff = self.times['result'] - self.times['eval']
            LOGGER.debug(f"result handling:  {diff:.2f} seconds")
            try:
                self._store(i, result, loader_config)
            except Exception as e:
                LOGGER.error(f'Error during storing: {e}')
                if self.mail:
                    notify_error(
                        self.config_path,
                        'storing',
                        e,
                        run=i,
                        loader_config=loader_config)
                continue
            self.times['store'] = time.perf_counter()
            diff = self.times['store'] - self.times['result']
            LOGGER.debug(f"storing took {diff:.2f} seconds")
            diff = self.times['store'] - self.times['run_start']
            LOGGER.debug(f"run {i+1} took {diff:.2f} seconds")
            if self.mail == 'run':
                notify_success(
                    self.config_path,
                    self.times,
                    result,
                    run=i,
                    loader_config=loader_config)

        self.times['final'] = time.perf_counter()
        diff = self.times['final'] - self.times['start']
        LOGGER.debug(f"overall duration: {diff:.2f} seconds")
        if self.mail == 'total':
            notify_success(self.config_path, self.times)

    def _get_pipeline_configuration(self, pipeline):
        clazz = pipeline.__class__.__name__
        # for pipeline objects
        if hasattr(pipeline, 'named_steps'):
            steps = pipeline.named_steps.items()
            ret = {
                name: self._get_pipeline_configuration(transformer)
                for name, transformer in steps
            }
            ret['TYPE'] = clazz
            return ret
        # for featureunion, transformerpicker objects
        elif hasattr(pipeline, 'transformer_list'):
            transformers = pipeline.transformer_list
            ret = {
                transformer[0]:
                self._get_pipeline_configuration(transformer[1])
                for transformer in list(transformers)
            }
            ret['TYPE'] = clazz
            return ret
        else:
            return clazz

    def _get_git_info(self):
        sha_commit_id = None
        remote_url = None
        is_dirty = None
        try:
            repo = git.Repo(search_parent_directories=True)
            is_dirty = repo.is_dirty()
            sha_commit_id = repo.head.object.hexsha
            if repo.remotes and hasattr(repo.remotes, 'origin'):
                remote_url = repo.remotes.origin.url
            return (sha_commit_id, remote_url, is_dirty)
        except git.GitError:
            return None, None, None

    def _get_platform_info(self):
        info = {}
        info['arch'] = platform.architecture()
        info['machine'] = platform.machine()
        info['node'] = platform.node()
        info['platform'] = platform.platform()
        info['processor'] = platform.processor()
        info['system'] = platform.system()
        return info

    def _store(self, run_number, result, dl_conf):
        """Stores the results of the pipeline."""

        if self.dataloader.is_multiloader and 'run_number' not in dl_conf:
            dl_conf['run_number'] = run_number
        if 'class' not in dl_conf:
            dl_conf['class'] = self.dataloader.__class__.__name__

        ev_conf = self.evaluator.configuration
        if type(ev_conf) == dict:
            ev_conf['class'] = self.evaluator.__class__.__name__

        pipeline_conf = self._get_pipeline_configuration(self.pipeline)

        config = {
            'git_info': self.git_info,
            'sourcefile': self.config_path,
            'config_file': self.config_file,
            'dataloader': dl_conf,
            'pipeline': pipeline_conf,
            'evaluator': ev_conf,
            'outcome': result,
            'durations': self.times,
            'platform': self._get_platform_info(),
        }

        for output_handler in self.output_handlers:
            try:
                output_handler.handle_result(config)
            except Exception as e:
                LOGGER.error(
                    f'output handler {output_handler} failed: {e}'
                )

    def _backup_result(self, result, directory=None):
        """
        Pickles the results of an evaluator.

        Args:
            result: passed from an evaluator.
        """
        # TODO: think of a useful naming/storage strategy
        with tempfile.NamedTemporaryFile(
                dir=directory, suffix='.result.bak',
                delete=False) as output_file:

            pickle.dump(result, output_file)
            LOGGER.info(f'wrote pickle to {output_file.name}')


def load_config(file_path):
    """
    Loads the config module from the given python file.
    It loads the module and checks whether it is a valid config module.

    Args:
        file_path: The path to the config module.
    """
    spec = importlib.util.spec_from_file_location('config', file_path)
    pipeline_config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pipeline_config)

    missing_members = []
    wrong_members = []
    if "dataloader" not in dir(pipeline_config):
        missing_members.append("dataloader")
    elif not isinstance(pipeline_config.dataloader, Loader):
        wrong_members.append("dataloader")

    if "pipeline" not in dir(pipeline_config):
        missing_members.append("pipeline")

    if "evaluator" not in dir(pipeline_config):
        missing_members.append("evaluator")
    elif not isinstance(pipeline_config.evaluator, Evaluator):
        wrong_members.append("evaluator")

    if "output_handlers" in dir(pipeline_config):
        if isinstance(pipeline_config.output_handlers, collections.Iterable):
            for handler in pipeline_config.output_handlers:
                if not isinstance(handler, OutputHandler):
                    wrong_members.append(f"handler: {handler}")
        elif isinstance(pipeline_config.output_handlers, OutputHandler):
            pipeline_config.output_handlers = [pipeline_config.output_handlers]
        else:
            wrong_members.append("output_handler")
    else:
        pipeline_config.output_handlers = []

    if len(missing_members) > 0:
        raise ValueError(
            f"Module {file_path} is not a valid config module."
            f"The following members are missing: {','.join(missing_members)}.")

    if len(wrong_members) > 0:
        raise ValueError(f"Module {file_path} includes invalid members:"
                         f"{','.join(wrong_members)}.")

    return pipeline_config
