import logging
import redis_lock
import json
from . import util
from .run_at import RunAt

log = logging.getLogger(__name__)

class Job:
    def __init__(self, name, period, at, func, redis, config, params):
        self.name = name
        self.period = period
        self.at = at
        self.func = func
        self.redis = redis
        self.running = False
        self.config = config
        self.params = params
        self.params["healthFailureCount"] = self.params.get("healthFailureCount") or 0
        #put params in redis
        self.exception = False
        self.redis.set(self.last_ran_key()+":params", json.dumps(params))

    def __repr__(self):
        temp = {} #removing_redis
        temp['name'] = self.name
        temp['period'] = self.period
        temp['at']=self.at
        temp['running'] = self.running
        # temp['config'] = self.config
        temp['params'] = self.params
        return temp
        # return json.dumps(temp, default=lambda x: getattr(x, '__dict__', str(x)))


    def run(self, now):
        lock = redis_lock.Lock(self.redis, self.name, expire=self.config["timeout"])
        if lock.acquire(blocking=False):
            try:
                if not self.ready_to_run(now):
                    return
                log.info("running job %s", self.name)

                self.running = True
                self.set_last_ran(now)

                try:
                    #read params from redis, to get updated values 
                    self.params = json.loads(self.redis.get(self.last_ran_key()+":params"))
                    self.func(self.params)
                except:
                    log.exception("%s job failed to run! Paused" % self.name)
                    self.exception = True
            finally:
                lock.release()
        else:
            log.info("could not acquire lock for job %s", self.name)
        self.running = False

    def ready_to_run(self, now):
        last_ran = self.last_ran(now)
        run_at = RunAt(self.period, self.at, now, self.config['timezone'], offset=last_ran).next_at()
        log.debug("%s next run is at %s, now is at %s, last ran was at %s", self.name, run_at, now, last_ran)
        if run_at > now or last_ran > now or self.exception:
            return False

        log.debug("%s run_at: %s, last_ran: %s, now: %s", self.name, run_at, last_ran, now)
        return True

    def last_ran_key(self):
        return "mani:job:%s" % self.name

    def set_last_ran(self, now):
        self.redis.set(self.last_ran_key(), util.to_timestamp_utc(now))

    def last_ran(self, now):
        last_ran = self.redis.get(self.last_ran_key())
        if last_ran:
            return util.to_datetime(last_ran)

        # new job
        last_ran = RunAt(self.period, self.at, now, self.config['timezone']).last_at()
        log.debug("%s new job, last ran would have been at %s", self.name, last_ran)

        return last_ran

    def is_running(self):
        return self.running

    def update_params(self, obj):
        self.params.update(obj)
        self.redis.set(self.last_ran_key()+":params", json.dumps(self.params))
    
    # def get_params(self):
    #     unpacked_object = json.loads(self.redis.get(self.last_ran_key()+":params").decode('utf-8'))
    #     return unpacked_object
