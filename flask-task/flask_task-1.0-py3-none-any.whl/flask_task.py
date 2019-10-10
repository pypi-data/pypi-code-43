from threading import Thread
import time, logging

class Task(Thread):
    def __init__(self, app=None, interval=5, multi=False):
        Thread.__init__(self)

        self.multi = multi
        self.working = False
        self.app = app

        self.interval = interval
        self.task = None
        if self.app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def decorator(self, func):
        self.task = func
        self.start()

    def run(self):
        while True:
            if self.app:
                with self.app.app_context():
                    start_time = time.time()
                    try:
                        self.task()
                    except Exception as err:
                        logging.error(err)
                    total_time = int(time.time() - start_time)
                    if total_time >= self.interval:
                        logging.warning('the process time is longer than the interval')
                        continue
                    interval = self.interval - total_time
                    time.sleep(interval)