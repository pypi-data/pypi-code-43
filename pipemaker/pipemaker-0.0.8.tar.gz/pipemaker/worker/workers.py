import multiprocess as  mp
import pandas as pd
import os
from ..queues.taskq import Taskq
from ..utils.defaultlog import log

def start(n=None, name=None):
    """ start workers locally """

    # defaults
    if n is None:
        n = os.cpu_count() - 1
    if name is None:
        # Processes are named after Scottish girls.
        # https://www.nrscotland.gov.uk/statistics-and-data/statistics/statistics-by-theme/vital-events/names
        here = os.path.dirname(os.path.abspath(__file__))
        df = pd.read_csv(f"{here}/babies-first-names-top-100-girls.csv").FirstForename.drop_duplicates()
        name = df.sample(1).iloc[0]

    # launch
    log.info(f"starting workers {name} n={n}")
    for i in range(n):
        p = mp.Process(target=worker_process, name=f"{name}_{i}")
        p.start()

def terminate():
    """ delete the taskq completely """
    taskq = Taskq()
    taskq.delete()


def stop_workers():
    """ stop all workers everywhere """
    taskq = Taskq()
    consumers = taskq.queue.method.consumer_count
    for n in range(consumers):
        taskq.put(taskq.STOP)

# def get_workers_local():
#     """ return number of local workers. NOTE api takes time to refresh.
#     """
#     r = requests.get("http://localhost:15672/api/queues/%2F/task_queue", auth=('guest', 'guest'))
#     if r.status_code==200:
#         taskq = dotdict(r.json())
#         return taskq.consumers
#     else:
#         raise Exception("api did not respond")

### process targets ##############################################################

def worker_process():
    """ taskq background process """
    from pipemaker.utils.defaultlog import log
    name = mp.current_process().name
    log.info(f"starting worker_process {name}")
    taskq = Taskq()
    taskq.listen()
    log.info(f"ending worker_process {name}")

