import logging
from google.protobuf import timestamp_pb2
from wf.pipeline.api import common_pb2
from wf.pipeline.api import experiment_pb2
from wf.pipeline.api import experiment_pb2_grpc
from kubernetes import client
from .error import LoopError
from .pipeline import run_pipeline, get_pipeline_status, delete_experiment, delete_job


app_log = logging.getLogger("wfp")


class ExperimentService(experiment_pb2_grpc.ExperimentServiceServicer):

    @classmethod
    def add_to_server(cls, server):
        """注册该服务到server中

        :param server: server对象
        :return:
        """
        app_log.debug('add ExperimentService to server')
        experiment_pb2_grpc.add_ExperimentServiceServicer_to_server(
            ExperimentService(), server)

    def Run(self, request, context):
        """
        Run an experiment
        """
        try:
            app_log.debug(
                'Run experiment name: {0}, job name: {1}'.format(
                    request.experiment_name,
                    request.job_name))

            job_id, exp_id = run_pipeline(request.experiment_name,
                                          request.experiment_description,
                                          request.job_name,
                                          request.nodes)
        except LoopError as e:
            return experiment_pb2.ExperimentRunResponse(
                code=common_pb2.ERROR_GRAPH_LOOPBACK,
                message=str(e))
        except Exception as e:
            app_log.warning(
                'Run experiment exception, experiment name: {0}, job name: {1}, exception: {2}'.format(
                    request.experiment_name, request.job_name, str(e)))

            return experiment_pb2.ExperimentRunResponse(
                code=common_pb2.ERROR_RUNTIME_EXCEPTION,
                message=str(e))

        return experiment_pb2.ExperimentRunResponse(
            code=common_pb2.OK,
            message='成功',
            job_id=job_id,
            exp_id=exp_id)

    def GetStatus(self, request, context):
        """
        Get status of an experiment
        """
        try:
            status_lookup = {
                "pending": common_pb2.PENDING,
                "running": common_pb2.RUNNING,
                "succeeded": common_pb2.SUCCEEDED,
                "skipped": common_pb2.SKIPPED,
                "failed": common_pb2.FAILED,
                "error": common_pb2.ERROR}

            workflow = get_pipeline_status(request.job_id)
            workflow_status = workflow['status']

            # 任务尚未开始
            if not workflow_status['startedAt'] and not workflow_status['finishedAt']:
                return experiment_pb2.ExperimentStatusResponse(
                    code=common_pb2.ERROR_WORKFLOW_PENDING,
                    message='实验运行尚未开始，请稍后重试')

            node_metrics = []
            for node_id, node in workflow_status['nodes'].items():
                nm = common_pb2.NodeMetric(
                    id=node['id'],
                    name=node['name'],
                    type=node['type'],
                    display_name=node['displayName'],
                    template_name=node['templateName'],
                    status=status_lookup[node['phase'].lower()])

                if node['startedAt']:
                    started_at = timestamp_pb2.Timestamp()
                    started_at.FromJsonString(node['startedAt'])
                    nm.started_at.CopyFrom(started_at)

                if node['finishedAt']:
                    finished_at = timestamp_pb2.Timestamp()
                    finished_at.FromJsonString(node['finishedAt'])
                    nm.finished_at.CopyFrom(finished_at)

                if 'message' in node:
                    nm.message = node['message']

                node_metrics.append(nm)

            response = experiment_pb2.ExperimentStatusResponse(
                code=common_pb2.OK,
                message='成功',
                status=status_lookup[workflow_status['phase'].lower()],
                node_metrics=node_metrics)

            if workflow_status['startedAt']:
                started_at = timestamp_pb2.Timestamp()
                started_at.FromJsonString(workflow_status['startedAt'])
                response.started_at.CopyFrom(started_at)

            if workflow_status['finishedAt']:
                finished_at = timestamp_pb2.Timestamp()
                finished_at.FromJsonString(workflow_status['finishedAt'])
                response.finished_at.CopyFrom(finished_at)

        except Exception as e:
            app_log.warning(
                'Query job status exception, job id: {0}, exception: {1}'.format(
                    request.job_id, str(e)))

            response = experiment_pb2.ExperimentStatusResponse(
                code=common_pb2.ERROR_RUNTIME_EXCEPTION,
                message=str(e))

        return response

    def GetNodeLog(self, request, context):
        """获取节点运行日志
        """
        try:
            namespace = request.namespace if request.namespace else 'kubeflow'

            api_client = client.CoreV1Api()
            logs = api_client.read_namespaced_pod_log(
                name=request.pod_id, namespace=namespace, container='main')

            response = experiment_pb2.NodeLogResponse(
                code=common_pb2.OK,
                message='成功',
                log=logs)
        except Exception as e:
            app_log.warning(
                'Query node log exception, pod: {0}, exception: {1}'.format(
                    request.pod_id, str(e)))

            response = experiment_pb2.NodeLogResponse(
                code=common_pb2.ERROR_RUNTIME_EXCEPTION,
                message=str(e))

        return response

    def DeleteExperiment(self, request, context):
        """删除实验
        """
        try:
            delete_experiment(request.id)

            response = experiment_pb2.ExperimentDeleteResponse(
                code=common_pb2.OK,
                message='成功')
        except Exception as e:
            app_log.warning(
                'delete experiment exception, experiment id: {0}, exception: {1}'.format(
                    request.id, str(e)))

            response = experiment_pb2.ExperimentDeleteResponse(
                code=common_pb2.ERROR_RUNTIME_EXCEPTION,
                message=str(e))

        return response

    def DeleteJob(self, request, context):
        """删除实验任务
        """
        try:
            delete_job(request.id)

            response = experiment_pb2.JobDeleteResponse(
                code=common_pb2.OK,
                message='成功')
        except Exception as e:
            app_log.warning(
                'delete job exception, job id: {0}, exception: {1}'.format(
                    request.id, str(e)))

            response = experiment_pb2.JobDeleteResponse(
                code=common_pb2.ERROR_RUNTIME_EXCEPTION,
                message=str(e))

        return response
