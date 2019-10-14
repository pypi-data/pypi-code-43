
import gc
import logging
import os
import pytz
import signal
import socket
import time
from datetime import datetime
import json
from .job import Job
from . import util

log = logging.getLogger(__name__)

class Scheduler:

    DEFAULT_CONFIG = {
      "timeout": 60,
      "heartbeat_key": "mani:heartbeat",
      "timezone": pytz.utc
    }

    TRAPPED_SIGNALS = (
        signal.SIGINT,
        signal.SIGTERM,
        signal.SIGQUIT
    )

    def __init__(self, redis, config = {}):
        self.jobs = {}
        self.redis = redis
        self.host = socket.gethostname()
        self.pid = os.getpid()

        self.running = False
        self.stopped = False

        self.config = self.DEFAULT_CONFIG.copy()
        self.config.update(config)
        # load existing jobs from redis
        # for key in r.scan_iter("mani:job:*"):


    def add_job(self, period, at, job_func, job_params ={}):   
        name = job_params.get("job_id") if job_params.get("job_id") else job_func.__name__
        if name in self.jobs:
            raise "duplicate job %s" % name
        
        job = Job(name, period, at, job_func, self.redis, self.config, job_params)
        self.jobs[name] = job
        return job

    def start(self):
        self.running = True
        self.trap_signals()
    
        while True:
            if self.stopped: break

            now = self.now()

            jobs = self.jobs_to_run(now)
            for job in jobs:
                job.run(now)

            self.heartbeat(now)

            if self.stopped: break

            self.sleep_until_next_second()

        log.info("stopped")

    def jobs_to_run(self, now):
        return filter(lambda j: j.ready_to_run(now), self.jobs.values())

    def heartbeat(self, now):
        ts = util.to_timestamp(now)
        self.redis.hset(self.config["heartbeat_key"], self.heartbeat_field(), ts)

    def heartbeat_field(self):
        return "%s##%s" % (self.host, self.pid)

    def now(self):
        return datetime.utcnow().replace(tzinfo=pytz.utc)

    def trap_signals(self):
        try:
            for sig in self.TRAPPED_SIGNALS:
                signal.signal(sig, self.stop)
        except ValueError: # for tests to pass (since it runs on a thread)
            log.warning("could not add handlers for trapping signals")

    def stop(self, _signal=None, _frame=None):
        self.stopped = True

    def sleep_until_next_second(self):
        # process gets hot otherwise
        gc.collect()

        now = self.now()
        sleeptime = 1.0 - (now.microsecond / 1000000.0)
        time.sleep(sleeptime)

    def get_printable_jobs(self):
        return [ self.jobs[x].__repr__() for x in (self.jobs)]

    def load_jobs(self, func):
        _jobs={}
        for key in self.redis.scan_iter("mani:job:*:params"):
            i=key.find(":params")
            job_name=key[9:i]
            _jobs[job_name]=json.loads(self.redis.get(key))
        for (key,val) in _jobs.items():
            if(val):
                print("added {0}".format(val.get("job_id")))
                interval= val.get('pingInterval').split(' ')[0] #TODO: put interval splitting logic in utils
                self.add_job(float(interval), None, func, val)
        return _jobs