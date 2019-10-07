import queue
import threading
import peewee as pw

db = pw.SqliteDatabase(
    'test.db',
#     threadlocals=True
)


class Container(pw.Model):
    contents = pw.CharField(default="spam")

    class Meta:
        database = db


class FeederThread(threading.Thread):

    def __init__(self, input_queue):
        super().__init__()

        self.q = input_queue

    def run(self):
        containers = Container.select()

        for container in containers:
            self.q.put(container)


class ReaderThread(threading.Thread):

    def __init__(self, input_queue):
        super().__init__()

        self.q = input_queue

    def run(self):
        while True:
            item = self.q.get()

            with db.execution_context() as ctx:
                # Get a new connection to the container object:
                container = Container.get(id=item.id)
                container.contents = "eggs"
                container.save()

            self.q.task_done()


if __name__ == "__main__":

    db.connect()
    try:
        db.create_tables([Container, ])
    except pw.OperationalError:
        pass
    else:
        [Container.create() for c in range(42)]
    db.close()

    q = queue.Queue(maxsize=10)

    feeder = FeederThread(q)
    feeder.setDaemon(True)
    feeder.start()

    for i in range(10):
        reader = ReaderThread(q)
        reader.setDaemon(True)
        reader.start()

    q.join()
