

MQ_COORDINATOR_EXCHANGE = 'coordinator'
MQ_COORDINATOR_EXCHANGE_TYPE = 'topic'
MQ_COORDINATOR_QUEUE = 'micropipes.coordinator'

MQ_WORKER_REGISTER = 'worker.register'
MQ_WORKER_REGISTERED_ID = 'worker.registered_id'
MQ_WORKER_UNREGISTER = 'worker.unregister'
MQ_WORKER_READY_FOR_JOB_START = 'worker.ready4jobstart'
MQ_WORKER_HEARTBEAT = 'worker.hearbeat'
MQ_WORKER_UNREGISTERED = 'worker.unregistered'
MQ_WORKER_USE_CAPACITY = 'worker.use.capacity'
MQ_WORKER_FREE_CAPACITY = 'worker.free.capacity'

MQ_JOB_FINISH_REQUEST = 'job.finish_request'
MQ_JOB_CANCEL_REQUEST = 'job.cancel_request'
MQ_JOB_START_REQUEST = 'job.start_request'
MQ_JOB_STOP_REQUEST = 'job.stop_request'
MQ_JOB_STOP_FORCED_REQUEST = 'job.stop_forced_request'
MQ_JOB_SUBMIT_REQUEST = 'job.submit.request'
MQ_JOB_SUBMIT_REQUESTED_ID = 'job.submit.requested_id'
MQ_JOB_EDIT_REQUEST = 'job.edit.request'
MQ_JOB_DELETE_REQUEST = 'job.delete.request'
MQ_JOB_REQUEST_CAPACITY = 'job.get.capacity'
MQ_JOB_FREE_CAPACITY = 'job.free.capacity'

MQ_COORDINATOR_BINDINGS = [MQ_WORKER_REGISTER, MQ_WORKER_UNREGISTER , MQ_WORKER_FREE_CAPACITY, MQ_WORKER_USE_CAPACITY,
                           MQ_WORKER_READY_FOR_JOB_START, MQ_WORKER_HEARTBEAT,
                           MQ_JOB_FINISH_REQUEST , MQ_JOB_START_REQUEST ,
                           MQ_JOB_CANCEL_REQUEST,  MQ_JOB_SUBMIT_REQUEST, MQ_JOB_EDIT_REQUEST,
                           MQ_JOB_DELETE_REQUEST, MQ_JOB_STOP_REQUEST, MQ_JOB_STOP_FORCED_REQUEST,
                           MQ_JOB_REQUEST_CAPACITY, MQ_JOB_FREE_CAPACITY ]

MQ_JOB_ASSIGN = 'job.assign'
MQ_JOB_UNASSIGN = 'job.unassign'
MQ_JOB_STATUS = 'job.status'
MQ_COORDINATOR_WORKER_BINDINGS = [MQ_JOB_ASSIGN, MQ_JOB_UNASSIGN, MQ_JOB_STATUS ]

JOB_STATUS_WAIT = 'status.wait'
JOB_STATUS_WAIT_PENDING = 'status.wait.pending'
JOB_STATUS_START_PENDING = 'status.start.pending'
JOB_STATUS_STARTED = 'status.started'
JOB_STATUS_FINISHED = 'status.finished'
JOB_STATUS_CANCELED = 'status.canceled'
JOB_STATUS_STOP = 'status.stop'
JOB_STATUS_STOP_PENDING = 'status.stop.pending'

WORKER_STATUS_UNKNOWN = 'status.unknown'
WORKER_STATUS_REGISTERED = 'status.registered'
WORKER_STATUS_UNREGISTERING = 'status.unregistering'

JOB_START_DATA = 'job.start.data'
JOB_FINISH_DATA = 'job.finish.data'

MQ_DATA_EXCHANGE = 'data'
MQ_DATA_EXCHANGE_TYPE = 'topic'

HEARTBEAT_CHECK_INTERVAL = 10
HEARTBEAT_DIFF = 120.0
HEARTBEAT_DIFF_ZOMBIE = HEARTBEAT_DIFF*15
HEARTBEAT_SEND_INTERVAL = HEARTBEAT_DIFF/4

CUSTOMER_ID_HEADER = 'customer_id'

# s tymto velmi opatrne
LOCK_BLOCKING_TIMEOUT = HEARTBEAT_CHECK_INTERVAL-1  # 9s
SMALL_LOCK_BLOCKING_TIMEOUT = LOCK_BLOCKING_TIMEOUT/30 # 0.3s
# nesmie byt 0, pretoze objekt moze zostat uzamknuty navzdy
# v tom pripade treba lock natvrdo vymazat z redisu ( dohladat ten lock - vid DISTRIBUTED_LOCK_KEY_FORMAT)
LOCK_TTL = LOCK_BLOCKING_TIMEOUT * 3  # 27s

JOB_PENDING_START_TIMEOUT = 20 # 20s
JOB_WAIT_REPEAT = JOB_PENDING_START_TIMEOUT * 30
JOB_PENDING_LOCKED_TIMEOUT = JOB_PENDING_START_TIMEOUT *3


STATS_LOG_INTERVAL = 60*60