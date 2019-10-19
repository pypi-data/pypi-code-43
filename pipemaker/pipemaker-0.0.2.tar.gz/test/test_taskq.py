from time import sleep
from pipemaker.mp.taskq import Taskq
from pipemaker.mp.workers import start, stop_workers
from pipemaker.master.mastertask import MasterTask


def stop_consuming(delay):
    log.info(f"stopping after {delay} seconds")
    sleep(delay)
    taskq = Taskq()
    taskq.delete()

def task1(a,b,c):
    """ mock task that adds inputs """
    return a+b+c

def test_put():
    # reset
    taskq = Taskq()
    taskq.delete()

    # add task
    taskq = Taskq()
    task = MasterTask(task1)
    task.inputs = (1,2,3)
    taskq.put(task)

    # check it is on the queue
    taskq = Taskq()
    assert taskq.queue.method.message_count==1

def test_get():
    taskq = Taskq()

    p = Process(target=stop_consuming, args=(2,))
    p.start()
    taskq.listen()

    taskq = Taskq()
    assert taskq.queue.method.message_count == 0

def test_multitask():
    from pipemaker.utils.defaultlog import log
    taskq = Taskq()
    taskq.delete()
    taskq = Taskq()

    start()

    delays = [10, 0, 0, 0, 0, 0, 0]
    for n in range(7):
        task = MasterTask()
        task.name = f"name={n}"
        task.inputs = dict(a=delays[n])
        task.delay =delays[n]
        taskq.put(task)
        log.info(f"put {n}")

    log.info("stopping")
    sleep(5)
    stop_workers()
    log.info("stopped")

    # todo use captured output
    log.info("check task 0 is last to complete")