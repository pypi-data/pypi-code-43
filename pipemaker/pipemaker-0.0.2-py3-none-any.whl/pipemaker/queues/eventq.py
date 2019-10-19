from .rabbitq import Rabbitq
import base64
import multiprocess as mp
import logging
log = logging.getLogger()

# fired when all tasks finished to notify calling mastertask
onCompleteAll = mp.Event()

class Eventq(Rabbitq):
    """ queue for processing events from workers

    * tasks from any worker_process can put events on the eventq
    * listener actions  the events e.g. updates the central database, launches jobs that were waiting
    * one eventq listener is safest to avoid database conflicts e.g. tasks added to taskq twice
    """
    name = "event_queue"

    def listen(self, onCompleteAll):
        # only needed for consumer
        from ..master.db import db
        from .taskq import Taskq

        self.onCompleteAll = onCompleteAll
        self.db = db
        self.taskq = Taskq()
        super().listen()

    def onGet(self, ch, method, properties, body):
        """ pass event to handler

        :param body: dotdict with time, event, process, output
        """
        try:
            body = self.decode(body)
            if body == self.STOP:
                self.onStop(method)
                return
            #log.info((body.event, body.url, body.process))
            getattr(self, body.event, self.onEvent)(body)
        except:
            log.exception("Error processing event")
        finally:
            self.db.commit()
            self.channel.basic_ack(delivery_tag=method.delivery_tag)

    # handlers ####################################################

    def onEvent(self, body):
        log.error(f"unassigned event {body}")

    def onRunning(self, body):
        db = self.db
        db(db.task.url==body.url).update(status="running", process=body.process, started=body.time, finished=None)

    def onProgress(self, body):
        db = self.db
        db(db.task.url == body.url).update(progress=int(body.progress))

    def onComplete(self, body):
        db = self.db

        # update the task on db and release any downstream
        db(db.task.url==body.url).update(status="completed", finished=body.time, progress=100)
        db(db.waiting.awaiting==body.url).delete()
        # commit to enable queries below
        db.commit()

        # signal all complete
        if not set([task.status for task in db(db.task.status).select(db.task.status)]) \
                        - set(["completed", "failed", "failed_upstream"]):
            self.onCompleteAll.set()
            return

        # run any tasks that can now run
        waitingtasks = [t.id for t in db(db.task.status == "waiting").select()]
        notready = [t.task for t in db(db.waiting).select()]
        ready = set(waitingtasks) - set(notready)
        for taskid in ready:
            task = db.task[taskid]
            task.update_record(status="ready")
            task = base64.b64decode(task.task)
            self.taskq.put(task, encoded=True)

    def onError(self, body):
        db = self.db
        db(db.task.url==body.url).update(status="failed", detail=str(body.exception))
        self.fail_downstream(body.url)

        # signal all complete
        if not set([task.status for task in db(db.task.status).select(db.task.status)]) \
               - set(["completed", "failed", "failed_upstream"]):
            self.onCompleteAll.set()
            return

    def fail_downstream(self, url):
        """ recursively fail all downstream tasks """
        db = self.db
        for w in db(db.waiting.awaiting == url).select():
            db(db.task.id==w.task).update(status="failed_upstream", details=url)
            self.fail_downstream(db.task[w.task].url)

    def onLoading(self, body):
        db = self.db
        db(db.task.url==body.url).update(status="loading")

    def onSaving(self, body):
        db = self.db
        db(db.task.url==body.url).update(status="saving")

# start eventq ################################################

def restart():
    """ start eventq listener in background """
    # delete existing to make sure only one eventq running
    eventq = Eventq()
    eventq.delete()
    p = mp.Process(target=eventq_process, args=(onCompleteAll,))
    p.start()

def eventq_process(onCompleteAll):
    """ eventq background process """
    eventq = Eventq()
    eventq.listen(onCompleteAll)
