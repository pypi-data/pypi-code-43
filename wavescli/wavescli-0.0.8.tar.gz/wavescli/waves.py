# -*- coding: utf-8 -*-
import tempfile
import os
import shutil

from celery import Celery
from celery.signals import before_task_publish

from kombu import Exchange, Queue

from wavescli.config import get_config
from wavescli.awsadapter import send_file, public_url
from wavescli.downloader import get_file


config = get_config()

app = Celery(config.WAVES_CLI_NAME)

# Atencao: pegar mais de 1 mensagem por vez pode ter perda
#          caso o container morra antes de processar todas
app.conf.broker_url = config.BROKER_URL
app.conf.result_backend = config.RESULT_BACKEND_URL
app.conf.worker_prefetch_multiplier = 1

app.conf.worker_send_task_events = True
app.conf.task_track_started = True
app.conf.task_send_sent_event = True
# app.conf.task_acks_late = 1

app.conf.task_queues = (
    Queue(config.QUEUE_NAME,
          Exchange(config.QUEUE_NAME),
          routing_key=config.QUEUE_NAME),
)

BaseTask = app.create_task_cls()


def get_celery_app():
    return app


class Values(object):
    pass


def send_update_execution(
        identifier, task_id, task_name, task_root_id,
        task_parent_id, status=None, inputs=None, args=None, results=None):
    """
    Envia para fila default
    """
    _4seconds = 4
    params = (
        identifier,
        task_id,
        task_name,
        task_root_id,
        task_parent_id,
        status,
        inputs,
        args,
        results,
    )
    sig_status = app.signature(
        'awebrunner.update_execution',
        args=params,
        kwargs={},
        queue='celery',
    )
    sig_status.apply_async(countdown=_4seconds)


@before_task_publish.connect
def task_updated(sender=None, headers=None, body=None, **kwargs):
    """
    - Atualizacao de status de tasks existentes
    - Cria tasks em tempo de execucao
    """
    task_name = headers.get('task')
    task_id = headers.get('id')

    if task_name == 'awebrunner.update_execution':
        return

    args_data, kwargs_data, signatures = body
    identifier = kwargs_data.get('identifier')
    task_root_id = headers.get('root_id')
    task_parent_id = headers.get('parent_id')

    send_update_execution(
        identifier=identifier,
        task_id=task_id,
        task_name=task_name,
        task_root_id=task_root_id,
        task_parent_id=task_parent_id,
        inputs=args_data,
        args=kwargs_data,)


@app.task(name='waves.ping')
def task_ping(seconds=10):
    import time
    time.sleep(seconds)
    return "pong"


class WavesBaseTask(BaseTask):
    """Abstract base class for all tasks in my app."""

    abstract = True

    def _initialize(self):
        self._clean_attrs()
        self.inputs = Values()
        self.outputs = Values()

    def _clean_attrs(self):
        for attr in ['call_updated', 'downloaded', 'uploaded', 'on_success_updated']:
            try:
                delattr(self, attr)
            except Exception:
                pass

    def _generate_task_attributes(self, args, kwargs):
        results, inputs = args
        if inputs.get('inputs'):
            inputs = inputs.get('inputs')
        self.inputs_values = inputs
        if results is not None:
            self.inputs_values = results

        self.outputs_values = kwargs.get('outputs', {})
        self.auto_download = kwargs.get('auto_download', [])
        self.auto_upload = kwargs.get('auto_upload', [])
        self.make_public = kwargs.get('make_public', [])
        self.identifier = kwargs.get('identifier')
        self.bucket = kwargs.get('bucket')

        self.task_id = self.request.id
        self.task_dir = os.path.join(tempfile.gettempdir(), self.task_id)
        self.inputs_dir = os.path.join(self.task_dir, 'inputs')
        self.outputs_dir = os.path.join(self.task_dir, 'outputs')

    def _download_inputs(self):
        if type(self.inputs_values) != dict:
            return

        for item in self.inputs_values.keys():
            self.inputs.__setattr__(item, self.inputs_values.get(item))
            if item not in self.auto_download:
                continue
            try:
                local_file = get_file(
                    self.inputs_values[item], self.inputs_dir)
                self.inputs.__setattr__(item, local_file)

            except Exception as error:
                raise RuntimeError('Error downloading: {}'.format(self.inputs_values.get(item)), error)
        self.downloaded = True

    def _upload_outputs(self, outputs, target):
        for item in self.auto_upload:
            try:
                local_file_path = self._replace_vars(outputs[item])

                filename = os.path.basename(local_file_path)
                remote_path = '{}/{}'.format(target, filename)
                remote_file = send_file(
                    local_file_path, self.bucket, remote_path)
                outputs[item] = remote_file

                if item in self.make_public:
                    outputs['{}_public'.format(item)] = public_url(remote_file)

            except Exception as error:
                raise RuntimeError('Error uploading: {}'.format(local_file_path), error)
        self.uploaded = True
        return outputs

    def _get_task_state(self):
        if self.request.id:
            return str(app.AsyncResult(self.request.id).state)

    def _update_execution(self, identifier, task_id,
                          inputs=None, params=None, result=None, status=None):
        if not status:
            status = self._get_task_state()

        send_update_execution(
            identifier=identifier,
            task_id=task_id,
            task_name=self.request.task,
            task_root_id=self.request.root_id,
            task_parent_id=self.request.parent_id,
            status=status,
            inputs=inputs,
            args=params,
            results=result)

    def _create_temp_task_folders(self):
        os.makedirs(self.inputs_dir)
        os.makedirs(self.outputs_dir)

    def _delete_temp_task_folders(self):
        shutil.rmtree(self.task_dir)

    def _get_env_variables(self, kwargs):
        env = kwargs.get('env', {})
        env['TASK_ID'] = self.request.id
        env['INPUTS_DIR'] = self.inputs_dir
        env['OUTPUTS_DIR'] = self.outputs_dir
        env['IDENTIFIER'] = self.identifier
        env['BUCKET'] = self.bucket
        return env

    def __call__(self, *args, **kwargs):
        self._initialize()
        self._generate_task_attributes(args, kwargs)

        if not hasattr(self, 'downloaded'):
            self._create_temp_task_folders()
            self._download_inputs()
        return super(WavesBaseTask, self).__call__(*args, **kwargs)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        super(WavesBaseTask, self).on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # TODO
        super(WavesBaseTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def send_auto_upload_outputs(self, delete_temp_folders=True):
        if hasattr(self, 'uploaded'):
            return self.results

        target = '{}/{}'.format(self.identifier, self.task_id)
        self.results = self._upload_outputs(self.results, target)

        if delete_temp_folders:
            self._delete_temp_task_folders()
        return self.results

    def on_success(self, retval, task_id, args, kwargs):
        if not hasattr(self, 'results'):
            self.results = retval

        results = self.results
        if not hasattr(self, 'on_success_updated'):
            self._update_execution(
                kwargs['identifier'], self.request.id, result=results)
        super(WavesBaseTask, self).on_success(results, task_id, args, kwargs)

    def _replace_vars(self, text):
        if type(self.inputs_values) == dict:
            for item in self.inputs_values.keys():
                if self.inputs_values[item]:
                    original = '${{ ' + 'inputs.{}'.format(item) + ' }}'
                    text = text.replace(original, self.inputs.__getattribute__(item))

        if type(self.outputs_values) == dict:
            for item in self.outputs_values.keys():
                if self.outputs_values[item]:
                    original = '${{ ' + 'outputs.{}'.format(item) + ' }}'
                    text = text.replace(original, self.outputs_values[item])
        return text
