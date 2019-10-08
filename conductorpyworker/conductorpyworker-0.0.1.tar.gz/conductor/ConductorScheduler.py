from __future__ import print_function, absolute_import
from conductor.conductor import WFClientMgr
from multiprocessing import Process, Event
import socket

hostname = socket.gethostname()


class ConductorScheduler(object):
    def __init__(self, server_url, worker_id=None):
        wfcMgr = WFClientMgr(server_url)
        self.workflowClient = wfcMgr.workflowClient
        self.taskClient = wfcMgr.taskClient
        self.worker_id = worker_id if worker_id is not None else hostname

    def poll(self, taskType):
        """
        taskType: str

        rtype
        polled: Dict[str, str]

        polled example:
        {
            "taskType": "task_1",
            "status": "IN_PROGRESS",
            "inputData": {
                "mod": null,
                "oddEven": null
            },
            "referenceTaskName": "task_1",
            "retryCount": 0,
            "seq": 1,
            "pollCount": 1,
            "taskDefName": "task_1",
            "scheduledTime": 1486580932471,
            "startTime": 1486580933869,
            "endTime": 0,
            "updateTime": 1486580933902,
            "startDelayInSeconds": 0,
            "retried": false,
            "callbackFromWorker": true,
            "responseTimeoutSeconds": 3600,
            "workflowInstanceId": "b0d1a935-3d74-46fd-92b2-0ca1e388659f",
            "taskId": "b9eea7dd-3fbd-46b9-a9ff-b00279459476",
            "callbackAfterSeconds": 0,
            "polledTime": 1486580933902,
            "queueWaitTime": 1398
        }
        """
        polled =  self.taskClient.pollForTask(taskType, self.worker_id)
        self.task = polled
        return polled

    def ack_task(self, taskId):
        self.taskClient.ackTask(taskId, self.worker_id)

    def update(self, task, status='COMPLETED'):
        """
        task: Dict[str, str]
        status: str - IN_PROGRESS|FAILED|COMPLETED

        task schema:
        {
            "workflowInstanceId": "Workflow Instance Id",
            "taskId": "ID of the task to be updated",
            "reasonForIncompletion" : "If failed, reason for failure",
            "callbackAfterSeconds": 0,
            "outputData": {
                //JSON document representing Task execution output     
            }
        }
        """
        task['status'] = status
		task['workerId'] = self.worker_id
        self.taskClient.updateTask(task)
