import inspect
import json
import logging
import os
import sys
import tempfile
import time
import uuid
import collections

from assemblyline_v3_service.common import digests
from assemblyline_v3_service.common import exceptions
from assemblyline_v3_service.common import identify
from assemblyline_v3_service.common import log, mock_forge
from assemblyline_v3_service.common import net
from assemblyline_v3_service.common import version
from assemblyline_v3_service.common.path import modulepath
from assemblyline_v3_service.common.result import Result
from assemblyline_v3_service.common.result import ResultSection
from assemblyline_v3_service.common.task import Task

Classification = mock_forge.get_classification()


class UpdaterFrequency(object):
    MINUTE = 60
    QUARTER_HOUR = MINUTE * 15
    HALF_HOUR = MINUTE * 30
    HOUR = MINUTE * 60
    QUAD_HOUR = HOUR * 4
    QUARTER_DAY = HOUR * 6
    HALF_DAY = HOUR * 12
    DAY = HOUR * 24

    @staticmethod
    def is_valid(freq):
        try:
            int(freq)
        except ValueError:
            return False

        return freq >= UpdaterFrequency.MINUTE


class UpdaterType(object):
    BOX = 'box'
    CLUSTER = 'cluster'
    PROCESS = 'process'
    NON_BLOCKING = 'non_blocking'

    @staticmethod
    def is_valid(utype):
        return utype in [UpdaterType.BOX, UpdaterType.CLUSTER, UpdaterType.PROCESS, UpdaterType.NON_BLOCKING]

    @staticmethod
    def blocking_types():
        return [
            UpdaterType.BOX,
            UpdaterType.CLUSTER,
            UpdaterType.PROCESS
        ]

    @staticmethod
    def unique_updater_types():
        return [
            UpdaterType.BOX,
            UpdaterType.CLUSTER
        ]


