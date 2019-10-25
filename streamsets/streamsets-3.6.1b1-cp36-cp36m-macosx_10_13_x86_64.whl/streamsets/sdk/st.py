# Copyright 2019 StreamSets Inc.

"""Abstractions for interacting with StreamSets Transformer."""

import copy
import io
import json
import logging
import zipfile
from datetime import datetime
from functools import wraps
from urllib.parse import urlparse
from uuid import uuid4

from . import st_api, st_models
from .exceptions import ValidationError
from .utils import SeekableList

logger = logging.getLogger(__name__)

# The `#:` constructs at the end of assignments are part of Sphinx's autodoc functionality.
DEFAULT_ST_USERNAME = 'admin'  #:
DEFAULT_ST_PASSWORD = 'admin'  #:
DEFAULT_START_STATUSES_TO_WAIT_FOR = ['RUNNING', 'FINISHED']  #:
DEFAULT_SNAPSHOT_TIMEOUT = 30  #:
DEFAULT_VALIDATE_TIMEOUT = 500  #:


class Transformer:
    """Class to interact with StreamSets Transformer.

    Args:
        server_url (:obj:`str`): URL of an existing ST deployment with which to interact.
        username (:obj:`str`, optional): ST username. Default: :py:const:`streamsets.sdk.st.DEFAULT_ST_USERNAME`.
        password (:obj:`str`, optional): ST password. Default: :py:const:`streamsets.sdk.st.DEFAULT_ST_PASSWORD`.
        control_hub (:py:class:`streamsets.sdk.ControlHub`, optional): A StreamSets Control Hub instance to use
            for SCH-registered Transformers. Default: ``None``.
        dump_log_on_error (:obj:`bool`): Whether to output Transformer logs when exceptions
            are raised by certain methods. Default: ``False``
    """
    VERIFY_SSL_CERTIFICATES = True
    def __init__(self,
                 server_url,
                 username=None,
                 password=None,
                 control_hub=None,
                 dump_log_on_error=False,
                 **kwargs):
        self.server_url = server_url
        self.username = username or DEFAULT_ST_USERNAME
        self.password = password or DEFAULT_ST_PASSWORD
        self.control_hub = control_hub
        self.dump_log_on_error = dump_log_on_error

        if self.server_url:
            sch_headers = {
                'X-SS-User-Auth-Token': self.control_hub.api_client.session.headers['X-SS-User-Auth-Token']
            } if self.control_hub else {}
            session_attributes = {'verify': self.VERIFY_SSL_CERTIFICATES}
            self.api_client = st_api.ApiClient(server_url=self.server_url,
                                               username=self.username,
                                               password=self.password,
                                               headers=sch_headers,
                                               dump_log_on_error=self.dump_log_on_error,
                                               session_attributes=session_attributes,
                                               **kwargs)

            # Keep track of the server host so that tests that may need it (e.g. to set configurations) can use it.
            self.server_host = urlparse(self.server_url).netloc.split(':')[0]
        else:
            self.server_host = None

        # ST definitions should be an attribute of this class, but we use a property for
        # access to handle necessary setup and synchronization tasks, so indicate internal use for
        # the underlying attribute with a leading underscore.
        self._definitions = None

        # Instances of :py:class:`streamsets.sdk.st_models.PipelineBuilder` require a blank pipeline (i.e.
        # an empty pipeline JSON) from our particular Transformer version. We keep track of this with an
        # instance attribute to avoid repetitive API calls.
        self._pipeline = None

    def _dump_st_log_on_error(*dec_args, **dec_kwargs):
        """A Python decorator to log ST when errors happen.

        Args:
            *dec_args: Optional positional arguments to be passed.
            **dec_kwargs: Optional keyword arguments to be passed, such as ``all`. ``all`` will
                include complete ST logs.
        """
        def outer_func(func):
            @wraps(func)
            def wrapped(self, *args, **kwargs):
                log_time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')
                try:
                    return func(self, *args, **kwargs)
                except:
                    if self.dump_log_on_error:
                        st_log = (self.get_logs()
                                  if dec_kwargs.get('all') else self.get_logs().after_time(log_time_now))
                        if st_log:
                            logger.error('Error during `%s` call. ST log follows ...', func.__name__)
                            print('------------------------- ST log - Begins -----------------------')
                            print(st_log)
                            print('------------------------- ST log - Ends -------------------------')
                    raise
            return wrapped
        if len(dec_args) == 1 and not dec_kwargs and callable(dec_args[0]):  # called without args
            return outer_func(dec_args[0])
        else:
            return outer_func

    @_dump_st_log_on_error
    def add_pipeline(self, *pipelines):
        """Add one or more pipelines to the Transformer instance.

        Args:
            *pipelines: One or more instances of :py:class:`streamsets.sdk.st_models.Pipeline`.
        """
        for pipeline in set(pipelines):
            # Only do the REST call to add the pipeline if an API client is available.
            if self.api_client:
                logger.info('Importing pipeline %s...', pipeline.id)
                response = self.api_client.import_pipeline(pipeline_id=pipeline.id,
                                                           pipeline_json=pipeline._data)
                status_command = self.api_client.get_pipeline_status(pipeline_id=pipeline.id)
                status_command.wait_for_status(status='EDITED')

    @_dump_st_log_on_error
    def remove_pipeline(self, *pipelines):
        """Remove one or more pipelines from the Transformer instance.

        Args:
            *pipelines: One or more instances of :py:class:`streamsets.sdk.st_models.Pipeline`.
        """
        for pipeline in set(pipelines):
            if self.api_client:
                logger.info('Deleting pipeline %s...', pipeline.id)
                self.api_client.delete_pipeline(pipeline_id=pipeline.id)

    def reset_origin(self, pipeline):
        """Reset origin offset.

        Args:
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): Pipeline object.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`.
        """
        return self.api_client.reset_origin_offset(pipeline.id)

    @property
    def pipelines(self):
        """Get all pipelines in the pipeline store.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of
                :py:class:`streamsets.sdk.st_models.Pipeline` instances.
        """
        pipeline_ids = [pipeline_configuration_info['pipelineId']
                        for pipeline_configuration_info
                        in self.api_client.get_all_pipeline_configuration_info().response.json()]
        pipelines_archive = zipfile.ZipFile(
            file=io.BytesIO(self.api_client.export_pipelines(body=pipeline_ids).response.content), mode='r'
        )
        pipelines = [json.loads(pipelines_archive.read(pipeline_filename).decode())
                     for pipeline_filename in pipelines_archive.namelist()]
        return SeekableList(self.get_pipeline_builder().import_pipeline(pipeline, regenerate_id=False)
                                .build(title=pipeline['pipelineConfig']['title'])
                            for pipeline in pipelines)

    def get_pipeline_builder(self, **kwargs):
        """Get a pipeline builder instance with which a pipeline can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.PipelineBuilder`.
        """
        if not self.api_client:
            raise Exception('ST must be started to get a PipelineBuilder instance.')

        # A :py:class:`streamsets.sdk.st_models.PipelineBuilder` instance takes an empty pipeline and a
        # dictionary of definitions as arguments. To get the former, we generate a pipeline in ST, export it,
        # and then delete it. For the latter, we simply pass along `self.definitions`.
        if not self._pipeline:
            create_pipeline_response = self.api_client.create_pipeline(pipeline_title='Pipeline Builder',
                                                                       auto_generate_pipeline_id=True).response.json()
            try:
                pipeline_id = create_pipeline_response['info']['pipelineId']
            except KeyError:
                pipeline_id = create_pipeline_response['info']['name']

            self._pipeline = self.api_client.export_pipeline(pipeline_id)
            self.api_client.delete_pipeline(pipeline_id)

        return st_models.PipelineBuilder(pipeline=copy.deepcopy(self._pipeline),
                                         definitions=self.definitions)

    @_dump_st_log_on_error
    def set_user(self, username, password=None):
        """Set the user with which to interact with ST.

        Args:
            username (:obj:`str`): Username of user.
            password (:obj:`str`, optional): Password for user. Default: same as ``username``.
        """
        self.username = username
        # If password isn't set, assume it's the same as the username to follow existing
        # conventions.
        self.password = password or username

        if self.api_client:
            self.api_client.set_user(self.username, self.password)

    @property
    def definitions(self):
        """Get an ST instance's definitions.

        Will return a cached instance of the definitions if called more than once.

        Returns:
            An instance of :py:class:`json`.
        """
        if self._definitions:
            return self._definitions

        # Getting definitions from ST requires a running deployment.
        if not self.api_client:
            raise Exception('ST must be started to get definitions.')

        self._definitions = self.api_client.get_definitions()
        return self._definitions

    @_dump_st_log_on_error
    def validate_pipeline(self, pipeline, **kwargs):
        """Validate a pipeline.

        Args:
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.
            timeout_sec (:obj:`int`): Timeout to wait for validation, in seconds.
                Default: :py:const:`streamsets.sdk.st.DEFAULT_VALIDATE_TIMEOUT`.
        """
        timeout_sec = kwargs.get('timeout_sec', DEFAULT_VALIDATE_TIMEOUT)
        logger.info('Validating pipeline %s ...', pipeline.id)
        validate_command = self.api_client.validate_pipeline(pipeline_id=pipeline.id,
                                                             timeout_sec=timeout_sec).wait_for_validate()
        response = validate_command.response.json()
        if response['status'] != 'VALID':
            if 'issues' in response and response['issues']:
                raise ValidationError(response['issues'])
            elif 'message' in response:
                raise ValidationError(response['message'])
            else:
                raise ValidationError('Unknown validation failure with status as {}'.format(response['status']))

    @_dump_st_log_on_error
    def start_pipeline(self, pipeline, runtime_parameters=None, **kwargs):
        """Start a pipeline.

        Args:
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.
            runtime_parameters (:obj:`dict`, optional): Collection of runtime parameters. Default: ``None``.
            wait (:obj:`bool`, optional): Wait for pipeline to start. Default: ``True``.
            wait_for_statuses (:obj:`list`, optional): Pipeline statuses to wait on.
                Default: ``['RUNNING', 'FINISHED']``.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.PipelineCommand`.
        """
        issues = self.api_client.get_pipeline_configuration(pipeline_id=pipeline.id)['issues']
        if issues['issueCount']:
            raise ValidationError(issues)

        logger.info('Starting pipeline %s ...', pipeline.id)
        pipeline_command = self.api_client.start_pipeline(pipeline_id=pipeline.id,
                                                          runtime_parameters=runtime_parameters)
        if kwargs.get('wait', True):
            pipeline_command.wait_for_status(status=kwargs.get('wait_for_statuses',
                                                               DEFAULT_START_STATUSES_TO_WAIT_FOR))

        return pipeline_command

    @_dump_st_log_on_error
    def stop_pipeline(self, pipeline, **kwargs):
        """Stop a pipeline.

        Args:
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.
            force (:obj:`bool`, optional): Force pipeline to stop. Default: ``False``.
            wait (:obj:`bool`, optional): Wait for pipeline to stop. Default: ``True``.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.StopPipelineCommand`.
        """
        logger.info('Stopping pipeline %s...', pipeline.id)
        stop_command = self.api_client.stop_pipeline(pipeline_id=pipeline.id)

        if kwargs.get('force', False):
            # Note: Pipeline force stop is applicable only after a pipeline stop.
            stop_command = self.api_client.force_stop_pipeline(pipeline_id=pipeline.id)

        if kwargs.get('wait', True):
            stop_command.wait_for_stopped()

        return stop_command

    @_dump_st_log_on_error
    def run_pipeline_preview(self, pipeline, rev=0, batches=1, batch_size=10, skip_targets=True, end_stage=None,
                             timeout=2000, stage_outputs_to_override_json=None, **kwargs):
        """Run pipeline preview.

        Args:
            pipeline (:obj:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.
            rev (:obj:`int`, optional): Pipeline revision. Default: ``0``.
            batches (:obj:`int`, optional): Number of batches. Default: ``1``.
            batch_size (:obj:`int`, optional): Batch size. Default: ``10``.
            skip_targets (:obj:`bool`, optional): Skip targets. Default: ``True``.
            end_stage (:obj:`str`, optional): End stage. Default: ``None``.
            timeout (:obj:`int`, optional): Timeout. Default: ``2000``.
            stage_outputs_to_override_json (:obj:`str`, optional): Stage outputs to override. Default: ``None``.
            wait (:obj:`bool`, optional): Wait for pipeline preview to finish. Default: ``True``.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.PreviewCommand`.
        """
        logger.info('Running preview for %s...', pipeline.id)
        preview_command = self.api_client.run_pipeline_preview(pipeline.id, rev, batches,
                                                               batch_size, skip_targets, end_stage,
                                                               timeout, stage_outputs_to_override_json)
        if kwargs.get('wait', True):
            preview_command.wait_for_finished()

        return preview_command

    @_dump_st_log_on_error
    def get_snapshots(self, pipeline=None):
        """Get information about stored snapshots.

        Args:
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`, optional): The pipeline instance.
                Default: ``None``.

        Returns:
            A list of :py:class:`streamsets.sdk.st_models.SnapshotInfo` instances.
        """
        snapshots = [st_models.SnapshotInfo(info) for info in self.api_client.get_snapshots()]
        return snapshots if not pipeline else [info for info in snapshots if info['name'] == pipeline.id]

    @_dump_st_log_on_error
    def capture_snapshot(self, pipeline, snapshot_name=None, start_pipeline=False,
                         runtime_parameters=None, batches=1, batch_size=10, **kwargs):
        """Capture a snapshot for given pipeline.

        Args:
            pipeline (:obj:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.
            snapshot_name (:obj:`str`, optional): Name for the generated snapshot. If set to ``None``,
                an auto-generated UUID (which can be recovered from the returned ``SnapshotCommand``
                object's ``snapshot_name`` attribute) will be used when calling the REST API. Default: ``None``.
            start_pipeline (:obj:`bool`, optional): If set to true, then the pipeline will be
                started and its first batch will be captured. Otherwise, the pipeline must be
                running, in which case one of the next batches will be captured. Default: ``False``.
            runtime_parameters (:obj:`dict`, optional): Runtime parameters to override Pipeline Parameters value.
                Default: ``None``.
            wait (:obj:`bool`, optional): Wait for capture snapshot to finish. Default: ``True``.
            wait_for_statuses (:obj:`list`, optional): Pipeline statuses to wait on.
                Default: ``['RUNNING', 'FINISHED']``.
            timeout_sec (:obj:`int`): Timeout to wait for snapshot, in seconds.
                Default: :py:const:`streamsets.sdk.st.DEFAULT_SNAPSHOT_TIMEOUT`.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.SnapshotCommand`.
        """
        timeout_sec = kwargs.get('timeout_sec', DEFAULT_SNAPSHOT_TIMEOUT)
        logger.info('Capturing snapshot (%d batches of size %d, timeout %d seconds) for %s...', batches, batch_size,
                    timeout_sec, pipeline.id)
        snapshot_command = self.api_client.capture_snapshot(pipeline_id=pipeline.id,
                                                            snapshot_name=snapshot_name or str(uuid4()),
                                                            start_pipeline=start_pipeline,
                                                            runtime_parameters=runtime_parameters,
                                                            batches=batches, batch_size=batch_size)
        if start_pipeline:
            status_command = self.api_client.get_pipeline_status(pipeline_id=pipeline.id)
            status_command.wait_for_status(status=kwargs.get('wait_for_statuses',
                                                             DEFAULT_START_STATUSES_TO_WAIT_FOR))

        if kwargs.get('wait', True):
            snapshot_command.wait_for_finished(timeout_sec)

        return snapshot_command

    @_dump_st_log_on_error
    def get_pipeline_acl(self, pipeline):
        """Get pipeline ACL.

        Args:
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.PipelineAcl`.
        """
        return st_models.PipelineAcl(self.api_client.get_pipeline_acl(pipeline_id=pipeline.id))

    @_dump_st_log_on_error
    def set_pipeline_acl(self, pipeline, pipeline_acl):
        """Update pipeline ACL.

        Args:
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.
            pipeline_acl (:py:class:`streamsets.sdk.st_models.PipelineAcl`): The pipeline ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`.
        """
        return self.api_client.set_pipeline_acl(pipeline_id=pipeline.id, pipeline_acl_json=pipeline_acl._data)

    @_dump_st_log_on_error
    def get_pipeline_permissions(self, pipeline):
        """Return pipeline permissions for a given pipeline.

        Args:
            pipeline (:obj:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.PipelinePermissions`.
        """
        return st_models.PipelinePermissions(self.api_client.get_pipeline_permissions(pipeline_id=pipeline.id))

    @_dump_st_log_on_error
    def get_pipeline_status(self, pipeline):
        """Get status of a pipeline.

        Args:
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.
        """
        logger.info('Getting status of pipeline %s...', pipeline.id)
        return self.api_client.get_pipeline_status(pipeline_id=pipeline.id)

    @_dump_st_log_on_error
    def get_pipeline_history(self, pipeline):
        """Get a pipeline's history.

        Args:
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.History`.
        """
        logger.info('Getting pipeline history for %s...', pipeline.id)
        return st_models.History(self.api_client.get_pipeline_history(pipeline_id=pipeline.id))

    @_dump_st_log_on_error
    def get_pipeline(self, pipeline_id):
        """Get a pipeline.

        Args:
            pipeline_id (:obj:`str`): Id of pipeline.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.Pipeline`.
        """
        exported_pipeline = self.api_client.export_pipeline(pipeline_id=pipeline_id)
        builder = self.get_pipeline_builder()
        builder.import_pipeline(exported_pipeline)
        return builder.build(title=exported_pipeline['pipelineConfig']['title'])

    @property
    def current_user(self):
        """Get currently logged-in user and its groups and roles.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.User`.
        """
        logger.info('Getting current user ...')
        return st_models.User(self.api_client.get_current_user())

    def get_logs(self, ending_offset=-1, extra_message=None, pipeline=None, severity=None):
        """Get logs.

        Args:
            ending_offset (:obj:`int`): ending_offset, Default: ``-1``.
            extra_message (:obj:`str`): extra_message, Default: ``None``.
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): The pipeline instance, Default: ``None``.
            severity (:obj:`str`): severity, Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.Log`.
        """
        pipeline_id = pipeline.id if pipeline is not None else None
        return st_models.Log(self.api_client.get_logs(ending_offset, extra_message,
                                                      pipeline_id, severity))

    def get_alerts(self):
        """Get pipeline alerts.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.Alerts`.
        """
        return st_models.Alerts(self.api_client.get_alerts())

    @_dump_st_log_on_error
    def get_bundle_generators(self):
        """Get available support bundle generators.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.BundleGenerators`.
        """
        return st_models.BundleGenerators(self.api_client.get_bundle_generators())

    @_dump_st_log_on_error
    def get_bundle(self, generators=None):
        """Generate new support bundle.

        Returns:
            An instance of :py:class:`zipfile.ZipFile`.
        """
        return self.api_client.get_bundle(generators)
