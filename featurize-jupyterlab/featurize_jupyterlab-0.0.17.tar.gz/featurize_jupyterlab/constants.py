from .proto import minetorch_pb2


COMMAND_TRAIN = minetorch_pb2.YoMessage.Command.Value('TRAIN')
COMMAND_HALT = minetorch_pb2.YoMessage.Command.Value('HALT')
COMMAND_KILL = minetorch_pb2.YoMessage.Command.Value('KILL')
COMMAND_NONE = minetorch_pb2.YoMessage.Command.Value('NONE')

STATUS_TRAINING = minetorch_pb2.HeyMessage.Status.Value('TRAINING')
STATUS_IDLE = minetorch_pb2.HeyMessage.Status.Value('IDLE')
STATUS_ERROR = minetorch_pb2.HeyMessage.Status.Value('ERROR')
STATUS_NOT_RUNNING = minetorch_pb2.HeyMessage.Status.Value('NOT_RUNNING')
STATUS_BOOTING = minetorch_pb2.HeyMessage.Status.Value('BOOTING')
STATUS_STARTING = minetorch_pb2.HeyMessage.Status.Value('STARTING')
STATUS_STOPPING = minetorch_pb2.HeyMessage.Status.Value('STOPPING')
STATUS_KILLING = minetorch_pb2.HeyMessage.Status.Value('KILLING')