class ServiceBase(object):

    # If a service indicates it is a BATCH_SERVICE, the driver will attempt to
    # spool multiple requests before invoking the services execute() method.
    BATCH_SERVICE = False

    SERVICE_ACCEPTS = '.*'
    SERVICE_REJECTS = 'empty|metadata/.*'

    SERVICE_CATEGORY = 'Uncategorized'
    SERVICE_CLASSIFICATION = Classification.UNRESTRICTED
    # The default cfg used when an instance of this service is created.
    # Override this in your subclass with sane defaults for your service.
    # Default service config is a key/value where the value can be str, bool, int or list. Nothing else
    SERVICE_DEFAULT_CONFIG = {}
    # The default submission parameters that will be made available to the users when they submit files to your service.
    # Override this in your subclass with sane defaults for your service.
    # Default submission params list of dictionary. Dictionaries must have 4 keys (default, name, type, value) where
    # default is the default value, name is the name of the variable, type is the type of data (str, bool, int or list)
    #  and value should be set to the same as default.
    SERVICE_DEFAULT_SUBMISSION_PARAMS = []
    SERVICE_DESCRIPTION = "N/A"
    SERVICE_DISABLE_CACHE = False
    SERVICE_ENABLED = False
    SERVICE_FILE_REQUIRED = True
    SERVICE_LICENCE_COUNT = 0
    SERVICE_REVISION = '0'
    SERVICE_SAVE_RESULT = True
    SERVICE_SAFE_START = False
    SERVICE_STAGE = 'CORE'
    SERVICE_SUPPORTED_PLATFORMS = ['linux']
    SERVICE_TIMEOUT = 60
    SERVICE_VERSION = '0'
    SERVICE_IS_EXTERNAL = False

    SERVICE_CPU_CORES = 1
    SERVICE_RAM_MB = 1024

    def __init__(self, cfg=None):
        # Start with default config and override that with anything provided.
        self.cfg = self.SERVICE_DEFAULT_CONFIG.copy()
        if cfg:
            self.cfg.update(cfg)

        log.init_logging()

        # Initialize non trivial members in start_service rather than __init__.
        self.log = logging.getLogger('assemblyline.svc.{}'.format(self.service_name().lower()))
        self.counters = collections.Counter()
        self.dispatch_queue = None
        self.result_store = None
        self.submit_client = None
        self.transport = None
        self.worker = None
        self._working_directory = None
        self._ip = '127.0.0.1'
        self.mac = net.get_mac_for_ip(net.get_hostip())
        self._updater = None
        self._updater_id = None
        self.submission_tags = {}

    def start(self):
        """
        Called at worker start.

        :return:
        """
        pass

    def stop(self):
        pass

    @classmethod
    def service_name(cls):
        return cls.__name__

    def set_stage(self, step):
        self.log.warning("Unable to set stage! Feature not supported in ALv4.")


    def get_tool_version(self):
        return ''

    @classmethod
    def get_default_config(cls):
        return {
            'accepts': cls.SERVICE_ACCEPTS,
            'category': cls.SERVICE_CATEGORY,
            'config': {k.lower(): v for k, v in cls.SERVICE_DEFAULT_CONFIG.items()},
            'submission_params': cls.SERVICE_DEFAULT_SUBMISSION_PARAMS,
            'description': cls.SERVICE_DESCRIPTION,
            'enabled': cls.SERVICE_ENABLED,
            'is_external': cls.SERVICE_IS_EXTERNAL,
            'licence_count': cls.SERVICE_LICENCE_COUNT,
            'name': cls.service_name(),
            'rejects': cls.SERVICE_REJECTS,
            'stage': cls.SERVICE_STAGE,
            'supported_platforms': cls.SERVICE_SUPPORTED_PLATFORMS,
            'timeout': cls.SERVICE_TIMEOUT,
            'version': cls.get_service_version,
        }

    @classmethod
    def get_service_version(cls):
        t = (
            version.SYSTEM_VERSION,
            version.FRAMEWORK_VERSION,
            cls.SERVICE_VERSION,
            cls.SERVICE_REVISION,
        )
        return '.'.join([str(v) for v in t])

    @staticmethod
    def parse_revision(revision):
        try:
            abs_path = os.path.abspath((inspect.stack()[1])[1])
            directory_of_1py = os.path.dirname(abs_path)
            return git_repo_revision(directory_of_1py)[:7]
        except Exception:
            print("Determining registration by fallback ")
            pass

        try:
            return revision.strip('$').split(':')[1].strip()[:7]
        except:
            return '0'

    def start_service(self):
        # Start this service. Common service start is performed and then
        # the derived services start() is invoked.
        # Services should perform any pre-fork (once per celery app) init
        # in the constructor. Any init/config that is not fork-safe or is
        # otherwise subprocess specific should be done here.

        try:
            self._ip = net.get_hostip()
        except:
            pass

        self.log.info('Service Starting: {}'.format(self.service_name()))

        # Tell the service to do its service specific imports.
        # We pop the CWD from the module search path to avoid
        # namespace collisions.
        cwd_save = sys.path.pop(0)
        self.import_service_deps()
        sys.path.insert(0, cwd_save)

        self.start()
        if self.SERVICE_SAFE_START:
            NamedQueue('safe-start-%s' % self.mac).push('up')

    def import_service_deps(self):
        """
        Do non-standard service specific imports.

        :return:
        """
        pass

    def _ensure_size_constraints(self, task):

        if not task or not task.result:
            return

        try:
            max_result_size = 1024 * 512
            serialized = json.dumps(task.as_service_result())
            if len(serialized) <= max_result_size:
                return

            task.oversized = True
            self.log.info("Result is oversized. Shrinking. ({})".format(len(serialized)))
            # Remove the tags and sections, leaving the score and tag_score intact.
            # Submit the oversized result as supplementary file.
            task.result['tags'] = []
            filename = '_'.join([self.service_name(), task.sha256, 'result.json'])
            result_path = os.path.join(self.working_directory, filename)
            with open(result_path, 'w') as f:
                f.write(serialized)

            file_info = identify.fileinfo(result_path)
            sha256 = file_info['sha256']
            mime = file_info['mime']

            task.supplementary.append(task.add_child(None, sha256, mime, 'oversized result', task.classification, result_path))

            oversize_notice_section = ResultSection(
                title_text="Result exceeded max size. Attached as supplementary file. Score has been preserved.")
            task.result['sections'] = [json.loads(json.dumps(oversize_notice_section))]
        except:
            self.log.exception("While shrinking oversized result")

    def handle_task(self, task):
        self.log.info('Start: {}/{} ({})'.format(task.sid, task.sha256, task.tag))
        self.task = task
        task.watermark(self.service_name(), self.get_service_version(), self.get_tool_version())
        task.save_result_flag = self.SERVICE_SAVE_RESULT

        # if task.profile:
        #     task.set_debug_info("serviced_on:%s" % self._ip)

        try:
            start_time = time.time()
            # First try to fetch from cache. If that misses,
            # run the service execute to get a fresh result.

            task.clear_extracted()
            task.clear_supplementary()
            # Pass it to the service for processing. Wrap it in ServiceRequest
            # facade so service writers don't see a request interface with 80 members.
            request = ServiceRequest(self, task)

            # Collect submission_tags
            if task.is_initial():
                self.submission_tags = {}
            else:
                self.submission_tags = task.get_submission_tags_name()

            old_result = self.execute(request)
            if old_result:
                self.log.warning("Service {} is using old convention "
                                 "returning result instead of setting "
                                 "it in request".format(self.service_name()))
                task.result = old_result
            elif task.save_result_flag and not task.result:
                self.log.info("Service {} supplied NO result at all. Creating empty result for the service...".format(self.service_name()))
                task.result = Result()

            task.milestones = {'service_started': start_time, 'service_completed': time.time()}
            if task.save_result_flag:
                task.result.finalize()
            self._success(task)
            # self._log_completion_record(task, (time.time() - start_time))
        except Exception as ex:
            print(ex)
            self._handle_execute_failure(task, ex, exceptions.get_stacktrace_info(ex))
            if not isinstance(ex, exceptions.RecoverableError):
                self.log.exception("While processing task: {}/{}".format(task.sid, task.sha256))
                raise
            else:
                self.log.info("While processing task: %s/%s", task.sid, task.sha256)
        finally:
            self._cleanup_working_directory()

    def _save_error(self, task, error_status, stack_info):
        task.error_message = stack_info
        task.error_status = error_status

        error = task.as_service_error()
        error_path = os.path.join(tempfile.gettempdir(), "{}_{}_error.json".format(task.sid, task.sha256))
        with open(error_path, 'w') as f:
            json.dump(error, f)
        self.log.info("Saving error to: {}".format(error_path))

    def _save_result(self, task):
        if not task.save_result_flag:
            return None

        result = task.as_service_result()
        result_path = os.path.join(tempfile.gettempdir(), "{}_{}_result.json".format(task.sid, task.sha256))
        with open(result_path, 'w') as f:
            json.dump(result, f)
        self.log.info("Saving result to: {}".format(result_path))

    def _cleanup_working_directory(self):
        # Actual file deletion done by task handler
        self._working_directory = None

    def _log_completion_record(self, task, duration):
        self.log.info("Done:  {}/{} C:{} S:{} T:{:.3f} Z:{}".format(
                      task.sid, task.srl,
                      1 if task.from_cache else 0,
                      task.score or 0,
                      duration,
                      task.size))

    def _handle_execute_failure(self, task, exception, stack_info):
        # Get rid of result in case it was what caused the problem.
        task.result = None
        # Also get rid of extracted and supplementary
        task.clear_extracted()
        task.clear_supplementary()
        if isinstance(exception, exceptions.RecoverableError):
            self.log.info('Recoverable Service Error (%s/%s) %s: %s', task.sid, task.sha256, exception, stack_info)
            self._save_error(task, 'FAIL_RECOVERABLE', stack_info)
        else:
            self.log.error('Service Error (%s/%s) %s: %s', task.sid, task.sha256, exception, stack_info)
            self._save_error(task, 'FAIL_NONRECOVERABLE', stack_info)

    def stop_service(self):
        # Perform common stop routines and then invoke the child's stop().
        self.log.info('Service Stopping: {}'.format(self.service_name()))
        self.stop()

    @staticmethod
    def get_task_age(task):
        received = 0
        try:
            received = task.request.get('sent')
        except:
            pass
        if not received:
            return 0
        return time.time() - received

    def _success(self, task):
        # if task.result:
        #     tags = task.result.get('tags', None) or []
        #     if tags:
        #         ExpiringSet(task.get_tag_set_name()).add(*tags)

        self._ensure_size_constraints(task)

        task.success()
        self._save_result(task)

    def execute(self, request):
        # type: (ServiceRequest) -> None
        raise NotImplementedError('execute() not implemented.')

    @property
    def working_directory(self):
        al_temp_dir = os.path.join(tempfile.gettempdir(), 'working_directory')
        if not os.path.isdir(al_temp_dir):
            os.makedirs(al_temp_dir)
        if self._working_directory is None:
            self._working_directory = al_temp_dir
        return self._working_directory

    def _register_update_callback(self, *args, **kwargs):
        self.log.warning("Unable to register update callback! Feature not supported in ALv4.")

    @property
    def source_directory(self):
        return modulepath(self.__class__.__module__)

    def _register_cleanup_op(self, *args, **kwargs):
        self.log.warning("Unable to register cleanup operation! Feature not supported in ALv4.")


