from . import constants as C
from .logger import get_runtime_logger

from .proto import minetorch_pb2, minetorch_pb2_grpc
from .experiment import Experiment


class MinetorchServicer(minetorch_pb2_grpc.MinetorchServicer):

    # TODO: performance of rpc server
    caches = {}

    def CreateGraph(self, request, context):
        # TODO: duplicate checking
        experiment = Experiment(request.identity)
        experiment.create_graph(request.graph_name)
        return minetorch_pb2.StandardResponse(
            status=0,
            message='ok'
        )

    def AddPoint(self, request, context):
        # TODO: performance
        experiment = Experiment(request.identity)
        experiment.add_point(request.graph_name, {'x': request.x, 'y': request.y})
        return minetorch_pb2.StandardResponse(
            status=0,
            message='ok'
        )

    def SendLog(self, request, context):
        # TODO: performance
        logger = get_runtime_logger(request.identity)
        getattr(logger, request.level.lower())(request.log)
        return minetorch_pb2.StandardResponse(
            status=0,
            message='ok'
        )

    def HeyYo(self, request, context):
        experiment = Experiment(request.identity)
        metadata = experiment.get_metadata()

        agent_status = request.status
        server_status = getattr(C, f"status_{metadata['status']}".upper())

        # Priority of status: Server Verb status > agent_status > server_status
        # TODO: find a way to set the status as not_running
        if server_status == C.STATUS_STARTING and agent_status == C.STATUS_IDLE:
            command = C.COMMAND_TRAIN
        elif server_status == C.STATUS_STOPPING and agent_status == C.STATUS_TRAINING:
            command = C.COMMAND_HALT
        elif server_status == C.STATUS_KILLING and agent_status == C.STATUS_IDLE:
            command = C.COMMAND_KILL
        else:
            experiment.update_metadata({
                'status': minetorch_pb2.HeyMessage.Status.Name(agent_status).lower()
            })
            command = C.COMMAND_NONE

        return minetorch_pb2.YoMessage(
            roger=True,
            command=command
        )
