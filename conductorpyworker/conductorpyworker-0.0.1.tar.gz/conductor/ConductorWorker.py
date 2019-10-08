#
#  Copyright 2017 Netflix, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from __future__ import print_function, absolute_import
import sys
import time
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from conductor.conductor import WFClientMgr
from multiprocessing import Process, Event
import socket 

hostname = socket.gethostname()


class WorkerExit(Exception):
    pass


class ConductorWorker(object):
    def __init__(self, server_url, polling_interval, worker_id=None, domain=None):
        wfcMgr = WFClientMgr(server_url)
        self.msg_slot = None
        self.workflowClient = wfcMgr.workflowClient
        self.taskClient = wfcMgr.taskClient
        self.polling_interval = polling_interval
        self.worker_id = worker_id if worker_id is not None else hostname
        self.domain = domain

    def execute(self, task, exec_function, *args, **kwargs):
        try:
            resp = exec_function(task, *args, **kwargs)
            if resp is None:
                raise Exception('Task execution function MUST return a response as a dict with status and output fields')
            task['status'] = resp['status']
            task['outputData'] = resp['output']
            task['logs'] = resp['logs']
            if resp.get('reasonForIncompletion') is not None:
                task['reasonForIncompletion'] = resp['reasonForIncompletion']
            self.taskClient.updateTask(task)
            print("task with id {} done".format(task['taskId']))
        except Exception as err:
            print('Error executing task: ' + str(err))
            task['status'] = 'FAILED'
            print("ERRROR:>>")
            print(str(err))
            task['reasonForIncompletion'] = str(err) + self.domain if self.domain else str(err) + str(self.worker_id) 
            self.taskClient.updateTask(task)
            print("task with id {} failed".format(task['taskId']))

    def close(self):
        self.msg_slot = WorkerExit

    def poll_and_execute(self, taskType, exec_function, *args, **kwargs):
        while True:
            time.sleep(float(self.polling_interval))
            polled = self.taskClient.pollForTask(taskType, self.worker_id, self.domain) if self.domain else self.taskClient.pollForTask(taskType, self.worker_id)
            if self.msg_slot is WorkerExit:
                raise WorkerExit()
            if polled is not None:
                print("polled task with id {}".format(polled['taskId']))
                self.taskClient.ackTask(polled['taskId'], self.worker_id)
                self.execute(polled, exec_function, *args, **kwargs)

    def _bootstrap(self, taskType, exec_function, *args, **kwargs):
        try:
            self.poll_and_execute(taskType, exec_function, *args, **kwargs)
        except WorkerExit:
            pass
        finally:
            self._terminated.set()

    def join(self):
        self._terminated.wait()

    def start(self, taskType, exec_function, args=(), kwargs={}):
        """
        there is no shared data between processes, thus you can call this method
        as many times as you want without worrying at safty.
        """
        self._terminated = Event()
        print('Polling for task ' + taskType + ' at a ' + str(self.polling_interval) + ' ms interval with worker id as ' + str(self.worker_id))
        unit = Process(target=self._bootstrap, args=(taskType, exec_function, )+tuple(args), kwargs=dict(kwargs))
        unit.daemon = True
        unit.start()