class ServiceRequest(object):
    def __init__(self, service, task):
        # type: (ServiceBase, Task) -> None

        self.log = logging.getLogger('assemblyline.svc.{}'.format(service.service_name().lower()))

        self.srl = task.sha256
        self.sid = task.sid
        # self.config = task.config
        self.tag = task.tag
        self.md5 = task.md5
        self.sha1 = task.sha1
        self.sha256 = task.sha256
        # self.priority = task.priority
        # self.ignore_filtering = task.ignore_filtering
        self.task = task
        # self.local_path = ''
        # self.successful = True
        # self.error_is_recoverable = True
        # self.error_text = None
        # self.current_score = task.max_score
        self.deep_scan = task.deep_scan
        self.extracted = task.extracted
        self.max_extracted = task.max_extracted
        self.path = task.sha256  # TODO: self.path = task.path or task.sha256

        self._svc = service

    @property
    def result(self):
        # type: () -> Result
        return self.task.result

    @result.setter
    def result(self, value):
        self.task.result = value

    def add_extracted(self, name, text, display_name=None, classification=None, submission_tag=None, normalize=lambda x: x):
        """
        Add an extracted file for additional processing.

        :param name: Path to file to attach
        :param text: Descriptive text about the file
        :param display_name: Optional display text
        :param classification: The classification of this extracted file. Defaults to current classification.
        :param submission_tag:
        :return: None
        """
        file_name = display_name or normalize(name)

        # Don't accept empty files
        # if os.path.getsize(name) == 0:
        #     self.log.warning("An empty file can't be added as an extracted file: {}".format(name))
        #     self.log.info("HERE1")
        #     return False

        return self.task.add_extracted(
            name, file_name, text, classification or self._svc.SERVICE_CLASSIFICATION
        )

    def add_supplementary(self, name, text, display_name=None, classification=None, normalize=lambda x: x):
        file_name = display_name or normalize(name)

        # # Don't accept empty files
        # if os.path.getsize(name) == 0:
        #     self.log.warning("An empty file can't be added as a supplementary file: {}".format(name))
        #     return

        return self.task.add_supplementary(
            name, file_name, text, classification or self._svc.SERVICE_CLASSIFICATION
        )

    def download(self):
        file_path = os.path.join(tempfile.gettempdir(), self.sha256)
        if not os.path.exists(file_path):
            raise Exception('Download failed. Not found on local filesystem')

        received_sha256 = digests.get_sha256_for_file(file_path)
        if received_sha256 != self.sha256:
           raise Exception('SHA256 mismatch between requested and downloaded file. {} != {}'.format(self.sha256, received_sha256))
        return file_path

    def set_service_context(self, msg):
        self.task.report_service_context(msg)

    def tempfile(self, sha256):
        return os.path.join(self._svc.working_directory, sha256)

    def get_param(self, name):
        # Does the parameter exist in the class?
        params_code = [x for x in self._svc.SERVICE_DEFAULT_SUBMISSION_PARAMS if x["name"] == name]
        params = [x for x in self.task.service_config if x == name]
        if params:
            return params[0]
        else:
            return params_code[0]['value']

    def drop(self):
        self.task.drop()
